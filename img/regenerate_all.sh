#!/bin/bash
# Regenerate all paper figures and copy to docs/paper/img/
# Run from repo root: bash docs/paper/img/regenerate_all.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
IMG="$ROOT/docs/paper/img"

echo "=== Regenerating paper figures ==="
echo "Repo root: $ROOT"

# Fig 1: Page fault patterns
echo "[1/9] Page fault patterns..."
cd "$IMG/pattern"
python combine_patterns.py
echo "  -> combined_patterns_1x5.pdf"

# Fig 2: Thread scheduling
echo "[2/9] Thread scheduling..."
cd "$IMG/pattern/vector_add"
python plot_thread_scheduling.py
# Fix: script may output to old path; copy to correct location
cp -f thread_scheduling_motivation.pdf "$IMG/pattern/vector_add/" 2>/dev/null || true
echo "  -> thread_scheduling_motivation.pdf"

# Fig 5: CLC policies
echo "[3/9] CLC policies..."
cd "$IMG/results-raw/clc"
python plot_figure.py
cp -f clc_policies_comparison.pdf "$IMG/results-raw/"
echo "  -> clc_policies_comparison.pdf"

# Fig 6: llama.cpp expert offloading
echo "[4/9] llama.cpp expert offload..."
cd "$ROOT/workloads/llama.cpp/uvm"
python visbasic.py
cp -f llama_uvm_combined_color.pdf "$IMG/results-raw/llama.cpp/"
echo "  -> llama_uvm_combined_color.pdf"

# Fig 7: vLLM KV-cache
echo "[5/9] vLLM KV-cache..."
cd "$ROOT/workloads/vllm/uvm/first-iter"
python generate_figures.py
cp -f ttft_tpot_combined.pdf "$IMG/results-raw/vllm/"
echo "  -> ttft_tpot_combined.pdf"

# Fig 8: GNN training
echo "[6/9] GNN training..."
cd "$ROOT/workloads/pytorch"
python visualize_all.py
cp -f uvm_benchmark_comparison.pdf "$IMG/results-raw/pytorch/"
echo "  -> uvm_benchmark_comparison.pdf"

# Fig 9: FAISS benchmark
echo "[7/9] FAISS benchmark..."
cd "$ROOT/workloads/faiss/results"
python plot_results.py
cp -f faiss_benchmark_results.pdf "$IMG/results-raw/faiss/"
echo "  -> faiss_benchmark_results.pdf"

# Fig 10: Multi-tenant scheduler
echo "[8/9] Multi-tenant scheduler..."
cd "$ROOT/docs/eval/multi-tenant-scheduler"
python plot_figures.py
cp -f fig_main_result.pdf "$IMG/results-raw/multi-tenant/scheduler_latency_throughput.pdf"
echo "  -> scheduler_latency_throughput.pdf"

# Fig 11: Multi-tenant memory priority
echo "[8b/9] Multi-tenant memory..."
cd "$ROOT/docs/eval/multi-tenant-memory"
python plot_all_kernels_stacked.py
cp -f all_kernels_stacked.pdf "$IMG/results-raw/multi-tenant/"
echo "  -> all_kernels_stacked.pdf"

# Fig 12: Two-tenant co-location
echo "[9/9] Two-tenant co-location..."
cd "$ROOT/workloads/llama.cpp/uvm"
python plot_colocated_results.py
cp -f fig_colocated_results.pdf "$IMG/results-raw/multi-tenant/"
echo "  -> fig_colocated_results.pdf"

# Fig 13: Device microbench
echo "[10/9] Device microbench..."
cd "$IMG/results-raw/runtime"
python plot_microbench.py
echo "  -> microbench_comparison.pdf"

echo ""
echo "=== Done. All figures regenerated in docs/paper/img/ ==="
echo "Manual figures (not regenerated): gpu-ebpf-arch.png, fig_exec_model.tex"
