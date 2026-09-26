<#
.SYNOPSIS
    Renders the folio deck and the three production items as plain HTML and
    opens them in a real browser.

.DESCRIPTION
    The .dc.html sources need the design host's runtime (window.React) to
    boot, which is why they only preview inside VS Code. This script does
    the small part of that job the artwork actually depends on: it lifts
    each <section> out of the source, substitutes the values renderVals()
    would have produced, re-points the relative asset paths, and wraps the
    result in a page that links the real stylesheets from design-system/.

    Nothing is copied. The previews link deck.css and the item stylesheets
    by absolute path, so they always show the current state of the design
    system — re-run this script after an edit and reload the tab.

    What a static preview does NOT give you: the prop panel, slide
    navigation, and the speaker notes. Pass the prop values as parameters
    instead. Everything that matters for judging print — true millimetre
    sizing, hairline weights, the webfonts, Ctrl+scroll zoom and a
    print-at-100% proof — behaves exactly as it does in the host.

.PARAMETER Item
    Which to build: folio, spine, tag, labels, mounts, meta, or
    all (default). meta is the design notes page: the design process and
    the graphic elements, drawn by the live deck.css. It includes the full
    colour system, token derivation, and masthead transitions. mounts is
    the A4 cutting scaffold for the experiment mounts on folio
    pages 9-11: the same slots at the same size, on paper an A4 printer
    can take. Print it at 100% with margins None and check its 100 mm bar.

.PARAMETER OutDir
    Where to write. Defaults to folio-preview in the system temp folder.

.PARAMETER Browser
    Path to a browser executable. Defaults to Chrome, then Edge, then
    whatever the shell has registered for .html.

.PARAMETER Guides
    Folio: overlay the six-column grid and the margin box. Spine: outline
    the trim inside the bleed. Equivalent to the showGuides / showTrim props.

.PARAMETER Bleed
    Folio: corner crop marks and the 3 mm bleed box. Equivalent to the
    showBleed prop.

.PARAMETER DashedSlots
    Mounts: draw the mount outlines as dashed cut guides rather than the
    hairline the A3 page prints. The slots are border-box, so this changes
    the look of the rule and not the size of the box. Equivalent to the
    dashedSlots prop.

.PARAMETER NoOpen
    Build once without launching a browser, and exit. This is the mode for
    tools and CI (print_pdfs.py uses it): no watching, no reload script.

.PARAMETER NoWatch
    Build once, open, and exit. Without it the script keeps running after
    it opens the browser and rebuilds whenever a file under design-system/
    changes. The built pages poll a small stamp file that each rebuild
    rewrites and reload themselves when it changes, keeping their scroll
    position: save a file, look at the browser. Ctrl+C stops watching. An
    edit to this script itself needs a restart.

.EXAMPLE
    .\scripts\preview.ps1
    Build everything and open it.

.EXAMPLE
    .\scripts\preview.ps1 -Item folio -Guides -Bleed
    The twelve pages with the production overlays on.

.EXAMPLE
    .\scripts\preview.ps1 -Item mounts
    The three A4 mount scaffolds, ready to print and cut against.

.EXAMPLE
    .\scripts\preview.ps1 -Item tag, labels
    The three swing tag designs side by side, to choose between.

.EXAMPLE
    .\scripts\preview.ps1 -Wine '#9A4656' -StudentNo 12345678 -NoOpen
    Try another wine colour and build without opening a window.

.EXAMPLE
    .\scripts\preview.ps1 -Item folio -NoWatch
    Build and open the folio once, then return to the prompt.
