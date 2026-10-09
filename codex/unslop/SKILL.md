---
name: unslop
description: Cut AI patterns, filler, vague claims, and overcomplicated phrasing while preserving meaning. Use when writing or reviewing documentation, instructions, messages, or assistant-written prose.
---

# Unslop

Edit text to remove AI patterns and add human voice.

## Process

1. Scan for the patterns below.
2. Rewrite. Preserve meaning and match the intended tone. Keep an unverified claim as uncertain as the source left it.
3. Add soul, using the next section when it fits the text.
4. Self-audit: "What makes this obviously AI generated?" Fix remaining tells.

## Adding soul

Removing patterns is half the job. Sterile, voiceless writing is just as obvious. Apply voice choices where they fit, such as explanations, replies, and messages. Keep reference pages, procedures, and agent instructions factual and direct.

- Have opinions. React to facts instead of neutrally listing pros and cons.
- Vary rhythm. Short sentences. Then longer ones that take their time. Mix it up.
- Acknowledge complexity. "Impressive but also kind of unsettling" beats "impressive."
- Use "I" when it fits.
- Let some mess in. Perfect structure looks machine-made.
- Be specific. Not "this is concerning" but "there's something unsettling about agents churning away at 3am."

## Patterns to detect and fix

### Content

1. **Puffery.** "pivotal moment", "testament to", "evolving landscape", "setting the stage for", "indelible mark", "deeply rooted". Cut puffery and state what happened.
2. **Name-dropping.** Listing media outlets without context. Pick one and say what was said.
3. **Superficial -ing phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Delete them or expand them with real sources.
4. **Promotional language.** "nestled", "vibrant", "breathtaking", "groundbreaking", "renowned", "stunning", "must-visit". Use neutral descriptions.
5. **Vague attributions.** "Experts believe", "Industry reports suggest", "Some critics argue". Name the source or delete the attribution.
6. **Formulaic challenges.** "Despite challenges... continues to thrive." Replace the formula with specific facts.

### Language

7. **AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape when abstract, pivotal, showcase, tapestry when abstract, testament, underscore, vibrant. Replace these with plain words.
8. **Fancy ways to say "is".** "serves as", "stands as", "boasts", "features". Just say "is" or "has".
9. **"Not just X, but Y."** State the point directly.
10. **Rule of three.** Do not force ideas into groups of three.
11. **Synonym cycling.** Pick one term and repeat it instead of cycling through synonyms such as protagonist, main character, central figure, and hero.
12. **False ranges.** Avoid "from X to Y" when X and Y are not on a meaningful scale. List the topics directly.

### Style

13. **Em dash overuse.** Avoid em dashes entirely. Use periods or commas. Do not replace every em dash with parentheses, en dashes, or hyphens. If a thought needs separation, end the sentence or use a comma.
14. **Colon overuse.** Colons are fine before a list or example. Do not use them as mid-sentence connectors. Rewrite the sentence so the relationship is clear without a colon.
15. **Boldface overuse.** Do not bold every proper noun or acronym.
16. **Inline-header lists.** A bold label followed by a colon that restates the line is a tell. Convert it to prose. A bold lead-in that ends in a period and introduces genuinely new detail is fine.
17. **Title case headings.** Use sentence case.
18. **Decorative emojis.** Remove them from headings and bullets.
19. **Curly quotes.** Replace them with straight quotes.

### Communication artifacts

20. **Chatbot phrases.** Remove "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", and "Found the smoking gun!".
21. **Cutoff disclaimers.** "While specific details are limited..." Find sources or remove the disclaimer.
22. **Sycophantic tone.** Respond directly instead of saying "Great question! You're absolutely right!".

### Filler

23. **Filler phrases.** Replace "In order to" with "To" and "Due to the fact that" with "Because". Delete "It is important to note that".
24. **Excessive hedging.** Replace "could potentially possibly be argued that it might" with "may".
25. **Generic conclusions.** State specific plans or facts instead of saying "The future looks bright.".

### Jargon

26. **Abstract metaphor nouns.** Substrate, wedge, vector, locus, vantage, nexus, primitive as a noun, harness as a metaphor, surface as in "API surface", bedrock, scaffolding as a metaphor, modality, paradigm, gold-plating, ratchet as a metaphor, evacuate for moving code, endgame, north star, and flywheel. Use the concrete word. "Substrate" becomes "base". "Wedge in" becomes "add". "Vector" becomes "way" or "method". "Gold-plating" becomes "more than the job needs". "Ratchet" becomes the mechanism's real name or "a limit that only tightens". "Evacuate" becomes "move out".

### Plain speech

27. **Say what it does, not how it feels.** "The database stays close at hand", "SQL you can read", and "types that follow your schema" name a feeling. Name the mechanism or a number instead. Ask what the sentence tells the reader to do or know, then write that. If you cannot restate it as a concrete instruction, fact, or number, cut it. If the sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it.
28. **Shorten or split dense sentences.** If the reader has to backtrack to parse a sentence, break it in two or drop clauses. Keep one idea per sentence.
29. **Active voice.** Prefer it. Catch "is/are/was/were + past participle" and name the actor: "queries are validated" becomes "the compiler validates queries", "the file is parsed by the loader" becomes "the loader parses the file". Passive is fine when the actor is unknown or genuinely does not matter.
30. **Cut adverbs, or use a stronger verb.** "Runs quickly" becomes "is fast" or a number. "Significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is wrong.
31. **Prefer the plain word.** "Utilize" becomes "use", "leverage" becomes "use", "facilitate" becomes "help", "numerous" becomes "many", and "in the event that" becomes "if". The fancier synonym is rarely clearer.
