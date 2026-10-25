# Visual explanations

Use this lens for teaching, diagrams, images, and interactive HTML. [Explain](../SKILL.md) owns the response length and writing rules.

## Choose a supported medium

Check the tools available in the current VS Code session before offering a preview, image, or browser interaction.

| The reader needs to understand | Use |
| --- | --- |
| A small change or one mechanism | Prose or a short walkthrough |
| Control flow, message order, or structure | Mermaid diagrams in Markdown |
| Position, overlap, or layout | A captured screen or an illustrative image, when the tools support it |
| How inputs change state or output | A self-contained interactive HTML file |

State when a diagram is source text rather than a confirmed rendered preview. If no preview tool exists, link the saved file and explain how to open it. Label simulations and illustrative values. Describe a screen as observed only when it was captured.

## Teach in layers

Use the conversation to identify the reader's goal and existing knowledge. Start with a plain definition, then connect it to the project.

Explain the problem each part solves and walk through a concrete use. Give the smallest complete layer, then let the reader choose the next one through the question tool. Keep the uncertainty labels from [Rationale and history](why.md).

For three or more interacting parts, build a diagram series. Start with the first relationship, redraw it with the next part, and add later edges as they become relevant.

- Keep each diagram to roughly six connected boxes with short labels.
- Put disconnected facts in prose.
- Assign each fact to text or a visual, so neither repeats the other.
- Use the same staged build-up for illustrative images.

## Make HTML disposable

Write one file with inline CSS and JavaScript. Keep it offline, without external assets, network requests, or a build step. Choose controls that expose the mechanism, such as a step button, input slider, or before-and-after toggle.

Base the content on verified facts. Keep source anchors visible in the page, and distinguish simulated state from observed results.

Save the file in the session's artifact or scratch directory. Add it to the repository only when the user requests that destination.

Use a browser or preview tool when available. Verify that the file opens and that its controls demonstrate the claimed behavior. Otherwise provide the file link and state that rendering and interaction remain unchecked.

Done when each visual explains something prose alone would make harder to follow, and each factual label can be traced to evidence.