#>
[CmdletBinding()]
param(
    [ValidateSet('all', 'folio', 'spine', 'tag', 'labels', 'mounts', 'meta')]
    [string[]] $Item = @('all'),

    [string] $OutDir = (Join-Path ([System.IO.Path]::GetTempPath()) 'folio-preview'),
    [string] $Browser,
    [switch] $NoOpen,
    [switch] $NoWatch,

    # Internal: set by the watch loop when it re-runs this script for a
    # rebuild, so the child builds and returns instead of watching again.
    [Parameter(DontShow)]
    [switch] $Rebuild,

    [switch] $Guides,
    [switch] $Bleed,
    [switch] $DashedSlots,

    [string] $Slate = '#4A4E69',
    [string] $Wine = '#8C3B4A',
    [string] $StudentNo = '12345678',
    [string] $GownSize = '10',

    # Trim height of the spine's cream band, in mm. The art box adds 3 mm
    # of bleed to it and the 60 degree slant re-derives from the total,
    # which is what the bandH prop does.
    [int] $SpineBandH = 44
)

$ErrorActionPreference = 'Stop'

$repo = Split-Path $PSScriptRoot -Parent
$ds = Join-Path $repo 'design-system'
if (-not (Test-Path $ds)) { throw "design-system not found at $ds" }

# file:/// URI for the design-system folder, used both for the stylesheet
# links and for repointing the sources' relative ./assets/ references.
# A Linux path already starts with / and a Windows one does not, so the
# slash is added only where it is missing: file:///C:/... and file:///home/...
$dsPath = $ds -replace '\\', '/'
if (-not $dsPath.StartsWith('/')) { $dsPath = '/' + $dsPath }
$dsUri = 'file://' + ($dsPath -replace ' ', '%20') + '/'

# ---------------------------------------------------------------------------
# Production overlays. The deck's own chrome() builds these as React
# elements from the showGuides / showBleed props; this is the same geometry
# as static HTML, so a preview can be checked against the margins and the
# trim without booting the runtime.
# ---------------------------------------------------------------------------
function New-Chrome {
    param([switch] $WithGuides, [switch] $WithBleed)

    if (-not ($WithGuides -or $WithBleed)) { return '' }
    $parts = New-Object System.Collections.Generic.List[string]

    if ($WithGuides) {
        $cols = (1..6 | ForEach-Object { '<div style="background:rgba(217,138,159,0.16)"></div>' }) -join ''
        $parts.Add('<div style="position:absolute;top:15mm;bottom:15mm;left:25mm;right:15mm;display:grid;grid-template-columns:repeat(6,1fr);column-gap:5mm">' + $cols + '</div>')
        $parts.Add('<div style="position:absolute;top:15mm;bottom:15mm;left:25mm;right:15mm;outline:0.25mm dashed rgba(26,26,26,0.5)"></div>')
    }

    if ($WithBleed) {
        foreach ($v in 'top', 'bottom') {
            foreach ($h in 'left', 'right') {
                $parts.Add('<div style="position:absolute;background:#1A1A1A;height:0.2mm;width:8mm;' + $v + ':3mm;' + $h + ':0mm"></div>')
                $parts.Add('<div style="position:absolute;background:#1A1A1A;width:0.2mm;height:8mm;' + $v + ':0mm;' + $h + ':3mm"></div>')
            }
        }
        $parts.Add('<div style="position:absolute;inset:3mm;outline:0.2mm dotted rgba(26,26,26,0.55)"></div>')
    }

    return '<div style="position:absolute;inset:0;pointer-events:none;z-index:5">' + ($parts -join '') + '</div>'
}

