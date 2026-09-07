# ASPLOS'27 #1797 — SOTA Research Baseline Hardware Feasibility Audit

**Paper:** gpubpf / gpu_ext (ASPLOS'27 submission #1797)  
**Scope:** Can named SOTA research *artifacts* be built and run on our hardware as head-to-head baselines?  
**Complementary file:** `reproducibility-commitments.md` (policy expressibility / HotCRP promise tiers — do not conflate)  
**Audit date:** 2026-08-03  
**Auditor method:** Primary sources only (GitHub README/requirements/releases, paper PDFs, arXiv HTML). Every URL below was fetched during this audit. Verdicts that could not be confirmed are marked **uncertain**.

---

## Hardware constraint (hard)

| Resource | Available |
|----------|-----------|
| GPU 1 | **1× NVIDIA GeForce RTX 5090**, 32 GB, **Blackwell sm_120**, driver **575.57.08** |
| GPU 2 | Tesla P40 (Pascal sm_61) — secondary only |
| Missing | A100, H100, multi-GPU, NVLink, MIG (5090 has no MIG) |
| Workloads | llama.cpp (gpt-oss-20b/120b MoE), vLLM (KV offload), FAISS SIFT, PyTorch GNN |
| Wall-clock | ~4 weeks, shared with writing |

**sm_120 floor (cross-cutting):** CUDA Toolkit **12.8+** for native Blackwell. PyTorch needs **cu128** builds with `sm_120` in `torch.cuda.get_arch_list()` (nightly/source from ~Jan 2025 onward; older `torch<=2.4` wheels stop at sm_90). Any artifact pinned to `torch==2.0`/`2.1`/`2.3` without rebuild is **not** a drop-in on the 5090.

---

## 1. Top-3 runnable (recommend for head-to-head on the 5090)

These three maximize reviewer value per unit of engineering risk under the 5090 constraint.

### 1) MoE-Infinity (EfficientMoE) — **best MoE H2H**

| Field | Value |
|-------|--------|
| Venue | arXiv 2024 → serving system paper ([arXiv:2401.14361](https://arxiv.org/abs/2401.14361)) |
| Artifact | https://github.com/EfficientMoE/MoE-Infinity — Apache-2.0, ~333★, last push **2026-08-03** (active) |
| sm_120 | **YES (explicit).** README: default build targets `sm_80`/`sm_90`; Blackwell needs `MOE_ENABLE_SM120=1` ([README § Install from Source](https://github.com/EfficientMoE/MoE-Infinity)) |
| Hardware | Single GPU with host/SSD expert offload; paper/open-source path does **not** require multi-GPU or NVLink. Suggested ≥16 GB VRAM for DeepSeek-V2-Lite; 32 GB 5090 is fine |
| Workload match | **Strong:** HF MoE class lists **GPT-OSS**, Mixtral, Qwen3-MoE, DeepSeek-V2/V3. Does **not** plug into our llama.cpp/vLLM submodules (separate HF runtime) |
| Effort | **MEDIUM** (build from source + CUTLASS + torch cu128) |

**First command to try:**
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu128
git clone --depth 1 https://github.com/NVIDIA/cutlass.git ~/cutlass
export CUTLASS_DIR=~/cutlass
git clone https://github.com/EfficientMoE/MoE-Infinity.git && cd MoE-Infinity
MOE_ENABLE_SM120=1 MOE_ENABLE_SM90=0 CUTLASS_DIR=~/cutlass \
  pip install --no-build-isolation -e .
CUDA_VISIBLE_DEVICES=0 python examples/deepseek_v2_chat_example.py --offload_dir /fast/ssd/moe-offload
```

**Main risk:** Open-source build is “redesigned / HF-friendly” and **differs from the paper’s extreme-performance path** (README disclaimer). Numbers will be fair as “public MoE-Infinity,” not as paper Table X. Also depends on successful SM120 CUDA extension compile on driver 575.

---

### 2) XSched (OSDI'25) — **best scheduling H2H without driver surgery**

| Field | Value |
|-------|--------|
| Venue | OSDI 2025 ([USENIX page](https://www.usenix.org/conference/osdi25/presentation/shen-weihang)); PDF in-repo |
| Artifact | https://github.com/XpuOS/xsched — Apache-2.0, ~176★, last push **2026-07-25** |
| sm_120 | **UNCERTAIN → likely Level-1 only.** Support matrix: CUDA Level-1 ✅ on Ampere (sm86) / Volta (sm70); **“Other NVIDIA GPUs” = not yet implemented (🔘)**. Shim intercepts driver APIs (architecture-agnostic in principle); Level-2/3 preemption unfinished even on Ampere |
| Hardware | Single consumer GPU OK; no MIG/NVLink required. Transparent `LD_PRELOAD` path |
| Workload match | **llama.cpp integration exists** in-tree (`integration/llama.cpp`). Good pairing with our MoE/llama.cpp eval |
| Effort | **MEDIUM** (cmake build + env-var transparent schedule) |

**First command to try:**
```bash
git clone https://github.com/XpuOS/xsched.git && cd xsched
git submodule update --init --recursive
make PLATFORM=cuda
# then follow examples/Linux/1_transparent_sched/README.md with env vars on a llama.cpp binary
```

**Main risk:** sm_120 may only get **shim + Level-1** (queue/preempt-lite), not paper-level Level-3. Still the most honest open scheduling artifact that does not require a **custom NVIDIA kernel module**. Artifacts also at https://github.com/XpuOS/xsched-artifacts and Zenodo 10.5281/zenodo.15327992.

---

### 3) LMCache (+ CacheBlend path) — **strengthen existing KV baseline (LOW risk)**

| Field | Value |
|-------|--------|
| Venue | Production stack; research lineage CacheGen (SIGCOMM'24), CacheBlend (EuroSys'25), LMCache survey paper [arXiv:2510.09665](https://arxiv.org/abs/2510.09665) |
| Artifact | https://github.com/LMCache/LMCache — Apache-2.0, ~11k★, last push **2026-08-04**, PyTorch Foundation |
| sm_120 | **Likely YES** if paired with modern vLLM + torch cu128 (project actively ships gpt-oss day-1 support, Aug 2025 blog). No pinned `torch==2.x` in top-level README |
| Hardware | Single GPU + CPU/disk tier fine; multi-node/RDMA optional |
| Workload match | **Direct:** vLLM connector; README claims **gpt-oss 20B/120B** support. Aligns with our `workloads/vllm/` |
| Effort | **LOW** (`pip install lmcache` + vLLM recipe) |

**First command to try:**
```bash
# inside workloads/vllm venv (uv)
uv pip install lmcache
# then follow https://docs.lmcache.ai/getting_started/quickstart.html with our vLLM submodule
```

**Main risk:** Reviewers may call this “framework baseline” not “research SOTA OS system.” Use it as the **KV research baseline we already cite**, with clearer methodology—not as the sole answer to Rev E/F. Pair with MoE-Infinity + XSched for a three-axis story (MoE / KV / sched).

---

### Near-miss runners (if Top-3 slip)

| System | Why near-miss | When to promote |
|--------|---------------|-----------------|
| **PowerInfer** (https://github.com/Tiiny-AI/PowerInfer) | Consumer-GPU MoE/sparse hybrid; MIT; active. Needs CUDA rebuild for sm_120; models are **ReLU-sparse Llama/Falcon**, not gpt-oss/Mixtral | If MoE-Infinity build fails; still a real H2H vs llama.cpp offload |
| **ProMoE** (https://github.com/promoe-opensource/promoe) | Paper claims transformers + **llama.cpp** integration ([arXiv:2410.22134](https://arxiv.org/abs/2410.22134)); small repo (~20★) | If we want llama.cpp-native MoE cache SOTA |
| **kvcached** (https://github.com/ovg-project/kvcached) | 2025/26 elastic KV via CUDA VMM; `pip install kvcached`; vLLM/SGLang | Stronger multi-tenant KV story; sm_120 status **uncertain** (CUDA VMM should work; not verified) |
| **NVBit ≥1.7.4** | **SM_120 added in 1.7.4**; README SM ≤12.1; latest **1.8** (2026-04) adds Blackwell TMA | Instrumentation/observability baseline, not policy H2H |

---

## 2. Full matrix

Legend — **sm_120:** YES / NO / REBUILD / UNCERTAIN / N/A. **Effort:** LOW / MEDIUM / HIGH / INFEASIBLE.

### 2.1 MoE / GPU-memory offloading

| System | Venue + paper | Artifact | Last commit* | sm_120 | HW blocker | Workload match | Effort |
|--------|---------------|----------|--------------|--------|------------|----------------|--------|
| **Huang et al. (Expert Buffering)** | arXiv 2023 [2303.06182](https://arxiv.org/abs/2303.06182) (Meta; Rev E named) | **NO CODE** — paper said “code will be open-sourced upon acceptance”; no GitHub found after search | — | N/A | — | Conceptual only (expert buffering / dynamic gating) | **INFEASIBLE** |
| **KTransformers** | SOSP'25 (repo cites SOSP; Tsinghua MadSys PDF) | https://github.com/kvcache-ai/ktransformers — Apache-2.0, ~19k★ | 2026-08-02 | **NO in wheels** — kt-kernel docs: CUDA SM **80/86/89/90 only** ([kt-kernel/README](https://github.com/kvcache-ai/ktransformers/blob/main/kt-kernel/README.md)); RTX 50 not listed | None if source rebuild with sm_120 succeeds | MoE hybrid CPU/GPU; Qwen3-MoE examples; **not** our llama.cpp submodule (SGLang-kt path) | **HIGH** (source rebuild + AMX/CPU path optional) |
| **MoE-Infinity** | arXiv'24 [2401.14361](https://arxiv.org/abs/2401.14361) | https://github.com/EfficientMoE/MoE-Infinity — Apache-2.0, ~333★ | 2026-08-03 | **YES** with `MOE_ENABLE_SM120=1` | None for single-GPU path | GPT-OSS, Mixtral, Qwen3-MoE; separate HF stack | **MEDIUM** |
| **Mixtral-offloading** | arXiv tech report [2312.17238](https://arxiv.org/abs/2312.17238) | https://github.com/dvmazur/mixtral-offloading — ~2.3k★ | 2024-04-08 (stale) | **REBUILD** — `torch>=2.1.0`, transformers 4.36.1 | None for 24–32 GB + host RAM | Mixtral-8x7B only; notebook-centric | **MEDIUM** |
| **Fiddler** | ICLR'25 / arXiv [2402.07033](https://arxiv.org/abs/2402.07033) | https://github.com/efeslab/fiddler — ~?★ (reachable) | uncertain (README 2024) | **NO** without rebuild — pins **torch==2.1.2** ([requirements.txt](https://raw.githubusercontent.com/efeslab/fiddler/main/requirements.txt)) | None (24 GB class OK) | Mixtral-8x7B only; PoC | **HIGH** |
| **ProMoE** | arXiv [2410.22134](https://arxiv.org/abs/2410.22134) | https://github.com/promoe-opensource/promoe — ~20★ | 2025-01-27 | UNCERTAIN | None claimed (consumer GPU paper) | Claims transformers + **llama.cpp** integration | **MEDIUM** |
| **Pre-gated MoE** | ISCA'24 [2308.12066](https://arxiv.org/abs/2308.12066) | https://github.com/ranggihwang/Pregated_MoE — FasterTransformer fork | ~7 commits (AE snapshot) | **REBUILD** — cmake `-DSM=80` table lists P40…A10, **no sm_120** ([README](https://github.com/ranggihwang/Pregated_MoE)) | Paper AE on A100-class; multi-GPU flags in cmake | Switch Transformer T5-MoE family, not gpt-oss | **HIGH** |
| **SwapMoE** | ACL'24 [2308.15030](https://arxiv.org/abs/2308.15030) | https://github.com/fqt111/SwapMoE (3★) / MobileLLM/SwapMoE (1★) | 2024-08 / 2024-10 | UNCERTAIN | uncertain | Off-the-shelf MoE; **uncertain** gpt-oss | **HIGH** (dormant tiny repos) |
| **EdgeMoE** | arXiv [2308.14352](https://arxiv.org/abs/2308.14352) | Code claimed at https://github.com/UbiquitousLearning/mllm (mobile/NPU-oriented stack) | uncertain | N/A / mobile | **On-device / mobile**, not 5090 datacenter H2H | Mobile MoE, not our stack | **INFEASIBLE** as fair GPU baseline |
| **DeepSpeed-MoE / ZeRO-Inference** | Microsoft; ongoing | https://github.com/deepspeedai/DeepSpeed — Apache-2.0, ~43k★ | 2026-08-04 | **Likely YES** with modern CUDA/torch (framework, not frozen AE) | ZeRO-Inference multi-GPU optional; single-GPU offload OK | MoE training/inference; integration effort with our models | **MEDIUM** |
| **FlexGen** | arXiv 2023 | https://github.com/FMInference/FlexLLMGen — Apache-2.0, ~9.3k★, **archived** | 2024-10-28 | REBUILD / stale | Single GPU OK by design | OPT/Llama-era throughput offload; not MoE-native | **MEDIUM** (archived) |
| **HeteGen** | (candidate list) | **NO CODE** found under this name for MoE offload research | — | N/A | — | — | **INFEASIBLE** |
| **PowerInfer / PowerInfer-2** | ASPLOS-era / arXiv [2312.12456](https://arxiv.org/abs/2312.12456); P2 [2406.06282](https://arxiv.org/abs/2406.06282) | https://github.com/Tiiny-AI/PowerInfer — MIT, ~9.7k★; P2 is **smartphone** framework (not desktop H2H) | 2026-05-11 | REBUILD (ggml-cuda) | P1: consumer GPU OK; P2: phone NPU/SoC | ReLU-sparse models; **not** gpt-oss; format PowerInfer-GGUF | **MEDIUM** (P1 only) |

\*Last commit from GitHub API/page at audit time when available; else from README activity.

### 2.2 KV-cache / inference memory

| System | Venue + paper | Artifact | Last commit* | sm_120 | HW blocker | Workload match | Effort |
|--------|---------------|----------|--------------|--------|------------|----------------|--------|
| **InfiniGen** | OSDI'24 | https://github.com/snu-comparch/InfiniGen — ~190★ | 2024-07-10 (4 commits) | **NO** — pins **torch==2.0.1** ([requirements.txt](https://raw.githubusercontent.com/snu-comparch/InfiniGen/main/requirements.txt)) | None otherwise | Offloading LLM KV; not vLLM plug-in | **HIGH** (torch port) |
| **CachedAttention / AttentionStore** | ATC'24 | **NO public system artifact found** (paper only; Huawei Cloud coauthors) | — | N/A | — | Multi-turn KV reuse concept | **INFEASIBLE** |
| **Mooncake** | FAST'25 Best Paper | https://github.com/kvcache-ai/Mooncake — Apache-2.0, ~6.1k★ | 2026-08-03 | UNCERTAIN | **Cluster-scale:** paper eval on multi-node **A800 + RDMA/NVLink**; disagg prefill/decode | Traces released; production Kimi stack — not single-5090 H2H | **INFEASIBLE** as fair H2H (discuss only) |
| **LMCache / CacheBlend / CacheGen** | EuroSys'25 / SIGCOMM'24 / arXiv'25 | https://github.com/LMCache/LMCache | 2026-08-04 | Likely YES (modern stack) | None for single-node | **gpt-oss**; vLLM | **LOW** |
| **Quest** | ICML'24 | https://github.com/mit-han-lab/Quest | ~21 commits | REBUILD — custom CUDA kernels; paper eval on **Ada6000 / RTX 4090** (sm_89), CUDA 12.4 | None | Long-context Llama/Mistral; **not** MoE gpt-oss | **HIGH** |
| **NEO** | (candidate list) | **uncertain** — no unique OSDI/ASPLOS artifact pinned under this name during audit | — | UNCERTAIN | — | — | **uncertain** |
| **Pie** | Programmable serving | https://github.com/pie-project/pie | active 2026 | UNCERTAIN | None claimed | Wasm inferlets; custom KV policies — different abstraction | **MEDIUM–HIGH** |
| **vAttention** | ASPLOS'25 | https://github.com/microsoft/vattention | ~124 commits | **REBUILD** — requires **PyTorch 2.3.0 + CUDA 12.1**, tested on **A100**; optional **custom UVM driver** for <2MB pages | A100-class validation; custom driver risk on 575 | Sarathi-Serve + Llama/Yi; not gpt-oss MoE | **HIGH** |
| **GMLake** | ASPLOS'24 | https://github.com/intelligent-machine-learning/glake (antgroup/glake) | uncertain | UNCERTAIN | Paper on **A100 80 GB** fragmentation; VMM stitching should be arch-agnostic | Training memory allocator; not inference MoE | **MEDIUM** |
| **Jenga** | (candidate) | **NO CODE** found under this name for KV systems | — | N/A | — | — | **INFEASIBLE** |
| **KVCached / kvcached** | 2025–26 (Berkeley Sky et al.) | https://github.com/ovg-project/kvcached | active | UNCERTAIN (CUDA VMM) | None for single GPU | vLLM/SGLang elastic KV | **MEDIUM** |

### 2.3 UVM / oversubscription

| System | Venue + paper | Artifact | Last commit* | sm_120 | HW blocker | Workload match | Effort |
|--------|---------------|----------|--------------|--------|------------|----------------|--------|
| **DeepUM** | ASPLOS'23 | **NO CODE** — ACM page / papers cite work; no public repo found (search: DeepUM ASPLOS github) | — | N/A | Modified UVM **driver** in paper design | DNN training UVM | **INFEASIBLE** |
| **G10** | MICRO/ISCA lineage [2310.09443](https://arxiv.org/html/2310.09443); Zenodo 10.5281/zenodo.8294395 | https://github.com/platformxlab/G10 — Apache-2.0 | few commits | **N/A (simulator)** | README: **any x86, no GPU required** — “performance simulation of DNN training” on UVMSmart traces | DNN training graphs, not our inference | **INFEASIBLE** as real-GPU H2H |
| **Forest** | ISCA'25 | **No public software artifact found** in this audit (SW/HW codesign; PDF only) | — | N/A | Prefetcher HW component | UVM page migration | **INFEASIBLE** / discussion |
| **Sentinel** | (candidate) | **NO CODE** found | — | N/A | — | — | **INFEASIBLE** |
| **TensorStore** | (candidate name collision w/ Google tensorstore) | Not a GPU UVM research baseline under this name | — | N/A | — | — | **skip** |

### 2.4 Scheduling / sharing / instrumentation

| System | Venue + paper | Artifact | Last commit* | sm_120 | HW blocker | Workload match | Effort |
|--------|---------------|----------|--------------|--------|------------|----------------|--------|
| **GPREEMPT** | ATC'25 | https://github.com/thustorage/GPreempt — Apache-2.0, ~25★ | 2025-05-18 | N/A | **Custom NVIDIA kernel module based on driver 550.120**; our driver is **575.57.08** — cannot load without replacing host driver (research-only, voids support) | TVM-compiled models, not llama.cpp/vLLM | **INFEASIBLE** (driver mismatch) |
| **Orion** | EuroSys'24 | https://github.com/eth-easl/orion (`cuda1011_version` for AE) | uncertain | REBUILD / CUDA 10–11 era AE branch | Paper AE uses older CUDA docker | Operator-level ML sharing | **HIGH** |
| **Tally** | ASPLOS'25 | https://github.com/tally-project/tally-bench (+ submodule `tally`) | ~140 commits on bench | UNCERTAIN | **Requires NVIDIA A100 40 GB**; Docker image **~130 GB**; paper eval on p4d A100 | Generic DL train/infer; not our MoE | **INFEASIBLE** on 5090-only claim of “same as paper”; **HIGH** if re-target |
| **XSched** | OSDI'25 | https://github.com/XpuOS/xsched | 2026-07-25 | UNCERTAIN (Other GPUs 🔘) | None | llama.cpp integration | **MEDIUM** |
| **Neutrino** | OSDI'25 | https://github.com/open-neutrino/neutrino | 2025-12-25 | UNCERTAIN | None for build | **Profiler** (eBPF-like probes), not a competing memory/sched policy | **MEDIUM** (wrong comparison type) |
| **REEF** | OSDI'22 | https://github.com/SJTU-IPADS/reef-artifacts | uncertain | N/A on CUDA 5090 | AE heavily **ROCm/AMD** + old Ubuntu; GPreempt AE notes REEF CUDA path unavailable | Idempotent kernels | **INFEASIBLE** on our CUDA stack |
| **Paella** | SOSP'23 | https://github.com/eniac/paella (also MachineLearningSystem/23sosp-paella) | uncertain | REBUILD | Driver tested **535.54.03**; software-defined sched needs model compiler co-design | Model serving microservices | **HIGH** |
| **TGS** | NSDI'23 | https://github.com/pkusys/TGS | uncertain | UNCERTAIN | Kubernetes/container cloud; kernel-rate control | DL training containers | **HIGH** |
| **LithOS** | SOSP'25 | **NO public code found** (paper claims ~5k LOC Rust; no GitHub in this audit) | — | N/A | TPC/atomization; Meta+CMU | Whole GPU OS | **INFEASIBLE** (no artifact) |
| **GCAPS** | ECRTS'24 | https://github.com/rtenlab/gcaps-super-repo | uncertain | N/A | **NVIDIA Tegra** driver context-switching RTOS | Real-time embedded | **INFEASIBLE** (wrong platform) |
| **NVBit** | MICRO'19 + ongoing NVlabs | https://github.com/NVlabs/NVBit/releases — binary artifacts | **v1.8** 2026-04-06 | **YES** — SM_120 since **v1.7.4**; README SM 3.5–**12.1**; driver **≤575.xx** (matches 575.57.08) | Research prototype EULA | Instrumentation, not policy baseline | **LOW–MEDIUM** (tooling) |

### 2.5 Newer systems reviewers may name (2025–2026)

| System | Note | Feasible on 5090? |
|--------|------|-------------------|
| **kvcached** | Elastic KV via CUDA VMM; Apache-2.0; vLLM/SGLang | **MEDIUM** — try `pip install kvcached --no-build-isolation` |
| **Pie** | Programmable Wasm serving | Different research question (programmability vs memory policy) |
| **HybriMoE** (DAC'25) | Hybrid CPU-GPU MoE | Code claimed PKU-SEC-Lab/HybriMoE — **uncertain**, not fully audited |
| **DAOP** | arXiv [2501.10375](https://arxiv.org/html/2501.10375v2); code https://github.com/ecolab-nus/DAOP | **uncertain** sm_120; MoE offload competitor |

---

## 3. Legitimately infeasible list (HotCRP-ready one-liners)

Paste-ready justifications. Each is backed by a fetched primary source.

1. **Huang et al. (arXiv:2303.06182, Expert Buffering):** No public artifact; the preprint stated code “will be open-sourced upon acceptance,” and no repository has appeared as of this audit — comparison is limited to conceptual discussion of expert buffering.

2. **DeepUM (ASPLOS'23):** No public code repository exists for the DeepUM UVM driver/prefetching system; paper describes a custom UVM page-fault path that cannot be re-run without an unpublished artifact.

3. **G10 (MICRO/ISCA UVM storage):** Public artifact (https://github.com/platformxlab/G10, Zenodo 10.5281/zenodo.8294395) is a **CPU-only performance simulator** extended from UVMSmart; it does not execute on real GPUs and cannot serve as a head-to-head baseline on RTX 5090.

4. **GPREEMPT (ATC'25):** Artifact requires a **patched NVIDIA open kernel module based on driver 550.120** (https://github.com/thustorage/GPreempt README); our production host runs driver **575.57.08**, and loading a 550-based research module is unsafe and unsupported — we implement a GPREEMPT-equivalent policy in gpubpf instead.

5. **Tally (ASPLOS'25):** Official AE harness **requires an NVIDIA A100 40 GB** and a ~130 GB Docker image (https://github.com/tally-project/tally-bench README “Required Hardware”); we have a single RTX 5090 32 GB and cannot reproduce their AE configuration.

6. **Mooncake (FAST'25):** Open-source stack targets **disaggregated multi-node prefill/decode with RDMA** (paper: multi-node A800 + NVLink/RDMA); our single 5090 without RDMA cluster is not a faithful deployment target for H2H serving metrics.

7. **LithOS (SOSP'25):** No public source release found; paper describes a full GPU OS (~5k LOC Rust) that cannot be executed without an artifact.

8. **CachedAttention / AttentionStore (ATC'24):** No public system codebase located; only paper-level description of hierarchical KV store — cannot run head-to-head.

9. **Forest (ISCA'25 UVM):** Software-hardware codesign without a released full-system artifact suitable for real-GPU baseline runs in this audit.

10. **REEF (OSDI'22) on our CUDA host:** Public AE paths emphasize **ROCm/AMD** and outdated Ubuntu; GPreempt AE notes REEF CUDA cannot run on current Ubuntu — not a viable CUDA 5090 baseline.

11. **GCAPS (ECRTS'24):** Artifact targets **NVIDIA Tegra** real-time drivers (https://github.com/rtenlab/gcaps-super-repo), not GeForce desktop GPUs.

12. **EdgeMoE:** Targets **on-device/mobile** MoE inference (mllm / phone SoCs), not a server GPU memory-management baseline comparable to gpubpf.

13. **InfiniGen as-is:** Public AE pins **PyTorch 2.0.1** (https://github.com/snu-comparch/InfiniGen/blob/main/requirements.txt), which has **no sm_120 kernels**; running requires a non-trivial port to torch cu128.

14. **Fiddler as-is:** Pins **torch==2.1.2** (https://github.com/efeslab/fiddler/blob/main/requirements.txt), incompatible with Blackwell without a full dependency modernization.

15. **KTransformers prebuilt wheels:** Official kt-kernel wheels document CUDA support for **SM 80/86/89/90 only** (https://github.com/kvcache-ai/ktransformers/blob/main/kt-kernel/README.md); Blackwell sm_120 requires uncharted source rebuild.

16. **vAttention paper config:** README requires **PyTorch 2.3.0 + CUDA 12.1**, tested on **A100**, and optional **custom NVIDIA UVM driver** for small pages — not a low-risk drop-in on driver 575 / sm_120.

17. **HeteGen / Jenga / Sentinel (as listed):** No identifiable public research artifacts under these names for the intended systems; cannot compare code that does not exist.

---

## 4. Uncertainties

Items explicitly **not invented** — need a short follow-up if HotCRP text depends on them:

| Item | What’s uncertain |
|------|------------------|
| XSched on sm_120 | Matrix marks “Other NVIDIA GPUs” unimplemented; Level-1 shim may still intercept 5090 — **not verified by a compile/run on this host** |
| MoE-Infinity SM120 compile | README documents the flag; we have **not** executed the build on this machine’s CUDA 12.8 toolchain |
| KTransformers source rebuild | Whether CUDA extensions accept `TORCH_CUDA_ARCH_LIST=12.0` / sm_120 is **unverified** |
| PowerInfer ggml-cuda on sm_120 | Expected to work if cmake uses CUDA 12.8 + arch list; **not verified** |
| ProMoE repo quality | Paper claims llama.cpp integration; repo is small and last pushed 2025-01 — completeness **uncertain** |
| Neutrino on Blackwell SASS/PTX | OSDI'25 claims CUDA support; SM120 SASS probing **uncertain** |
| kvcached VMM on 5090 | CUDA virtual memory APIs should be arch-agnostic; **not run** |
| GMLake / Orion / Paella / TGS exact last-commit dates and torch pins | Partial page loads; treat as **uncertain** until re-cloned |
| LithOS private release | Possibly available via authors; not public at audit time |
| NVBit driver “≤575.xx” exactness | README states `CUDA driver version: <= 575.xx`; our 575.57.08 is at the ceiling — **smoke-test required** before relying on it |
| Star counts | Approximate at API fetch time (rate-limit mid-audit); re-check before citing exact ★ in paper |
| “SOSP'24” vs “SOSP'25” for KTransformers | Local rebuttal folder has `ktransformers-sosp24.pdf`; live repo citation year shows **2025** — use the PDF/DOI you ship, not the informal year label |

---

## 5. Recommendation for HotCRP (does not rewrite reproducibility-commitments)

| Promise tier | What to say |
|--------------|-------------|
| **Safe H2H to attempt** | MoE-Infinity (MoE expert offload SOTA with explicit sm_120 path); XSched (sched, transparent, no driver patch); LMCache (KV, already in eval) |
| **Safe non-run justifications** | Huang / DeepUM / LithOS / CachedAttention: **no public artifact**; G10: **simulator-only**; GPREEMPT: **driver 550 module vs our 575**; Tally: **A100-required AE**; Mooncake: **multi-node RDMA** |
| **Do not promise** | Full Huang reproduction; GPREEMPT kernel module on 575; Tally AE numbers on 5090; InfiniGen/Fiddler without torch modernization time |
| **Expressibility vs re-run** | Keep GPREEMPT-**equivalent** gpubpf policy foreground (see `reproducibility-commitments.md`); cite XSched/Neutrino as related scheduling/instrumentation with optional partial runs |

### Suggested revision-plan sentence (hardware-honest)

> For state-of-the-art *runnable* research baselines under our single RTX 5090 (sm_120) constraint, we will head-to-head against **MoE-Infinity** (activation-aware expert offload; public artifact with explicit `MOE_ENABLE_SM120`) and strengthen the **LMCache** KV comparison; for preemptive multi-tenant scheduling we compare against **XSched**’s open transparent stack rather than GPREEMPT’s driver-550 kernel module, which cannot load on driver 575.57.08. Systems without public artifacts (Huang et al. Expert Buffering, DeepUM, LithOS) or simulator-only artifacts (G10) are discussed with citable unavailability rather than silent omission.

---

## 6. Evidence index (fetched URLs)

| URL | Used for |
|-----|----------|
| https://github.com/EfficientMoE/MoE-Infinity | MoE-Infinity sm_120, models, install |
| https://github.com/kvcache-ai/ktransformers + kt-kernel/README.md | KTransformers SM list |
| https://github.com/efeslab/fiddler + requirements.txt | Fiddler torch pin |
| https://github.com/dvmazur/mixtral-offloading | Mixtral-offloading |
| https://github.com/snu-comparch/InfiniGen + requirements.txt | InfiniGen torch 2.0.1 |
| https://github.com/microsoft/vattention | vAttention A100 / torch 2.3 |
| https://github.com/platformxlab/G10 | G10 simulator-only |
| https://github.com/thustorage/GPreempt | Driver 550.120 requirement |
| https://github.com/XpuOS/xsched | XSched matrix / llama.cpp |
| https://github.com/open-neutrino/neutrino | Neutrino profiler |
| https://github.com/NVlabs/NVBit + /releases | SM_120 since 1.7.4; driver ≤575 |
| https://github.com/LMCache/LMCache | LMCache / gpt-oss |
| https://github.com/kvcache-ai/Mooncake | Mooncake cluster scope |
| https://github.com/Tiiny-AI/PowerInfer | PowerInfer consumer GPU |
| https://github.com/tally-project/tally-bench | Tally A100 requirement |
| https://github.com/ranggihwang/Pregated_MoE | Pre-gated DSM table |
| https://github.com/mit-han-lab/Quest | Quest Ada/4090 eval |
| https://github.com/ovg-project/kvcached | kvcached |
| https://arxiv.org/abs/2303.06182 | Huang et al. |
| https://arxiv.org/pdf/2410.22134 | ProMoE code URL claim |
| https://arxiv.org/html/2410.07381v3 | Tally paper AE context |
| https://github.com/promoe-opensource/promoe | ProMoE repo |
| https://github.com/deepspeedai/DeepSpeed | DeepSpeed |
| https://github.com/FMInference/FlexLLMGen | FlexGen archived |
| https://github.com/eth-easl/orion | Orion |
| https://github.com/pkusys/TGS | TGS |
| https://github.com/eniac/paella | Paella |
| https://github.com/rtenlab/gcaps-super-repo | GCAPS Tegra |

---

*End of audit. File is standalone; do not treat as a HotCRP promise until authors select rows from §1 and §3.*
