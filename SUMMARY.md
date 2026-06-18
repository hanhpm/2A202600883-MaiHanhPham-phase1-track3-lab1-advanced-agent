# Reflexion Agent Benchmark Summary

Student: Mai Hanh Pham  
StudentID: 2A202600883  
Date: 2026-06-18  
Lab folder: `2A202600883-MaiHanhPham-phase1-track3-lab1-advanced-agent`

## 1. Benchmark Scope

This summary compares two OpenAI API models on three datasets using both ReAct and Reflexion agents.

| Dataset label | File | QA examples | Run records | Notes |
|---|---|---:|---:|---|
| mini | `data/hotpot_mini.json` | 8 | 16 | Small scaffold dataset |
| hotpot | `data/hotpot_test_100.json` | 100 | 200 | Converted from HotpotQA distractor data |
| golden_hotpot | `data/hotpot_golden.json` | 20 | 40 | Golden evaluation set |

Models evaluated:

| Model | Output folder pattern |
|---|---|
| `gpt-4o-mini` | `outputs/llm_gpt4o_mini*` |
| `gpt-4.1-mini` | `outputs/llm_gpt41_mini*` |

Cost note: the local reports store total API tokens only, not separate input and output tokens. Therefore cost is reported as an estimated range:

`min_cost = total_tokens * input_price / 1,000,000`  
`max_cost = total_tokens * output_price / 1,000,000`

Pricing assumptions used:

| Model | Input / 1M tokens | Output / 1M tokens |
|---|---:|---:|
| `gpt-4o-mini` | `$0.15` | `$0.60` |
| `gpt-4.1-mini` | `$0.40` | `$1.60` |

## 2. Main Results

| Dataset | Model | Agent | Correct | EM | Avg attempts | Avg tokens | Avg latency |
|---|---|---|---:|---:|---:|---:|---:|
| mini | `gpt-4o-mini` | ReAct | 7/8 | 0.875 | 1.00 | 341.25 | 2.78s |
| mini | `gpt-4o-mini` | Reflexion | 7/8 | 0.875 | 1.25 | 508.62 | 3.28s |
| mini | `gpt-4.1-mini` | ReAct | 8/8 | 1.000 | 1.00 | 352.88 | 3.95s |
| mini | `gpt-4.1-mini` | Reflexion | 8/8 | 1.000 | 1.00 | 352.50 | 2.53s |
| hotpot | `gpt-4o-mini` | ReAct | 67/100 | 0.670 | 1.00 | 1,697.39 | 2.70s |
| hotpot | `gpt-4o-mini` | Reflexion | 76/100 | 0.760 | 1.63 | 3,916.99 | 6.11s |
| hotpot | `gpt-4.1-mini` | ReAct | 82/100 | 0.820 | 1.00 | 1,712.91 | 2.47s |
| hotpot | `gpt-4.1-mini` | Reflexion | 92/100 | 0.920 | 1.29 | 2,760.58 | 4.05s |
| golden_hotpot | `gpt-4o-mini` | ReAct | 17/20 | 0.850 | 1.00 | 379.55 | 2.85s |
| golden_hotpot | `gpt-4o-mini` | Reflexion | 17/20 | 0.850 | 1.30 | 603.20 | 3.75s |
| golden_hotpot | `gpt-4.1-mini` | ReAct | 19/20 | 0.950 | 1.00 | 395.55 | 2.49s |
| golden_hotpot | `gpt-4.1-mini` | Reflexion | 19/20 | 0.950 | 1.10 | 498.95 | 3.19s |

## 3. Reflexion Lift

| Dataset | Model | EM delta | Attempt delta | Token delta | Latency delta |
|---|---|---:|---:|---:|---:|
| mini | `gpt-4o-mini` | +0.000 | +0.25 | +167.37 | +0.50s |
| mini | `gpt-4.1-mini` | +0.000 | +0.00 | -0.38 | -1.41s |
| hotpot | `gpt-4o-mini` | +0.090 | +0.63 | +2,219.60 | +3.41s |
| hotpot | `gpt-4.1-mini` | +0.100 | +0.29 | +1,047.67 | +1.58s |
| golden_hotpot | `gpt-4o-mini` | +0.000 | +0.30 | +223.65 | +0.90s |
| golden_hotpot | `gpt-4.1-mini` | +0.000 | +0.10 | +103.40 | +0.70s |

Key observation: Reflexion helped most on the larger `hotpot` dataset. For `gpt-4o-mini`, Reflexion improved EM from `0.67` to `0.76`. For `gpt-4.1-mini`, Reflexion improved EM from `0.82` to `0.92`. On the smaller mini and golden sets, Reflexion did not improve final EM because the base ReAct run was already strong or the remaining errors were not fixed by an extra reflection pass.

## 4. Time And Cost Summary

