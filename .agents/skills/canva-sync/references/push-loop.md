# The push loop

One page at a time, inside a transaction, with a gate in front of it. Read `canva-connector.md` first if the
connector has not been probed yet.

## Before the first page

The gates in `SKILL.md` all have to have passed: `doctor`, `build --verify` with every page inside tolerance,
`extract`, an answered `ops --summary`, and a `probe` that matched. Nothing below is safe otherwise.

## Per page

1. **Open a transaction** for the design and note the transaction id. Everything below happens inside it, so a
   failure anywhere can be cancelled without leaving half a page in someone's account.

2. **Elements, in chunks.**

   ```text
   canva_sync.py ops --page 01 --phase elements --chunk-size 250 --chunk 1
   ```

   Without `--chunk` the command prints how many chunks there are, on stderr. With `--chunk N` it prints that
   chunk's operation array on stdout and nothing else, so it can be piped. Apply the chunks in order: they are
   in paint order, and applying them out of order stacks the page wrong. The first operation of chunk 1 carries
   the page's speaker notes.

   Chunk size is a trade-off against the connector's payload limit. 250 is a reasonable start; drop it if a
   call is rejected for size.

3. **Collect the text element ids.** The response echoes the page. The text elements, in document order, are
   the text operations in the order they were applied. Keep that list.

4. **Format.** Created text carries no styling, so every text element needs a follow-up:

   ```text
   canva_sync.py ops --page 01 --phase format --id-list id1,id2,id3
   ```

   or `--ids FILE`, or `--ids -` to read them from stdin, one per line. The count has to match the page's text
   count exactly; if it does not, the command says so and exits 1 rather than pairing styling with the wrong
   text. That mismatch usually means a chunk was applied twice or not at all.

5. **Look at it.** Fetch the page thumbnail and compare it with `<output_dir>/verify/out-01.png`. This is a
   human-level check, not a pixel one: is it the same page?

6. **Commit the transaction.**

## On the first page of an unverified dialect

`probe` can only confirm that the connector has the tools; it cannot always confirm that the operation names
mean what this pipeline thinks they mean. So on the very first page pushed with a dialect marked `unverified`:

- push chunk 1 only,
- read the page back and check that the shapes, the image frames and the text are all there,
- then run `check --dump -` for that page,

before pushing anything else. If the connector accepted the operations but produced nothing, the vocabulary is
wrong: stop, and say which operation types were sent.

## When something fails

Cancel the transaction. Report the page, the chunk, the operation index if the connector gives one, and the
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