# ---------------------------------------------------------------------------
# The documents. `Vals` mirrors each component's renderVals(); `W`/`H`
# are the design size, needed because a .page sets only its height and takes
# its width from the deck-stage canvas.
# ---------------------------------------------------------------------------
$docs = [ordered]@{
    folio  = @{
        Out = 'folio.html'; Source = 'Folio Deck.dc.html'; Css = $null
        Name = 'The Raven''s Ledger'; Sub = 'Folio deck, twelve pages, A3 297 x 420 mm'
        W = '297mm'; H = '420mm'
        Vals = @{
            slate = $Slate; wine = $Wine; bandHmm = '26mm'; studentNo = $StudentNo
            gownSize = $GownSize
            chrome = (New-Chrome -WithGuides:$Guides -WithBleed:$Bleed)
        }
    }
    spine  = @{
        Out = 'binder-spine.html'; Source = 'Binder Spine Insert.dc.html'; Css = 'binder-spine.css'
        Name = 'Binder spine insert'; Sub = 'A2 sheet 420 x 594 mm, trim 59 x 436 mm'
        W = '420mm'; H = '594mm'
        Vals = @{
            slate = $Slate; wine = $Wine; studentNo = $StudentNo
            bandHmm = "$($SpineBandH + 3)mm"
            trimOutline = $(if ($Guides) { '0.2mm dotted rgba(26,26,26,0.55)' } else { 'none' })
        }
    }
    tag    = @{
        Out = 'swing-tag.html'; Source = 'Swing Tag.dc.html'; Css = 'swing-tag.css'
        Name = 'Swing tag'; Sub = 'A4 sheet, trim 70 x 120 mm, front and back'
        W = '210mm'; H = '297mm'
        Vals = @{ slate = $Slate; wine = $Wine; gownSize = $GownSize; studentNo = $StudentNo }
    }
    labels = @{
        Out = 'product-labels.html'; Source = 'Product Labels.dc.html'; Css = 'product-labels.css'
        # Sheets 1 and 2 are the same run as it reads and mirrored; the
        # orientation is fixed in each section, not a value.
        Name = 'Product labels'; Sub = 'A4 x 4, patch 71 x 48 mm, dress, overskirt and collar, as it reads and mirrored'
        W = '210mm'; H = '297mm'
        Vals = @{ gownSize = $GownSize; studentNo = $StudentNo }
    }
    # The A4 cutting scaffold for folio pages 9-11. Its .ms-sheet is sized
    # 100% x 100% rather than 210 x 297mm - the deck host takes the sheet
    # size from the x-import attributes and this preview from W/H below, and
    # the slots inside are in millimetres either way. That is the whole point
    # of the document, so W/H here are the real A4 and the mounts land at
    # the same size they do on the A3 folio.
    mounts = @{
        Out = 'mount-scaffold.html'; Source = 'Mount Scaffold A4.dc.html'; Css = 'mount-scaffold.css'
        Name = 'Mount scaffold'; Sub = 'A4 x 3, 36 experiment mounts at 34.9 x 28.5 mm - print at 100%, margins None'
        W = '210mm'; H = '297mm'
        Vals = @{
            accent = '#C9A264'; studentNo = $StudentNo
            slotRule = $(if ($DashedSlots) { '0.25mm dashed #1A1A1A' } else { '0.12mm solid #1A1A1A' })
            calDisplay = 'flex'
        }
    }
    # The design notes: a static page, no sections and no tokens, that
    # links deck.css and draws the type, the house mark, the rules, the
    # plates and the colourways with the folio's own classes. It explains
    # the design process and keeps a ledger of changes at its foot.
    meta   = @{
        Out = 'design-notes.html'; Static = 'meta/design-process.html'
        Name = 'Design notes'; Sub = 'The design process and the graphic elements, drawn by the live stylesheet'
    }
}

$wanted = if ($Item -contains 'all') { @($docs.Keys) } else { $Item }

# ---------------------------------------------------------------------------
$head = @"
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,900&family=PT+Serif:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="${dsUri}deck.css">
"@

