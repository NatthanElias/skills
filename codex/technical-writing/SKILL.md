---
name: technical-writing
description: Structure and revise documents people read, including READMEs, tutorials, how-to guides, runbooks, reference pages, design explanations, slide text, and PR descriptions. Use writing-for-agents for agent instructions.
---

# Technical writing

Write so a tired engineer understands the page on the first read. This skill owns document type, sentences, and layout. Apply `$unslop` for word choice, filler, voice, and AI patterns to every document it touches. Use `$writing-for-agents` for skills, agent definitions, instruction files, and references written primarily for agents. For academic papers, also follow the user's academic-writing requirements and applicable academic-writing skill.

When a rule makes a sentence worse, fix the sentence another way. Preserve meaning and the certainty of the source.

## Pick one Diátaxis type

Ask whether the reader wants to act or understand, and whether they are learning or working.

| Reader's goal | Learning | Working |
| --- | --- | --- |
| Act | Tutorial | How-to |
| Understand | Explanation | Reference |

- Tutorial. Open with what the reader builds. Every step produces a visible result; show the expected output, prompt, or log line. Keep explanation to one clause and a link. Write commands with a consistent guiding voice, using "we" where appropriate.
- How-to. Solve one problem for a competent reader. Give the actions. Offer forks as "If you want x, do y." Name the page by its task, such as "How to rotate the signing key". A runbook is a how-to.
- Reference. Describe facts, options, limits, and errors without instruction or opinion. Mirror the structure of the thing described. Generate it from code where practical.
- Explanation. Answer one real why-question through decisions, constraints, and alternatives. Interpretations and opinions belong here. An architecture decision record is an explanation.

Keep one primary type per page. Move substantial content of another type to its own page and link it when that improves navigation. A README introduces the project in one or two sentences and links the relevant guides. Retain essential getting-started information when the project needs it.

## Address the reader

- Use "you" and the present tense. Use "will" for events that happen later.
- Write instructions as commands, such as "Run `mvn test`."
- Put the condition or warning before the instruction so the reader can skip what does not apply.
- Put the common case first and exceptions after.
- Write procedures without "please", "simply", "easy", or "quickly".
- Describe what exists now. Leave promised features out.
- Use the target page's title or a short description as link text. Follow the client's file-link format for local artifacts.

## Make each sentence read one way

- Give each instruction its own sentence. Split sentences longer than about 20 words when that improves clarity.
- Keep articles, such as "Remove the backup file."
- Place "only" and "not" beside the word they modify.
- Unpack noun stacks, such as "the script that checks the proto import budget".
- Point each "it", "they", and "this" at one noun. Repeat the noun when needed.
- Give every clause its own verb.
- Keep "that" when it resolves ambiguity.
- Use "both...and" or "either...or" when grouping could be misread.
- End sentences with periods instead of joining instructions with semicolons. Write "a, b, or both" instead of "and/or".
- Write "for example" and "that is" instead of Latin abbreviations.
- Preserve the wording of sentences outside the requested edit.

## Lay out the page

Write headings that state the point. Task headings are verb phrases; concept headings are noun phrases. Use one h1 per standalone page and no skipped levels. Follow the surrounding hierarchy when editing a section.

Number sequences and use bullets for parallel items. Introduce lists with complete sentences and keep items parallel. Use connected prose when a list adds no clarity.

Put commands and symbols in code font, and UI labels in bold. Use real codebase names. Keep clickable paths as links when supported. Use serial commas. State when a list is partial instead of ending with "etc.".

For formatted documents or slide decks, use the applicable document or presentation skill for creation, rendering, and visual verification. These prose rules do not replace that workflow.

## PR descriptions

Apply the sentence and layout rules without forcing a Diátaxis type. Lead with the concrete problem and resulting behavior. Include relevant validation and material limitations. Link long logs, revision lists, and metric tables rather than pasting them. Follow the repository template.

## Review

Finish when each applicable item holds:

1. Pages have one primary type, with links where types meet.
2. Instructions are commands with their conditions first.
3. Instructions, pronouns, modifiers, and clause verbs have clear targets.
4. Each concept has one name throughout the documents.
5. Symbols, paths, counts, commands, and observed outputs match the relevant revision. Label anything unverified.
6. `$unslop` has been applied without changing meaning or source certainty.
