# OpenCode Go model choices

Checked 2026-10-09. Recommendations target the five roles in the orchestration
skill and the base Go plan. They are judgments from public measurements, not
benchmarks of this exact Slim workflow.

## Two choices per role

| Role | Recommended | Alternative | Reason |
| --- | --- | --- | --- |
| orchestrator | GLM-5.3-Flash, `max` | Claude Haiku 5.5, `xhigh` | GLM gives sustained coordination a strong agentic score and larger Go allowance. Haiku is a newer, competitive option with a smaller allowance. |
| oracle | MiMo-V2.6-Pro, default | Claude Haiku 5.5, `max` | MiMo has the strongest general and coding results among this shortlist at low measured task cost. Haiku provides a different model family for independent review. |
| explorer | GPT-6 Luna, `xhigh` | DeepSeek V4.1 Flash, `max` | Luna suits bounded, read-only evidence extraction at low cost. DeepSeek has stronger long-context and terminal results for difficult repository investigations. |
| librarian | GPT-6 Luna, `xhigh` | MiMo-V2.6-Flash, default | Luna is economical for primary-source extraction and summaries. MiMo offers a larger Go allowance for sustained research. The root still verifies citations. |
| fixer | GLM-5.3-Flash, `max` | DeepSeek V4.1 Flash, `max` | GLM has stronger terminal results at slightly lower measured task cost. DeepSeek trades some success rate for higher measured output throughput. |

The IDs and verified variants live in [go-models.json](go-models.json). The
default/default entries omit `variant`; inventing `high` for a model without
that variant would not reproduce a tested setting. The setup does not silently
switch existing model choices or install automatic fallbacks.

## Measurements behind the choices

AA measures benchmark workloads with its own harness and provider settings.
Task cost below is its weighted cost across Intelligence Index tasks, not
Terminal-Bench-only cost, a cost per successful fix, or your Go bill.

| Evaluated profile | Intelligence Index | Terminal-Bench 4.0 | AA-LCR | AA cost/task | Source |
| --- | ---: | ---: | ---: | ---: | --- |
| MiMo-V2.6-Pro | 46 | 35% | 86% | $0.13 | [AA comparison](https://artificialanalysis.ai/models/comparisons/mimo-v2-6-pro-vs-glm-5-3-flash) |
| GLM-5.3-Flash | 42 | 33% | 80% | $0.25 | [AA comparison](https://artificialanalysis.ai/models/comparisons/mimo-v2-6-pro-vs-glm-5-3-flash) |
| Claude Haiku 5.5, max | 43 | 33% | 83% | $0.21 | [AA efforts](https://artificialanalysis.ai/models/comparisons/claude-haiku-5-5-vs-claude-haiku-5-5-xhigh) |
| Claude Haiku 5.5, xhigh | 41 | 29% | 78% | $0.12 | [AA efforts](https://artificialanalysis.ai/models/comparisons/claude-haiku-5-5-vs-claude-haiku-5-5-xhigh) |
| DeepSeek V4.1 Flash, max | 39 | 27% | 84% | $0.27 | [AA comparison](https://artificialanalysis.ai/models/comparisons/mimo-v2-6-flash-vs-deepseek-v4-1-flash) |
| MiMo-V2.6-Flash | 38 | 23% | 74% | $0.06 | [AA comparison](https://artificialanalysis.ai/models/comparisons/mimo-v2-6-flash-vs-deepseek-v4-1-flash) |
| GPT-6 Luna, xhigh | 35 | 8% | 80% | $0.04 | [AA comparison](https://artificialanalysis.ai/models/comparisons/gpt-6-luna-xhigh-vs-gpt-6-sol-high) |

The index version is 4.3.2. AA-LCR measures long-context reasoning; it does not
test whether a librarian cites sources correctly. Terminal-Bench is more
relevant to execution than the aggregate index. Weight these measures by role,
rather than treating index points per dollar as a universal quality score.
See [AA methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking).

AA's GLM profile is not labeled with a named effort in its comparison. The
installed Go model exposes `low`, `high`, and `max`; choosing `max` for complex
coordination/coding is a workflow judgment, not proof that Go reproduces AA's
profile. Haiku search listings describe fallback behavior; benchmark harness
behavior and Go serving may differ. None of the public scores guarantees the
same quality or speed inside OpenCode.

## Apply Go's actual limits

On the base Go plan, the current monthly allowances are $60 for GLM-5.3-Flash,
DeepSeek V4.1 Flash, and MiMo-V2.6-Flash; $15 for MiMo-V2.6-Pro, GPT-6 Luna, and
Claude Haiku 5.5. These are usage accounting limits, not separate cash charges.
Go also applies shorter rolling limits, and provider-specific cached-token
prices affect actual usage. [OpenCode Go usage limits](https://docs.opencode.ai/docs/go/#usage-limits).

That is why GLM is the sustained-work default even though MiMo Pro has a lower
AA task cost and a higher index. Reserve MiMo Pro for consequential advice and
independent verification. If research consumes Luna's allowance, the MiMo Flash
alternative preserves a low-cost research lane. Compare real completed-task
usage before deciding that either is cheaper for your projects.

## Why the older defaults changed

MiniMax M3 and Qwen3.7 Plus remain available, but AA reports indices 29 and 25
and task costs $0.51 and $0.22 respectively. They do not justify being this
workflow's default decision-makers against the newer shortlist.
[AA comparison](https://artificialanalysis.ai/models/comparisons/minimax-m3-vs-qwen3-7-plus).

Kimi K3 reports index 44 at $2.00/task and 13% Terminal-Bench versus GLM's 42,
$0.25/task, and 33%. Its general score does not make it the best-value fixer.
[AA comparison](https://artificialanalysis.ai/models/comparisons/glm-5-3-flash-vs-kimi-k3).

Qwen3.8 Flash's Go ID does not establish that it matches AA's
`Qwen3.8-Flash-Next` snapshot. Space Bunny and temporary free models lack a
verified comparable result in this review. Keep them as candidates for measured
local trials rather than assigning them critical roles from their names alone.

## Availability and freshness

The [dated client catalog](go-catalog.json) records 31 models from
`opencode models opencode-go --refresh --verbose`. The official Go documentation
also lists 31 current models. The [models API](https://opencode.ai/zen/go/v1/models)
lists additional legacy IDs. An ID in that API does not prove your account can
run it through the installed client. Refresh on the target machine before
selecting a preset. [Current Go model list](https://docs.opencode.ai/docs/go/#how-it-works).

Revalidate when Go's lineup/pricing changes, model aliases point to new
snapshots, AA changes its index or harness, or the local client adds/removes
variants. Newer releases are a useful shortlist signal; measured quality,
task cost, serving latency, and role fit decide the final choice.
