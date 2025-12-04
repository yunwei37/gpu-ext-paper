% Core new contri:

% story:
% many memory, sched,
% no OS level


% paper:

% hXDP (offload to device)
% XRP (kernel driver)
% cache\_ext/sched\_ext

% (safe, efficient) fine-grain, unified(cross device) and global(multi-tenant), transparent

% 1. support for xxx memory management (pretech, eviction)
%     a. find a interface, where we need hooks 
%     b. build eBPF runtime around it on GPU device for: expanding eBPF into SIMT space
%     c. build a SIMT aware verification for safety
% 2. xxx schedule (GPU: fine-grain thread block level scheduler; driver: addimisson, set priority and premetion)
%     a. find a interface, where we need hooks
%     b. safety
% 3. trace/observebility?

% what we have done

% tracing

% 1. A set bcc style of observability tools on device (gpu memory access, fine-grain scheduler thread block / thread enter / end) neutrino can do
% 2. bcc style trace tools that can show page fault, prefecth decistion / eviction decisitons, GPU scheduler create queue / descrtoy queue / (our interfcae/hooks)
% 3. trace across CPU and GPU (launchlate, etc)

% policy

% 4. memory policy LFU/FIFO/MRU... (driver) preftech policy seq / tree / stide (driver, global)
% 5. GPU side: CLC style work stealing policy, prefetch policy (prefecth some memory without block computing)
% 6. together: prefetch

% eval:
% efficient,
% multi-tenant,
% transparent,
% unified(cross device)

% 1. sync or small kernels (gemm, vector add)
% 2. pytorch / llama.cpp / vllm / faiss
% 3. run multi together

