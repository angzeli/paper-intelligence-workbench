# Reading Sessions

Reading sessions are local records that help a researcher track daily reading
without fabricating notes or claims.

## Purpose

A session records:

- paper being read
- project
- start and completion timestamps
- reading goal
- status before and after
- duration
- whether notes or claims were added
- user-provided follow-up actions

The tool does not read papers automatically and does not create session
outcomes unless the user supplies them.

## Commands

```bash
paperwb reading start PAPER_ID --project zis_photocatalysis --goal "Check evidence locations"
paperwb reading finish SESSION_ID --project zis_photocatalysis --status deeply_read --duration-minutes 45
paperwb reading status --project zis_photocatalysis
```

`reading start` creates a local session record and generates a note template
only when the note is missing. Existing notes are preserved unless
`--force-note` is explicitly provided. If an explicit `--out` report path
already exists, `reading start` and `reading finish` fail before changing the
registry, note, or session log unless `--force` is supplied.

Session logs default to:

```text
.paperwb/reading_sessions.jsonl
```

This path is ignored by git. To make reproducible reports for examples or
tests, pass an explicit `--sessions` path.

## Safety Rules

- Do not use sessions as evidence by themselves.
- Do not mark a paper as read unless the user finishes a session with a status.
- Do not overwrite note files without `--force-note`.
- Keep session summaries user-written.
- Treat `claims_added` as a user-supplied count, not proof that claims are
  complete.
- Treat warnings about malformed session logs or corrupt follow-up completion
  state as data-cleanup prompts. The CLI skips unreadable records instead of
  guessing.
