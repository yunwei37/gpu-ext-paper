# ASPLOS'27 #1797 — SOTA MoE / Model-Weight Offload Baseline Feasibility Audit

**Paper:** gpubpf / gpu_ext (ASPLOS'27 submission #1797, "Safe and Programmable OS-Level GPU Resource Management with eBPF")
**Scope (this file only):** MoE / model-weight offloading systems — the family Reviewer E and Reviewer F point at ("compare against SOTA research, not just framework-managed baselines"). KV-cache, UVM, scheduling, and instrumentation systems are audited separately in `sota-baseline-feasibility.md`; they are intentionally NOT repeated here.
**Audit date:** 2026-08-03
**Method:** Primary sources only. The two load-bearing sm_120 verdicts (MoE-Infinity, KTransformers) were fetched directly by the auditor from the repos/issues cited; the remaining candidates were verified by research agents against the fetched GitHub repos / arXiv pages listed in §5. No URL is cited that was not fetched. Unverifiable claims are marked **uncertain** rather than invented.

---

## Hardware constraint (hard)

| Resource | Available |
|----------|-----------|
| GPU 0 | **1× NVIDIA GeForce RTX 5090**, 32 GB, **Blackwell sm_120**, driver **575.57.08** |
| GPU 1 | Tesla P40 (Pascal sm_61) — secondary only |
| Missing | A100, H100, multi-GPU, NVLink, MIG (5090 has no MIG), FP8-only datacenter paths |
| Workload | llama.cpp serving **gpt-oss-20b / gpt-oss-120b** with expert offload to host DRAM under VRAM oversubscription |
| Budget | ~4 weeks, shared with writing |

**The crux — sm_120 ≠ sm_100.** NVIDIA "Blackwell" spans multiple compute capabilities:
- **sm_100** = datacenter Blackwell (B100 / B200 / GB200) — features (TMA, FP8 clusters) we do **not** have.
- **sm_120** = consumer/workstation Blackwell (**RTX 5090**, RTX 5080, RTX PRO 6000 Blackwell) — our chip.

A project that "supports Blackwell sm_100 / B200" does **not** support our RTX 5090. This single distinction invalidates more than one candidate below. PyTorch sm_120 kernels require torch ≥ 2.6/2.7 with a **cu126/cu128** build; any artifact pinned to `torch==2.0/2.1/2.2/2.3` has no sm_120 kernels and fails with "no kernel image available for execution."

---

## 1. Systems we should actually try (recommend)

Only two candidates are both (a) runnable-class on sm_120 and (b) able to host a real gpt-oss-class MoE offload workload. Everything else is either missing code, frozen on a pre-Blackwell stack, on the wrong GPU class, or the wrong model family.

### 1) MoE-Infinity (EfficientMoE) — **the only verified sm_120 + gpt-oss MoE baseline**

| Field | Value |
|-------|-------|
| Venue / paper | arXiv:2401.14361 (v3 Mar 2025); no published venue confirmed from fetched sources |
| Artifact | https://github.com/EfficientMoE/MoE-Infinity — Apache-2.0, **333★ / 32 forks / 226 commits** (read off the repo header) |
| sm_120 | **YES — explicit, first-hand verified.** README "Prerequisites": *"The from-source build targets `sm_80`/`sm_90` by default; for Blackwell (`sm_120`, e.g. RTX PRO 6000 / **RTX 50-series**) build with `MOE_ENABLE_SM120=1`."* Build line: `MOE_ENABLE_SM120=1 ... pip install --no-build-isolation -e .`; pulls `torch --index-url .../cu128`. Native FP4 path auto-selected on SM120. |
| gpt-oss | **YES** — supported-models table lists `openai/gpt-oss-*` (registered in `moe_infinity/common/constants.py`). (DeepSeek-V4-Flash FP4 / gpt-oss-120b DFlash are in active PRs as of Jul 2026, so treat the largest configs as not-yet-merged.) |
| HW we lack | None. Designed for memory-constrained single GPUs (README suggests ≥16 GB). No NVLink/multi-GPU/FP8-only needed; multi-GPU is optional round-robin. |
| Runtime | Own HuggingFace-compatible runtime + OpenAI-compatible server; does **not** plug into our llama.cpp submodule. |
| Effort | **MEDIUM** (from-source build + CUTLASS + cu128 torch; PyPI wheel is a placeholder) |

**Concrete first command:**
```bash
uv run --directory workloads/llama.cpp pip install "setuptools>=78.1.1,<82" wheel ninja py-cpuinfo
uv run --directory workloads/llama.cpp pip install torch --index-url https://download.pytorch.org/whl/cu128
git clone --depth 1 https://github.com/NVIDIA/cutlass.git ~/cutlass && export CUTLASS_DIR=~/cutlass
git clone https://github.com/EfficientMoE/MoE-Infinity.git && cd MoE-Infinity
MOE_ENABLE_SM120=1 MOE_ENABLE_SM90=0 CUTLASS_DIR=~/cutlass uv run pip install --no-build-isolation -e .
CUDA_VISIBLE_DEVICES=0 python examples/deepseek_v2_chat_example.py --offload_dir /fast/ssd/moe-offload
```

**Main risk:** the README itself warns *"This open-sourced version has been redesigned to be HuggingFace-friendly and differs from the version reported in the paper, which prioritizes extreme performance."* So numbers we produce are "public MoE-Infinity," fair as an artifact comparison, not as a re-run of the paper's headline table. Secondary risk: the from-source install path was actively stabilizing through Jul 2026 (PRs #116/#129 fixing install failures); expect some build friction on the first attempt.

---

### 2) DeepSpeed (ZeRO-Inference / DeepSpeed-MoE) — **generic weight-offload SOTA, plausible on sm_120**

| Field | Value |
|-------|-------|
| Venue / paper | ZeRO-Offload (ATC'21), ZeRO-Infinity (SC'21), DeepSpeed-MoE (ICML'22), DeepSpeed-Inference (SC'22) |
| Artifact | https://github.com/deepspeedai/DeepSpeed — Apache-2.0, **~42.9k★**, active through 2026/05 (SuperOffload won an ASPLOS'26 Best-Paper HM); **not archived/sunset** (the rumor is false — no archival notice on the repo or deepspeed.ai) |
| sm_120 | **REBUILD-NEEDED, plausibly feasible.** `requirements/requirements.txt` pins only `torch>=2.0.0` (no upper bound → a current cu128 torch is legal); `setup.py` builds all CUDA ops **JIT** and honors `TORCH_CUDA_ARCH_LIST`. Set `TORCH_CUDA_ARCH_LIST="8.0;8.6;8.9;9.0;12.0"`. README lists tested archs as Pascal/Volta/Ampere/Hopper but adds "this doesn't mean your GPU won't work if it isn't in this category." |
| gpt-oss | Not a bundled model, but reachable as any HF MoE model via the `deepspeed/moe/` + HF `transformers` path if a converter exists. **uncertain** whether gpt-oss drops in cleanly. |
| HW we lack | None blocking — ZeRO-Inference explicitly targets single-GPU + CPU/NVMe offload (exactly our 5090 + host-DRAM). Multi-GPU is for training, not the inference/offload path. |
| Runtime | Own runtime; not llama.cpp. |
| Effort | **MEDIUM** (install recent torch + JIT-rebuild ops for sm_120; main work is wiring gpt-oss weights and a fair single-batch offload config) |

**Concrete first command:**
```bash
uv run --directory workloads/llama.cpp pip install torch --index-url https://download.pytorch.org/whl/cu128
TORCH_CUDA_ARCH_LIST="12.0" uv run pip install deepspeed
# then a ZeRO-Inference single-GPU offload config for a Mixtral/Qwen-MoE checkpoint
# (see deepspeed/inference/v2; exact launch depends on the model chosen)
```

**Main risk:** DeepSpeed-MoE is a training-era MoE framework; its *inference offload* path is less battle-tested on consumer Blackwell than MoE-Infinity's. gpt-oss model wiring is **uncertain**. If gpt-oss does not drop in, fall back to a Mixtral-8x7B or Qwen3-30B-A3B checkpoint and frame it as "the same offload question on a comparable MoE."

---

### Optional stretch track (only if §1.1/§1.2 succeed early)

**KTransformers (SOSP'25).** Reviewers will name it, so it is worth a **smoke-test build**, but with eyes open: its GPU acceleration does **not** officially cover sm_120 (see §2 row + §4). The CPU/llamafile backend may run, but performance without an AMX host CPU is low, and it has **no gpt-oss** and no llama.cpp path. Treat as "we attempted; here is why the GPU path cannot serve as a fair 5090 baseline" — which is itself a citable result.

---

## 2. Full matrix — one row per candidate

Legend — **sm_120:** YES / NO / REBUILD / UNCERTAIN / N/A. **Effort:** LOW / MEDIUM / HIGH / INFEASIBLE.

| System | Venue + paper | Artifact (URL / last commit / license / ★) | sm_120 (evidence) | HW we lack | gpt-oss? | llama.cpp? | Effort |
|--------|---------------|---------------------------------------------|-------------------|------------|----------|-----------|--------|
| **MoE-Infinity** | arXiv'24 [2401.14361](https://arxiv.org/abs/2401.14361) | https://github.com/EfficientMoE/MoE-Infinity ; active Jul 2026 ; Apache-2.0 ; 333★ | **YES** — README: `MOE_ENABLE_SM120=1` for RTX 50-series (fetched) | none | **yes** (`gpt-oss-*`) | no (own runtime) | **MEDIUM** |
| **DeepSpeed / ZeRO-Inference** | ATC'21 / SC'21 / ICML'22 | https://github.com/deepspeedai/DeepSpeed ; active 2026/05 ; Apache-2.0 ; ~42.9k★ | **REBUILD** — `torch>=2.0.0` (open), JIT ops honor `TORCH_CUDA_ARCH_LIST=12.0` (fetched setup.py/requirements) | none (single-GPU offload OK) | **uncertain** (HF MoE path) | no (own runtime) | **MEDIUM** |
| **KTransformers** | **SOSP'25** | https://github.com/kvcache-ai/ktransformers ; active Jun 2026 ; Apache-2.0 ; 19.2k★ | **NO (official)** — kt-kernel README GPU matrix = SM **80/86/89/90 only**, no Blackwell row; issue #2056: official "SM90 (Hopper); upstream sglang = SM100 **datacenter** (B100/B200/GB200)" — sm_120 (5090) not covered (both fetched first-hand) | high-perf GPU path needs SM90; CPU path wants AMX | **no** (not listed) | no (sglang-kt runtime) | **HIGH** |
| **Huang et al. (Expert Buffering)** | arXiv'23 [2303.06182](https://arxiv.org/abs/2303.06182) (Rev E named) | **NO CODE** — arXiv "links to code" empty; no Papers-With-Code entry; no `facebookresearch/*` repo | N/A | datacenter-class study | no | n/a | **INFEASIBLE** |
| **Mixtral-offloading** | arXiv'23 [2312.17238](https://arxiv.org/abs/2312.17238) (tech report) | https://github.com/dvmazur/mixtral-offloading ; **last commit Jan 5 2024** ; MIT ; 2.3k★ | **NO/REBUILD** — `torch>=2.1.0` + **`transformers==4.36.1`** + HQQ pinned to a 2023 hash; notebook-only | none (24 GB class) | **no** (Mixtral-8x7B only) | no | **HIGH**; INFEASIBLE for gpt-oss |
| **Fiddler** | ICLR'25 / arXiv [2402.07033](https://arxiv.org/abs/2402.07033) | https://github.com/efeslab/fiddler ; **last commit Apr 28 2024** ; Apache-2.0 ; 267★ | **REBUILD** — pins **`torch==2.1.2`** + `transformers==4.36.2` (requirements.txt fetched) | none (proven on 24 GB) | **no** (Mixtral-8x7B only) | no | **MEDIUM** (for Mixtral); INFEASIBLE for gpt-oss |
| **ProMoE** | arXiv [2410.22134](https://arxiv.org/abs/2410.22134) | https://github.com/promoe-opensource/promoe ; **last commit Oct 30 2024** ; no LICENSE ; 20★ | **UNCERTAIN / cannot build** — `CMakeLists.txt` hardcodes `compute_70/compute_80`; real system on **private SJTU GitLab** (issues #2/#3, unanswered) | none claimed | **no** (DeepSeek/Qwen1.5-MoE) | claimed but **privately gated** | **INFEASIBLE** (artifact not public) |
| **Pre-gated MoE** | **ISCA'24** / arXiv [2308.12066](https://arxiv.org/abs/2308.12066) | https://github.com/ranggihwang/Pregated_MoE ; last commit May 4 2024 ; Apache-2.0 ; 63★ | **NO** — FasterTransformer fork; `CMakeLists.txt: set(SM_SETS 52 60 61 70 75 80 86 89 90)` stops at sm_90; FT is NVIDIA-**deprecated** (folded into TRT-LLM, no Blackwell) | **A100** (README: "build on A100") | **no** (Switch Transformer / T5-MoE) | no (FT C++ runtime) | **INFEASIBLE** |
| **SwapMoE** | **ACL'24** / arXiv [2308.15030](https://arxiv.org/abs/2308.15030) | https://github.com/fqt111/SwapMoE — **README-only, 3★, 0 forks** | **N/A — NO CODE** (no source/build files) | n/a | no (Swin/GPT-MoE research backbones) | no | **INFEASIBLE** |
| **EdgeMoE** | arXiv [2308.14352](https://arxiv.org/abs/2308.14352) | https://github.com/UbiquitousLearning/mllm ; active Jun 2026 ; MIT ; ~1.6k★ | **UNCERTAIN / wrong target** — mobile-first (Arm CPU, Qualcomm QNN, Ascend NPU); CUDA only experimental for Jetson Orin/Thor; no sm_120/5090 listed | mobile/NPU target, not server GPU | **no** (MiniCPM-MoE; gpt-oss only *planned*) | no (own C++ runtime) | **INFEASIBLE** as server-GPU baseline |
| **FlexGen (FlexLLMGen)** | ICML'23 / arXiv [2303.06865](https://arxiv.org/abs/2303.06865) | https://github.com/FMInference/FlexLLMGen ; **ARCHIVED Dec 1 2024 (read-only)** ; Apache-2.0 ; 9.4k★ | **NO** — frozen OPT-era 2023 code; no Blackwell/sm_120, no MoE path; `torch>=1.12` | none (built for single T4 16 GB) | **no** (OPT only) | no | **INFEASIBLE** for MoE |
| **HeteGen** | **MLSys'24** / arXiv [2403.01164](https://arxiv.org/abs/2403.01164) | **NO CODE** — lead author homepage lists only `[paper]`; no GitHub repo; no arXiv code link | N/A | conceptually fits, but unreachable | no (dense LLaMA only) | no | **INFEASIBLE** |
| **PowerInfer** | **SOSP'24** / arXiv [2312.12456](https://arxiv.org/abs/2312.12456) | https://github.com/Tiiny-AI/PowerInfer ; last **code** commit Jul 2025, last CUDA Sep 2024 ; MIT ; 9.7k★ | **NO/REBUILD** — old ggml snapshot built with deprecated `-DLLAMA_CUBLAS=ON`; no sm_120/gpt-oss mention anywhere | none (RTX 4090 paper) | **no** (ReLU-sparse Llama/Falcon only; gpt-oss only in the closed Tiiny product) | ggml fork (diverged) | **INFEASIBLE** for gpt-oss |
| **PowerInfer-2** | arXiv [2406.06282](https://arxiv.org/abs/2406.06282) | **NO CODE** (folded into commercial Tiiny AI product) | N/A | **smartphone/NPU** (OnePlus, 47B on phone) | no (TurboSparse-Mixtral-47B) | no | **INFEASIBLE** (wrong platform) |
| **HybriMoE** | **DAC'25** / arXiv [2504.05897](https://arxiv.org/abs/2504.05897) | https://github.com/PKU-SEC-Lab/HybriMoE ; 6 commits, stale (Apr 2025) ; Apache-2.0 ; 118★ | **REBUILD/likely NO** — vendored `ktransformers` (`pyproject name="ktransformers"`); pins CUDA 12.1 / torch≥2.3; inherits KT's SM90-only GPU path | none in principle | no (DeepSeek-V2-Lite only) | no (KT runtime) | **HIGH** (just run upstream KT instead) |
| **DAOP** | **DATE'25** / arXiv [2501.10375](https://arxiv.org/abs/2501.10375) | https://github.com/ecolab-nus/DAOP ; "proof-of-concept" ; Apache-2.0 ; 5★ | **NO** — pins **`torch==2.2.2`** + `transformers==4.44.0` (requirements.txt fetched) | none (A6000 paper) | no (Mixtral / Phi-3.5-MoE) | no | **MEDIUM** (PoC), but no gpt-oss |

\*Star counts / last-commit dates observed at audit time (2026-08-03). re-check before citing exact figures in paper text.

---

## 3. Infeasible list (HotCRP-ready one-liners)

Paste-ready, each backed by a fetched primary source. These are systems we will **discuss with a citable unavailability reason** rather than silently omit.

1. **Huang et al., arXiv:2303.06182 (the work Reviewer E named):** No public artifact exists — the arXiv "links to code" field is empty and no `facebookresearch/*` repository accompanies the paper; the expert-buffering / dynamic-gating idea can only be discussed conceptually, not run.
2. **HeteGen (MLSys'24):** No public code repository accompanies the paper (the lead author's project page lists only `[paper]`); the heterogeneous CPU-GPU tensor-parallel scheme cannot be reproduced as an executable baseline.
3. **PowerInfer-2 (arXiv:2406.06282):** Targets smartphone SoC + NPU (e.g. 47B on a OnePlus); no desktop CUDA artifact and no code release — wrong platform for a single-RTX-5090 head-to-head.
4. **SwapMoE (ACL'24):** The public repository (github.com/fqt111/SwapMoE) is README-only with no source, build files, or model code; there is nothing to execute.
5. **EdgeMoE:** The artifact (mllm) is a mobile/NPU inference stack (Arm CPU, Qualcomm QNN, Ascend NPU; CUDA only experimental on Jetson Orin/Thor) with no gpt-oss support — not a server-GPU memory-management baseline.
6. **FlexGen / FlexLLMGen:** The repository was **archived read-only on 2024-12-01** and is OPT-only with no MoE code path; it cannot serve as a gpt-oss MoE offload baseline.
7. **Pre-gated MoE (ISCA'24):** Built on NVIDIA-**deprecated FasterTransformer** (folded into TRT-LLM in 2023); its `CMakeLists.txt` arch table stops at sm_90, the README says "build on A100," and it targets Switch-Transformer / T5-MoE — no Blackwell, no A100, no gpt-oss.
8. **PowerInfer (desktop), for gpt-oss:** Open-source PowerInfer runs only ReLU/ReGLU-sparse Llama/Falcon models (per its README FAQ); gpt-oss exists only in the closed Tiiny AI product (issue #274), and its ggml snapshot predates Blackwell.
9. **KTransformers (SOSP'25), as a fair 5090 baseline:** Its official GPU-acceleration matrix covers only SM 80/86/89/90 (kt-kernel README); issue #2056 confirms support is "SM90 (Hopper)" and that upstream sglang reaches only **sm_100 datacenter** Blackwell (B100/B200/GB200), **not sm_120** (RTX 5090) — and it has no gpt-oss model and no llama.cpp path.
10. **DAOP (DATE'25):** Pins `torch==2.2.2`, which predates sm_120 kernels, and supports only Mixtral / Phi-3.5-MoE — not gpt-oss.
11. **ProMoE (arXiv:2410.22134):** The actual system lives in a **private SJTU GitLab**; open issues #2 and #3 (unanswered) confirm the public cannot clone the patched transformers/llama.cpp it depends on — the "llama.cpp integration" is not publicly deliverable.
12. **Mixtral-offloading (arXiv:2312.17238) for gpt-oss:** Frozen at a Jan-2024 notebook on `torch>=2.1` / `transformers==4.36.1`, Mixtral-8x7B only — no gpt-oss path and no sm_120 adaptation.
13. **HybriMoE (DAC'25):** A 6-commit vendored copy of KTransformers; running upstream KTransformers is strictly better than its stale snapshot, and it inherits the same sm_120 gap.

---

## 4. The one conflict we resolved first-hand (KTransformers)

Two research passes disagreed on KTransformers sm_120. We fetched the authoritative sources directly:

- **kt-kernel README** (https://github.com/kvcache-ai/ktransformers/blob/main/kt-kernel/README.md): the GPU Compatibility Matrix lists **Hopper 9.0, Ada 8.9, Ampere 8.6/8.0** as ✅ and explicitly says *"Single wheel supports SM 80/86/89/90 (Ampere, Ada, Hopper)."* **There is no Blackwell row.**
- **Issue #2056** (https://github.com/kvcache-ai/ktransformers/issues/2056): a user asks "does 0.6.3 support 4090 or 5090?" and quotes the official statement: *"Supported GPUs: SM90 (Hopper: H100/H200/H20/H800). Upstream sglang targets SM100 (Blackwell datacenter: B100/B200/GB200) so far."*

**Verdict:** the disagreement came from conflating an in-progress partial fix (issue #2001, an SM_120 zero-output bug for one model on an RTX PRO 4000) with **official support**. The authoritative install doc and the user-facing support statement both confirm the **GPU-acceleration path is SM90-only and does not cover sm_120 (the 5090's compute capability)**. sm_100 is datacenter Blackwell; our chip is sm_120. Even setting sm_120 aside, KTransformers has **no gpt-oss** model and **no llama.cpp** path (it uses a kvcache-ai fork of SGLang), so it is not a direct gpt-oss/llama.cpp baseline in any case. We record it as a stretch smoke-test only.

---

## 5. Uncertainties (things this audit did NOT establish)

| Item | What's uncertain |
|------|------------------|
| MoE-Infinity build on our exact toolchain | README documents `MOE_ENABLE_SM120=1`; we have **not** executed the build on this host's CUDA 12.8 driver 575 stack — first attempt may hit the install-path fixes still landing in Jul 2026 (PRs #116/#129). |
| MoE-Infinity gpt-oss-120b path | `gpt-oss-*` is registered, but 120b DFlash speculative decoding is still an open PR (#131) — treat 120b as not-yet-merged. |
| DeepSpeed gpt-oss wiring | ZeRO-Inference is plausibly sm_120-clean via `TORCH_CUDA_ARCH_LIST`, but whether **gpt-oss** drops into the HF MoE path is **unverified**; a Mixtral/Qwen3-MoE fallback may be needed. |
| KTransformers CPU-only run on the 5090 | The llamafile/AMX CPU backend *might* run with no GPU kernels; performance on a non-AMX host CPU is expected to be poor. Not tested. |
| Fiddler after torch upgrade | `torch==2.1.2`→≥2.7 may just work for Mixtral (experts run on CPU), but **unverified** on sm_120. |
| DAOP after torch upgrade | torch 2.2.2→≥2.7 upgrade is mandatory and risks breaking the `transformers==4.44.0` pin; not attempted. |
| PowerInfer ggml-cuda sm_120 | Would need CUDA 12.8 + arch-list rebuild on a frozen fork; not attempted. No gpt-oss regardless. |
| ProMoE private access | Issues #2/#3 are unanswered; if SJTU grants GitLab access the calculus could change, but the dormant Oct-2024 llama.cpp fork would then still need a Blackwell port. |
| Star/commit figures | Observed at fetch time 2026-08-03; re-confirm exact numbers before quoting in the paper. |
| 2025–2026 very-recent MoE-offload systems | A survey surfaces candidates (e.g. CoX-MoE, TriMoE, DALI, SpecMoE, MoE-SpAc) as DAC'26/arXiv papers. We did **not** independently fetch these in this audit and their code/sm_120 status is **uncertain**; none has a verified public artifact on sm_120. Flag for a follow-up only if a reviewer specifically raises one. |
| KTransformers venue label | Repo citation block gives SOSP'25 (DOI 10.1145/3731569.3764843); a local `ktransformers-sosp24.pdf` filename in the rebuttal folder predates this — cite the DOI/README year in any HotCRP text. |

---

## 6. Evidence index (URLs fetched during this audit)

| URL | Used for | Fetched by |
|-----|----------|-----------|
| https://github.com/EfficientMoE/MoE-Infinity (README) | sm_120 flag, gpt-oss support, ≥16 GB, "differs from paper" disclaimer, 333★ | auditor (first-hand) |
| https://github.com/kvcache-ai/ktransformers/blob/main/kt-kernel/README.md | GPU matrix = SM 80/86/89/90 only; no Blackwell | auditor (first-hand) |
| https://github.com/kvcache-ai/ktransformers/issues/2056 | official "SM90; sglang SM100 datacenter" — sm_120 not covered | auditor (first-hand) |
| https://github.com/kvcache-ai/ktransformers | repo header (19.2k★), SOSP'25 citation, activity through Jun 2026 | auditor + agent |
| https://github.com/kvcache-ai/ktransformers/issues/2001, /2083, /2058, /2081 | in-progress sm_120 partial fix (#2001); FP8/MoE asserts block sm_120 (#2058/#2081); unmerged fork needed (#2083) | agent |
| https://arxiv.org/abs/2303.06182 | Huang et al. — no code link | agent |
| https://arxiv.org/abs/2401.14361 ; /abs/2312.17238 ; /abs/2402.07033 ; /abs/2410.22134 ; /abs/2308.12066 ; /abs/2308.15030 ; /abs/2308.14352 ; /abs/2303.06865 ; /abs/2403.01164 ; /abs/2312.12456 ; /abs/2406.06282 ; /abs/2504.05897 ; /abs/2501.10375 | per-system paper/venue | agent |
| https://github.com/dvmazur/mixtral-offloading (+ /commits/master) | last commit Jan 5 2024; notebook-only; 2.3k★ | agent |
| https://raw.githubusercontent.com/dvmazur/mixtral-offloading/master/requirements.txt | `transformers==4.36.1`, HQQ hash pin | agent |
| https://github.com/efeslab/fiddler (+ raw requirements.txt) | pins `torch==2.1.2`; last commit Apr 28 2024; 267★ | agent |
| https://github.com/promoe-opensource/promoe (+ install.md, CMakeLists.txt, issues #2/#3) | private SJTU GitLab deps; CMake hardcodes compute_70/80; 20★ | agent |
| https://raw.githubusercontent.com/ranggihwang/Pregated_MoE/master/CMakeLists.txt | `set(SM_SETS … 90)` — no sm_120; FasterTransformer-deprecated | agent |
| https://github.com/fqt111/SwapMoE | README-only; 3★; no code | agent |
| https://github.com/UbiquitousLearning/mllm | EdgeMoE artifact — mobile/NPU-first | agent |
| https://github.com/deepspeedai/DeepSpeed (+ setup.py, requirements) | not archived; `torch>=2.0.0`; JIT ops honor TORCH_CUDA_ARCH_LIST | agent |
| https://github.com/FMInference/FlexLLMGen | archived 2024-12-01; OPT-only | agent |
| https://oahzxl.github.io ; github.com/search?q=HeteGen | HeteGen: no `[code]`; 1 irrelevant repo hit → NO CODE | agent |
| https://github.com/Tiiny-AI/PowerInfer (+ /issues?q=gpt-oss) | ReLU-sparse models only; gpt-oss only in closed product (#274); last CUDA commit Sep 2024 | agent |
| https://github.com/PKU-SEC-Lab/HybriMoE (+ install.sh, pyproject.toml) | vendored `ktransformers`; CUDA 12.1 / torch≥2.3 | agent |
| https://raw.githubusercontent.com/ecolab-nus/DAOP/main/requirements.txt | `torch==2.2.2`, `transformers==4.44.0` | agent |

---

## 7. Bottom line for the revision

- **Run MoE-Infinity** as the primary MoE-expert-offload SOTA research baseline on the 5090 — it is the only candidate that simultaneously has explicit `sm_120` support, registered `gpt-oss-*` model support, and a public serving runtime. State plainly that the public build differs from the paper's extreme-performance version.
- **Run DeepSpeed ZeRO-Inference** as the second axis (generic weight-offload SOTA) if its gpt-oss (or fallback Mixtral/Qwen3-MoE) wiring comes together in week 1.
- **For Reviewer E's specifically-named paper (Huang et al., arXiv:2303.06182):** cite it as the conceptual origin of gating-driven expert buffering, and note in the response that **no public artifact exists** for it (this is a legitimate, citable reason, not an omission).
- **For every other named system,** the infeasibility is hardware- or artifact-grounded (no code; archived/deprecated stack; wrong GPU class sm_100≠sm_120; wrong model family; smartphone/NPU) and is recorded in §3 as a one-liner suitable for the HotCRP response.

*Suggested hardware-honest sentence for the response:*
> Under our single-RTX-5090 (sm_120) constraint we head-to-head against **MoE-Infinity** (activation-aware expert offload; the only public MoE research artifact with an explicit `MOE_ENABLE_SM120` build and `gpt-oss` support) and **DeepSpeed ZeRO-Inference** (generic weight-offload SOTA). The system Reviewer E named (Huang et al., arXiv:2303.06182) has no released artifact, so we discuss its gating-driven expert-buffering mechanism with that citable unavailability rather than claim a reproduction we cannot perform; KTransformers' GPU path is SM90/sm_100-only and does not cover the 5090's sm_120, and it lacks a gpt-oss model path, so it cannot serve as a fair on-device baseline on our hardware.

*End of MoE-scope audit. This file is standalone and scoped to MoE / model-weight offload only; KV/UVM/scheduling/instrumentation baselines live in `sota-baseline-feasibility.md`. Treat no row as a HotCRP promise until the authors pick from §1 and §3.*
