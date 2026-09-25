# The push loop

One page at a time, inside a transaction, with a gate in front of it. Read `canva-connector.md` first if the
connector has not been probed yet.

## Before the first page

The gates in `SKILL.md` all have to have passed: `doctor`, `build --verify` with every page inside tolerance,
`extract`, an answered `ops --summary`, and a `probe` that matched. Nothing below is safe otherwise.

## Pages that do not exist yet

A label with no page id in the local id file has no Canva page to push into. Add it first, in its own
transaction:

```text
canva_sync.py ops --page 05 --phase page
```

prints one `add_page` operation sized and coloured like the repo page. Apply it with `edit-design` on the last
existing page's `page_index`, read the design back, confirm the new page is where it belongs (`reorder_page`
moves it if not), commit once the person approves, then run `check --dump - --refresh-ids` so the new page's id is
recorded. Pages are mapped by position, so add them in label order.

## Per page

1. **Open a transaction.** `read-design` with `open_transaction: true` and `"thumbnails"` in `filter.fields`.
   Note the `transaction_id`. Everything below happens inside it, so a failure anywhere can be cancelled without
   leaving half a page in someone's account.

2. **Elements, in chunks.**

   ```text
   canva_sync.py ops --page 01 --phase elements --chunk-size 40 --chunk 1
   ```

   Without `--chunk` the command prints how many chunks there are, on stderr. With `--chunk N` it prints that
   chunk's operation array on stdout and nothing else, so it can be piped. Apply each chunk with `edit-design`:
   the `transaction_id`, the page's 1-based `page_index`, `finalize: "keep_open"` and the array as `operations`.
   Apply the chunks in order: they are in paint order, and applying them out of order stacks the page wrong. The
   first operation of chunk 1 carries the page's speaker notes.

   Chunk size is a trade-off against the connector's payload limit. 40 has gone through cleanly; drop it if a
   call is rejected for size.

3. **Save the last response.** Each `edit-design` call returns the draft page with every element's `id` and its
   text. Save the response to the last chunk as JSON under `<output_dir>/`.

4. **Format.** Created text carries no styling, so every text element needs a follow-up:

   ```text
   canva_sync.py ops --page 01 --phase format --from-dump <output_dir>/p01-elements.json
   ```

   pairs each repo text with the Canva element holding the same words and emits `format_text` operations
   addressed by locator id. It exits 1 and lists the texts it could not pair rather than guess; that usually
   means a chunk was applied twice or not at all. `--ids FILE` or `--id-list a,b,c` take ids in text order
   instead, and a bare element id is turned into a locator id with the page id. Apply the array with
   `edit-design` exactly as in step 2.

5. **Look at it.** `read-design` with the `transaction_id` and `"thumbnails"` returns the draft. Compare it with
   `<output_dir>/verify/out-01.png`. This is a human-level check, not a pixel one: is it the same page? Save the
   draft's design content and run `check --dump FILE --page 01`.

6. **Commit, with approval.** Show the person the preview and the check result, and commit (`finalize:
   "commit"`, no operations) only once they approve. The connector requires it and the commit cannot be undone.

## On the first page of an unverified dialect

`probe` can only confirm that the connector has the tools; it cannot always confirm that the operation names
mean what this pipeline thinks they mean. So on the very first page pushed with a dialect marked `unverified`:

- push chunk 1 only,
- read the page back and check that the shapes, the image frames and the text are all there,
- then run `check --dump -` for that page,

before pushing anything else. Once a whole page has gone through, been checked and committed, set the dialect's
`status` to `verified` and record the date in its description. If the connector accepted the operations but produced nothing, the vocabulary is
wrong: stop, and say which operation types were sent.

## When something fails

Cancel the transaction (`finalize: "cancel"`, no operations). Report the page, the chunk, the operation index if the connector gives one, and the
error. Do not retry the same chunk against a committed transaction, and do not move on to the next page: a
partial page is easier to fix than a partial design.

## After the push

```text
canva_sync.py check --dump design.json
canva_sync.py check --dump - --page 03
canva_sync.py check --dump design.json --refresh-ids
```

`--refresh-ids` writes the design id and the page ids from the dump into the local id file. That is how a fresh
Canva design gets wired up once its pages exist, and it is the only thing this tool writes outside the output
folder.

Text Canva has that the repository does not is either an edit someone made in Canva or a leftover from an
earlier push. Report it and let a person decide. The deck is not edited to agree with Canva.

## Without a local id file

Every operation carries the literal `PAGE_ID` and every image is a placeholder rectangle. That is enough to
generate and inspect operations on a fresh clone, which is exactly what `selftest` does.
