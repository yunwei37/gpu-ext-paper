# ASPLOS'27 #1797 — SOTA KV-Cache / LLM-Inference Memory-System Feasibility Audit

**Paper:** gpubpf (submission #1797) — OS-level GPU resource management with eBPF, page-granularity UVM policies, transparent to applications.
**Scope of this file:** **KV-cache and LLM-inference memory-management systems only.** Sibling file `sota-baseline-feasibility.md` covers MoE-offload, scheduling, and UVM/oversubscription systems; the two do not overlap.
**Audit date:** 2026-08-03.
**Method:** Primary sources only (GitHub repo, README, `requirements.txt`/`pyproject.toml`/`CMakeLists.txt`, CI, issues, paper PDF/arXiv). The five most decision-critical claims were re-fetched directly by the auditor; remaining sources were fetched during a parallel primary-source research pass. Verdicts that could not be confirmed are marked **uncertain** — nothing below is invented.

**Reviewer trigger:** Reviewer E (leaning reject) asks for comparison against *state-of-the-art research* systems (not just vLLM CPU offload / LMCache) and specifically asks whether/how eBPF handles **KV-cache offload to storage** (Weka/Vast/Nvidia CMX) rather than CPU DRAM. Reviewer F (leaning reject) asks the same for GPU memory management/offloading generally. This file answers: *which of those named research systems can we actually build and run head-to-head on our hardware, and which cannot, with a citable reason.*

---

## Hardware constraint (hard)

| Resource | Available |
|----------|-----------|
| GPU | **1× NVIDIA GeForce RTX 5090**, 32 GB, **Blackwell sm_120** (compute 12.0), driver **575.57.08** |
| Missing | A100, H100, multi-GPU, NVLink, MIG, GPUDirect-Storage hardware, RDMA/RoCE fabric, CXL |
| Workload | vLLM serving with KV-cache offload under VRAM pressure; metrics throughput / TTFT / TPOT / P99 |
| Wall-clock | ~4 weeks, shared with writing |

**Local vLLM fork** (`workloads/vllm/vllm/`): recent **vLLM main** (setuptools-scm `0.1.dev9970+g3ec7b0515`), **torch 2.8.0**. UVM is added transparently via `VLLM_USE_UVM=1` → `vllm/device_allocator/uvm.py` swaps the GPU allocator for **`cudaMallocManaged`** (managed memory), plus an `LD_PRELOAD` shim (`cuda_malloc_managed_preload.cpp`). **Implication for baselines:** any system that *also* replaces the low-level CUDA allocator (vAttention's `cuMemMap`, vTensor/GMLake's `cuMemAlloc` interception, Jenga's PagedAttention rewrite) collides with this shim at the same layer. This is the dominant integration-risk axis below.

**sm_120 floor (cross-cutting):** native Blackwell needs CUDA Toolkit **12.8+** and a PyTorch **cu128+** build with `sm_120` in `torch.cuda.get_arch_list()`. Wheels pinned to **torch ≤ 2.5** (e.g. `torch==2.0.1`, `2.1.x`, `2.3.x`) ship **no sm_120 kernels** and are not drop-in; custom CUDA extensions compiled only for `sm_80`/`sm_90` must be recompiled with `TORCH_CUDA_ARCH_LIST` including `12.0`.

---

## 1. What we should actually try (1–2 systems)

Of 17+ audited systems, **only two are both runnable on a single 5090 and add distinct reviewer value beyond what the submission already compares.** The headline finding: the *only* SOTA research KV-offload artifact that runs on our UVM-modified vLLM **and** has a storage backend is **LMCache** (which we already compare against); the strongest *distinct-engine* research comparator that drops in on sm_120 is **SGLang (RadixAttention)**.

### 1) LMCache — exercise the **local-disk/SSD backend** (answers Reviewer E; LOW–MEDIUM)

| Field | Value |
|-------|--------|
| Venue / paper | arXiv [2510.09665](https://arxiv.org/abs/2510.09665); now a **PyTorch Foundation** project (Oct 2025). CacheBlend (EuroSys'25) and CacheGen (SIGCOMM'24) are folded into this same codebase. |
| Artifact | [github.com/LMCache/LMCache](https://github.com/LMCache/LMCache) — Apache-2.0, ~11k★, ~2,060 commits, nightly wheels dated 2026-08-03 (active) |
| sm_120 | **YES (rebuild).** `pyproject.toml` `[tool.cibuildwheel]`: `TORCH_CUDA_ARCH_LIST = "7.5;8.0;8.6;8.9;9.0;10.0;12.0"` with comment `# 12.0: RTX 50-series (PTX)`. *(Directly fetched and re-verified.)* Runtime deliberately does **not** pin torch (`requirements/common.txt`); build against our torch 2.8.0+cu128 via `--no-build-isolation`. |
| HW blocker | None for single-GPU + CPU-DRAM + local-disk offload. |
| Storage tier? | **YES** — first-class backends: CPU RAM, **local disk (FileSystem / Raw Block)**, Redis/Valkey, Mooncake, InfiniStore, S3, NIXL, GDS. The **local FileSystem / Raw-Block** path runs on a plain NVMe **without** GDS hardware we lack. *(docs.lmcache.ai/mp/l2_storage/file_and_block.html)* |
| Why try it | (a) Directly answers Rev E's "offload to storage" question; (b) converts the existing LMCache comparison into an explicit *research-system, multi-tier* comparison; (c) only ~no-new-HW path to a storage-tier KV datapoint. |

**First command to try:**
```bash
# 0. in the vLLM workload venv (uv-managed, torch 2.8.0+cu128)
cd workloads/vllm
# 1. build LMCache against the venv's torch (TORCH_CUDA_ARCH_LIST already incl. 12.0)
git clone https://github.com/LMCache/LMCache.git /tmp/LMCache
LMCACHE_CUDA_MAJOR=12 uv pip install --no-build-isolation -e /tmp/LMCache
# 2. configure the local-disk L2 backend per
#    https://docs.lmcache.ai/mp/l2_storage/file_and_block.html  (FileSystem or Raw Block on NVMe)
# 3. serve with OUR UVM allocator + LMCache connector:
VLLM_USE_UVM=1 uv run python -m vllm.entrypoints.openai.api_server \
    --model <gpt-oss-20b / llama-3-8b> ...   # plus LMCache connector config (extra_config)
```

**Main risk:** LMCache's connector subclasses vLLM's deep-internal `KVConnectorBase_V1` and ships **per-vLLM-version shims** (`lmcache_connector_v1_085.py`, `_0180`, `_0201`); our fork is vLLM-main @ `g3ec7b0515`, so the connector ABI must match that commit. Separately, LMCache moves KV via **pinned host buffers + CUDA streams**, whose interaction with UVM *managed-memory* pages is uncharacterized. Smoke-test coexistence before promising numbers. (gpt-oss-120b needs TP=2 and won't fit one 32 GB card; use gpt-oss-20b, on which LMCache's CacheBlend/CacheGen are "Not validated" per the gpt-oss recipe page.)

### 2) SGLang (RadixAttention) — research-grade alternative-engine H2H (LOW)

| Field | Value |
|-------|--------|
| Venue / paper | RadixAttention: **SOSP'24** ("SGLang: Efficient Execution of Structured Language Model Programs"). |
| Artifact | [github.com/sgl-project/sglang](https://github.com/sgl-project/sglang) — Apache-2.0, ~31k★, extremely active |
| sm_120 | **YES (drop-in).** Default wheels are CUDA 13; `cu129` fallback pulls `torch==2.11.0+cu129` — **both cover sm_120** (CUDA ≥12.8 floor). Default attention backend FlashInfer is sm75+ with Blackwell tiles. *(install doc directly fetched and re-verified.)* |
| HW blocker | None. Single-GPU serving is a first-class mode. |
| Storage tier? | No — RadixAttention prefix cache is GPU+CPU DRAM. (LMCache supplies the storage tier when paired.) |
| Why try it | Lowest-risk way to show gpubpf's UVM page-granularity policies on vLLM against a **cited research serving engine's own prefix cache**, same model/workload/5090. |

**First command to try:**
```bash
docker run --gpus all --shm-size 32g -p 30000:30000 lmsysorg/sglang:latest \
  python3 -m sglang.launch_server --model-path <llama-3-8b / qwen> \
  --host 0.0.0.0 --port 30000
# if FlashInfer misbehaves on sm_120, add: --attention-backend triton --sampling-backend pytorch
```

**Main risk:** SGLang is a **separate engine**, not a vLLM plugin — it is an alternative-system comparison, not an allocator-level drop-in, so it does not directly stress the page-granularity/UVM mechanism that is gpubpf's contribution. Use it to bracket "where gpubpf's transparent OS-level policy sits vs a framework-native radix prefix cache," not as the closest mechanism comparator.

### Conditional 3rd — Pie (SOSP'25), only if reviewer pushes on programmability

[Pie](https://github.com/pie-project/pie) (~195★, Apache-2.0, very active) ships **prebuilt `cuda12.8` binaries with an explicit `sm120` (RTX 50) target** ([install doc](https://pie-project.org/docs/guide/install)) — the cleanest sm_120 build of any system audited. It runs vLLM as a **subprocess over RPC** (does not touch the allocator), so conflict with our UVM shim is LOW. **But** Pie's research question is *programmability* (Wasm "inferlets"), and it has **no storage-tier KV story**; it is a programmability/abstraction comparator, not a memory-policy one. Try only if a reviewer asks for a programmable-serving baseline.

---

## 2. Full matrix

Legend — **sm_120:** YES / NO / REBUILD / UNCERTAIN / N/A. **Offload tier:** DRAM / **STORAGE**(NVMe/SSD) / both / none. **Effort:** LOW / MEDIUM / HIGH / **INFEASIBLE**.

### 2.1 KV-cache offload / transfer

| System | Venue + paper (fetched) | Artifact | sm_120 (evidence) | Offload tier | vLLM? (version) | Effort |
|--------|-------------------------|----------|-------------------|--------------|------------------|--------|
| **InfiniGen** | OSDI'24, [arXiv:2406.19707](https://arxiv.org/abs/2406.19707) | [snu-comparch/InfiniGen](https://github.com/snu-comparch/InfiniGen) ~190★, Apache-2.0, 4 commits, frozen Jul 2024 | **NO** — `requirements.txt` pins `torch==2.0.1` (re-verified) | DRAM | **No** (built on FlexGen) | **INFEASIBLE** (torch port + not vLLM) |
| **CachedAttention / AttentionStore** | ATC'24, [arXiv:2403.19708](https://arxiv.org/abs/2403.19708) | **NO CODE** (0 GitHub hits) | N/A (no code) | **DRAM + STORAGE** (hierarchical HBM→DRAM→disk) | No (custom Huawei engine) | **INFEASIBLE** (no artifact; 4×A100 headline) |
| **Mooncake** | FAST'25 Best Paper, [arXiv:2407.00079](https://arxiv.org/abs/2407.00079) | [kvcache-ai/Mooncake](https://github.com/kvcache-ai/Mooncake) 6.1k★, Apache-2.0, active | **REBUILD** (CUDA ≤12.9 & 13 wheels; no torch pin; verify arch list in C++/CUDA `.so`) | **DRAM + STORAGE (NVMe)** + cross-node | **Yes** (v1 `MooncakeStoreConnector`; no version pin) | **INFEASIBLE as faithful H2H** (eval needs RDMA/RoCE cluster) |
| **KVCached / kvcached** | (Berkeley; cited as baseline by later work, e.g. arXiv:2606.24506) | org [github.com/kvcached](https://github.com/kvcached) → **"This organization has no public repositories."** (re-verified) | N/A (no code) | uncertain | uncertain | **INFEASIBLE** (no public artifact) |

### 2.2 Cache / compression family (all one lab, folded into LMCache)

| System | Venue + paper | Artifact | sm_120 | Offload tier | vLLM? | Effort |
|--------|---------------|----------|--------|--------------|-------|--------|
| **LMCache** | arXiv'25 [2510.09665](https://arxiv.org/abs/2510.09665) | [LMCache/LMCache](https://github.com/LMCache/LMCache) 11k★, Apache-2.0, active | **YES** (rebuild vs torch 2.8; arch list incl. `12.0`) | **DRAM + STORAGE (FS/Raw Block/GDS)** | Yes (main/nightly) | **MEDIUM** ← *try this* |
| **CacheBlend** | EuroSys'25, [arXiv:2405.16444](https://arxiv.org/abs/2405.16444) | **No standalone** — abstract states code is in LMCache; `sirius-labs/CacheBlend` → 404 | via LMCache | via LMCache | via LMCache | **LOW** (as LMCache feature) |
| **CacheGen** | SIGCOMM'24, [arXiv:2310.07240](https://arxiv.org/abs/2310.07240) | [UChi-JCL/CacheGen](https://github.com/UChi-JCL/CacheGen) 168★, frozen Oct 2024, **self-deprecated → LMCache** | **REBUILD/UNCERTAIN** (`torchac_cuda` kernel pre-sm_120; 2024 conda env) | codec only (not a tier) | standalone = 2024 vLLM (**hard conflict**) | **HIGH** standalone / **LOW-limited** via LMCache legacy |

### 2.3 Virtual-memory / paged-KV / defragmentation (closest mechanism comparators)

| System | Venue + paper | Artifact | sm_120 (evidence) | Offload tier | vLLM? (conflict) | Effort |
|--------|---------------|----------|-------------------|--------------|-------------------|--------|
| **vAttention** | ASPLOS'25, [arXiv:2405.04437](https://arxiv.org/abs/2405.04437) | [microsoft/vattention](https://github.com/microsoft/vattention) ~507★, MIT, dormant post-2024 | **REBUILD/UNCERTAIN** — README: "requires **PyTorch 2.3.0** and **CUDA 12.1**…tested…on **A100**" (re-verified). <2 MB pages need a **custom UVM driver pinned to 545.23.06** ≠ our 575.57.08; only the 2 MB-page `cuDriver` path is portable, after a rebuild | none (in-GPU demand paging) | **No** (Sarathi-Serve, an old vLLM fork). **SEVERE conflict**: both hook `cuMem*` VMM | **INFEASIBLE** as H2H |
| **vTensor** | arXiv'24 [2407.15309](https://arxiv.org/abs/2407.15309) | [antgroup/glake](https://github.com/antgroup/glake) `/GLakeServe`, **archived Oct 2025** | **NO** — `GLakeServe/CMakeLists.txt`: `CUDA_SUPPORTED_ARCHS "7.0;7.5;8.0;8.6;8.9;9.0"`; `requirements-cuda.txt`: `torch==2.3.0` | DRAM (CPU↔GPU) | **SEVERE conflict** — bundles its own old vLLM + replaces allocator + custom flash-attn | **INFEASIBLE** |
| **GMLake** | ASPLOS'24, [arXiv:2401.08156](https://arxiv.org/abs/2401.08156) | [antgroup/glake](https://github.com/antgroup/glake) `/GMLake`, **archived** | **REBUILD/UNCERTAIN** (umbrella README: "compatible with PyTorch-1.13.1") | none (roadmap only) | **Wrong workload** (DNN *training* allocator, not serving); `libcuda.so` interceptor **collides with our UVM `LD_PRELOAD` shim** | **INFEASIBLE** / irrelevant |
| **Pie** | SOSP'25 (paper PDF ingim.org) | [pie-project/pie](https://github.com/pie-project/pie) ~195★, Apache-2.0, active | **YES** (prebuilt `cuda12.8` `sm120`/RTX-50 binary) | none | vLLM as **subprocess via RPC** (pins vLLM 0.21/torch 2.11 — ahead of our 2.8); LOW conflict | **LOW** to run / MODERATE to wire |

### 2.4 Approximation / eviction / framework

| System | Venue + paper | Artifact | sm_120 (evidence) | Offload tier | vLLM? | Effort |
|--------|---------------|----------|-------------------|--------------|-------|--------|
| **Quest** | ICML'24, [arXiv:2406.10774](https://arxiv.org/abs/2406.10774) | [mit-han-lab/Quest](https://github.com/mit-han-lab/Quest) ~400★, MIT, dormant | **REBUILD** — `pyproject.toml` pins `torch==2.5.0`, `flash-attn==2.6.3` (no sm_120); kernels use `CMAKE_CUDA_ARCHITECTURES=native` (will retarget) | none (in-GPU sparsity) | No (HF Transformers pipeline) | **MEDIUM** (flash-attn-on-sm_120 risk) |
| **NEO** | arXiv'24 [2411.01142](https://arxiv.org/abs/2411.01142) (under review) | **NO CODE** (0 GitHub hits) | N/A | DRAM | Indirect (SwiftLLM, "adaptable to vLLM") | **INFEASIBLE** (no artifact) |
| **H2O** | NeurIPS'23 | [FMInference/H2O](https://github.com/FMInference/H2O) ~529★, MIT | **YES** (no torch pin, **no custom CUDA kernels**, pure-Python eviction) | DRAM (+disk via FlexGen) | No (FlexGen/HF) | **LOW** (accuracy baseline only) |
| **Jenga** | arXiv'25 [2503.18292](https://arxiv.org/abs/2503.18292) (inference Jenga; *not* SOSP'23 OS Jenga) | **NO CODE** (no repo at any probed author/org URL) | N/A | DRAM (in-allocator) | **Would conflict** — rewrites PagedAttention allocator | **INFEASIBLE** (no artifact) |
| **FlexGen** | arXiv'23 [2303.06865](https://arxiv.org/abs/2303.06865) | [FMInference/FlexLLMGen](https://github.com/FMInference/FlexLLMGen) 9.4k★, **archived Dec 2024** | **YES** (no CUDA pin, pure-Python LP scheduler) | **DRAM + STORAGE (SSD)** — canonical | No (own engine) | **LOW to run, LOW value** (OPT-only) |
| **SGLang (RadixAttention)** | SOSP'24 | [sgl-project/sglang](https://github.com/sgl-project/sglang) 31k★, Apache-2.0 | **YES** (cu129/cu130 wheels; FlashInfer sm75+) | DRAM (prefix cache) | Separate engine | **LOW** ← *try this* |

### 2.5 2025–2026 closer prior work a reviewer may raise

| System | Venue / link | Artifact | Storage vs DRAM | sm_120? |
|--------|--------------|----------|-----------------|---------|
| **Jenga (2025)** | arXiv:2503.18292 | **NO CODE** | DRAM | uncertain |
| **Tutti** | arXiv:2605.03375 (2026) | not yet found | **STORAGE (NVMe, GPU io_uring, GDS competitor)**; vLLM-integrated | uncertain |
| **ITME** | arXiv:2606.12556 (2026) | hardware prototype (SK Hynix CMM + FPGA) | CXL + NVMe | **NO** — needs CXL HW we lack |
| **DUAL-BLADE** | ICDCS'26, arXiv:2604.26557 | TBD | **STORAGE (NVMe-direct)**, edge LLM | uncertain |
| **NVIDIA CMX** | (Context Memory Extension) | **none — hardware feature of GB300/NVL72**, no software artifact | HW | **NO** — not 5090-reproducible |
| "AttentionStore" / "Pensieve" | — | **No such KV system exists** on arXiv/GitHub (arXiv API: 0 hits); "AttentionStore" is the *storage component* of CachedAttention; "Pensieve" is a 2017 video-caching RL paper — likely misattributions | — | — |

---

## 3. Infeasible / not-runnable list (HotCRP-ready one-liners)

Each is backed by a fetched primary source. Paste-ready; group as needed.

1. **InfiniGen (OSDI'24):** the public artifact pins **`torch==2.0.1`** ([requirements.txt](https://github.com/snu-comparch/InfiniGen)), whose wheels have no Blackwell sm_120 kernels, and it is built on FlexGen rather than vLLM, so it cannot be a drop-in baseline on a UVM-modified recent vLLM.
2. **CachedAttention / AttentionStore (ATC'24):** no public code artifact exists (GitHub search returns zero repositories); only the paper describes the hierarchical HBM→DRAM→disk store, which therefore cannot be run.
3. **Mooncake (FAST'25):** its evaluated advantage is **disaggregated multi-node prefill/decode over RDMA/RoCE** (paper: multi-node A800 + NVLink/RDMA); a single RTX 5090 with no fabric is not a faithful deployment for serving H2H metrics.
4. **KVCached / kvcached:** the GitHub organization states **"This organization has no public repositories,"** so there is no artifact to build or compare against.
5. **NEO (arXiv:2411.01142):** no public source repository exists; the system is described only in an under-review preprint.
6. **CacheBlend (EuroSys'25) / CacheGen (SIGCOMM'24):** these are **not independent of LMCache** — CacheBlend's arXiv abstract states its code lives in [LMCache/LMCache](https://github.com/LMCache/LMCache), and CacheGen's standalone repo self-deprecates to LMCache; the frozen CacheGen standalone further pins a 2024 vLLM and a pre-sm_120 `torchac_cuda` kernel, so it cannot run on a UVM-modified recent vLLM without a from-scratch port.
7. **vAttention (ASPLOS'25):** the README requires **PyTorch 2.3.0 + CUDA 12.1** (pre-sm_120), is tested on **A100**, integrates with **Sarathi-Serve** (not modern vLLM), and its <2 MB-page path needs a **custom NVIDIA UVM kernel module pinned to driver 545.23.06**, which cannot load on our driver 575.57.08; its `cuMemMap` VMM layer also collides with our UVM allocator shim.
8. **vTensor (arXiv:2407.15309):** the artifact ([antgroup/glake](https://github.com/antgroup/glake) `/GLakeServe`) is **archived**, its `CMakeLists.txt` `CUDA_SUPPORTED_ARCHS` stops at **9.0** (no sm_120), it pins **torch 2.3.0**, and it bundles its own old vLLM whose allocator collides with our UVM fork.
9. **GMLake (ASPLOS'24):** the artifact is **archived**, it targets **DNN *training*** memory defragmentation (not inference/KV), and its `libcuda.so`/`libc10_cuda.so` interceptor directly collides with our UVM `LD_PRELOAD` shim.
10. **Jenga (arXiv:2503.18292, 2025):** no public artifact exists; the in-allocator design would in any case rewrite the same PagedAttention layer our UVM fork replaces.
11. **Quest (ICML'24):** not a vLLM plugin (HF Transformers pipeline) and pins `torch==2.5.0`/`flash-attn==2.6.3` without sm_120; relevant only as a *long-context sparsity/accuracy* datapoint, not a serving-throughput baseline.
12. **FlexGen (arXiv'23):** the repo is **archived** and wires up only **OPT-family** models; it is the canonical storage-tier offload prior art but not a 5090-era serving baseline for our workload.
13. **ITME (2026) / NVIDIA CMX:** ITME requires **CXL hardware** we lack; CMX is a **GB300/NVL72 hardware feature** with no 5090-reproducible software artifact.
14. **"AttentionStore" / "Pensieve" as named KV systems:** we could not locate any such system (arXiv API returns zero hits); we believe these are misattributions (AttentionStore = CachedAttention's disk tier; Pensieve = an unrelated 2017 video-caching paper) and treat them as non-systems.

---

## 4. Reviewer E's storage-tier question — direct answer

Reviewer E asked how eBPF handles **KV offload to storage** (Weka/Vast/EverPure/Nvidia CMX). The runnable evidence:

- The **only storage-tier KV system we can actually run on this 5090** is **LMCache's local-disk backend** (`FileSystem` / `Raw Block` on a plain NVMe; GDS backend exists but needs hardware we lack). This is the concrete datapoint for a storage-tier comparison, and it is the same artifact the submission already cites — we will exercise its **disk backend** explicitly.
- **Mooncake** has a real NVMe tier but is cluster-shaped; its storage path collapses to local-NVMe-on-one-node on our box (the evaluated RDMA benefit is absent), so it is discussed, not benchmarked.
- **CachedAttention/AttentionStore** and **FlexGen** are the canonical *storage*-tier prior art in the literature, but the former has **no artifact** and the latter is **archived/OPT-only**.
- **Tutti (2026)** is the newest GPU-native NVMe KV work (GPU `io_uring`, a GDS competitor); we could not confirm a public artifact or sm_120 support, so it is flagged here as the system most likely to be raised and marked **uncertain** rather than promised.
- **Nvidia CMX** is a hardware feature of GB300/NVL72, not reproducible on a single consumer Blackwell GPU; it is not a software baseline we can run.

**Net:** the design-level answer to Rev E (how gpubpf would extend to a storage tier) belongs in the paper text (revision-plan R9 already covers this); the *runnable* storage-tier baseline is LMCache-on-local-NVMe, which we will add.

---

## 5. Uncertainties

Items explicitly **not invented** — verify before any HotCRP text depends on them.

| Item | What's uncertain |
|------|------------------|
| LMCache ↔ our UVM fork coexistence | connector ABI must match our vLLM-main commit; UVM managed pages vs LMCache pinned-buffer streams interaction **uncharacterized** — needs a smoke test |
| SGLang FlashInfer on sm_120 | cu129/cu130 wheels cover sm_120 in principle; one edge case may need `--attention-backend triton` fallback — **not run on this host** |
| Pie paper venue | README claims SOSP'25; PDF URL fetched but text not machine-extracted — venue treated as "2025" pending DOI |
| Pie ↔ our UVM vLLM | pins vLLM 0.21 / torch 2.11 (ahead of our 2.8); swapping our wheel is plausible but **untested** |
| Mooncake `.so` arch list | CUDA 12.9/13 wheels advertised; whether the transfer-engine NVCC arch list includes `12.0` **not verified** (would need a source rebuild) |
| Mooncake on single node | builds/installs, but a degenerate TCP-local config the paper never benchmarked — **low scientific value**, not "uncertain" on facts |
| Quest flash-attn on sm_120 | flash-attn 2.6 has no prebuilt sm_120 wheel; rebuild risk **unverified** |
| vAttention 2 MB-page path on sm_120 | portable in principle (stock `cuDriver` VMM) but **never rebuilt against torch cu128**; <2 MB page path is definitively blocked by the driver-545 requirement |
| Jenga / NEO / Tutti / DUAL-BLADE artifacts | no public repo found; **uncertain** whether a private release exists via authors |
| Star counts | approximate at fetch time (GitHub rate-limits mid-audit); re-check before quoting exact ★ in the paper |
| gpt-oss-120b | needs TP=2 on a single 32 GB card → unrunnable here; all gpt-oss datapoints use **gpt-oss-20b**, on which LMCache's CacheBlend/CacheGen are "Not validated" |

---

## 6. Recommendation snapshot

| Bucket | Action |
|--------|--------|
| **Run (this revision)** | **LMCache local-disk/SSD backend** (storage-tier KV, answers Rev E) + **SGLang RadixAttention** (research-engine H2H). |
| **Conditional** | **Pie** if a reviewer demands a programmable-serving comparator (sm_120-native, no storage tier). |
| **Discuss, don't run** | vAttention (closest same-venue mechanism — cite the driver-545 / torch-2.3 / allocator-conflict reasons), Mooncake (RDMA), CachedAttention/FlexGen (storage-tier prior art), Quest/H2O (sparsity/accuracy, different metric). |
| **Cite as unavailable** | InfiniGen (torch 2.0.1), KVCached/NEO/Jenga (**NO CODE**), vTensor/GMLake (archived/no sm_120), CMX/ITME (hardware we lack). |
| **Do not promise** | Any vAttention <2 MB-page number on driver 575; any Mooncake RDMA number; any gpt-oss-120b number on one 32 GB card. |

---

## 7. Evidence index (fetched URLs)

The five (*) were re-fetched directly by the auditor this session; the remainder were fetched during the parallel primary-source research pass.

- *https://raw.githubusercontent.com/LMCache/LMCache/dev/pyproject.toml — **TORCH_CUDA_ARCH_LIST incl. `12.0` (RTX 50-series PTX)**; build torch 2.13.0, runtime unpinned
- https://docs.lmcache.ai/mp/l2_storage/file_and_block.html — local FileSystem / Raw-Block NVMe backends
- https://docs.lmcache.ai/recipes/gpt_oss.html — gpt-oss validated; 120b needs TP=2; CacheBlend/CacheGen "Not validated" for gpt-oss
- https://github.com/LMCache/LMCache — repo, ~11k★, active
- *https://docs.sglang.io/get_started/install.html — **cu129/cu130 wheels; torch 2.11.0+cu129; FlashInfer sm75+**; 5090-class covered
- https://github.com/sgl-project/sglang — repo, ~31k★
- *https://raw.githubusercontent.com/snu-comparch/InfiniGen/main/requirements.txt — **`torch==2.0.1`** (sm_120 blocker)
- https://arxiv.org/abs/2406.19707 — InfiniGen paper
- https://github.com/snu-comparch/InfiniGen — repo, frozen
- *https://github.com/kvcached — **"This organization has no public repositories."**
- *https://raw.githubusercontent.com/microsoft/vattention/main/README.md — **"requires PyTorch 2.3.0 and CUDA 12.1…tested…on A100"; <2 MB pages need custom UVM driver (545.23.06); Sarathi-Serve not vLLM**
- https://github.com/microsoft/vattention — repo, ~507★
- https://github.com/microsoft/vattention/tree/main/nvidia-vattn-uvm-driver — modified driver pinned to 545.23.06
- https://arxiv.org/abs/2405.04437 — vAttention paper
- https://github.com/antgroup/glake/blob/master/GLakeServe/CMakeLists.txt — `CUDA_SUPPORTED_ARCHS "7.0;…;9.0"` (no sm_120); repo archived Oct 2025
- https://github.com/antgroup/glake/blob/master/GLakeServe/requirements-cuda.txt — `torch==2.3.0`
- https://arxiv.org/abs/2407.15309 — vTensor paper
- https://arxiv.org/abs/2401.08156 — GMLake paper (training defrag, A100 80GB)
- https://pie-project.org/docs/guide/install — prebuilt `cuda12.8` `sm120` (RTX 50) binary
- https://github.com/pie-project/pie — repo, ~195★; vLLM subprocess driver pins vLLM 0.21/torch 2.11
- https://github.com/kvcache-ai/Mooncake — repo, 6.1k★; CUDA 12.9/13 wheels; no torch pin
- https://arxiv.org/abs/2407.00079 — Mooncake paper (multi-node A800 + RDMA)
- https://arxiv.org/abs/2403.19708 — CachedAttention/AttentionStore paper (no artifact)
- https://arxiv.org/abs/2310.07240 — CacheGen paper; repo github.com/UChi-JCL/CacheGen (self-deprecated → LMCache)
- https://arxiv.org/abs/2405.16444 — CacheBlend paper (code in LMCache; sirius-labs/CacheBlend → 404)
- https://github.com/mit-han-lab/Quest/blob/main/pyproject.toml — `torch==2.5.0`, `flash-attn==2.6.3`
- https://arxiv.org/abs/2406.10774 — Quest paper
- https://arxiv.org/abs/2411.01142 — NEO paper (no artifact)
- https://github.com/FMInference/H2O — repo, no CUDA kernels, FlexGen/HF
- https://github.com/FMInference/FlexLLMGen — repo, archived, OPT-only, DRAM+SSD offload
- https://arxiv.org/abs/2503.18292 — Jenga (2025, inference; no artifact)
- https://arxiv.org/abs/2605.03375 — Tutti (2026, NVMe KV; artifact uncertain)
- https://arxiv.org/abs/2606.12556 — ITME (2026, needs CXL HW)
- arXiv API (export.arxiv.org/api/query): ti:"AttentionStore" → 0; all:"Pensieve"+"KV cache" → 0 (non-existent as KV systems)

---

*End of audit. Standalone file. This is a feasibility assessment, not a HotCRP promise — select rows from §1/§3 once smoke-tests confirm the §5 uncertainties.*
