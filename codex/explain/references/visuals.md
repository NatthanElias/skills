# Visuals and teaching

Read this reference when teaching a topic in depth, or when producing a diagram, image or interactive HTML explainer. Style rules live in [../SKILL.md](../SKILL.md).

## Use the environment's tools

Use whatever diagram, image-generation, HTML preview, browser or file-creation tools the active environment provides. Check what exists before you offer a medium. Mermaid in Markdown renders in many chat clients. When nothing renders, save the file and give its path.

## Teach as a conversation

1. Pick the few things the reader should walk away understanding. Base them on why they ask (changing, reviewing, debugging or learning) and on what they already know, as the conversation shows. Skip what they know.
2. Start with a plain definition. Name the thing, give its common name if it has one, and say what it is in general terms. Then tie it to this case: "In Morfe, `X` uses this to ...".
3. Explain each part so it clicks. Say what problem it solves and how it works. Walk through what happens as someone uses it. A list of functions and constants is reference material, and teaching explains the idea behind them.
4. Give the smallest complete answer, then stop and let the reader respond. Add layers when they ask. Offer to go deeper or move on, and follow their lead.
5. Say each point plainly. Skip quizzes, requests to repeat things back, and labels that flag a part as hard or important.
6. Keep the confidence language from [why.md](why.md) intact. Its hedges are findings.

## Choose the medium by the idea

| Idea | Medium |
| --- | --- |
| One small change or a single mechanism | Prose |
| A flow, sequence or structure where labels carry the meaning | Mermaid diagram series |
| A spatial idea, such as layout, overlap or a before-and-after position | Generated whiteboard-style image with a few short labels |
| An idea the reader learns by changing inputs and watching state | Disposable interactive HTML |

A single simple point needs no figure. Draw only from facts you have. Mark any illustrative or simulated value as such, and never draw a screen you did not capture.

## Diagram build-up rule

For three or more moving parts, draw a short series of diagrams. Each diagram redraws the previous one and adds one part, so the reader watches the system assemble. To teach A to B to C, draw A to B, then redraw with C, then redraw with the return edge or the next piece. One all-at-once chart is reference material.

- At most about six boxes per diagram.
- Short labels, at most about eight words, written as plain words.
- Connect every box. A status list or a set of unconnected boxes belongs in text.
- State each fact once, in the text or in a diagram.
- The build-up rule applies to generated images too.

## Disposable interactive HTML

- Write one self-contained file with inline CSS and JS. Use no network requests and no build step.
- Pick controls that expose the idea, such as tabs per stage, a slider for an input, a state table that updates per step, or a before-and-after toggle.
- Fill it from verified facts, and keep the `file:line` anchors from the explanation visible in the page.
- Save it to the environment's artifact or scratch location, or a temporary path. Write it into the repository only when the user asks.
- Render it with the environment's preview tool when one exists. Otherwise give the path to open in a browser.

## Done when

Each visual adds one idea the text alone would carry less well, and the reader can trace every label back to a fact or anchor.