| Model | Dataset | Total tokens | Total latency | Cost estimate |
|---|---|---:|---:|---:|
| `gpt-4o-mini` | mini | 6,799 | 48.5s | `$0.0010 - $0.0041` |
| `gpt-4o-mini` | hotpot | 561,438 | 881.4s | `$0.0842 - $0.3369` |
| `gpt-4o-mini` | golden_hotpot | 19,655 | 131.9s | `$0.0029 - $0.0118` |
| `gpt-4o-mini` | all datasets | 587,892 | 1,061.8s / 17.7m | `$0.0882 - $0.3527` |
| `gpt-4.1-mini` | mini | 5,643 | 51.8s | `$0.0023 - $0.0090` |
| `gpt-4.1-mini` | hotpot | 447,349 | 651.6s | `$0.1789 - $0.7158` |
| `gpt-4.1-mini` | golden_hotpot | 17,890 | 113.5s | `$0.0072 - $0.0286` |
| `gpt-4.1-mini` | all datasets | 470,882 | 817.0s / 13.6m | `$0.1884 - $0.7534` |

Efficiency comparison:

- `gpt-4.1-mini` used fewer total tokens than `gpt-4o-mini` across the completed runs: `470,882` vs `587,892`.
- `gpt-4.1-mini` also finished faster overall: `13.6m` vs `17.7m`.
- Because the assumed per-token price for `gpt-4.1-mini` is higher, the estimated total cost range is higher than `gpt-4o-mini` despite lower token usage.

## 5. Failure Mode Summary

| Dataset | Model | Agent | None | Wrong final answer |
|---|---|---|---:|---:|
| mini | `gpt-4o-mini` | ReAct | 7 | 1 |
| mini | `gpt-4o-mini` | Reflexion | 7 | 1 |
| mini | `gpt-4.1-mini` | ReAct | 8 | 0 |
| mini | `gpt-4.1-mini` | Reflexion | 8 | 0 |
| hotpot | `gpt-4o-mini` | ReAct | 67 | 33 |
| hotpot | `gpt-4o-mini` | Reflexion | 76 | 24 |
| hotpot | `gpt-4.1-mini` | ReAct | 82 | 18 |
| hotpot | `gpt-4.1-mini` | Reflexion | 92 | 8 |
| golden_hotpot | `gpt-4o-mini` | ReAct | 17 | 3 |
| golden_hotpot | `gpt-4o-mini` | Reflexion | 17 | 3 |
| golden_hotpot | `gpt-4.1-mini` | ReAct | 19 | 1 |
| golden_hotpot | `gpt-4.1-mini` | Reflexion | 19 | 1 |

The dominant remaining failure mode is `wrong_final_answer`. This usually means the answer was plausible but did not match the gold answer after evaluation. On the 100-example HotpotQA set, Reflexion reduced wrong final answers substantially:

- `gpt-4o-mini`: `33` wrong answers down to `24`
- `gpt-4.1-mini`: `18` wrong answers down to `8`

## 6. Model-Level Evaluation

`gpt-4.1-mini` produced the best accuracy. It matched or beat `gpt-4o-mini` on every dataset, with the largest advantage on `hotpot`: Reflexion EM reached `0.92` compared with `0.76` for `gpt-4o-mini`. It also required fewer Reflexion retries on the larger dataset, with average Reflexion attempts of `1.29` instead of `1.63`.

`gpt-4o-mini` was cheaper under the pricing assumptions and still benefited from Reflexion on the 100-example dataset. It is a reasonable low-cost baseline, but it left more wrong final answers on the larger HotpotQA set.

Reflexion is most worthwhile on the larger `hotpot` dataset. On `mini` and `golden_hotpot`, it increased token and latency cost without improving EM. This suggests Reflexion should be used adaptively: run one ReAct pass first, then trigger reflection only when the evaluator identifies a likely incomplete or wrong answer.

## 7. Final Conclusion

Best accuracy configuration: `gpt-4.1-mini` with Reflexion on `hotpot`, reaching `92/100` correct with EM `0.92`.

Best low-cost configuration: `gpt-4o-mini` with ReAct or adaptive Reflexion, depending on whether the task prioritizes budget or accuracy.

Recommended submission configuration: use `gpt-4.1-mini` with Reflexion for final benchmark quality, and report the cost tradeoff clearly. For production-like usage, use adaptive Reflexion to avoid paying for extra reflection calls when the first answer is already correct.

## 8. Source Output Files

| Dataset | Model | Report |
|---|---|---|
| mini | `gpt-4o-mini` | `outputs/llm_gpt4o_mini/report.json` |
| mini | `gpt-4.1-mini` | `outputs/llm_gpt41_mini/report.json` |
| hotpot | `gpt-4o-mini` | `outputs/llm_gpt4o_mini_hotpot100/report.json` |
| hotpot | `gpt-4.1-mini` | `outputs/llm_gpt41_mini_hotpot100/report.json` |
| golden_hotpot | `gpt-4o-mini` | `outputs/llm_gpt4o_mini_golden_hotpot/report.json` |
| golden_hotpot | `gpt-4.1-mini` | `outputs/llm_gpt41_mini_golden_hotpot/report.json` |