$shellCss = @"
  html { background: #6E6E6E; }
  body { margin: 0; padding: 0 0 60px; font-family: 'PT Serif', Georgia, serif; }
  /* Every shell class is pv- prefixed. The artwork's own stylesheets are
     linked into this page unscoped, so a bare name here lands on the
     sheets too: .bar was the swing tag's divider hairline, and the
     toolbar's padding turned it into a black block. */
  .pv-bar { position: sticky; top: 0; z-index: 30; background: #1A1A1A; color: #F5EFE2;
         font-size: 13px; line-height: 1.4; padding: 9px 16px; display: flex; gap: 16px;
         align-items: baseline; flex-wrap: wrap; }
  .pv-bar b { font-weight: 700; }
  .pv-bar a { color: #EECAD4; }
  .pv-bar span { opacity: 0.6; font-size: 12px; }
  .stack { display: flex; flex-direction: column; align-items: center; gap: 30px; padding-top: 26px; }
  .pv-tag { font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase;
            color: #E4E0E0; margin: 0 0 6px 2px; }
  /* Sheets carry their own millimetre size; .pv pins the design box so an
     element that overruns is clipped at the page edge rather than silently
     making the box taller. That is the overflow probe. */
  .pv { position: relative; overflow: hidden; box-shadow: 0 2px 14px rgba(0,0,0,0.4); flex: none; }

  /* Print: the sheet alone, one per page, at its authored millimetre size.
     Everything the shell adds for reading on screen - the sticky toolbar,
     the page labels, the stack's gap and top padding, the body's bottom
     padding - is layout above and around the sheet, so leaving any of it
     in shifts the artwork down the paper and spills the tail of it onto a
     second sheet. That is the whole point of a true-size proof, so all of
     it goes. The @page rule that names the paper is emitted per document,
     from its own W/H, next to this block. */
  @media print {
    html { background: #FFF; }
    body { margin: 0; padding: 0; }
    .pv-bar, .pv-tag { display: none !important; }
    .stack { display: block; padding: 0; gap: 0; }
    /* Backgrounds and hairlines are the artwork, not decoration the
       browser may drop to save ink. */
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .pv {
      box-shadow: none;
      break-inside: avoid;
      page-break-inside: avoid;
      /* Size containment: an absolutely positioned child that overruns the
         design box must not count toward the print document's width, or
         Chromium shrinks the whole proof to fit and the millimetres lie.
         Safe here because .pv is sized outright by its inline width/height. */
      contain: size;
    }
    .stack > div { break-after: page; page-break-after: always; }
    .stack > div:last-child { break-after: auto; page-break-after: auto; }
  }
"@

# ---------------------------------------------------------------------------
# Live reload. The pages are file:// URLs, so there is no server to push a
# change and fetch() of a sibling file is blocked. A <script src> of one is
# not, so each page re-adds a script tag for live-reload.js every 600 ms.
# Each rebuild rewrites that file with a new stamp. The page remembers the
# first stamp it sees and reloads when the stamp changes, so a page left
# over from an earlier run reloads once per rebuild rather than looping.
# Scroll position is carried across the reload in sessionStorage. Tools and
# CI build with -NoOpen and get none of this.
# ---------------------------------------------------------------------------
$live = $Rebuild -or -not ($NoOpen -or $NoWatch)
$reloadJs = if (-not $live) { '' } else {
    @'
<script>
(function () {
  var key = 'pv-scroll:' + location.pathname, seen = null;
  try {
    var at = JSON.parse(sessionStorage.getItem(key) || 'null');
    sessionStorage.removeItem(key);
    if (at) addEventListener('load', function () { scrollTo(at[0], at[1]); });
  } catch (e) {}
  function poll() {
    var el = document.createElement('script');
    el.src = './live-reload.js?t=' + Date.now();
    el.onload = el.onerror = function () {
      el.remove();
      var now = window.__pvStamp;
      if (seen !== null && now && now !== seen) {
        try { sessionStorage.setItem(key, JSON.stringify([scrollX, scrollY])); } catch (e) {}
        location.reload();
        return;
      }
      if (now) seen = now;
      setTimeout(poll, 600);
    };
    document.head.appendChild(el);
  }
  poll();
})();
</script>
'@
}

$built = @()

foreach ($key in $wanted) {
    $doc = $docs[$key]

    # Static pages pass through whole: no sections, no tokens. Their source
    # sits one level under design-system/, so ../ refs resolve to the
    # design-system root - the same repointing trick as ./ below, one level
    # up. The shell toolbar is injected so navigation matches the built items.
    if ($doc.Static) {
        $src = Join-Path $ds $doc.Static
        if (-not (Test-Path $src)) { Write-Warning "skipped $key - $($doc.Static) not found"; continue }

        $raw = Get-Content -LiteralPath $src -Raw
        $raw = [regex]::Replace($raw, '(?<=["''(])\.\./', $dsUri)
        # The toolbar is screen chrome: it sits above the page in flow, so
        # printing with it in place pushes the artwork down the paper.
        # A static page ships its own head, so the print rule rides along
        # with the bar rather than going into $shellCss.
        $bar = '<style>@media print { .pv-bar { display: none !important; } ' +
               'body { margin: 0; padding: 0; } ' +
               '* { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }</style>' +
               '<div class="pv-bar" style="position:sticky;top:0;z-index:30;background:#1A1A1A;color:#F5EFE2;' +
               'font:13px/1.4 ''PT Serif'',Georgia,serif;padding:9px 16px;display:flex;gap:16px;' +
               'align-items:baseline;flex-wrap:wrap"><b>' + $doc.Name + '</b>' +
               '<span style="opacity:0.6;font-size:12px">' + $doc.Sub + '</span>' +
               '<a href="./index.html" style="color:#EECAD4">&larr; all items</a></div>' + $reloadJs
        $raw = $raw -replace '<body>', ('<body>' + $bar)

        if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
        $dest = Join-Path $OutDir $doc.Out
        Set-Content -LiteralPath $dest -Value $raw -Encoding UTF8
        $built += [pscustomobject]@{ Key = $key; Name = $doc.Name; Sub = $doc.Sub; File = $doc.Out; Pages = 1 }
        Write-Host "  $($doc.Name.PadRight(22)) 1 page(s)  ->  $dest"
        continue
    }

    $src = Join-Path $ds $doc.Source
    if (-not (Test-Path $src)) { Write-Warning "skipped $key - $($doc.Source) not found"; continue }

    $raw = Get-Content -LiteralPath $src -Raw

    # Not $matches - that is an automatic variable and assigning to it here
    # would clobber the engine's own capture state.
    $sections = [regex]::Matches($raw, '(?s)<section([^>]*)>(.*?)</section>')
    if ($sections.Count -eq 0) { Write-Warning "skipped $key - no <section> found"; continue }

    $unresolved = New-Object System.Collections.Generic.HashSet[string]
    $pages = foreach ($m in $sections) {
        $attrs = $m.Groups[1].Value
        $body = $m.Groups[2].Value

        # Substitute the way renderVals() does; an unknown token renders
        # empty and is reported, which is how the runtime treats it too.
        $body = [regex]::Replace($body, '\{\{\s*(\w+)\s*\}\}', {
                param($mm)
                $k = $mm.Groups[1].Value
                if ($doc.Vals.Contains($k)) { [string]$doc.Vals[$k] }
                else { [void]$unresolved.Add($k); '' }
            })

        # Relative refs are resolved against the source's own folder, not
        # against wherever this preview is written.
        $body = [regex]::Replace($body, '(?<=["''(])\./', $dsUri)

        $label = ([regex]::Match($attrs, 'data-label="([^"]*)"')).Groups[1].Value
        if (-not $label) { $label = '&nbsp;' }

        "<div><div class=`"pv-tag`">$label</div><div class=`"pv`" style=`"width:$($doc.W);height:$($doc.H)`">$body</div></div>"
    }

    if ($unresolved.Count) { Write-Warning "$key - unresolved tokens: $($unresolved -join ', ')" }

    # Css is one sheet or an ordered list of them; tag 2 needs tag 1's sheet
    # underneath its own, so the links are emitted in the order given.
    $itemCss = ''
    foreach ($sheet in @($doc.Css | Where-Object { $_ })) {
        $itemCss += "`n<link rel=`"stylesheet`" href=`"$dsUri$sheet`">"
    }
    $title = "$($doc.Name) - $($doc.Sub)"

    $html = @"
<!DOCTYPE html><html><head><meta charset="utf-8">
<title>$title</title>
$head$itemCss
<style>
$shellCss
  /* Ask for the paper the sheet was drawn on, with no printer margin of
     its own: A3 for the folio, A2 for the spine, A4 for the rest. Without
     this the browser paginates the design box against Letter or A4 and
     scales it, and nothing on the sheet measures what it says. */
  @page { size: $($doc.W) $($doc.H); margin: 0; }
</style></head><body>
<div class="pv-bar">
  <b>$($doc.Name)</b>
  <span>$($doc.Sub) &middot; $($sections.Count) page(s)</span>
  <a href="./index.html">&larr; all items</a>
  <span>Ctrl + scroll to zoom &middot; Ctrl+0 resets &middot; Ctrl+P prints at true size</span>
</div>
<div class="stack">
$($pages -join "`n")
</div>
$reloadJs
</body></html>
"@

    if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
    $dest = Join-Path $OutDir $doc.Out
    Set-Content -LiteralPath $dest -Value $html -Encoding UTF8
    $built += [pscustomobject]@{ Key = $key; Name = $doc.Name; Sub = $doc.Sub; File = $doc.Out; Pages = $sections.Count }
    Write-Host "  $($doc.Name.PadRight(22)) $($sections.Count) page(s)  ->  $dest"
}

if (-not $built) { throw 'nothing was built' }

# ---------------------------------------------------------------------------
# Index. Always lists every document so the folio sits beside the items even
# when only one of them was rebuilt; a card for something not yet built
# still resolves once you run the script without -Item.
# ---------------------------------------------------------------------------
$flags = @()
if ($Guides) { $flags += 'guides' }
if ($Bleed) { $flags += 'bleed' }
if ($DashedSlots) { $flags += 'mount slots dashed' }
if ($Slate -ne '#4A4E69') { $flags += "slate $Slate" }
if ($Wine -ne '#8C3B4A') { $flags += "wine $Wine" }
$flagLine = if ($flags) { ' &middot; ' + ($flags -join ' &middot; ') } else { '' }

$cards = foreach ($key in $docs.Keys) {
    $d = $docs[$key]
    $b = $built | Where-Object Key -EQ $key
    $state = if ($b) { "$($b.Pages) page(s)" } else { 'not built in this run' }
    $cls = if ($b) { 'card' } else { 'card stale' }
    "<a class=`"$cls`" href=`"./$($d.Out)`"><b>$($d.Name)</b><span>$($d.Sub)</span><em>$state</em></a>"
}

$index = @"
<!DOCTYPE html><html><head><meta charset="utf-8">
<title>The Raven's Ledger - previews</title>
$head
<style>
  body { background: #F5EFE2; color: #1A1A1A; font-family: 'PT Serif', Georgia, serif; margin: 0; padding: 46px 40px 60px; }
  h1 { font-family: Fraunces, Georgia, serif; font-weight: 900; font-size: 30px; line-height: 1.05; margin: 0 0 4px; }
  .lede { font-size: 14px; color: #5A5052; margin: 0 0 30px; max-width: 74ch; line-height: 1.5; }
  .card { display: block; max-width: 660px; margin-bottom: 10px; padding: 14px 18px;
          background: #FEFBFC; border-left: 4px solid #8AA3BC; text-decoration: none; color: #1A1A1A; }
  .card:hover { background: #EDF1F5; }
  .card b { display: block; font-family: Fraunces, Georgia, serif; font-weight: 900; font-size: 18px; }
  .card span { display: block; font-size: 13px; color: #5A5052; margin-top: 2px; }
  .card em { display: block; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase;
             font-style: normal; color: #8A8082; margin-top: 5px; }
  .card.stale { border-left-color: #C9BEC1; opacity: 0.55; }
  .foot { font-size: 12px; color: #6A6062; margin-top: 30px; line-height: 1.6; max-width: 74ch; }
  code { font-family: 'Courier New', monospace; background: #EAE2D3; padding: 1px 4px; }
</style></head><body>
<h1>The Raven&rsquo;s Ledger</h1>
<div class="lede">Static previews rendered from the .dc.html sources against the live stylesheets in <code>design-system/</code>. Sheets are sized in real millimetres: Ctrl&nbsp;+&nbsp;scroll to zoom freely, Ctrl+P to print a true-size proof.$flagLine</div>
$($cards -join "`n")
<div class="foot">While <code>pwsh .\scripts\preview.ps1</code> is running, every save under <code>design-system/</code> rebuilds these pages and the open tabs reload themselves. Without it running, re-run the script and reload.<br>
Options: <code>-Item folio|spine|tag|labels|mounts|meta</code>, <code>-Guides</code>, <code>-Bleed</code>, <code>-DashedSlots</code>, <code>-Slate</code>, <code>-Wine</code>, <code>-GownSize</code>, <code>-StudentNo</code>, <code>-NoWatch</code>, <code>-NoOpen</code>. Run <code>Get-Help .\scripts\preview.ps1 -Full</code> for the rest.</div>
$reloadJs
</body></html>
"@

$indexPath = Join-Path $OutDir 'index.html'
Set-Content -LiteralPath $indexPath -Value $index -Encoding UTF8
Write-Host "  index                  ->  $indexPath"

# Written last, so a page that sees the new stamp reloads into finished files.
if ($live) {
    $stamp = [DateTime]::UtcNow.Ticks
    Set-Content -LiteralPath (Join-Path $OutDir 'live-reload.js') -Value "window.__pvStamp = '$stamp';" -Encoding UTF8
}

# ---------------------------------------------------------------------------
if ($NoOpen -or $Rebuild) { return }

function Resolve-Browser {
    param([string] $Explicit)
    if ($Explicit) {
        if (Test-Path $Explicit) { return $Explicit }
        Write-Warning "browser not found at $Explicit - falling back"
    }
    $candidates = @(
        (Join-Path $env:ProgramFiles 'Google\Chrome\Application\chrome.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'Google\Chrome\Application\chrome.exe'),
        (Join-Path $env:ProgramFiles 'Microsoft\Edge\Application\msedge.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe')
    )
    foreach ($c in $candidates) { if ($c -and (Test-Path $c)) { return $c } }
    return $null
}

# A single target keeps repeat runs from stacking up tabs: the same file
# path reloads in place if the tab is already open and you refresh it.
$target = if ($built.Count -eq 1) { Join-Path $OutDir $built[0].File } else { $indexPath }

$exe = Resolve-Browser -Explicit $Browser
if ($exe) {
    Start-Process -FilePath $exe -ArgumentList $target
    Write-Host "`nopened in $(Split-Path $exe -Leaf): $target"
}
else {
    # No known browser on disk; hand it to whatever the shell has registered.
    Start-Process -FilePath $target
    Write-Host "`nopened with the shell's registered handler: $target"
}

if ($NoWatch) { return }

# ---------------------------------------------------------------------------
# Watch. Each rebuild re-runs this script with the same parameters plus
# -Rebuild, so the build logic has one home. Editors often save in several
# writes (temp file, rename, touch), so the loop waits for 300 ms of quiet
# before it rebuilds. The output folder is not under design-system/, so the
# rebuild's own writes do not trigger another one.
# ---------------------------------------------------------------------------
$childArgs = @{}
foreach ($k in $PSBoundParameters.Keys) { $childArgs[$k] = $PSBoundParameters[$k] }
$childArgs.Rebuild = $true

$watcher = New-Object System.IO.FileSystemWatcher $ds
$watcher.IncludeSubdirectories = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, LastWrite, DirectoryName'

Write-Host "`nwatching $ds - save a file and the open tabs reload. Ctrl+C stops."
try {
    while ($true) {
        $change = $watcher.WaitForChanged([System.IO.WatcherChangeTypes]::All, 500)
        if ($change.TimedOut) { continue }
        $names = [System.Collections.Generic.List[string]]::new()
        $names.Add($change.Name)
        while (-not ($next = $watcher.WaitForChanged([System.IO.WatcherChangeTypes]::All, 300)).TimedOut) {
            if (-not $names.Contains($next.Name)) { $names.Add($next.Name) }
        }

        Write-Host "`n$(Get-Date -Format 'HH:mm:ss')  changed: $($names -join ', ')"
        try { & $PSCommandPath @childArgs }
        catch { Write-Warning "rebuild failed: $($_.Exception.Message) - still watching" }
    }
}
finally {
    $watcher.Dispose()
}
