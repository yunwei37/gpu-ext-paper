# Figure Sources

All figure generation scripts are in this repo. Paths are relative to repo root (`gpu_ext/`).

## Figure → Script Mapping

| Paper Figure | Image Path | Script | Output Name |
|---|---|---|---|
| Fig 1: Page fault patterns | `img/pattern/combined_patterns_1x5.pdf` | `docs/paper/img/pattern/combine_patterns.py` | `combined_patterns_1x5.pdf` |
| Fig 2: Thread scheduling | `img/pattern/vector_add/thread_scheduling_motivation.pdf` | `docs/paper/img/pattern/vector_add/plot_thread_scheduling.py` | `thread_scheduling_motivation.pdf` |
| Fig 3: Architecture | `img/gpu-ebpf-arch.png` | Manual (draw.io / design tool) | — |
| Fig 4: Execution model | `tex/fig_exec_model.tex` | TikZ (inline LaTeX) | — |
| Fig 5: CLC policies | `img/results-raw/clc_policies_comparison.pdf` | `docs/paper/img/results-raw/clc/plot_figure.py` | `clc_policies_comparison.pdf` |
| Fig 6: llama.cpp expert offload | `img/results-raw/llama.cpp/llama_uvm_combined_color.pdf` | `workloads/llama.cpp/uvm/visbasic.py` | `llama_uvm_combined_color.pdf` |
| Fig 7: vLLM KV-cache | `img/results-raw/vllm/ttft_tpot_combined.pdf` | `workloads/vllm/uvm/first-iter/generate_figures.py` | `ttft_tpot_combined.pdf` |
| Fig 8: GNN training | `img/results-raw/pytorch/uvm_benchmark_comparison.pdf` | `workloads/pytorch/visualize_all.py` | `uvm_benchmark_comparison.pdf` |
| Fig 9: FAISS benchmark | `img/results-raw/faiss/faiss_benchmark_results.pdf` | `workloads/faiss/results/plot_results.py` | `faiss_benchmark_results.pdf` |
| Fig 10: Scheduler latency | `img/results-raw/multi-tenant/scheduler_latency_throughput.pdf` | `docs/eval/multi-tenant-scheduler/plot_figures.py` | `fig_main_result.pdf` |
| Fig 11: Memory priority | `img/results-raw/multi-tenant/all_kernels_stacked.pdf` | `docs/eval/multi-tenant-memory/plot_all_kernels_stacked.py` | `all_kernels_stacked.pdf` |
| Fig 12: Two-tenant co-location | `img/results-raw/multi-tenant/fig_colocated_results.pdf` | `workloads/llama.cpp/uvm/plot_colocated_results.py` | `fig_colocated_results.pdf` |
| Fig 13: Device microbench | `img/results-raw/runtime/microbench_comparison.pdf` | `docs/paper/img/results-raw/runtime/plot_microbench.py` | `microbench_comparison.pdf` |
| Table 1, Table 2 | — | — | Manually maintained in LaTeX |

## Known Issues

- `plot_thread_scheduling.py` has hardcoded output path to old repo (`co-processor-demo/gbpf-paper/`). Needs fixing.
- `visbasic.py` saves to CWD (`llama_uvm_combined_color.pdf`), not to `docs/paper/img/`.
- `plot_figures.py` (scheduler) outputs `fig_main_result.pdf`, needs rename to `scheduler_latency_throughput.pdf`.
- `generate_updated_figures.py` generates **alternate** versions (`gnn_capability_progression.pdf`, `faiss_benchmark_results_v2.pdf`) not currently used in paper.

## Regenerate All Figures

```bash
# From repo root:
bash docs/paper/img/regenerate_all.sh
```
