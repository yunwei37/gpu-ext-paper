# SemiAnalysis: AMD Advancing AI (MI350X and MI400)

Source: https://newsletter.semianalysis.com/p/amd-advancing-ai-mi350x-and-mi400-ualoe72-mi500-ual256

(Paid Substack newsletter, no PDF available)

## Section: "MIG Partitioning is Wasting Time and Engineering Resources"

AMD is investing engineering effort into a GPU partitioning capability that would fragment individual GPUs into eight smaller units. The authors contend this represents misallocated resources because production inference deployments inherently require full-GPU allocations.

Key quotes:

> "No customers are asking for this. Meta, OpenAI, x.AI are all not asking for this because all online inferencing workloads require one GPU at a minimum."

> "Meta, OpenAI, x.AI all want the opposite of this and want AMD to have better support for multi-node inferencing using at least 16 GPUs"

The authors characterize this as a fundamental misalignment between AMD's engineering priorities and actual market demands. They argue that the major customers want multi-node inference (DeepEP, disaggregated prefill), not sub-GPU partitioning.

## Context for rebuttal

- This criticizes **static hardware partitioning** (MIG-style) at hyperscaler scale
- The argument is specific to Meta/OpenAI/x.AI scale deployments where models require >= 1 full GPU
- Does NOT address software-level co-location of heterogeneous workloads (inference + training) on shared GPUs, which is what gpubpf targets
- GPU underutilization is well-documented even at smaller scales (Orion EuroSys'24: 40% compute, 55% memory; MuxFlow SCIS'24: 42% memory across 20K+ GPUs)
