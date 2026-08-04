# ASPLOS'27 #1797 — SOTA Feasibility Audit: GPU Scheduling / Sharing / UVM / Instrumentation

**Paper:** gpubpf / gpu_ext (ASPLOS'27 submission #1797, "safe, dynamic, full-stack GPU resource management via eBPF").
**Scope of this file:** GPU **scheduling / multi-tenant sharing / UVM oversubscription / device-side instrumentation** research baselines. The sibling file `sota-baseline-feasibility.md` covers MoE / KV / inference-memory and must not be conflated.
**Audit date:** 2026-08-03.
**Method:** primary sources only. URLs in the §6 evidence index were fetched during this audit (the load-bearing sm_120 / driver verdicts were re-fetched directly by the auditor; secondary metadata — star counts, last-commit dates — is approximate at fetch time and marked `approx.`). Where a claim could not be confirmed it is written **uncertain** rather than invented.

---

## Hardware constraint (hard)

| Resource | Available |
|----------|-----------|
| GPU 0 | **1× NVIDIA GeForce RTX 5090**, 32 GB, **Blackwell sm_120**, driver **575.57.08** (R575 → CUDA 12.8) |
| GPU 1 | Tesla P40 (Pascal sm_61) — secondary only |
| Missing | A100, H100, multi-GPU, NVLink, **MIG (the 5090 has no MIG)** |
| Workloads | llama.cpp + vLLM inference, PyTorch GNN training, FAISS vector search |
| Wall-clock | ~4 weeks, shared with writing |

**sm_120 / driver-575 floor (cross-cutting).** Blackwell sm_120 needs CUDA Toolkit **12.8+**. Any artifact whose build hard-codes `-arch=sm_XX` with `XX ≤ 90`, or whose run path pins `torch==2.0–2.3` (no sm_120 kernels), is **not** a drop-in on the 5090. Two distinct classes of blocker recur below and are separated explicitly: **(a) driver-surgery blockers** — artifacts that patch/rebuild the NVIDIA kernel module against a *specific old driver branch* (550.x, 535.x) and therefore cannot co-exist with driver 575.57.08; and **(b) toolchain blockers** — artifacts pinned to old CUDA / torch / TF whose build emits no sm_120 binary.

---

## 1. The systems we should actually try

Two artifacts maximize reviewer value per unit of engineering risk under the sm_120 / driver-575 / single-GPU constraint, and both are **userspace LD_PRELOAD shims with no kernel-module surgery**.

### 1) XSched (OSDI'25) — best preemptive-scheduling H2H, runs on sm_120 today

| Field | Value |
|-------|-------|
| Venue / paper | OSDI'25, "XSched: Preemptive Scheduling for Diverse XPUs" — https://www.usenix.org/conference/osdi25/presentation/shen-weihang |
| Artifact | https://github.com/XpuOS/xsched — Apache-2.0, ~176★ (approx.), last commit **2026-07-24** (active) |
| **sm_120 + driver 575** | **Level-1 works; Level-2/3 do not.** Verified directly in `platforms/cuda/hal/src/arch/arch.cpp` ([raw](https://raw.githubusercontent.com/XpuOS/xsched/main/platforms/cuda/hal/src/arch/arch.cpp)): the arch switch has cases only for `35`/`70`/`86`, and **`default: return std::make_shared<CudaQueueLv1>(stream);`** — sm_120 (compute capability 12.0) falls through to Lv1. Lv1 = stream-level suspend/resume (inter-kernel preemption) using only driver APIs, no SASS. `Guardian::Instance()` and `TarpHandler::Instance()` return `nullptr` for unknown arch, so Lv2 (threadblock) and Lv3 (trap) are unavailable on sm_120 until an `sm120.cpp` is written. A compile-time `kCudaLv3ImplementationTsg` path bypasses the arch switch but is not the default. No `CUDA_ARCHITECTURES` is set by XSched itself (it compiles no `.cu` kernels). No driver patch. |
| Hardware blocker | None (single consumer GPU; no MIG/NVLink). |
| Workload match | **Strong:** first-party `integration/llama.cpp/` (priority-based scheduling between multiple `llama-server` instances via `XSCHED_POLICY=HPF`); also a Triton integration. Pairs directly with our llama.cpp eval. |
| Effort | **LOW** for Lv1; HIGH only if we wanted Lv2/Lv3 (new `sm120.cpp`). |
| Policy as eBPF? | **runnable as-is (Lv1 fallback).** Policy layer (`sched/`) is modular/pluggable. |

**First command to try:**
```bash
git clone https://github.com/XpuOS/xsched.git && cd xsched
git submodule update --init --recursive
make PLATFORM=cuda                 # builds the LD_PRELOAD shim + Lv1 HAL
# then follow integration/llama.cpp/README.md: patch llama.cpp, build two llama-server
# instances, and set XSCHED_POLICY / priorities as documented
```
**Main risk:** the Lv1 `default` path is the *fallback*, not a configuration the authors tested on Blackwell — it may intercept correctly but give coarser preemption granularity than the paper's Lv3 results on Ampere/Volta, so reported numbers must be labeled "XSched Lv1 on sm_120," not "XSched (paper)." This is still the **most honest open scheduling artifact that does not require a custom NVIDIA kernel module.**

### 2) Orion (EuroSys'24) — best co-location artifact for the PyTorch/GNN axis

| Field | Value |
|-------|--------|
| Venue / paper | EuroSys'24, "Orion: Interference-aware, Fine-grained GPU Sharing for ML Applications", DOI 10.1145/3627703.3629578 |
| Artifact | https://github.com/eth-easl/orion — MIT, ~164★ (approx.), last commit 2025-11-26 (`main`); paper AE = `cuda1011_version` branch |
| **sm_120 + driver 575** | **Likely buildable (no hard SM cap).** Verified in the README ([raw](https://raw.githubusercontent.com/eth-easl/orion/main/README.md)): `main` is "tested on NVIDIA H100 and RTX-3090, with CUDA 12.6"; Orion intercepts CUDA/cuDNN/cuBLAS via `LD_PRELOAD` and the capture lib links `-lcudart -lcudnn -lcublas` with **no `nvcc -arch=` flag** (no PTX compile, so no hard SM ceiling). Driver 575 (CUDA 12.8) is a superset of the tested 12.6 stack. Two real friction points: the example `LD_PRELOAD` path pins versioned libs `libcudnn.so.9` / `libcublas.so.12`, which must be repointed to whatever a torch-cu128 install bundles; and Orion needs **per-kernel SM profiles** (`PROFILE.md`) regenerated on the 5090. |
| Hardware blocker | None hard (single GPU fine; no MIG/NVLink/cloud). |
| Workload match | **Good for PyTorch GNN training + vLLM co-location** (intercepts cuDNN/cuBLAS). Weaker for llama.cpp (ggml kernels, no cuDNN). Assumes 1 high-priority + N best-effort clients. |
| Effort | **MEDIUM** (rebuild + re-profile kernels on 5090 + fix versioned lib paths). |
| Policy as eBPF? | **runnable as-is (after rebuild + re-profile).** Scheduling policy is config/JSON-driven. |

**First command to try:**
```bash
git clone -b main https://github.com/eth-easl/orion.git && cd orion
# follow INSTALL.md; build the capture lib + scheduler
# generate per-kernel profiles for the GNN/vLLM workload on the 5090 (PROFILE.md)
# fix the LD_PRELOAD lib paths to the torch-cu128-bundled libcudnn/libcublas, then:
LD_PRELOAD=<orion>/src/cuda_capture/libinttemp.so:<torch>/nvidia/cudnn/lib/libcudnn.so.<N>:<torch>/nvidia/cublas/lib/libcublas.so.<N> \
  python3 benchmarking/launch_jobs.py --algo orion --config_file benchmarking/config.json
```
**Main risk:** Orion relies on **pre-profiled per-kernel SM demand**, so results are only as faithful as the 5090 re-profiling; and the LithOS paper (SOSP'25) explicitly states Orion's public code "was tied to specific CUDA drivers and software stacks," which is why they re-implemented it rather than running it. Treat any head-to-head as "public Orion on sm_120," not paper-Table numbers.

> **Near-miss runner (promote if XSched or Orion slips):** none of the other scheduling artifacts are low-risk on sm_120 (see §3). The only additional *runnable* artifact in this whole scope is **NVBit** (§4), which is an instrumentation tool, not a scheduling policy.

---

## 2. Full matrix

Legend — **sm_120:** `YES` / `NO` / `REBUILD` / `PARTIAL` / `SIM` / `uncertain` / `N/A`. **Effort:** LOW / MEDIUM / HIGH / INFEASIBLE.

### 2.1 Scheduling / multi-tenant sharing

| System | Venue, year, paper | Artifact (URL · license · ★ · last commit) | sm_120 + driver 575 (evidence) | HW blocker / sim? | Workload match | Effort | Policy as eBPF? |
|--------|--------------------|---------------------------------------------|--------------------------------|-------------------|----------------|--------|------------------|
| **XSched** | OSDI'25 ([USENIX](https://www.usenix.org/conference/osdi25/presentation/shen-weihang)) | [XpuOS/xsched](https://github.com/XpuOS/xsched) · Apache-2.0 · ~176★ · 2026-07-24 | **PARTIAL (Lv1).** `arch.cpp` `default→CudaQueueLv1`; Lv2/3 `nullptr` for sm_120 (no `sm120.cpp`) | None | llama.cpp integration; inference co-location | **LOW** | **runnable as-is (Lv1)** |
| **Orion** | EuroSys'24 (DOI 10.1145/3627703.3629578) | [eth-easl/orion](https://github.com/eth-easl/orion) · MIT · ~164★ · 2025-11-26 | **REBUILD, likely OK.** README: tested H100/RTX-3090 CUDA 12.6; LD_PRELOAD shim, no `nvcc -arch` (no SM cap). Re-profile kernels on 5090 | None | PyTorch/vLLM co-location (cuDNN/cuBLAS); weak for llama.cpp | **MEDIUM** | **runnable as-is (after rebuild+re-profile)** |
| **GPreempt** | ATC'25 ([repo](https://github.com/thustorage/GPreempt)) | [thustorage/GPreempt](https://github.com/thustorage/GPreempt) · Apache-2.0 · ~25★ · 2025-05-18 (frozen AE) | **NO (doubly blocked).** README pins **driver 550.120** + `git apply patch/driver.patch` on `open-gpu-kernel-modules`; `CMakeLists.txt` hard-codes `set(CMAKE_CUDA_ARCHITECTURES 80)` **and** `-arch=sm_80` cubin. 550 driver cannot drive a 5090 | **driver-surgery** (must replace host kernel module, voids support); GDRCopy; self-modified TVM | DISB BERT inference + miniWeather/EMOGI BE (inference co-location) | **INFEASIBLE** | **policy reimplementable** (priority-ordered runlist / LC-preempts-BE) |
| **Paella** | SOSP'23 ([repo](https://github.com/eniac/paella)) | [eniac/paella](https://github.com/eniac/paella) · MIT · ~72★ · last real code 2023-08-27 | **uncertain (toolchain).** Own `CMakeLists.txt` takes `-DCMAKE_CUDA_ARCHITECTURES=<arch>` (no hardcode); README "tested on 535.54.03" (unmodified). **Blocker:** requires `tvm-llis` (TVM **v0.10**, pre-Blackwell) to compile models → cannot emit sm_120 kernels | None at topology level (ran on T4/P100) | Low-latency multi-model serving (SLO) | **HIGH** | **policy reimplementable, harder** (SM-virtualization policy is coupled to block-level interception mechanism) |
| **Salus** | MLSys'20, [arXiv:1902.04610](https://arxiv.org/abs/1902.04610) | [SymbioticLab/Salus](https://github.com/SymbioticLab/Salus) · Apache-2.0 · ~150★ · last code 2020-03-09 | **NO (toolchain).** Salus itself is arch-agnostic userspace, but README: "tightly coupled" to `tensorflow-salus` (TF **1.x**, CUDA 9/10) which has **no sm_120 target**; EOL fork | None (userspace) | TF 1.x training-job co-location; **not** our stack | **INFEASIBLE** | **policy reimplementable** (iteration-level packing / fair share) |
| **Tally** | ASPLOS'25 | [tally-project/tally-bench](https://github.com/tally-project/tally-bench) · license unstated · ~10★ · 2024-12-07 | **NO as-is.** README "Required Hardware": **"An NVIDIA A100 GPU with 40 GB"** + 85 GB RAM + ~**130 GB** docker image (`wzhao18/tally:bench`); A100-era CUDA stack. MPS/time-slicing modes exist on Blackwell but the image is A100-pinned | **A100 required** (AE); not simulator | Concurrent DL train+infer (Azure trace) | **HIGH** (rebuild image for sm_120) | **policy reimplementable** (MPS-based non-intrusive isolation) |
| **TGS** | NSDI'23 ([USENIX](https://www.usenix.org/conference/nsdi23/presentation/wu)) | [pkusys/TGS](https://github.com/pkusys/TGS) · Apache-2.0 · ~98★ · 2023-06-26 (stale, 2 commits) | **NO as-is.** Container-cloud + RPC + `hijack` CUDA lib; `test_mig.sh` (**MIG path unreachable on 5090**); CUDA-11.x-era docker images | cloud/container node; **MIG** configs | DL training (TF/PyTorch/ESPnet2) | **HIGH** | **policy reimplementable** (transparent API-hijack sharing) |
| **REEF** | OSDI'22 | [SJTU-IPADS/reef-artifacts](https://github.com/SJTU-IPADS/reef-artifacts) · license in repo · AE snapshot | **NO on our CUDA host.** GPreempt's own README (fetched) states: *"the original REEF repository only supports the ROCm driver of Ubuntu 18.04, the corresponding code cannot be executed on the current version of Ubuntu."* REEF AE is ROCm/AMD-centric | ROCm/AMD + old Ubuntu | Idempotent-kernel preemption (real-time + DNN) | **INFEASIBLE** (CUDA path) | **policy reimplementable** (idempotent-preempt concept) |
| **LithOS** | SOSP'25, [arXiv:2504.15465](https://arxiv.org/abs/2504.15465) | **NO CODE.** No public repo (GitHub search returns only unrelated repos); paper says ~5k LoC Rust, design "deferred to a separate technical report" | N/A (no artifact). Design (CUDA Driver-API interposition over MPS, dynamic TPC enumeration, single A100/CUDA 12.8) is *architecturally* sm_120-compatible | none in design (MPS) but unreproducible | TRT-LLM/Triton inference stacking + training | **INFEASIBLE** | **neither** — the contribution *is* the interposition+atomization mechanism, not a separable policy |
| **GCAPS** | ECRTS'24 ([repo](https://github.com/rtenlab/gcaps-super-repo)) | [rtenlab/gcaps-super-repo](https://github.com/rtenlab/gcaps-super-repo) · MIT · ~16★ · 2024-05-17 | **NO (wrong driver family).** Top-level README + `gcaps_driver_patch/`: real-time driver-context patches against the **Tegra `nvgpu`** kernel driver (Jetson Xavier NX, L4T R35.2.1, kernel `5.10.104-tegra`). The 5090 uses `nvidia.ko` (R575), not `nvgpu.ko` — patches cannot apply | **Jetson/Tegra embedded**; real-time RTOS | Custom real-time CUDA tasks | **INFEASIBLE** | **neither** — mechanism is a Tegra-driver patch absent on the 5090 |
| **MuxFlow** | Sci. China Inf. Sci. 67(12), 2024; [arXiv:2303.13803](https://arxiv.org/abs/2303.13803) | **NO CODE.** GitHub search returns only unrelated Go/video tools; deployed internally at "CompanyX" (10–20k-GPU cluster) | N/A | **cluster-scale** production system | online-LS + offline-BE fleet co-location | **INFEASIBLE** | **policy reimplementable** (MPS SM-capping + two-level protection + matching) |
| **SGDRC** | PPoPP'25, [arXiv:2407.13996](https://arxiv.org/abs/2407.13996) | **NO CODE** (GitHub search: 0 repos) | **NO.** Two mechanisms: SM-masking (portable) **and** VRAM cache-coloring from a **reverse-engineered VRAM-channel hash map** — the latter is GPU-specific and must be re-reverse-engineered from scratch for Blackwell/GDDR7/sm_120 (no source) | single-GPU inference colocation; no MIG | concurrent DNN inference (11 DNNs) | **HIGH** | **partial** — SM-masking reimplementable; VRAM-coloring not without Blackwell channel RE |

### 2.2 UVM / memory oversubscription

| System | Venue, year, paper | Artifact | sm_120 + driver 575 (evidence) | HW blocker / sim? | Workload match | Effort | Policy as eBPF? |
|--------|--------------------|----------|--------------------------------|-------------------|----------------|--------|------------------|
| **G10** | MICRO'23, [arXiv:2310.09443](https://arxiv.org/abs/2310.09443) (NOT ISCA) | [platformxlab/G10](https://github.com/platformxlab/G10) · Apache-2.0 · ~44★ · 2023-09-19 | **SIM (CPU-only).** README §0: *"executed on any x86 machine with at least 30 GB of main memory"*; §2.2: *"do a performance **simulation** of the DNN training"*; output exe `gpg`; traces pre-bundled (BERT/VIT/Inceptionv3/ResNet152/SENet154). DeepUM/prefetch_lru/FlashNeuron/lru appear only as **simulated** baselines inside G10's own simulator | **simulator-only** (no GPU/driver touched) | DNN **training** traces only | **INFEASIBLE** as real-GPU H2H | **policy reimplementable** (cleanest source — tensor-vitality + smart-migration in `analysis.cc`) |
| **DeepUM** | ASPLOS'23 (Vol.2), DOI 10.1145/3575693.3575736 | **NO CODE** (GitHub search 0 hits; no AE badge) | **NO.** Custom NVIDIA UVM kernel-driver modification (reference list cites Sakharnykh UVM-perf work, Mosaic, vDNN); pre-Blackwell by ~3 years; no source to forward-port to driver 575 | **driver-surgery**; no source | DNN training (BERT/GPT-2/ResNet) | **INFEASIBLE** | **policy reimplementable in principle** (tensor-lifecycle prefetch on `cudaMemPrefetchAsync`) — depends on UVM struct_ops surface on driver 575 |
| **Sentinel** | HPCA'21, DOI 10.1109/HPCA51647.2021.00057 (NOT ASPLOS/ISCA) | **NO CODE** | **NO.** Tiered HBM+DRAM+NVM/Optane allocation (refs: Nouveau, Nimble, Espresso, Optane). Single-5090 box has **no second device-local memory tier** | **tiered-memory** hardware model (Optane EOL) | DNN training (TF, MoE refs) | **INFEASIBLE** | **neither** — no second memory tier exists on one Blackwell card for the policy to decide over |
| **TensorStore** | n/a (name collision) | [google/tensorstore](https://github.com/google/tensorstore) · Apache-2.0 · ~1.5k★ · active | **N/A — wrong system.** Google's ndarray I/O library (zarr/N5/S3 backends). No UVM, no oversubscription, no driver component. The "TensorStore" UVM research system **does not exist** | n/a | array I/O (checkpoints, neuroimaging) | **skip** | **neither** — no UVM policy to reimplement |

### 2.3 Device-side instrumentation

| System | Venue, year, paper | Artifact | sm_120 + driver 575 (evidence) | HW blocker / sim? | Workload match | Effort | Policy as eBPF? |
|--------|--------------------|----------|--------------------------------|-------------------|----------------|--------|------------------|
| **NVBit** | MICRO'19 + ongoing NVlabs | [NVlabs/NVBit](https://github.com/NVlabs/NVBit) · NVIDIA EULA (research prototype) · ~344★ · **v1.8** 2026-04-06 | **YES** — see §4. SM_120 added in **v1.7.4** (2025-02-11); v1.8 affirms Blackwell. README: SM `>=3.5 && <=12.1`, driver `<=575.xx` (our 575.57.08 is within) | none | SASS-level instruction/mem tracing — instrumentation-overhead table | **LOW** (prebuilt tarballs) | **tool, not a policy** |
| **Neutrino** | OSDI'25 ([USENIX](https://www.usenix.org/conference/osdi25/presentation/huang-songlin)) | [open-neutrino/neutrino](https://github.com/open-neutrino/neutrino) · **no license declared** · ~265★ · main 2025-07-01 (artifact branch active to 2025-12-25) | **likely YES (uncertain).** eBPF-like probes injected at **PTX** (forward-compatible ISA); README hardware table lists "NVIDIA/CUDA/PTX ✅" with **no SM cap** and no driver requirement. sm_120 not explicitly tested. All 3 OSDI'25 AE badges | none apparent | fine-grained kernel value/timestamp probing | **MEDIUM** (custom PyTorch/CUTLASS rebuild; cuBLAS/cuFFT/cuSPARSE **unsupported ❌**; no OSS license) | **tool, not a policy** |
| **CUDAAdvisor** | CGO'18 | [sderek/CUDAAdvisor](https://github.com/sderek/CUDAAdvisor) · MIT · ~53★ · **2018-08-24 (~8 yrs dead)** | **NO.** README: "cc 3.5 or later", LLVM 4.0, CUDA 7.0. LLVM compiler-**pass** profiler (needs app source), not dynamic binary instrumentation | abandoned toolchain | source-level profiling; cannot instrument pre-compiled kernels | **INFEASIBLE** | **tool, not a policy** (and not even binary instrumentation) |
| **GPA** | commercial (Intel) | Intel "Graphics Performance Analyzer" — closed, **Intel iGPUs only** | **N/A — wrong vendor.** Intel GPA targets Intel graphics (DirectX/Vulkan). No NVIDIA/CUDA support. (Intel.com pages returned HTTP 403 during audit; identity per well-known product, **not freshly source-verified**.) | **wrong vendor** | Intel graphics profiling | **INFEASIBLE** | **neither** — wrong platform; if a *different* "GPA" research paper was intended, give author/venue to re-audit |

---

## 3. Infeasible list (HotCRP-ready one-liners)

Each is backed by a fetched primary source. Paste-ready.

1. **GPreempt (ATC'25):** its public artifact patches and rebuilds the NVIDIA kernel module against **driver 550.120** (`thustorage/GPreempt` README) and hard-codes `sm_80` in its `CMakeLists.txt`; our host runs driver **575.57.08** for the RTX 5090, so the module cannot load, and we implement a GPreempt-equivalent priority-preemption policy in gpubpf instead.

2. **Salus (MLSys'20):** the executor is "tightly coupled" to a TensorFlow **1.x** fork (`SymbioticLab/Salus` README) built on CUDA 9/10, which emits no sm_120 binary; forward-porting EOL TF 1.x to CUDA 12.8 is out of scope, so we compare against Salus's policy only.

3. **Tally (ASPLOS'25):** the AE harness states "Required Hardware: An NVIDIA A100 GPU with 40 GB" and ships a ~130 GB Docker image (`tally-project/tally-bench` README); our single RTX 5090 (32 GB, no MIG) cannot reproduce the AE configuration.

4. **TGS (NSDI'23):** its stale (2023) container-cloud artifact uses MIG configurations (`test_mig.sh`) and CUDA-11.x Docker images that the MIG-less RTX 5090 cannot run.

5. **REEF (OSDI'22) on CUDA:** per the GPreempt artifact's own note, the REEF repository "only supports the ROCm driver of Ubuntu 18.04" and "cannot be executed on the current version of Ubuntu"; it is not a viable CUDA/Blackwell baseline.

6. **Paella (SOSP'23):** serving any model requires the `tvm-llis` fork pinned to TVM **v0.10** (pre-Blackwell), which cannot emit sm_120 kernels without rebasing onto TVM ≥0.16 — a multi-week codegen port.

7. **LithOS (SOSP'25):** no public source release exists (the paper defers implementation to "a separate technical report"); the system cannot be executed without an artifact.

8. **MuxFlow (Sci. China Inf. Sci. '24):** no public artifact exists; it is a production-internal, cluster-scale (10k+ GPU) scheduler, not reproducible on a single workstation.

9. **SGDRC (PPoPP'25):** no public code, and half of its contribution (VRAM cache-coloring) is derived from a **reverse-engineered VRAM-channel hash map specific to Ampere/Hopper GDDR6/HBM** that must be re-derived from scratch for Blackwell/GDDR7.

10. **GCAPS (ECRTS'24):** its driver patch targets the **Tegra `nvgpu`** kernel driver on Jetson (Xavier NX, kernel `5.10.104-tegra`), a different driver family from the 5090's `nvidia.ko` (R575) — it cannot apply to a discrete GeForce GPU.

11. **DeepUM (ASPLOS'23):** no public code repository exists for its custom UVM kernel-driver/prefetching system, so the design cannot be re-run without an unpublished artifact.

12. **G10 (MICRO'23):** its artifact is a **CPU-only performance simulator** (`platformxlab/G10` README: "executed on any x86 machine … do a performance simulation of the DNN training") that consumes pre-bundled training traces and never executes on a real GPU, so it cannot serve as a head-to-head baseline on the RTX 5090.

13. **Sentinel (HPCA'21):** no public artifact, and its allocation model assumes physically distinct **HBM + DRAM + NVM/Optane tiers** that a single Blackwell consumer card does not possess.

14. **TensorStore:** not a UVM research system — the only artifact under this name is Google's ndarray I/O library (`google/tensorstore`), unrelated to GPU memory oversubscription.

15. **CUDAAdvisor (CGO'18):** abandoned since 2018, it is an LLVM source-level compiler pass (CUDA 7.0 / LLVM 4.0) that cannot instrument modern pre-compiled kernels and has never supported sm_120.

16. **GPA:** refers to Intel Graphics Performance Analyzer, a closed tool for **Intel iGPUs**, not an NVIDIA/CUDA device-side instrumentation system.

---

## 4. NVBit sm_120 answer (called out separately — a reviewer asked why one table uses an older GPU)

**Short answer:** NVBit **officially supports sm_120 / RTX 5090 / Blackwell**, and our driver 575.57.08 is within its supported range. If our instrumentation-overhead table used an older GPU, the only technically-valid reason is that **the run predates 2025-02-11**, when sm_120 support did not yet exist; a 5090 re-run is now possible and is the correct fix.

**Evidence (all fetched directly during this audit):**

- **First sm_120 release — `NVBit-1.7.4`, published 2025-02-11.** Release body (from the [GitHub releases API](https://api.github.com/repos/NVlabs/NVBit/releases), tag `v1.7.4`) literally reads:
  > `### Added`  `- Added SM_120 support`
- **Latest release — `NVBit-1.8`, published 2026-04-06.** Release body reaffirms:
  > `### Added` `- Added TMA support (Alpha release with limitations)` `- Hopper and Blackwell are supported.`
- **README requirements** ([raw](https://raw.githubusercontent.com/NVlabs/NVBit/master/README.md)):
  - `SM compute capability: >= 3.5 && <= 12.1`  → sm_120 (12.0) is **inside**.
  - `CUDA driver version: <= 575.xx`  → our **575.57.08** is **inside** (at the ceiling).
  - `CUDA version: >= 12.0`  → satisfied.
- **Known open Blackwell issues** (not blockers, but explain residual caution): issue #165 "Wrong URZ in Blackwell" (URZ register retains legacy value on SM120/SM100); issue #152 `record_reg_vals` example tool "crashes in SM_120"; issue #148 `UVIMNMX.S32` crash on SM_120 **closed/fixed in 1.7.5**. Core SASS instrumentation works; a few decoding edge cases remain.

**Version recommendation for driver 575.57.08:** use **≥ v1.7.4** (sm_120 floor). The best header/driver match for our R575/CUDA-12.8 host is **v1.7.5** (CUDA **12.9** headers, includes the 1.7.4 sm_120 work plus SASS-decoding fixes). **v1.7.6+ move to CUDA 13.0/13.2 headers** and are likely intended for newer (R580+) drivers; whether v1.8's CUDA-13.2-header build is fully functional on driver 575.57.08 is **uncertain** (flagged in §5). Default to v1.7.5 for the overhead table; only move to v1.8 if a TMA/Blackwell-decoding feature it adds is required.

**Recommended first command (LOW effort, prebuilt):**
```bash
wget https://github.com/NVlabs/NVBit/releases/download/v1.7.5/nvbit-Linux-x86_64-1.7.5.tar.bz2
tar xjf nvbit-Linux-x86_64-1.7.5.tar.bz2
# build any tool under tools/ (e.g. inscount) and LD_PRELOAD it into a workload kernel
```

---

## 5. Uncertainties (not invented)

| Item | What is uncertain |
|------|-------------------|
| **XSched Lv1 on sm_120** | The `arch.cpp` `default→CudaQueueLv1` path is the *fallback*, not a configuration the XSched authors validated on Blackwell. It should intercept and give inter-kernel preemption, but **no compile/run was performed on this host** — numbers must be labeled "Lv1 on sm_120," not paper-Level. |
| **XSched Lv3 TSG path on sm_120** | A compile-time `kCudaLv3ImplementationTsg` path bypasses the arch switch and *might* give driver-TSG preemption on Blackwell (driver 575 exposes it); **not confirmed wired for sm_120**. |
| **Orion re-profile fidelity** | Orion's quality depends on per-kernel SM-demand profiles; the 5090 re-profiling is assumed correct but **not executed**, and the versioned `LD_PRELOAD` lib paths (`libcudnn.so.9`/`libcublas.so.12`) will need repointing to the torch-cu128-bundled sonames. |
| **Paella sm_120** | Paella's own CMake is arch-parametric, but the `tvm-llis` (TVM v0.10) blocker means **no model can be compiled** without rebasing onto TVM ≥0.16; effort/feasibility of that rebase is **unverified**. |
| **Neutrino on Blackwell PTX** | PTX is forward-compatible and the README claims CUDA/PTX support with no SM cap, but **sm_120 is not explicitly tested**; cuBLAS/cuFFT/cuSPARSE are explicitly unsupported, complicating vLLM/llama.cpp integration. No OSS license declared (reuse posture unclear). |
| **NVBit v1.7.6/v1.8 on driver 575** | v1.7.6+ ship CUDA 13.0/13.2 headers; whether full functionality works on R575 (CUDA 12.8) or requires R580+ is **unverified** — v1.7.5 (CUDA 12.9 headers) is the conservative choice. |
| **TGS / GCAPS / Salus exact metadata** | Star counts and precise last-commit dates are approximate (audit-time API/page reads); the **infeasible** verdicts do not depend on them (they rest on MIG/Tegra/TF-1.x blockers, which are source-confirmed). |
| **GPA identity** | Intel.com returned HTTP 403 during audit; "GPA = Intel Graphics Performance Analyzer" is the well-known product identity but was **not freshly source-verified**. If a different "GPA" research paper was intended, supply author/venue to re-audit. |
| **DeepUM / Sentinel driver specifics** | ACM DL / IEEE Xplore pages were paywalled/empty; the UVM-driver (DeepUM) and tiered-memory (Sentinel) scopes are inferred from their Crossref reference lists, not the implementation sections. The **NO CODE** verdict is independent of this. |
| **SGDRC eval GPUs** | `arxiv.org/html/2407.13996v1` and `v2` returned 404; the exact two eval GPUs ("two NVIDIA GPUs" per abstract) could not be confirmed, but the verdict (no code + Blackwell VRAM-RE needed) does not depend on it. |

---

## 6. Evidence index (URLs fetched during this audit)

Load-bearing sm_120 / driver verdicts were fetched directly by the auditor (first block); secondary/metadata sources were fetched by parallel research agents and are listed for traceability.

**Fetched directly by the auditor:**
- https://raw.githubusercontent.com/XpuOS/xsched/main/platforms/cuda/hal/src/arch/arch.cpp — XSched Lv1 `default` fallback; Lv2/Lv3 `nullptr`
- https://raw.githubusercontent.com/thustorage/GPreempt/master/README.md — driver 550.120, kernel-module patch, GDRCopy; REEF CUDA-unusable note
- https://raw.githubusercontent.com/thustorage/GPreempt/master/CMakeLists.txt — `sm_80` hardcoded (`CMAKE_CUDA_ARCHITECTURES 80` + `-arch=sm_80` cubin)
- https://raw.githubusercontent.com/NVlabs/NVBit/master/README.md — SM `<=12.1`, driver `<=575.xx`
- https://api.github.com/repos/NVlabs/NVBit/releases — v1.7.4 "Added SM_120 support" (2025-02-11); v1.8 "Hopper and Blackwell are supported" (2026-04-06)
- https://raw.githubusercontent.com/tally-project/tally-bench/master/README.md — A100-40GB, 130GB image, 85GB RAM
- https://raw.githubusercontent.com/eth-easl/orion/main/README.md — H100/RTX-3090 CUDA 12.6 main; LD_PRELOAD shim, no `nvcc -arch`
- https://raw.githubusercontent.com/open-neutrino/neutrino/main/README.md — PTX eBPF-like probes, no SM cap, cuBLAS unsupported
- https://raw.githubusercontent.com/platformxlab/G10/main/README.md — "any x86 machine", "performance simulation", pre-bundled training traces
- https://raw.githubusercontent.com/rtenlab/gcaps-super-repo/main/README.md — ECRTS'24, driver-patch + userspace, real-time

**Fetched by research agents (secondary):**
- https://github.com/XpuOS/xsched (+ CMakeLists, Makefile, cuda-platform tree, level1 source, llama.cpp integration, commits)
- https://github.com/thustorage/GPreempt (+ commits, patch contents)
- https://github.com/SymbioticLab/Salus (+ README, CMakeLists, commits) — note `SARC/UVA` and `SARC/salus` 404
- https://github.com/eniac/paella (+ README, CMakeLists, sosp23_artifact) and https://github.com/eniac/tvm-llis
- https://github.com/tally-project/tally-bench (+ commits)
- https://github.com/pkusys/TGS (+ README, build scripts, test_mig.sh)
- https://github.com/SJTU-IPADS/reef-artifacts
- https://arxiv.org/abs/2504.15465 (LithOS) and GitHub search (no repo)
- https://github.com/rtenlab/gcaps-super-repo/gcaps_driver_patch/readme.md (Tegra nvgpu)
- https://arxiv.org/abs/2303.13803 (MuxFlow → Sci. China Inf. Sci. '24); GitHub search (no system repo)
- https://arxiv.org/abs/2407.13996 (SGDRC → PPoPP'25); GitHub search (0 repos)
- https://github.com/platformxlab/G10 (+ src listing, commits, arXiv → confirmed MICRO'23)
- https://api.crossref.org/works/10.1145/3575693.3575736 (DeepUM ASPLOS'23 refs); GitHub/arXiv search (no code)
- https://api.crossref.org/works/10.1109/HPCA51647.2021.00057 (Sentinel HPCA'21 refs); search (no code)
- https://github.com/google/tensorstore (name collision confirmed)
- https://github.com/NVlabs/NVBit/issues (#165, #152, #148 — Blackwell sm_120)
- https://github.com/open-neutrino/neutrino (+ API, commits)
- https://github.com/sderek/CUDAAdvisor (+ README, commits — dead 2018)
- https://www.intel.com/.../graphics-performance-analyzer (403 — Intel GPA identity not freshly verified)

---

*End of audit. Standalone file; not a HotCRP promise until authors select rows from §1 and §3. Companion: `sota-baseline-feasibility.md` (MoE/KV/inference-memory) and `reproducibility-commitments.md` (policy expressibility).*
