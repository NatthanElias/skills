# Mechanism and structure

Use this lens to explain a function, subsystem, algorithm, protocol, or project rule. [Explain](../SKILL.md) owns the response length and writing rules.

## Trace the behavior

For a narrow question, read the target, its callers, and the tests that constrain it. For a subsystem, follow inputs from the entry point through decisions and state changes to the outputs. Include relevant failure paths.

Follow the selected repository boundaries and the workspace's delegation policy. Use [orchestrate](../../orchestrate/SKILL.md) before any subagent dispatch. A single execution trace stays in the main session.

Use code to establish present behavior. Use [Rationale and history](why.md) when the question concerns intent.

## Build the explanation

Cover only the parts the question needs, in this order:

1. Define the subject, its purpose, and its inputs and outputs.
2. Introduce the types, services, or records needed to follow it.
3. Walk through a concrete execution path. Name the actor and action at each step, and link its implementation.
4. Give a short file map when the reader needs to work on the subsystem.
5. Describe non-obvious limits, failure modes, and unresolved questions.

Explain complexity through its constraints rather than a list of functions. Use a small code excerpt only when the exact expression matters. Keep analogies faithful to the actual mechanism.

For a flow with several interacting parts, use the build-up technique in [Visual explanations](visuals.md).

Done when the reader can predict the relevant path, including its decisions, and locate the code that implements each step.
