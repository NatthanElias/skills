---
name: simplify
description: Simplify code for clarity while preserving exact behavior. Use when a working implementation needs readability or complexity reduction, or when a review calls for a focused refactor.
---

# Code simplification

Simplify code by reducing complexity while preserving exact behavior. The goal is not fewer lines. It is code that is easier to read, understand, modify, and debug. Every simplification must pass a simple test: "Would a new team member understand this faster than the original?"

## When to use

- After a feature is working and tests pass, but the implementation feels heavier than it needs to be
- During code review when readability or complexity issues are flagged
- When you encounter deeply nested logic, long functions, or unclear names
- When refactoring code written under time pressure
- When consolidating related logic scattered across files
- After merging changes that introduced duplication or inconsistency

Do not use this skill when the code is already clean and readable, when its behavior is not understood yet, when a simpler version would measurably hurt performance, or when the module is about to be rewritten as throwaway code.

## The five principles

### 1. Preserve behavior exactly

Do not change what the code does. Change only how it expresses that behavior. Preserve all inputs, outputs, side effects, error behavior, and edge cases. If you are unsure whether a simplification preserves behavior, do not make it.

Before every change, ask:

- Does this produce the same output for every input?
- Does this maintain the same error behavior?
- Does this preserve the same side effects and ordering?
- What proportionate final-state verification will reveal a behavior change?

### 2. Follow project conventions

Simplification means making code more consistent with the codebase, not imposing external preferences.

Before simplifying:

1. Read `AGENTS.md`, `CONTRIBUTING.md`, and other project conventions that apply.
2. Study how neighboring code handles similar patterns.
3. Match the project's style for imports, naming, function style, error handling, and type annotations.

### 3. Prefer clarity over cleverness

Explicit code is better than compact code when the compact version requires a mental pause to parse.

- Replace nested ternaries with readable control flow.
- Replace dense inline transforms with named intermediate steps when they clarify intent.
- Keep helpful names even if they cost a few extra lines.

### 4. Maintain balance

Watch for over-simplification:

- Do not inline away names that carry meaning.
- Do not merge unrelated logic into one larger function.
- Do not remove abstractions that serve testability or extensibility.
- Do not optimize for line count over comprehension.

### 5. Scope to what changed

Default to simplifying recently modified code. Avoid unrelated refactors unless the user explicitly asks for them.

## Process

### Step 1: Understand before touching

Before changing or removing anything, understand why it exists.

Answer:

- What is this code's responsibility?
- What calls it? What does it call?
- What are the edge cases and error paths?
- Are there tests that define expected behavior?
- Why might it have been written this way?

If you cannot answer these questions, read more context first.

### Step 2: Look for simplification opportunities

Signals include:

- Deep nesting
- Long functions with mixed responsibilities
- Nested ternaries
- Boolean flag arguments
- Repeated conditionals
- Generic or misleading names
- Duplicated logic
- Dead code
- Wrappers or abstractions that add no value

### Step 3: Apply changes incrementally

Make one simplification at a time. For each simplification, make the change, use a proportionate final-state verification plan to check preservation, and keep it only when the evidence supports preservation.

Separate refactoring from feature work whenever possible.

### Step 4: Verify the result

After simplifying, confirm that:

- The code is genuinely easier to understand.
- The diff is clean and reviewable.
- Project conventions still match.
- No behavior, error handling, or side effects changed.

## Final-state verification

Use a proportionate final-state verification plan for the final diff. Run checks required by the repository and release instructions. Add or repeat evidence only when the changed scope or a stated uncertainty warrants it.
