---
name: technical-writing
description: Writing documents for HUMANS. Use when writing or reviewing a README, tutorial, how-to, runbook, slide deck, reference page, design explanation, PR description, etc.
---

# Technical writing

Write so a tired engineer understands the page on the first read. This skill sets the document type, the sentences and the layout. `unslop` owns word choice, filler, voice and AI tells, so apply it to every document this skill touches. For skills, agent definitions and instruction files, use `writing-for-agents`.

When a rule makes a sentence worse, fix the sentence another way.

## Pick one Diátaxis type

Two questions pick the type: does the reader want to act or to understand, and are they learning or working?

| | Learning | Working |
| --- | --- | --- |
| Act | Tutorial | How-to |
| Understand | Explanation | Reference |

- **Tutorial.** Open with what the reader will build. Every step produces a visible result, so show the expected output, prompt or log line. Keep explanation to one clause and a link. Write as "we", in commands.
- **How-to.** Solve one problem the reader has. Assume competence and give only the actions. Offer forks as "If you want x, do y." Name the page by the task: "How to rotate the signing key". A runbook is a how-to.
- **Reference.** Describe facts, options, limits and errors with no instruction or opinion. Mirror the structure of the thing described. Generate it from code where possible.
- **Explanation.** Answer one real "why" question with design decisions, constraints and alternatives. Opinion belongs here and only here. An architecture decision record is an explanation.

Keep one type per page. When content of another type turns up, move it to its own page and link it. A README states what the project is in one or two sentences, then links to the other pages.

## Address the reader

- Talk to the reader as "you", in the present tense. Use "will" only for events that happen later.
- Write instructions as commands: "Run `make test`."
- Put the condition or warning before the instruction: "To delete the record, run...". The reader skips what does not apply.
- Put the common case first and the exceptions after.
- Write procedures without "please", "simply", "easy" or "quickly".
- Describe what exists now. Leave promised features out.
- Use the target page's title or a short description as link text.

## Make each sentence read one way

- Give each instruction its own sentence, and split one longer than about 20 words.
- Keep "the" and "a": "Remove the backup file", not "Remove backup file".
- Place "only" and "not" next to the word they change: "fails only on growth".
- Unpack noun stacks: "the script that checks the proto import budget", not "the proto import budget check script".
- Point every "it", "they" and "this" at one noun. Repeat the noun when in doubt.
- Give every clause its own verb: "Phase 1 moves the converters and Phase 2 moves the runtime."
- Keep "that" when it fixes the parse: "Ensure that the switch is off."
- Use "both...and" or "either...or" when "and" or "or" could group two ways.
- End sentences with periods instead of semicolons. Write "a, b, or both" instead of a slash or "and/or".
- Write "for example" and "that is" instead of Latin abbreviations.
- Keep the wording of sentences you did not change.

## Lay out the page

- Write headings that state the point. A task heading is a verb phrase and a concept heading is a noun phrase. Use one h1 per page and no skipped levels.
- Number sequences and bullet everything else. Introduce each list with a full sentence and keep the items parallel.
- Put code, paths, commands and symbols in code font, and UI labels in bold. Use the real name from the codebase.
- Use serial commas. Say up front when a list is partial instead of ending it with "etc.".

## PR descriptions

Apply every section except document type. A reviewer reads a PR description in under a minute. Link logs, SHA lists and metric tables instead of pasting them.

## Example

Before:

> Configuration of the proto import ratchet budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

After:

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos. If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.

## Review checklist

The review is done when every item passes. Item 1 applies only to a set of documents.

1. Each page has one document type, with links where types meet.
2. Every instruction is a command with its condition in front.
3. No sentence carries two instructions.
4. "Only" sits next to the word it changes, every pronoun points at one noun, and every clause has a verb.
5. Each thing has one name across the documents.
6. Every symbol, path and count is real at this commit.
7. `unslop` has been applied.
