# gpubpf 投稿稿审查报告(2026-09-07)

文档类别:**需要用户裁定**。这份报告要你决定改哪几处、按什么顺序改、以及什么时候投。

审查对象是 ASPLOS 2027 的重投稿,系统名 gpubpf,标题 "Safe and Programmable OS-Level GPU Resource Management with eBPF"。这篇稿子在 ASPLOS'27 四月轮是 paper #1797,拿到 major revision,现在这一版是修改后的重投。评审是双盲。

## 结论与判断

这一版不能按现状投出去。**引用部分已经在 2026-09-08 由 huyp 修复并重新编译验证,见本报告《引用部分的修复记录》一节;其余各处仍未改。**

审查查出七处 blocker 级缺陷。其中四处决定稿子能不能进入评审:参考文献里有一条在 PDF 里印成 `[? ]`;正文超出页数上限,而且是靠一处被 CFP 明令禁止的模板改动压出来的;稿子引入的十五处图里有十四处的图内文字按印出来的效果小于 8pt;正文有两句话把 eGPU 说成 gpubpf 自己的早期版本,等于在双盲评审里自报作者身份。另外三处会让稿子进了评审再被抓住:一条引用把七个人的 ASPLOS'19 论文挂在另外三个人名下;引言和背景两处用来立论的 73% 这个数字,三篇被引论文没有一篇报过;摘要和结论里的 0.7--3.3% 这个开销区间,两个端点都不是那七个复现策略测出来的。

从整份材料里读出来的一个判断:这一稿的问题不是"没有查",而是"查出来的结论没有走到正文里"。合作者关于匿名的警告至今还留在源文件的批注里,而被警告的那两句话一个字没改;作者自己的行数复核文档写明四处数字错了 198 行、并且声称已经改到正文,而正文里搜不到改过之后的任何一个数字;两张图的绘图脚本已经把图例从 eBPF 改成 gpubpf,而稿子里带的图还是旧的,审稿人上一轮正是抱怨过这一点;revision-comments.md 里对审稿人许下的几条承诺,在现稿里找不到对应的句子。这四件事互相独立,却是同一个模式。所以这一轮改稿的重点不是再查一遍,而是把已经查明的结论逐条落到 `.tex` 文件上。

危害排序也和直觉不一样。引用格式问题读者要翻到参考文献才看得见;而正文的数字与图上画的东西对不上,审稿人拿正文对着图看一眼就能发现,这一类这一稿至少有十二处,其中 MoE-Infinity 那一处的高低顺序是反的——正文说 gpubpf 比原生实现降得多,图上画的是原生实现降得多。

### 改完要多久

审计材料里没有给出工时估计,所以下面按改动的性质分类,而不是给一个编出来的小时数。

- 三处 blocker 是机械改动:给一个 bib 条目补 `year` 字段、删掉 `main.tex` 里的一行 `\geometry`、把两句话里的"the workshop version"改写成"eGPU"。
- 一处 blocker 是换一条 bib 条目:把挂错作者的那条整条替换成正确记录。
- 两处 blocker 需要先做判断再动笔:73% 这个数字是换成被引论文真正报过的数,还是换一批引用;0.7--3.3% 这个区间是按七个复现策略重算,还是把那个 3.2% 单独拆出来说明它测的是别的东西。
- 一处 blocker 是逐张返工:十四处图要按印出来的尺寸重新生成,其中十三处是 matplotlib 画的矢量图、一处是位图。
- 另有 60 条参考文献里的 38 条要补可点击的链接,这是逐条的工作。

### 要你定的四件事

1. **十四处图是否全部重做。** CFP 写明 HotCRP 的自动检查抓不到图内字号,这一条是作者自己的责任;不重做就是把一处已知的形式违规带进投稿。
2. 60 条参考文献里没有链接的那 38 条是否全补 DOI。CFP 把"每条带一个可点击的链接"写进了硬性要求表,并写了违反这些限制可能不经评审就被拒。
3. 60--80%、1.3 倍、10--16% 这几个数字是改数字还是改说法。按实测改数字会削弱结论(60--80% 的真实区间是 17% 到 81%;vLLM 那处的吞吐实际低于对照),按说法改则要给每一句补上适用范围。
4. **那七个复现策略是谁写的,agent 还是作者本人。** 这一条只有你知道。引言现在写的是 59 条策略全部由 agent 生成,而这七个策略是这一轮新增的、不在 59 之内,所以引言那句话怎么改取决于这个答案。

### 必须改与改了更好,以及编号怎么对上

多智能体审计交出 74 条发现,分成 8 条 blocker、37 条 major、29 条 minor。8 条 blocker 去重之后是 4 个缺陷:73% 那个数字被两条发现分别按引言和背景各记一次,双盲匿名那两句话被四条发现从不同角度各记一次。主 agent 自己另外亲手查到三个同等严重的缺陷(参考文献印成 `[? ]`、正文超页、图内字号),审计没有覆盖到。所以这份报告按 **7 个 blocker 级缺陷** 来讲,与"8 条 blocker 发现"是同一批问题的两种数法。

必须改的是这 7 个 blocker 级缺陷加 37 条 major。改了更好的是 29 条 minor,主要是参考文献元数据、大小写、缩写重复定义这一类。审查的可信度依据:每一条发现都另派一个代理去反驳它,反驳不掉的才留下来;主 agent 又从中挑出最要紧的十几条亲手重新核了一遍,没有一条被推翻。审计的组织方式与逐条验证记录见附录 A。

## 这份报告分七章,外加一节修复记录

下面七章各自处理一类问题,先一次列全:

1. **过不了形式审查的四处**——参考文献印成 `[? ]`、正文超页、图内字号小于 8pt、参考文献缺可点击链接。
2. **双盲匿名:两处把 eGPU 说成 gpubpf 自己的早期版本**——合作者警告过,警告还在源文件里,句子没改。
3. **引用挂错作者、挂错论文,或者支撑不了正文的说法**——一条挂错作者,一个立论数字三篇被引论文都没报过,另有十一处引用的内容与正文的说法对不上。
4. **正文的数字与图上画的对不上**——至少十二处,包括一处高低顺序与图相反。
5. **论文内部前后矛盾,以及交叉引用指到没有内容的章节**——同一个系统被放进两个互斥的分类,四处交叉引用指错地方。
6. **回应审稿意见时承诺过、但没有落到稿子里的五处**——承诺写在 revision-comments.md 里,稿子里找不到对应的句子。
7. **已经核实无误、不必再查的部分**——这一章的用处是划出边界,让你不必把已经核过的数字再核一遍。

下面按第一章到第七章的顺序逐章展开。每一章先给这一章的结论,再逐条讲问题;blocker 级的缺陷连同它所在的文件和行号写在正文里,major 与 minor 的逐行位置放在报告最后的附录 B 到附录 G,与章号一一对应。每一条按同一个模板写:是什么问题、依据是什么、怎么改。

## 一、过不了形式审查的四处

这一章的结论:四处里有两处是一行改动就能消除的,而两处都会在编辑或者审稿人打开 PDF 的头几分钟里被看到。**图内字号那一处是四处里唯一需要返工的,CFP 明确写了自动检查器抓不到它、责任在作者。**

### 1.1 参考文献印成 `[? ]`（已修复）

问题:`tex-revision/cite.bib` 第 2091--2096 行的 `prevail-verifier` 条目没有 `year` 字段,ACM-Reference-Format 因此输出 `\bibitem[{PREVAIL contributors}([n.\,d.])]`;`[n.\,d.]` 里那个没有加花括号的右方括号把 LaTeX 的可选参数截断了。

依据:编译出来的 `main.pdf` 第 7 页印的是 "use PREVAIL [? ] with GPU helper and map models",参考文献第 [39] 条印的是 "]prevail-verifier PREVAIL contributors. [n. d.]. PREVAIL: ..."。`main.log` 里有对应的一行:"Package natbib Warning: Citation `prevail-verifier' on page 7 undefined"。引用这个条目的是 `tex-revision/implementation.tex` 里 "Device-side programs use PREVAIL~\cite{prevail-verifier}" 那一句。

改法:给这个条目补一个 `year` 字段。

### 1.2 正文超页,原因是一处被 CFP 禁止的模板改动

问题:`main.tex` 第 15 行是 `\geometry{top=1in,bottom=1in,left=0.75in,right=0.75in,includeheadfoot}`。CFP 禁止改模板,而这一行正是在改模板;它把版面压窄之后正文反而变长,直接导致超页。

依据:acmart 的 sigplan 模板默认 `\textheight` 是 646.0pt,加上这一行之后是 610.0pt。带着这一行编译,正文(第 1 到 7 节加致谢)排到第 14 页左栏,参考文献从第 14 页右栏开始,正文约 13.4 页;删掉这一行,正文在第 13 页结束,参考文献从第 13 页右栏开始,正文约 12.5 页。ASPLOS'27 的上限是正文 11 页、major revision 加 2 页共 13 页,致谢和参考文献不计入。

改法:删掉 `main.tex` 第 15 行。删掉之后正文回到 13 页上限之内,模板改动也一并消除。

### 1.3 图内文字按印出来的效果小于 8pt

问题:稿子引入的十五处图里有十四处的图内文字,按印在纸上的实际大小算低于 8pt,多数落在 5pt 附近。CFP 的原话是图表内文字"应当让读者看到 9pt 或更大,小于 8pt 的字体不允许",并且写明 HotCRP 的检查器不会抓这一条、由作者自己负责。

依据:每张图的实际字号按"图 PDF 里 Tf 操作符给出的字号 × 引入宽度 ÷ 自然宽度"算出来。最小值最低的几张是:combined_patterns_1x5_v2 最小 4.6pt、thread_scheduling 最小 4.6pt、clc 的 microbench_combined 最小 4.8pt、vllm 的 ttft_tpot_combined 最小 4.8pt、runtime 的 microbench 最小 4.8pt。唯一合规的是 obs-overhead-with-array,它按 2.067 倍放大引入,实际 14.5--15.5pt。逐张的测量值见附录 B。

改法:这些图现在是在 18 英寸的画布上用 28pt 字排版、再缩到自然宽度的 19% 引入。要按最终印出来的尺寸重新生成:单栏图约 3.35 英寸宽,通栏图约 7.0 英寸宽,字号设 8 到 9pt。另有一处手绘的 tikz 图标签同样偏小,见附录 B。

### 1.4 参考文献缺可点击的链接（已修复）

问题:60 条参考文献里有 38 条既没有 URL 也没有 DOI,点不开。这个数是主 agent 直接数 `main.bbl` 里 60 条 `\bibitem` 得到的:38 条既没有 `\url`、`\showDOI`、`\href`,也没有 `doi.org`。

依据:CFP 的硬性要求表里,参考文献那一行写的是"8pt;不限页数;列出所有作者的全名,不许用 et al.;附上指向文档的链接,最好是 DOI;让正文里的引用编号可点击"。紧接着的一句是,违反这些限制的投稿可能不经评审就被拒。全名和不用 et al. 这半条已经满足,渲染出来的参考文献里没有出现 "et al." 或缩写名。

改法:给缺链接的条目补 `doi` 或 `url` 字段后重跑 bibtex。其中五条 arXiv 预印本条目改成 `eprint`/`archivePrefix` 形式,ACM-Reference-Format 会渲染成可点击的 arXiv 链接。这一条的严重等级审计定为 minor,但它和前三处落在同一张 CFP 检查表上,所以放在这一章。

## 二、双盲匿名:两处把 eGPU 说成 gpubpf 自己的早期版本

这一章的结论:两句话都还在,而合作者当初写下的警告也还在同一个仓库的源文件里,一字未改。**这是七个 blocker 里最不该留到投稿版的一个,因为改法早就写在批注里了。**

问题:两处句子把参考文献 [54] 那篇 eGPU 论文称作 gpubpf 的早期版本,等于宣称这篇投稿和 eGPU 是同一批作者。

- `tex-revision/implementation.tex` 第 56 行:"Unlike the workshop version~\cite{egpu}, which relies on atomic synchronization, \sys{} avoids cross-SM primitives to prevent hardware stalls."
- `tex-revision/eval.tex` 第 506 行:"We do not compare policy-level performance against the prior workshop version or Neutrino because they are limited to read-only observability (\S\ref{sec:background})."

第二句连引用都没带,读者只能把它读成"我们自己的早先版本"。

依据:两句话都进了编译出来的 PDF,分别在第 7 页和第 14 页。参考文献 [54] 在 PDF 第 16 页印的是 "Yiwei Yang, Tong Yu, Yusheng Zheng, and Andrew Quinn. 2025. eGPU: Extending eBPF Programmability and Observability to GPUs. In Proceedings of the 4th Workshop on Heterogeneous Composable and Disaggregated Systems. 73-79.",`main.tex` 里被 `\iffalse` 关掉的作者块里是同样这四个名字。合作者 Andrew Quinn 的批注至今留在 `tex-revision/discussion.tex` 第 5 行,原文是:`don't say "A prior workshop version", it deanonymizes us and we'll get rejected for it.  Just name the prior system.` CFP 的匿名一节写着 "Cite own studies as written by a third party.",以及 "Improperly anonymized submissions will likely be rejected without review."

一个限定要说清楚:同样这一句在四月的 #1797 投稿里就已经存在,那一轮拿到的是 major revision 而不是不经评审就拒。所以说它必然导致 desk reject 是过头的说法。它的确切性质是一处已知的匿名违规,而且是合作者点名要求改、至今没改的那一处。

改法:照批注说的做,用第三方口吻直接点名。`tex-revision/implementation.tex` 第 56 行改成 "Unlike eGPU~\cite{egpu}, which relies on atomic synchronization, ...";`tex-revision/eval.tex` 第 506 行改成 "...against eGPU~\cite{egpu} or Neutrino~\cite{neutrino} because ..."。同一份 eval.tex 第 500 行已经写成 "eGPU~\cite{egpu}",改完前后一致。`tex-revision/discussion.tex` 第 19 行的 "A prior workshop paper~\cite{egpu}" 已经是第三方口吻,可以不动。第 506 行那句里的交叉引用另有问题,见第五章。

## 三、引用挂错作者、挂错论文,或者支撑不了正文的说法

这一章的结论:两处是 blocker,一处把七个人的论文挂在另外三个人名下,一处让全篇的立论数字失去出处。**除这两处之外,还有十一处正文的说法与它所引的论文对不上,其中五处是被引论文根本不研究那个负载。** 这一类不会挡住形式审查,但只要审稿人顺手点开一篇被引论文就会发现,而 ASPLOS 的审稿人多半读过其中几篇。

### 3.1 一条引用把七个人的 ASPLOS'19 论文挂在另外三个人名下（已修复）

问题:`tex-revision/cite.bib` 第 2036--2041 行的 `kehne2019etc` 条目,标题是 ASPLOS'19 那篇 "A Framework for Memory Oversubscription Management in Graphics Processing Units",作者却写成 Jens Kehne、Jonathan Metter、Frank Bellosa 三个人。

依据:Crossref 对这个标题的记录(DOI 10.1145/3297858.3304044,ASPLOS '19,第 49--63 页)给出的作者是 Chen Li、Rachata Ausavarungnirun、Christopher J. Rossbach、Youtao Zhang、Onur Mutlu、Yang Guo、Jun Yang 七个人,与条目里的三个人没有一个重合。Kehne、Metter、Bellosa 是另一篇论文 GPUswap(VEE 2015,DOI 10.1145/2731186.2731192)的作者。雪上加霜的是条目类型写成了 `@misc`,而 ACM-Reference-Format 的 misc 处理函数不读 `booktitle`,所以 `booktitle={ASPLOS}` 被静默丢掉:渲染出来的那一条参考文献只有作者、年份、标题,没有会场、没有页码、没有 DOI。这个条目还是引言里 73% 那句话的引用之一,所以它是一条读者会看到的参考文献。

改法:整条替换成正确记录,类型改成 `@inproceedings`,作者填七个人,booktitle 填 "Proceedings of the Twenty-Fourth International Conference on Architectural Support for Programming Languages and Operating Systems (ASPLOS '19)",页码 49--63,DOI 10.1145/3297858.3304044。条目的 key 里带着错误的作者姓氏,一并改掉更稳妥。

编号已经查实:主 agent 从编译出来的 PDF 里取出参考文献编号,这一条是 **[28]**,印的是 "Jens Kehne, Jonathan Metter, and Frank Bellosa. 2019. A Framework for Memory Oversubscription Management in Graphics Processing Units.";同一页上 [26] 是 TimeGraph、[27] 是 Gdev。审计材料里写 [26] 的那一处是错的。

### 3.2 立论用的 73% 这个数字,三篇被引论文都没有报过

问题:73% 这个数字在稿子里出现两次,都是用来立论的。

- `tex-revision/intro.tex` 第 10 行:"optimal eviction and prefetch policies can improve performance by up to 73\% under memory oversubscription~\cite{park2025helm,kehne2019etc,ganguly2019interplay}"
- `tex-revision/background.tex` 第 37 行:"UVM eviction and prefetch policies alone can impact execution time by up to 73\%~\cite{ganguly2019interplay,park2025helm}"

依据:三篇被引论文自己报的数字分别是别的数。Ganguly 等人的 ISCA '19 论文,两份独立下载的全文里 "73" 这个字符串一次都没有出现,它自己的结论是相对 4KB LRU 页替换平均快 93%、相对 2MB LRU 平均快 18.5%。ETC(即 `kehne2019etc` 那个标题对应的 ASPLOS '19 论文)自己的结论是相对最强基线在有数据共享的规则应用上快 60.4%、在不规则应用上快 270%。HELM(`park2025helm`,SC '25)自己的结论是相对默认 UM 行为平均快 3.5 倍。

一处取材说明:ETC 和 HELM 的全文在 ACM 数字图书馆后面,自动抓取拿回来的是 Cloudflare 的 403,人在浏览器里能正常打开。所以"这两篇的正文里有没有 73% 这个数"没有被穷尽核对过;上面引的是两篇论文自己的摘要结论。Ganguly 那一篇是全文核过的,确定没有。

改法:两种做法,选一种。一是把 73% 换成被引论文真正报过的数,并把引用收窄到报那个数的那一篇。二是保留 73%,但要指出它出自哪一篇的哪一节或哪一张图——如果它确实是 ETC 或 HELM 正文里的一个数字,就要给到节级的指向,而不是三篇一起引。

### 3.3 十一处正文说法与被引论文对不上

这十一处分四类,每一处的文件、行号、引用的原句和核对办法都在附录 D。

第一类,被引论文根本不研究正文说的那个负载,共五处。引言里"aggressive memory prefetching improves latency for LLM MoE inference"和"increases the latency of graph analytics queries"两半都引 Ganguly 等人的 ISCA '19 论文,而那篇论文的全文里 MoE、LLM、transformer、graph analytics 出现次数都是零,它跑的是 Rodinia 和 PolyBench 风格的基准、显卡是 GTX 1080ti。引言里"throughput-oriented scheduling improves average latency of vector search"引 Sarathi-Serve 和 GPreempt,两篇都不研究向量搜索。背景里"MoE inference favors specialized eviction over default LRU"引 FlexGen 和 vLLM,两篇的全文里 MoE、expert、LRU 出现次数都是零。背景里"GNN training demands aggressive sequential prefetch"引 Lin 等人和 Gunrock,两篇都不研究 GNN 训练也不提 prefetch。

第二类,被引论文给的机制与正文写的机制不同甚至相反,共两处,与第一类有重叠。Ganguly 等人给的危害机制是"prefetch 触发的逐出把复用中的页挤掉",不是正文写的"把内存带宽用满";那篇论文还专门讲了大块传输会提高 PCIe 带宽(从 4KB 时的 3.2219 GB/s 升到 1024KB 时的 11.223 GB/s)。Lin 等人报的访问模式是"树形结构上的指针跳转造成随机访问",与正文说的 sequential 正好相反;而同一个背景文件早七行自己写的也是"GNN training shows irregular random access from pointer-chasing graph traversal"。

第三类,引用挂在主题完全不同的论文上,共四处。`bachl2021flow` 被当成 XDP 引用了两次,那篇是在 eBPF 上做机器学习入侵检测、用的是 raw socket 而不是 XDP;现在这份参考文献里根本没有真正的 XDP 论文。`dwivedula2025policysmith` 被列在"CPU scheduling"下,那篇的两个案例是 web 缓存和 TCP 拥塞控制。`cao2023gpu` 被用来支撑向量搜索的访问模式,那篇研究的是 GPU 上的关系数据库,跑 SSB 和 TPC-H。`alphaevolve2025` 被当成"编译器启发式"的例子,AlphaEvolve 优化的是编译器已经生成的代码,论文自己把"接进编译器"写成未来工作。

第四类,被引系统的性质与正文给它的归类相反,共两处。XSched 被列进"缺乏跨应用可见性和硬件控制"的用户态框架,而 XSched 的调度器是一个跨进程跨容器协调的守护进程、明确维护全局状态,并且在第 2、3 级抢占上会打补丁改驱动、下发未公开的 ioctl。Salus 和 PILOT 被列成"利用应用语义做请求调度和 KV-cache 卸载"的例子,两篇都不做 KV-cache 卸载,PILOT 的摘要还专门说它是透明的、不用应用语义。

另有一处属于第三类但对象是网页:`implementation.tex` 把 HMM 和 `migrate_vma` 的依据指向 `https://docs.kernel.org/gpu/drm-mm.html`,这个页面的标题是 "DRM Memory Management",里面 GPU SVM、HMM、`migrate_vma` 一个都没有;同一个地址还被另一个 bib 条目用了一次,于是参考文献里出现两条标题不同、地址相同的记录。

### 3.4 参考文献元数据本身的问题（大部分已修复）

除上面几条外,参考文献里还有一批元数据错误,全部是 major 或 minor,逐条在附录 D。最要紧的三条:LMCache 那条列了 10 个作者、领头写成 Cheng, Yihua,而 arXiv 2510.09665 是 11 个作者、领头是 Yuhan Liu,漏掉的是 Rui Zhang,而 CFP 要求列全所有作者;AlphaEvolve 那条把白皮书的标题和一篇博客文章的地址拼在同一个条目里,作者写成机构名 "Google DeepMind",而带这个标题的文档署了 18 个人名;ShareGPT 那条声明为 `@inproceedings` 却没有 `booktitle`,这是 `main.blg` 里唯一一条 "Warning--empty booktitle",印出来没有任何会场信息,而且 `note` 字段里的私人批注被当成书目内容一起印了出来。

## 四、正文的数字与图上画的对不上

这一章的结论:这一类的危害比引用格式问题大得多,因为审稿人不必查任何外部资料——把正文那句话和同一页上的图放在一起看一眼就能发现。**这一稿里这一类至少有十二处,其中一处的高低顺序是反的:正文说 gpubpf 把 TTFT 降得比原生实现多,图上画的是原生实现降得多。**

还有一个共同点值得先说:这一类里有两处不是算错,是"算对了但没有把结论搬到稿子上"。作者自己的行数复核文档写明四处数字错了 198 行、并写明已经改到正文,而正文里搜不到改过之后的任何一个数字;两张图的绘图脚本已经把图例改成 gpubpf,而稿子里带的图还是旧的。

### 4.1 摘要和结论的 0.7--3.3% 区间,两个端点都不是那七个复现策略测出来的(blocker)

问题:`tex-revision/abstract.tex` 第 19 行和 `tex-revision/conclusion.tex` 第 8 行都写 "0.7--3.3\%",结论那一句的主语是"七个已发表资源管理策略的对照复现"。

依据:全稿没有 3.3% 这个数。`tex-revision/eval.tex` 第 447--449 行报的是 0.7%(Expert Buffering)和 3.2%(UVM policy),所以上端点先是一个抄错的数字。更要紧的是 3.2% 那一条的主语是 "A UVM policy verified by the kernel ... with prefetch disabled",测的是缺页处理,不属于那七个系统里的任何一个。按绘图脚本读的原始数据算,七个复现策略相对原生实现的实际区间大致是 -1% 到 +1.9%,其中三处 gpubpf 比原生实现更快(FineMoE -0.33%、Hummingbird 的 BurstGPT 到达模式 -0.99%、GPreempt -0.30%)。评估里另外报过的 0.21%(FineMoE)和"最多 1.18%"(POD)也都落在所述区间之外。

改法:把区间换成七个复现策略实际测出来的范围,并说明其中有几个 gpubpf 不慢于原生实现;把 3.2% 那一条单独拿出来说明它测的是缺页处理这个机制,不是七个复现之一。摘要和结论两处要同时改。

### 4.2 MoE-Infinity 的 TTFT,正文与图的高低顺序相反

问题:`tex-revision/eval.tex` 里写 "the native implementation and \sys{} reduce TTFT by 22.1\% and 22.5\%, respectively",按这句话 gpubpf 比原生实现好。图上画的是相反的。

依据:两条独立的证据指向同一结论。一是绘图用的数据文件里,这个面板的三个值是 baseline 1.97594、原生实现 1.51344、gpubpf 1.53596,算出来的降幅是原生 23.41%、gpubpf 22.27%。二是主 agent 把那张图按 1200 dpi 渲染出来、按颜色分别量三根柱子的高度,得到原生 23.4%、gpubpf 22.2%,而且 gpubpf 那根蓝柱比原生那根橙柱高 8 个像素,远超过抗锯齿造成的误差。正文印的 22.1 和 22.5 两个数,图上一个都没有。

改法:按图上的值重写这一句,写成原生降 23.4%、gpubpf 降 22.3%,并且不要再说 gpubpf 在这一处胜过原生实现。

### 4.3 llama.cpp 的 4.8 倍点错了配置

问题:`tex-revision/eval.tex` 写 "4.8$\times$ over framework offloading (\texttt{ncmoe=64})",而 4.8 倍是对 `ncmoe=32` 的比值。

依据:绘图脚本里 decode 阶段的五个值依次是 16.34、18.18、7.72、49.31、86.89,对应 ncmoe=64、ncmoe=32、UVM only、UVM user hint、UVM gpubpf。86.89 除以 18.18 等于 4.779,是对 ncmoe=32 的比值;对 ncmoe=64 的比值是 86.89 除以 16.34,等于 5.318。同一段落里其余数字都与这份数据对得上,所以数据来源是对的,错的只是括号里点的配置。

改法:两种都行,把括号改成 `ncmoe=32`,或者把 4.8 倍改成 5.3 倍。摘要和引言里的这个数字要跟着一起改。

### 4.4 vLLM 的 1.3 倍吞吐与原始数据相反,而且那张图根本没画吞吐

问题:`tex-revision/eval.tex` 写 gpubpf 相对 vLLM 默认的框架托管卸载"把平均和 p99 首字延迟改善 1.7 到 2 倍、把解码吞吐改善 1.3 倍",并把这两件事一起指向 vLLM 那张图。

依据:生成那张图的脚本里,四个配置 CPU Offload(8GB)、UVM Baseline、UVM gpubpf、LMCache 的输出吞吐依次是 190.40、149.56、183.28、278.21。gpubpf 相对 CPU offload 是 183.28 比 190.40,也就是 0.96 倍,比对照低,不是高 1.3 倍。首字延迟那半句是站得住的,平均 1.66 倍、p99 1.88 倍,四舍五入落在 1.7 到 2 倍里。全套数据里唯一接近 1.3 的量是平均每个输出 token 的时间,324.13 比 235.68 等于 1.375 倍,那是单请求延迟的比值,不是系统吞吐。更根本的是,那张图只有两个面板,左边是首字延迟、右边是每个输出 token 的时间,图上没有任何吞吐,所以这张图无论如何支撑不了一个吞吐主张。

同一张图的图题还写着 "Time-to-first-token and decoding throughput",而右面板的坐标轴标签是 "Time per Output Token (ms)",图题点了一个图上没有的量。

一处相关的表述问题:同一句里说 gpubpf "matching LMCache"。按同一份数据,gpubpf 赢在首字延迟和 p99 尾延迟,LMCache 赢在总吞吐和输出吞吐,两项都是 1.52 倍。图上只画了首字延迟和每 token 时间,这个 1.5 倍的吞吐差距读者看不到,而正文用的词是"匹配"。

改法:把吞吐那半句删掉,或者换成实际测到的量并说明它是每 token 时间;把图题里的 "decoding throughput" 改成 "time per output token";把"matching LMCache"收窄到尾延迟,或者把吞吐面板补进图里。

### 4.5 Faiss 的 10--16% 只在大数据集上成立

问题:`tex-revision/eval.tex` 写 "For search workloads, \sys reduces latency by 10--16\% across different \texttt{nprobe} settings",这句话没有点数据集,读起来像是整个实验的结论。

依据:那张图上标注了六个点。SIFT100M 上是 -15.9%、-11.1%、-10.5%,正是正文那个区间。SIFT50M 上是 +1.5%(nprobe=1)、+0.1%(nprobe=4)、-0.3%(nprobe=16),没有收益,其中 nprobe=1 还是 1.5% 的退步。紧挨着的上一句在讲建索引时间时是按数据集分开写的,所以这一句不写数据集,读起来更像是覆盖整个实验。

改法:把这句话收窄到 100M 数据集,并把 50M 上的结果照实写出来。

### 4.6 60--80% 与图上标的 17% 和 81% 对不上

问题:`tex-revision/eval.tex` 写 gpubpf 的 warp 一致执行和合并的 map 访问"把开销降低 60--80\%",两个端点都被它自己引的那张图否掉。

依据:那张图给十个操作各标了一个降幅,依次是 -65%、-68%、-17%、-81%、-80%、-70%、-69%、-79%、-78%、-78%,对应 Empty probe、Entry probe、Entry+Exit、Exit probe、Array lookup、Array update、Ringbuf、Global timer、Memtrace、Per-GPU-thread array。真实区间是 17% 到 81%。写成 60--80% 既盖住了最差的那一项,又削掉了最好的那一项。

改法:写成 17--81%,或者说明这句话讲的是哪几个操作、并点出 Entry+Exit 是例外。

### 4.7 作者自己的行数复核结论,从来没有落到稿子里

问题:仓库里的 `asplos-27-rebuttal/loc-reconciliation.md` 第 7--8 行写着"现行草稿已经把 sequential prefetch 改成 573、把 573+304 写成约 880、把 573+472+45 写成 1090、把 472+454+408 写成 1334",同一份文件第 123--129 行把四处标成 "OFF BY 198"。稿子里这四处一个都没有改。

依据:在 `tex-revision/*.tex` 里搜 573,一条都搜不到。稿子仍然印着 375(四处)、约 680、约 890、约 926。另有一处内部矛盾指向同一个地方:双租户那一段写"约 926 LOC,由 Quota LRU、Tree-based Prefetch 和 Dynamic Timeslice 三者组成",而 926 恰好等于前两者之和(472 加 454),第三个组件 Dynamic Timeslice 的 408 行没有算进去;三者相加是 1334,正好是复核文档给的那个数。

改法:先确定 573 这个数是否仍然成立(复核文档测的源码树不在这个仓库里,无法重新数一遍),然后把四处 375 一起改掉,并把两个合计数按新数字重算。双租户那一处要么改成约 1330,要么把 Dynamic Timeslice 从组件列表里去掉。

### 4.8 同类的另外五处

这五处的证据链和上面几处一样,细节在附录 E:GPreempt 那一段的三个毫秒数来自数据文件里一组图上没有画的连续负载数据,而图上画的那两组数在正文里一次都没出现;设备端观测开销那一句里的 5.57% 与它并排的五个数不是同一次实验,同一个工具在配对实验里测到的是 90.71%;llama.cpp 和 clc 两张图仍然把系统标成 "eBPF" 而不是 gpubpf,而两份绘图脚本早就改过来了,上一轮审稿人正是抱怨过这一点;Faiss 那张图的图例承诺了一条红色的 gpubpf 曲线,而绘图脚本里颜色表的键名多了一个词、永远匹配不上,面板 (a) 里根本没有红线,gpubpf 的两次运行画成了两条分不开的灰线;摘要里 1.76 倍那句没有任何限定,而引言和结论的同一个数都写了 "up to"。

## 五、论文内部前后矛盾,以及交叉引用指到没有内容的章节

这一章的结论:没有 blocker,但有一处矛盾不需要任何外部资料就能看出来——同一个系统 LithOS 被放进同一小节里两个互斥的分类,两段各自的收尾句对它下了相反的判断。**四处交叉引用指到的章节里没有被引的内容,其中一处正是全篇唯一一处解释"为什么不做那个对比实验"的句子。** 逐条的文件、行号与核对办法在附录 F。

### 5.1 LithOS 被同时归进驱动级和用户态两类

背景一节里,LithOS 先出现在"驱动级策略"那一段,那一段的收尾句说这些做法都要改 OS 内核或驱动、既不安全(bug 会让内核崩溃)也不动态;几行之后,同一个引用键又出现在"主机用户态运行时与库"那一段,那一段的收尾句说这些框架安全且动态、但不是全栈的。两段对同一个系统下了相反的判断。相关工作一节又重复了一次驱动级的归类。

依据:LithOS 的 SOSP '25 论文自己写的是用 Rust 实现、提供一个名为 LibLithOS 的动态链接库来模仿原生 CUDA 库、建在 MPS 之上;论文里没有内核模块,也没有驱动源码补丁。它里面说的 "driver level" 指的是用户态的 CUDA Driver API,不是内核态驱动。所以用户态那一处的归类是对的,驱动级那两处是错的。

改法:把驱动级那两处的 LithOS 去掉,只保留用户态那一处;背景文件里同一行的中文注释一并改掉。

### 5.2 四处交叉引用指到没有被引内容的章节

最要紧的一处:评估里那句"我们不与 eGPU 和 Neutrino 做策略级性能对比,因为它们只能只读观测",把依据指向第 2 节,而第 2 节从头到尾没有出现 Neutrino、eGPU、NVBit,也没有出现只读观测这个说法。支撑这句话的是第 6 节相关工作。这一句是全篇唯一一处解释为什么不做那个对比实验的话,而上一轮审稿人正是问过这件事,所以指错地方的代价比一般的交叉引用错误大。

另外三处:讨论一节里讲"异步的跨设备效果"时指向第 3.2 节"Resource State Machines",而讲这件事的是第 3.4 节"Asynchronous Execution Model";评估里讲策略由三个程序组成时同样指向第 3.2 节,而描述这三个程序的是第 3.6 节"Example: MoE Expert Offloading",第 3.6 节目前没有 `\label` 所以引不了;设计一节把"跨设备操作要几毫秒"的依据指向背景里的一个小节,那一节没有任何延迟数字,而同一段里那个 "6.6 ms DMA prefetch" 在全稿只出现一次,既没有实验也没有引用。

### 5.3 "59 条策略全部由 agent 生成"与这一轮新增的策略对不上

引言两处和评估一处都写着 59 条评估用的策略全部由 AI agent 生成,20 天、974 次基准运行、244 次代码修改这几个数字也一并从四月那一版原样搬了过来。这一轮新增了七个已发表系统的复现策略和一条 LMCache 的 cuFile 策略,而在四月投稿 PDF 的抽取文本里搜 MoE-Infinity、Hummingbird、POD-Attention、Expert Buffering、FineMoE、cuFile 都没有命中,说明这些是新增的、不在 59 之内。于是两种读法必居其一,而两种都与稿子现在的说法冲突:要么这些新策略算在 59 里(时间上不成立),要么不是所有被评估的策略都由 agent 生成(那么引言那句和贡献列表里那一条都不成立)。作者在 revision-comments.md 第 16 行写的是 "we will implement the policy instead",读起来是作者自己实现。

这一条要先由你回答"七个复现策略是谁写的",才能定改法,已列进开头的待定事项。

### 5.4 图的编号顺序与第一次被引用的顺序不一致

`fig:microbench` 那个通栏浮动体声明在评估文件的中段,而它第一次被引用在将近两百行之后。结果读者在 PDF 里先在第 11 页遇到对 Figure 17 的引用、再在第 13 页遇到对 Figure 18 的引用,最后才在第 13 页遇到对 Figure 16 的第一次引用。图应当按第一次被引用的顺序编号。改法是把这个浮动体的声明移到"Device-side Runtime Optimization"那一段之前。

### 5.5 与外部事实对不上的两处

第一处是机器配置:评估的方法一节写 "Server~B with dual Intel Gold 6138 (80 cores)"。Intel 官方规格页给 Xeon Gold 6138 的是 20 核 40 线程,双路是 40 核 80 线程,稿子把线程数当成了核数,核数虚报一倍。同一句里 Server A 的 "Core Ultra 9 285K (24 cores)" 是对的。产品全名是 "Intel Xeon Gold 6138",稿子少了 Xeon 两个字。

第二处是系统名的大小写:那篇 ATC '25 论文自己的标题页写的是 "GPreempt",稿子和 bib 里一律写成全大写的 "GPREEMPT",涉及背景一节、评估三处、Table 2、Fig. 15 的面板 (g) 和 cite.bib。论文用的是小型大写字体排版,所以纯文本形式应当写 GPreempt。

另有一处版本号写法:llama.cpp 稿子里写 "version 7101",上游的 tag 是 `b7101`。

### 5.6 排版与用词的小问题

这一类共六项,不影响判断,列在附录 F:UVM 和 SIMT 各被展开定义了两次,eBPF 在被展开之前已经在摘要、引言、背景里用了三十多次;设计一节有一处用了 Unicode 弯撇号,而全稿其余撇号都是 ASCII;一张图的图题把 CPU 写成了小写 cpu;两条参考文献的标题里花括号相邻没有空格,印出来是 "TimeGraph:GPU"、"Real-TimeMulti-Tasking"、"Gdev:First-ClassGPU";四个手册类条目把同一个网址在 `url` 和 `note` 里各写一遍,印出来同一行连着出现两次;有七个 `\label` 定义了却从没被引用,其中 `sec:related` 零引用正是 5.2 里那处交叉引用错误的另一半。

## 六、回应审稿意见时承诺过、但没有落到稿子里的五处

这一章的结论:**这五处的共同点是承诺写在 `asplos-27-rebuttal/` 下的文档里,而稿子里找不到对应的句子。** 审稿人会拿修改说明对照正文读,承诺缺一条,读起来就是这一轮没有认真处理他的意见。逐条的出处与原文在附录 G。

第一处,关于 MIG 的那条区分。承诺是把 gpubpf 的软件共置场景与 SemiAnalysis 批评所针对的静态分区区分开,回应的是 Reviewer E 的一条质疑。对应的 bib 条目已经加进 `cite.bib`,但全稿 60 个引用键里没有它,没有任何一句话引用它,也没有任何一句话做这个区分。稿子里跟分区沾边的只有背景一节说 MIG 的资源边界固定不能动态再平衡、评估一节说租户共享一块未分区的 GPU,两句都没提那条批评。

第二处,agent 的提示词与基准脚本。承诺出现三次,包括"会把提示词和基准脚本作为公开 artifact 发布"和"agent 提示词与交互日志会作为公开 artifact 发布",回应的是 Reviewer E 要求补充 agent 设置细节。稿子里没有任何 artifact 可用性声明,除了模型名、运行次数和 API 费用之外也没有任何提示词或脚本细节。评估里"agent 在没有人工审查和指导的情况下自主生成了全部策略逻辑"这一句因此没有办法被检验。

第三处,引言里的政策与机制分离。shepherd 的原话是希望明确讨论全篇的头条改进数字来自策略还是来自机制,并特别点了摘要和引言。摘要里有一句,引言里没有。引言的评估总结和贡献列表也完全没有提这一轮新增的七个已发表策略的对照复现,而那正是这一轮最主要的新证据。

第四处,SASS 那一句。实现一节写"对于没有 PTX 的应用,主机侧策略仍然通过驱动钩子工作,另有一个基于 NVBit 的原型把编译后的 eBPF 代码插进 SASS",这是对 Reviewer A 那个问题的直接回答,而全稿只有这一句提到 SASS,没有规模、没有实验、没有例子。仓库里 2026-09-07 的进展记录描述的路径是另一条:clang 编出 BPF ELF、经 PREVAIL 与 SIMT 验证、再由 eBPF 转 NVPTX、用 CUDA 12.9 的 ptxas 编到 sm_120、通过 CUDA Driver API 装载,与稿子那句里的 NVBit 插桩不是同一条路径。

第五处,配套的修改说明文档。`resubmission-changes.tex` 与现在这一版稿子对不上三处,主 agent 逐条读过原文确认:它开头写的是 "This paper was previously submitted to OSDI'26 (Spring cycle) and rejected",讲的是上一轮 OSDI 被拒之后的修改,不是 ASPLOS 四月轮之后的修改;它给的论文标题是 "Safe and Programmable GPU Resource Management with eBPF",比稿子实际的标题少了 OS-Level 三个词;它写的评估结构是四个 RQ,还写了一个 18 个 GPU 程序、5 个不安全用例被正确拒绝的验证器正确性实验,而稿子里只有两个 RQ、没有那个实验。`Makefile` 的 `all` 目标同时构建 `main.pdf` 和 `resubmission-changes.pdf`,所以这份文档是当前构建的一部分。还剩一个要你定的点:这份文档这次是否仍要随投稿一起交。要交就得整篇按现稿重写;不交就把它从 `Makefile` 的 `all` 目标里去掉,免得再被当成配套材料。


## 引用部分的修复记录（huyp,2026-09-08）

**这一节记的是已经改掉、并且重新编译验证过的部分。** 上面各章保留了缺陷原来的描述,以便日后回看当时错在哪;凡是标了"（已修复）"的小节,内容已经不再是稿子现在的状态。修复只动了 `tex-revision/cite.bib` 和 `tex-revision/intro.tex` 里的两处引用键,没有改任何一句正文论述。

重新编译之后的验证结果:未定义引用 0 处(此前 1 处);60 条参考文献全部带上了可点击的链接(此前 38 条没有);bibtex 警告从 80 条降到 77 条,剩下的都是 ACM 格式下不影响渲染的 publisher 与 address 字段为空;页数 16 页不变。

### 改掉了什么

第一,`prevail-verifier` 补了 `year = {2026}`。正文第 7 页原本印的 `[? ]` 现在印的是 `[39]`,文献表第 39 条也恢复成正常的一行。

第二,`kehne2019etc` 整条换成了真正的记录:作者改成 Chen Li、Rachata Ausavarungnirun、Christopher J. Rossbach、Youtao Zhang、Onur Mutlu、Yang Guo、Jun Yang 七人,条目类型从 `@misc` 改成 `@inproceedings`,补上 ASPLOS '19 的完整会场名、页码 49--63 和 DOI 10.1145/3297858.3304044。现在文献表第 28 条印的是 "Chen Li, Rachata Ausavarungnirun, Christopher J. Rossbach, Youtao Zhang, Onur Mutlu, Yang Guo, and Jun Yang. 2019."。**键名仍然叫 `kehne2019etc`,与内容不符,留着是为了不改动正文里那一处 `\cite`;要改成 `li2019etc` 的话需要同时改 `tex-revision/intro.tex` 第 10 行。**

第三,XDP 那条引用换成了真正的 XDP 论文。新增 `hoiland2018xdp` 条目(Toke Høiland-Jørgensen 等七人,CoNEXT '18,页码 54--66,DOI 10.1145/3281411.3281443),`tex-revision/intro.tex` 第 50 行和第 85 行原来指向 `bachl2021flow` 的两处 `\cite` 都改指它。`bachl2021flow` 那条机器学习入侵检测的论文因此不再被引用,自动从文献表里消失。

第四,`bpftime` 的两个作者名按 USENIX 官方 BibTeX 更正:`Lai, XiaoZheng` 改成 `Lai, Xiaozheng`,`Quinn, Andrew` 改成 `Quinn, Andi`,并补上页码 557--574 和 USENIX 的文章地址。

第五,`lmcache` 的作者列表按 arXiv 2510.09665 更正为十一人、第一作者改回 Yuhan Liu、补上原先漏掉的 Rui Zhang,标题的大小写也保护起来,现在印的是 "LMCache: An Efficient KV Cache Layer for Enterprise-Scale LLM Inference" 而不是 "Lmcache"。

第六,两条标题里单词粘连的问题改掉了。文献表现在印的是 "TimeGraph: GPU Scheduling for Real-Time Multi-Tasking Environments" 和 "Gdev: First-Class GPU Resource Management in the Operating System"。

第七,大小写问题一并改掉:`Nvbit ... nvidia gpus` 改成 `NVBit ... NVIDIA GPUs`,`Uvmbench` 改成 `UVMBench`,两条 `organization={Ieee}` 改成 `IEEE`。改完之后全文再搜 "Ieee" 是 0 处。

第八,`wang2024gcaps` 从 arXiv 预印本换成 ECRTS 2024 的正式发表版本,带上 DOI 10.4230/LIPIcs.ECRTS.2024.14。`sharegpt` 这条原本是没有 booktitle 的 `@inproceedings`,补上了 ICLR 2024 的会场名和 arXiv 地址。`ganguly2019interplay` 的 booktitle 从光秃秃的 "ISCA" 展开成完整会场名,并补上页码 224--235 与 DOI。

第九,`linux-gpusvm-doc` 原来指向 `https://docs.kernel.org/gpu/drm-mm.html`,而那个页面标题是 "DRM Memory Management",全文没有 HMM、migrate_vma 或 GPU SVM 的内容。现在改指 `https://docs.kernel.org/mm/hmm.html`,条目标题相应改成 "Heterogeneous Memory Management (HMM)"。四条 `@manual` 条目里把同一个网址在 `note` 字段又印一遍的写法也删掉了。`amdgpu-userq-doc` 的年份从 2024 改成 2025。

第十,给此前没有链接的条目补了 DOI 或者正式地址,一共 17 个 DOI 和 12 个地址。每一个 DOI 都是拿标题去 Crossref 查、标题相似度 1.00 才采用的;每一个地址都实际请求过、确认返回 200。**其中两个地址我起初是按命名规律推出来的,请求之后返回 404,已经换成从站点索引里取到的真地址** —— FlexGen 是 `proceedings.mlr.press/v202/sheng23a.html`,Salus 是 `proceedings.mlsys.org` 上那条 `d9cd83bc...` 的地址。

### 没有动的部分,以及为什么

**凡是要改变论文主张的,一处都没有动。** 这些需要你自己判断:

引言和背景两处的 73%,三篇被引论文都没有报过这个数(第 3.2 节)。改法有两种,一种是换成被引论文真正报过的数,一种是换一批引用,两种都会改变这句话说的内容。

引言里把 Ganguly 那篇 2019 年的 GPGPU 研究当成 MoE 推理和图分析查询的证据(第 3.3 节),以及正文十一处类似的"被引论文支撑不了这句话"的地方。这些要么换引用要么改说法,都是主张层面的决定。

LithOS 被同时归进驱动级和用户态两类(第 5.1 节)。这要先定它属于哪一类,再改正文。

摘要与结论的 0.7--3.3%、MoE-Infinity 那张图的高低顺序、llama.cpp 的 4.8 倍、vLLM 的 1.3 倍、Faiss 的 10--16%、设备端的 60--80%、以及作者自己复核出来的行数(第四章整章)。这些是数字与实验结果的对应关系,不属于引用问题。

`alphaevolve2025` 那条把白皮书的标题配了博客的地址(第 3.4 节提到)。这一条没有动,因为要判断作者本来想引哪一份文件,猜一个反而可能改错。

`spirv-ir-rfc` 那条署名 "LLVM Community",按 CFP 应当写具体的人名。这一条没有动,因为我没有核实到那位作者在论坛上的真名,**不能拿一个没查实的名字填进参考文献**。

"三处 blocker 是机械改动"里剩下的两处也没有动:`main.tex` 第 15 行那行 `\geometry`,以及 `tex-revision/implementation.tex` 第 56 行与 `tex-revision/eval.tex` 第 506 行的两处"the workshop version"。这两处不是引用问题,而且删 `\geometry` 会让全文重排、影响所有图表的落位,应当由你在确认页数口径之后一次做完。

### 改完之后参考文献的编号变了

`bachl2021flow` 退出、`hoiland2018xdp` 进来,按字母序重排之后有几条的编号移动了。上面各章里出现的编号按修复后的版本是:XDP 那条新的是 [19];TimeGraph 从 [26] 变成 [25];Gdev 从 [27] 变成 [26];ETC 那条仍然是 [28];PREVAIL 仍然是 [39];NVBit [48];GCAPS [51];eGPU [54];bpftime [59];LMCache [31];Ganguly [13];LithOS [9]。

## 七、已经核实无误、不必再查的部分

这一章的结论:这一节的用处是划出边界。**下面这些数字、引用和排版检查项已经逐条核过并且成立,改稿时不必再核一遍**,把时间放到前六章上。

评估里的数字,与绘图脚本或原始数据对得上的有这些:llama.cpp 那一段的 1.76 倍、prefill 下降 40%、"在默认 UVM 的 4% 以内"、13% 四个数;clc 微基准的 1.34 倍、1.77 倍、-8%、约 11% 的延迟下降、重尾负载上 Greedy 的 +20%;双租户的 TPOT 40--45%、TTFT 14--20%、GNN 28%;127 倍的 SM 不均衡(382 除以 3 等于 127.33,算术正确,只是它是 16 个 SM 上的最大值除最小值、最小值只有 3 个线程);超订比例 1.25 倍和 1.84 倍;SIFT 三个数据集 9.5/24/48 GB 与 128 维 float32 的换算相符;延迟敏感任务 p99 改善 96%;安全事件 24+18+2+2+4 等于 50;Faiss"八条策略里只有两条为正"与"约 75% 为负"自洽。三个策略行数合计 820、890、680 在现行数字口径下是自洽的(注意这三个合计的基数 375 本身有问题,见第四章)。

图与正文对得上的有这些:Fig. 15 的面板 (a) 到 (g) 顺序与 Table 2 和图题的对应关系一致;须状线出现在 (b)、(f)、(g) 三个面板,与图题说的一样;面板 (e) 的 x 轴标签是 "Llama / 128",面板 (g) 的 x 轴标签是 100 和 200,都与图题一致;面板 (b) 印的 -12.85% 与正文一致;面板 (f) 的柱子与 76.9/27.0/27.3 秒一致;面板 (e) 的柱子与 5.360/4.322/4.344 毫秒一致。

引用元数据经 Crossref 核对无误的有六条:park2025helm、lin2025forest、kim2025dream、wang2024suv、kamath2025pod、yu2026finemoe,作者、会场、页码都对(其中 park2025helm 和 kim2025dream 的引用键名字有误导性,键里的姓氏不是第一作者,但印出来的内容是对的)。Table 2 里四行与原始论文核对无误:Expert Buffering、GPreempt、XSched、Hummingbird 的机制描述都与各自论文的原文一致。软件版本全部为真实发布:Faiss v1.13.0、vLLM v0.11.0、PyTorch v2.9.0、llama.cpp b7101、Linux 6.15、NVIDIA 驱动 575.57.08。

排版与匿名检查项,已核实没有问题的有四项:`\begin{comment}` 块之外没有 `\vspace`(评估文件里那一处在注释块内,不起作用);渲染出来的 PDF 里没有会场名、作者名、单位名泄漏;没有可见的 `\todo`、`\arq`、`xxx` 之类占位宏被渲染出来;所有 `\label` 都能解析、所有 `\ref` 和 `\Cref` 的目标都存在,每一张渲染出来的图和表都至少被正文引用一次。

## 附录 A:审查是怎么做的,以及编号怎么对照

### A.1 审查的组织方式

审查分两层。第一层是 13 个维度的审计代理,分别负责引用元数据、引用支撑、内部一致性、交叉引用、事实核对、格式政策、构建错误、匿名、主张与证据的落差等方向。第二层是对抗式验证:每一条被报出来的发现,都另派一个代理去反驳它,反驳不掉的才留下。两层合计 108 个代理,没有失败的。经过第二层之后留下 74 条发现,分成 8 条 blocker、37 条 major、29 条 minor。

主 agent 另外做了两件事。一是自己独立查了一遍,得到编号 B1 到 B23 的发现,其中三条(参考文献印成 `[? ]`、正文超页、图内字号)是审计没有覆盖到的 blocker 级缺陷。二是从审计的 74 条里挑出最要紧的十几条亲手重新核过,编号 R1 到 R7,全部成立,没有一条被推翻。

### A.2 报告章节与原始编号的对照

- 第 1.1 节(`[? ]` 引用)= B1。
- 第 1.2 节(正文超页)= B2。
- 第 1.3 节(图内字号)= B11,审计侧对应 W36。
- 第 1.4 节(参考文献缺链接)= W46 与 W48。
- 第二章(双盲匿名)= W4、W5、W6、W7 四条,指向同两句话。
- 第 3.1 节(挂错作者)= B16,审计侧对应 W2、W14、W19。
- 第 3.2 节(73%)= B17,审计侧对应 W1 与 W8。
- 第 3.3 节(十一处)= W11、W12、W13、W37、W38、W39、W40、W41、W42、W43、W44、W50、W73、W16、R7、B18。
- 第 3.4 节(元数据)= W15、W17、W18、W20、W51、W52、W54、W55、W56、W57、W58、W59、W60、W61、W62、W64、R6。
- 第 4.1 节(0.7--3.3%)= B6,审计侧对应 W3 与 W21。两份材料给的等级不同:主 agent 的 B6 只处理"3.3% 这个数在稿子里不存在"这一层,定为 major;审计的 W3 处理的是"区间被安到七个复现策略头上而两个端点都不是它们测出来的"这一层,定为 blocker。这份报告按 blocker 处理,因为审计那一层的问题主 agent 没有反对过。
- 第 4.2 节(MoE-Infinity)= R1,审计侧对应 W25。
- 第 4.3 节(4.8 倍)= B3,审计侧对应 W26。
- 第 4.4 节(vLLM)= B4、B5、B21,审计侧对应 W31。
- 第 4.5 节(Faiss)= B10,审计侧对应 W29。
- 第 4.6 节(60--80%)= B22,审计侧对应 W28。
- 第 4.7 节(行数)= R2、B13,审计侧对应 W27 与 W32。
- 第 4.8 节(另外五处)= W34、W30、B8、B9、W9。
- 第 5.1 节(LithOS)= R3,审计侧对应 W10 与 W22。
- 第 5.2 节(交叉引用)= B12、W23、W33、W35、W65、W66、W69。
- 第 5.3 节(59 条策略)= W45 与 W68。
- 第 5.4 节(图编号顺序)= R5,审计侧对应 W47。
- 第 5.5 节(外部事实)= B20(审计侧 W24)与 B19。
- 第 5.6 节(排版小问题)= B14、B15、B7、R4、W53、W64、W59、W71。
- 第六章(承诺没落实)= W63、W70、W74、W72、W49。
- 第七章(已核实无误)= MAIN_FINDINGS 里标为 "Checked and CORRECT"、"Cross-checks that DO hold"、"Citation metadata verified CORRECT"、"More Table-2 rows verified CORRECT"、"Software versions verified CORRECT" 以及标签核对那几段。

## 附录 B:第一章的逐条细节

### B.1 `[? ]` 引用的完整证据

出错的条目在 `tex-revision/cite.bib` 第 2091--2096 行,键名 `prevail-verifier`,引用点在 `tex-revision/implementation.tex` 的 "Device-side programs use PREVAIL~\cite{prevail-verifier}"。缺 `year` 字段导致 ACM-Reference-Format 输出 `\bibitem[{PREVAIL contributors}([n.\,d.])]`,`[n.\,d.]` 里未加花括号的 `]` 截断了 LaTeX 的可选参数。渲染结果:`main.pdf` 第 7 页 "use PREVAIL [? ] with GPU helper and map models";参考文献第 [39] 条 "]prevail-verifier PREVAIL contributors. [n. d.]. PREVAIL: ..."。`main.log` 中的告警原文:`Package natbib Warning: Citation 'prevail-verifier' on page 7 undefined`。

### B.2 页数的测量过程

`main.tex` 第 15 行:`\geometry{top=1in,bottom=1in,left=0.75in,right=0.75in,includeheadfoot}`。acmart 的 sigplan 选项默认 `\textheight` 为 646.0pt;加上这一行后为 610.0pt。带这一行编译:正文(第 1 到 7 节加致谢)排到第 14 页左栏,参考文献从第 14 页右栏开始,正文约 13.4 页。去掉这一行编译:正文在第 13 页结束,参考文献从第 13 页右栏开始,正文约 12.5 页。ASPLOS'27 CFP 的规定是正文 11 页,major revision 加 2 页共 13 页,致谢与参考文献不计入;CFP 另外禁止改动模板,也禁止用 `\vspace` 压版面。

### B.3 每张图的实际字号

测量办法:实际字号 =(图 PDF 内容流里 Tf 操作符给出的字号)×(`\includegraphics` 请求的宽度 ÷ 图的自然宽度)。取值用 `\columnwidth` =(505.89 − 24.0)÷ 2 = 240.9pt,`\textwidth` = 505.89pt。下面每一项写"图号 图名:缩放倍数,源字号,实际字号,最小值"。

- 图 1 `gpu_stack_figure`:0.402,16--24pt,6.4--9.6pt,最小 6.4pt。
- 图 2 `combined_patterns_1x5_v2`:1.018,4.5--7pt,4.6--7.1pt,最小 4.6pt。
- 图 3 `thread_scheduling`:0.290,16--22pt,4.6--6.4pt,最小 4.6pt。
- 图 4 `gpu-ebpf-arch.png`:这一处是位图不是矢量图,量不到 Tf 字号,改按像素量。原图 1240 × 740 像素,以 `\columnwidth` = 240.9pt 引入,合每 pt 5.147 像素。图里最大的那几个标签之一 "Userspace",墨迹从第 93 行像素到第 120 行像素,高 28 像素,印出来是 5.44pt;这一段墨迹跨的是大写字顶到 p 的下伸部,约占字身的 0.92,所以字号约 5.9pt。图里的 "(a.)"、"(b.)" 这类标注比它还小。
- 图 6 `clc/microbench_combined`:0.199,24--34pt,4.8--6.8pt,最小 4.8pt。
- 图 8 `llama.cpp/llama_uvm_combined_color`:0.186,28--36pt,5.2--6.7pt,最小 5.2pt。
- 图 9 `vllm/ttft_tpot_combined`:0.186,26--32pt,4.8--6.0pt,最小 4.8pt。
- 图 10 `pytorch/uvm_benchmark_comparison`:0.230,22--36pt,5.1--8.3pt,最小 5.1pt。
- 图 11 `faiss/faiss_benchmark_results`:0.256,20--28pt,5.1--7.2pt,最小 5.1pt。
- 图 12 `scheduler_latency_throughput`:0.244,22--28pt,5.4--6.8pt,最小 5.4pt。
- 图 13 `all_kernels_stacked`:0.218,26--34pt,5.7--7.4pt,最小 5.7pt。
- 图 14 `fig_colocated_results`:0.217,24--30pt,5.2--6.5pt,最小 5.2pt。
- 图 15 `matched-policy-panels`:1.004,7pt,7.0pt,最小 7.0pt。
- 图 16 `runtime/microbench_comparison`:0.440,11--20pt,4.8--8.8pt,最小 4.8pt。
- 图 17 `obs-overhead-with-array`:2.067,7--7.5pt,14.5--15.5pt,唯一合规。

另有一处手绘图标签:`tex-revision/fig_exec_model.tex` 第 39 行的 `node[above, font=\scriptsize] {workqueue}`。acmart 以 10pt 运行,`\scriptsize` 等于 7pt,再乘图内 0.97 的节点缩放得 6.79pt;PDF 里实际发出的是 `6.9738 Tf`,按包围盒量得 6.51pt,同页 10pt 正文字为 9.31pt。同一张图里其余节点用 `\small`,是合规的。

张数已经查实,并且更正了主 agent 先前的一个漏算。稿子一共有 15 处 `\includegraphics`(背景 3 处、设计 1 处、评估 11 处),其中 14 处是矢量 PDF,1 处是位图 `img/gpu-ebpf-arch.png`。主 agent 起初只量了 14 张矢量图、报 13 张不合规,把那张位图漏在测量范围之外;补量之后那张位图的字号约 5.9pt,同样不合规。所以正确的说法是:**15 处引入的图里 14 处不合规,唯一合规的是 `obs-overhead-with-array`**。审计代理当时数的 15 处是对的。

### B.4 没有可点击链接的参考文献

按 `.bbl` 文件统计,60 条里有 38 条既没有 `\url`、`\showDOI`、`\href`,也没有 `doi.org`。键名是:agrawal2024taming、bachl2021flow、cao2023gpu、che2009rodinia、chen2025ktransformers、lmcache、coppock2025lithos、ding2025asap、fan2025gpreempt、ganguly2019interplay、gim2025pie、grauer2012auto、gu2020uvmbench、huang2023towards、neutrino、kato2011timegraph、kato2012gdev、kehne2019etc、kwon2023efficient、lin2024towards、ng2023paella、pan2024survey、rasley2020deepspeed、ravi2021pilot、shen2025xsched、sheng2023flexgen、shoeybi2019megatron、villa2019nvbit、sharegpt、wang2016gunrock、wang2024gcaps、xiao2018gandiva、egpu、yu2020fine、kernelintercept、zheng2025schedcp、bpftime、zussman2025cache_ext。

按渲染出来的 PDF 统计,验证代理数到 37 条(它同时用 PDF 的链接注解交叉核对:第 14 页 11 个、第 15 页 22 个、第 16 页 10 个,合计 43 个 URI 链接,全文共 213 个链接注解)。两个数的差别在计数口径,结论一致。CFP 的原文在 `asplos27-cfp.md` 第 99 行:`| reference entries | 8pt; no page limit; list full names of all author (no "et al."); include link to document (preferably DOI); make references to citations clickable |`;第 102 行:`Submissions that violate any of these restrictions might be rejected without being reviewed.`

## 附录 C:第二章的逐条细节

两句话的位置与渲染结果:`tex-revision/implementation.tex` 第 56 行,渲染在 `main.pdf` 第 7 页;`tex-revision/eval.tex` 第 506 行,渲染在第 14 页。`main.pdf` 共 16 页,eGPU 那条参考文献 [54] 在第 16 页。对应的 bib 条目在 `tex-revision/cite.bib` 第 1635 行,`@inproceedings{egpu,...}`,`author={Yang, Yiwei and Yu, Tong and Zheng, Yusheng and Quinn, Andrew}`。

合作者批注的完整原文,位置在 `tex-revision/discussion.tex` 第 5 行:

```
%\arq{This is a really short related work section. One additional change, don't say "A prior workshop version", it deanonymizes us and we'll get rejected for it.  Just name the prior system.}
```

CFP 的两句原文在 `asplos27-cfp.md`:第 109 行 `Cite own studies as written by a third party.`;第 111 行 `Improperly anonymized submissions will likely be rejected without review.`

eGPU 的作者身份来自两个来源:Crossref 记录 10.1145/3723851.3726984,以及 ACM 的作者校样页面,两处都给出 Yiwei Yang、Tong Yu、Yusheng Zheng、Andrew Quinn 四人。

行号已经查实:`main.tex` 里被 `\iffalse` 关掉的作者块是第 126 行到第 149 行(`\iffalse % real authors` 在第 126 行,`\fi % end real authors` 在第 149 行)。审计材料给的 127--148 与 130--155 两个区间都不准。

一处被验证代理修正的说法:有一条审计发现称"只有 `discussion.tex` 第 19 行被改过,另外两处漏改",验证代理指出这不能从仓库里证实——`git log` 对 `tex-revision/discussion.tex` 只有一个压缩过的提交 `85724cc Update on Overleaf`,第 5 行的批注和第 19 行的正文在那次提交里都是新增,没有"改了这一处、漏了那两处"的历史记录。所以正确的说法是三处的现状,不是三处的修改历史。

## 附录 D:第三章的逐条细节

### D.1 挂错作者那一条的完整记录

条目位置 `tex-revision/cite.bib` 第 2036--2041 行,原文:

```
@misc{kehne2019etc,
  title={A Framework for Memory Oversubscription Management in Graphics Processing Units},
  author={Jens Kehne and Jonathan Metter and Frank Bellosa},
  year={2019},
  booktitle={ASPLOS}
}
```

Crossref 对 DOI 10.1145/3297858.3304044 的记录:标题一致;作者 Chen Li、Rachata Ausavarungnirun、Christopher J. Rossbach、Youtao Zhang、Onur Mutlu、Yang Guo、Jun Yang;容器为 Proceedings of the Twenty-Fourth International Conference on Architectural Support for Programming Languages and Operating Systems;出版日期 2019-04-04;页码 49--63。作者自存的 PDF 在 https://rausavar.github.io/pubs/li_asplos19_final.pdf ,首页作者行与 Crossref 一致。Kehne、Metter、Bellosa 三人对应的是 Crossref 10.1145/2731186.2731192,标题 GPUswap,VEE 2015。

`@misc` 丢掉 `booktitle` 的机制:决定读哪些字段的是文献样式而不是 BibTeX 程序本身,ACM-Reference-Format.bst 的 `misc` 函数从不读 `booktitle`,所以这个字段留在 `.bib` 里、永远到不了输出。可以在 `main.bbl` 里看到标题之后跟着两个空的 `\newblock`。

### D.2 73% 的核对记录

Ganguly 等人的 ISCA '19 论文取了两份独立副本:https://par.nsf.gov/servlets/purl/10157887 与作者页面 https://people.cs.pitt.edu/~debashis/papers/ISCA2019.pdf 。对全文抽取的文本做百分数枚举,得到的完整集合是 10%、18.5%、20%、50%、52%、93%、110%、125%,没有 73%。摘要原句:"an average of 93% and 18.5% performance speed-up compared to LRU based 4KB and 2MB page replacement strategies, respectively"。

ETC(即 `kehne2019etc` 标题对应的论文)摘要原句:"outperforms the state-of-the-art baseline by 60.4% and 270% for regular applications with data sharing and irregular applications, respectively"。对作者自存 PDF 全文搜 "73",命中的是引用编号 [73]、参考文献条目和一个 NSF 项目号,没有 73% 这个结果。

HELM(`park2025helm`,SC '25,DOI 10.1145/3712285.3759812)摘要原句:"outperforms default UM behavior by 3.5x on average"。

取材说明:ETC 与 HELM 的正式全文在 ACM 数字图书馆,自动抓取返回 Cloudflare 的 403 人机校验页,人在浏览器里能打开。上面 ETC 的全文核对用的是作者自存副本,HELM 只核到摘要。

### D.3 十一处正文说法与被引论文对不上

每一项写"位置:正文原句 → 核对结果"。

- `tex-revision/intro.tex` 第 17 行:"aggressive memory prefetching improves latency for LLM MoE inference by reducing memory stalls~\cite{park2025helm,ganguly2019interplay}, but increases the latency of graph analytics queries because it over-saturates memory bandwidth~\cite{ganguly2019interplay}" → Ganguly 全文里 MoE、mixture-of-expert、LLM、language model、graph analytic 命中数均为 0;"saturat" 命中数为 0。它跑的是 Rodinia 和 PolyBench 的七个基准,工作集 4MB 到 38.5MB,平均 15.5MB。它给的机制是逐出把复用页挤掉:摘要原句 "as the GPU memory is filled to its capacity, such prefetching mechanism quickly proves to be counterproductive due to locality unaware eviction policy"。带宽方向相反:表 1 给出 4KB 时 3.2219 GB/s、1024KB 时 11.223 GB/s。
- `tex-revision/intro.tex` 第 19 行:"throughput-oriented scheduling improves average latency of vector search but degrades tail latency for interactive inference~\cite{agrawal2024taming,fan2025gpreempt}" → Sarathi-Serve 全文对 "vector search"、"nearest neighbor"、"retrieval" 命中数均为 0;GPreempt 对 "vector" 命中数为 0,它的负载是 DISB 里 6 个 DNN 推理负载加上科学计算与图计算两个合成负载。GPreempt 也不用 "tail latency" 这个词,它报的是平均端到端延迟。后半句两篇都支撑。
- `tex-revision/intro.tex` 第 28 行:`\cite{dwivedula2025policysmith}` 挂在 "CPU scheduling" 下 → PolicySmith(arXiv 2510.08803)的两个案例是 web 缓存与 TCP 拥塞控制,全文里 CPU/进程调度只出现在引言的旁述和相关工作的列举里,没有案例、没有评估。同一句里的 `zheng2025schedcp` 是支撑 CPU 调度的。
- `tex-revision/intro.tex` 第 28 行:`\cite{alphaevolve2025}` 挂在 "compiler heuristics" 下 → AlphaEvolve 的章节标题是 "3.3.1 Improving data center scheduling"、"3.3.2 Enhancing Gemini kernel engineering"、"3.3.3 Assisting in hardware circuit design"、"3.3.4 Directly optimizing compiler-generated code",没有讲编译器启发式的一节;3.3.4 节自己写把发现的优化并进编译器是"potential"和"in the longer term"。同一句把 AlphaEvolve 真正做出成果的数据中心调度归给了另外两条引用。
- `tex-revision/intro.tex` 第 42 行:"User-space frameworks~\cite{ng2023paella,shen2025xsched,gim2025pie,chen2025ktransformers} are safe and dynamic but are not full-stack since policies lack cross-application visibility and hardware control" → XSched(OSDI '25)第 5.1 节:"The scheduler runs as a daemon process, coordinating all XQueues from different processes";第 5.3 节:"enabling XSched to schedule XQueues across both processes and containers";第 6.2 节改过 Intel NPU 驱动,第 6.3 节通过驱动 ioctl 调整 TSG 做抢占。两半都不成立。同样的说法在 `tex-revision/discussion.tex` 第 13 行与 `tex-revision/background.tex` 第 95、99、101 行重复。
- `tex-revision/intro.tex` 第 50 行:"Similar to prior work on resource management~\cite{schedext-docs, zussman2025cache_ext, bachl2021flow}" → `bachl2021flow` 是 arXiv 2102.09980,eBPF 上的机器学习流量入侵检测,全文对 "resource"、"schedul"、"cache" 命中数均为 0。
- `tex-revision/intro.tex` 第 85 行:"XDP~\cite{bachl2021flow}" → 同一篇论文,正文里 XDP 只出现在它自己的参考文献里,它的部署方式是 "opening a raw socket on the network interface"。真正的 XDP 论文是 Crossref 10.1145/3281411.3281443,"The eXpress data path",CoNEXT 2018,第 54--66 页,作者 Toke Høiland-Jørgensen、Jesper Dangaard Brouer、Daniel Borkmann、John Fastabend、Tom Herbert、David Ahern、David Miller。现行参考文献里没有这一篇。
- `tex-revision/background.tex` 第 11 行:"User-space frameworks (e.g., vLLM, Salus, PILOT) leverage application semantics (e.g., neural structures, latency constraints) to implement request scheduling and KV-cache offloading policies" → Salus(MLSys '20)与 PILOT(HiPC '21)全文对 "KV"、"key-value"、"offload" 命中数均为 0;PILOT 的摘要说它是透明的,输入信号是显存占用而不是应用语义。
- `tex-revision/background.tex` 第 30 行:"vector search alternates between sequential scans (index build) and random probes (query)~\cite{pan2024survey,cao2023gpu}" → Cao 等人(PVLDB vol.17,第 441--454 页)全文对 "vector search"、"nearest neighbor"、"vector database"、"vector index"、"embedding" 命中数均为 0,它跑的是 SSB 与 TPC-H。这一条被验证代理从 major 下调为 minor,因为条目本身的元数据是对的,错的只是挂在哪句话上。
- `tex-revision/background.tex` 第 37 行:"MoE inference favors specialized eviction over default LRU~\cite{sheng2023flexgen,kwon2023efficient}" → FlexGen 全文对 "MoE"、"mixture-of-expert"、"expert"、"LRU"、"evict" 命中数均为 0,它跑的是 OPT-30B 和 OPT-175B 这类稠密模型;vLLM 全文对 "MoE"、"mixture"、"expert"、"LRU" 命中数均为 0,它唯一的逐出策略是序列级的 "all-or-nothing eviction policy"。两个键在 PDF 里合印成 "[29, 43]"。
- `tex-revision/background.tex` 第 37 行:"GNN training demands aggressive sequential prefetch~\cite{lin2024towards,wang2016gunrock}" → Lin 等人(PVLDB vol.18,p599)全文对 "prefetch" 与 "training" 命中数均为 0,它的原句是 "tree-based structures that involve pointer jumping, which results in a random memory access pattern",评估的是 BFS、PageRank、Betweenness Centrality;Gunrock(PPoPP '16)对 "prefetch"、"neural"、"training" 命中数均为 0。同一个文件第 30 行自己写的是 "GNN training shows irregular random access from pointer-chasing graph traversal"。
- `tex-revision/implementation.tex` 第 12 行:把 HMM 与 `migrate_vma` 的依据指向 `linux-gpusvm-doc`(`tex-revision/cite.bib` 第 1502--1508 行)→ 该条目的 `url` 是 https://docs.kernel.org/gpu/drm-mm.html ,页面标题为 "DRM Memory Management",对 "GPU SVM"、"gpusvm"、"Shared Virtual Memory"、"SVM"、"migrate_vma"、"HMM" 的命中数全部为 0。真正的页面是 https://docs.kernel.org/gpu/rfc/gpusvm.html ,其源文件 2025-03-06 才加进内核,而条目写的年份是 2023;HMM 的页面是 https://docs.kernel.org/mm/hmm.html 。同一个地址还被 `drm-gpu-sched`(第 1514 行)使用,于是参考文献里出现两条标题不同、地址相同的记录;`linux-gpusvm-doc` 的 `note` 字段里写的 "Section ``DRM GPU scheduler''" 在那个页面上的实际标题是 "GPU Scheduler"。

### D.4 参考文献元数据的逐条问题

- `lmcache`(`tex-revision/cite.bib` 第 23--25 行):条目列 10 位作者、以 Cheng, Yihua 领头。arXiv 2510.09665 列 11 位:Yuhan Liu、Yihua Cheng、Jiayi Yao、Yuwei An、Xiaokun Chen、Shaoting Feng、Yuyang Huang、Samuel Shen、Rui Zhang、Kuntai Du、Junchen Jiang;仓库里 `asplos-27-rebuttal/ref/lmcache-2510.09665.pdf` 的元数据与之一致。漏掉的是 Rui Zhang。渲染成第 [9] 条,在第 14 页。标题存成句首大写,印出来是 "Lmcache",而正式标题是 "LMCache: An Efficient KV Cache Layer for Enterprise-Scale LLM Inference"。一处需注意:前三位作者带等贡献标记,两个来源对第二、第三位的排序不一致,改的时候以正式版为准。
- `alphaevolve2025`(第 1999--2005 行):`title` 是白皮书兼 arXiv 预印本的标题,`url` 指向的却是一篇标题不同的博客文章,`author` 写成机构名 `{{Google DeepMind}}`。带这个标题的文档署 18 位作者:Alexander Novikov、Ngân Vũ、Marvin Eisenberger、Emilien Dupont、Po-Sen Huang、Adam Zsolt Wagner、Sergey Shirobokov、Borislav Kozlovskii、Francisco J. R. Ruiz、Abbas Mehrabian、M. Pawan Kumar、Abigail See、Swarat Chaudhuri、George Holland、Alex Davies、Sebastian Nowozin、Pushmeet Kohli、Matej Balog,arXiv 编号 2506.13131。要么按预印本改,要么按博客改标题,不要混在一条里。
- `sharegpt`(第 16--21 行):`@inproceedings` 却没有 `booktitle`,这是 `main.blg` 第 68 行唯一一条 `Warning--empty booktitle`;`note` 字段里的批注被当成书目内容印了出来。论文是 arXiv 2309.11235,正式发表在 ICLR 2024。
- `ganguly2019interplay`(第 2043--2048 行):`booktitle` 只写了 "ISCA",没有页码、DOI、URL。Crossref 10.1145/3307650.3322224 给的是 Proceedings of the 46th International Symposium on Computer Architecture,第 224--235 页,2019-06-22。
- `wang2024gcaps`(第 9--14 行):引的是 arXiv 版,正式版在 ECRTS 2024,LIPIcs 第 298 卷第 14 篇,第 14:1--14:25 页,DOI 10.4230/LIPIcs.ECRTS.2024.14。两处提醒:审计最初称这篇拿过 ECRTS 2024 的 Outstanding Paper,验证代理查了会议日程存档,确认这个说法不成立;arXiv v1 上印的 DOI 尾号是 11,那个号解析到另一篇论文,正确的是 14。
- `villa2019nvbit`(第 1620--1626 行):标题存成 "Nvbit: A dynamic binary instrumentation framework for nvidia gpus",印出来就是这样。正式标题是 "NVBit: A Dynamic Binary Instrumentation Framework for NVIDIA GPUs"。验证代理指出原因不是缺花括号——同一份 bib 里 `GCAPS: GPU ...` 没加花括号也印对了大写,问题是存进去的字符串本身就是小写。
- `bpftime`(第 453--458 行,姓名在第 455 行):`Lai, XiaoZheng` 中间的大写 Z 是错的,三个原始来源都印 "Xiaozheng Lai",同一份 bib 第 1199 行也写对了。审计同时报了另外两处(最后一位作者印成 "Andrew Quinn" 而正式版是 "Andi Quinn";条目缺页码 557--574),验证代理对这两处的判定在材料里被截断,没有完整结论。
- `organization={Ieee}`(第 1873、1882 行):印出来是 "Ieee",而同一份 bib 在第 146、207、222、247、269、330、338、784、1848 行都写的是 IEEE。
- `gu2020uvmbench`(第 1885 行):标题存成句首大写,印出来是 "Uvmbench",正式标题是 "UVMBench: A Comprehensive Benchmark Suite for Researching Unified Virtual Memory in GPUs",arXiv 2007.09822。
- `amdgpu-userq-doc`(第 1529 行):年份写 2024,而 `Documentation/gpu/amdgpu/userq.rst` 最早的提交是 2025-05-02,2024 年不存在这个文档。
- `spirv-ir-rfc`(第 1567 行):作者写 `LLVM Community`,实际发帖人是 Jon Chesterfield,发帖时间 2025-03-11。
- 四个 `@manual` 条目(第 1476、1507、1515、1531 行)把同一个网址同时写进 `url` 和 `note`,ACM-Reference-Format 会把它印两遍。
- `kernelintercept`(第 1591 行):`booktitle` 写成 "USENIX Annual Technical Conference (ATC)",没有年份也没有页码,而同一份参考文献里其它 USENIX 条目都带年份。对应的 USENIX 页面是 https://www.usenix.org/conference/atc25/presentation/zhang-shulai 。
- `yu2026finemoe`(第 2075--2081 行):缺页码。Crossref 与 OpenAlex 都给出第 176--191 页,DOI 10.1145/3767295.3769319。这一条不违反 CFP 的任何硬性要求,只是与同一份 bib 里 125 个 `@inproceedings` 条目中 107 个带页码的惯例不一致。
- `zheng2025schedcp`(第 1992--1997 行)与 `ding2025asap`(第 2007--2012 行)没有链接,对应的 arXiv 是 2509.01245 与 2511.03844;`dwivedula2025policysmith` 缺 DOI 10.1145/3772356.3772413。

TimeGraph 与 Gdev 两条标题里缺空格那一处,列在附录 F。

## 附录 E:第四章的逐条细节

### E.1 0.7--3.3% 的完整核对

位置:`tex-revision/abstract.tex` 第 19 行 "incurs 0.7--3.3\% overhead when executing policies reproduced from prior work";`tex-revision/conclusion.tex` 第 8 行 "Matched reimplementations of seven published resource-management policies show that this generality costs only 0.7--3.3\% over ad-hoc implementations of the same policy"。

评估里的两个数在 `tex-revision/eval.tex`:第 447 行 "Expert Buffering incurs 0.7\% overhead. Across ten shapes, POD's operator latency in paired runs decreases by up to 0.44\% or increases by up to 1.18\%";第 449 行 "A UVM policy verified by the kernel incurs 3.2\% overhead with prefetch disabled in fifteen paired runs measuring page-fault handling"。七个系统的表在 `tex-revision/eval.tex` 第 383--401 行,依次是 MoE-Infinity、Expert Buffering、FineMoE、Hummingbird、POD-Attention、XSched、GPreempt,里面没有"关闭 prefetch 的 UVM 策略"这一行。

按 `tex-revision/img/results-raw/revision/matched-policy-panels.json` 与 `port-panels.json` 逐个算出的 gpubpf 相对原生实现的代价:MoE-Infinity 1513.44 → 1535.96 ms,+1.49%;Expert Buffering 5.663 → 5.621 token/s,+0.74%;FineMoE 4.4994 → 4.5144 token/s,-0.33%;Hummingbird 周期到达 1.830785 → 1.864302 ms,+1.83%,BurstGPT 到达 4.989155 → 4.939697 ms,-0.99%;POD 4.322043 → 4.344273 ms,+0.51%;XSched 26.9784 → 27.2502 s,+1.01%;GPreempt 1.614817 → 1.610008 ms,-0.30%。绘图脚本 `plot_port_panels.py` 的图例映射是 `("baseline","Baseline"),("original","Native policy"),("port","gpubpf")`。

### E.2 MoE-Infinity 那张图的量法

数据文件 `tex-revision/img/results-raw/revision/matched-policy-panels.json` 里 `moe-infinity` 面板的三个值:`baseline` 1.97594、`original` 1.51344、`port` 1.53596。相对 baseline 的降幅是原生 23.41%、gpubpf 22.27%。

主 agent 的独立量法:把 `matched-policy-panels.pdf` 按 1200 dpi 渲染,按颜色掩码分离三根柱子(baseline 灰 102,102,102;原生橙 217,119,6;gpubpf 蓝 0,114,178),三根柱共用 y=1483 像素的基线。灰柱顶 820,高 663 像素;橙柱顶 975,高 508 像素,降幅 (663−508)/663 = 23.4%;蓝柱顶 967,高 516 像素,降幅 (663−516)/663 = 22.2%。蓝柱比橙柱高 8 个像素。

### E.3 llama.cpp 那一段的全部数字

绘图脚本 `img/results-raw/llama.cpp/visbasic.py` 的配置与数据:配置依次是 `ncmoe=64`、`ncmoe=32`、`UVM only`、`UVM user hint`、`UVM gpubpf`;decode(tg128)依次是 16.34、18.18、7.72、49.31、86.89;prefill(pp512)相关值 238.48(默认 UVM)、144.00(用户 hint)、229.67(gpubpf)、260.14(ncmoe=32)。

由此:86.89 ÷ 18.18 = 4.779;86.89 ÷ 16.34 = 5.318;86.89 ÷ 49.31 = 1.762(正文的 1.76 倍);144.00 ÷ 238.48 = 0.604(正文的"hint 让 prefill 下降 40%");229.67 ÷ 238.48 = 0.963(正文的"在默认 UVM 的 4% 以内");260.14 ÷ 229.67 = 1.133(正文的"ncmoe=32 的 prefill 高 13%")。除 4.8 倍那一处点错配置外,这一段其余数字全部成立。

### E.4 vLLM 那张图的全部数据

`img/results-raw/vllm/generate_figures.py` 里四个配置 `CPU Offload (8GB)`、`UVM Baseline`、`UVM gpubpf`、`LMCache` 的数据:

- `output_throughput`:190.40、149.56、183.28、278.21
- `total_throughput`:391.14、307.26、376.53、571.54
- `tpot_mean`:324.13、374.23、235.68、222.24
- `ttft_mean`:8387.80、9642.27、5042.22、5401.71
- `ttft_p99`:14937.16、16549.02、7933.22、10072.64
- `tpot_p99`:817.94(LMCache)对 583.74(gpubpf);`tpot_median`:149.84(LMCache)对 207.69(gpubpf);`benchmark_duration`:79.30 秒(LMCache)对 120.36 秒(gpubpf)

由此:gpubpf 相对 CPU Offload 的输出吞吐 183.28 ÷ 190.40 = 0.963;首字延迟均值 8387.80 ÷ 5042.22 = 1.66,p99 14937.16 ÷ 7933.22 = 1.88;每 token 时间均值 324.13 ÷ 235.68 = 1.375,中位数 215.65 ÷ 207.69 = 1.038。LMCache 相对 gpubpf 的总吞吐与输出吞吐都是 1.52 倍。生成的图文件是 `ttft_tpot_combined.pdf`,在 `tex-revision/eval.tex` 第 158 行引入,只有首字延迟与每 token 时间两个面板。

### E.5 Faiss 搜索延迟的六个标注点

正文位置 `tex-revision/eval.tex` 第 216 行,图文件 `img/results-raw/faiss/faiss_benchmark_results.pdf`。图里嵌的六个标注是 1.5%、0.1%、-11.1%、-15.9%、-0.3%、-10.5%。绘图脚本 `plot_results.py` 把归一化延迟算成 `pref_latency/base_latency`,标注值算成 `(norm_lat - 1.0)*100`,SIFT50M 的标签放在标记下方(`xytext` 偏移 0,-20,`va='top'`),SIFT100M 放在上方(0,+15,`va='bottom'`)。按包围盒的横纵坐标配对得到:SIFT50M 是 +1.5%(nprobe=1)、+0.1%(nprobe=4)、-0.3%(nprobe=16);SIFT100M 是 -15.9%、-11.1%、-10.5%。

一处补充:同一小节第 210 行引入了 20M、50M、100M 三个数据集规模,而面板 (b) 只画了 50M 和 100M 两个,所以"across different nprobe settings"实际覆盖的是两个规模,其中一个有收益。

### E.6 设备端开销那十个操作的降幅

正文位置 `tex-revision/eval.tex` 第 502 行,图在第 330 行引入,文件 `img/results-raw/runtime/microbench_comparison.pdf`,渲染在 `main.pdf` 第 12 页。图里自带的十个标注按图上顺序是 -65%、-68%、-17%、-81%、-80%、-70%、-69%、-79%、-78%、-78%,对应 Empty probe、Entry probe、Entry+Exit、Exit probe、Array lookup、Array update、Ringbuf、Global timer、Memtrace、Per-GPU-thread array。

用绘图脚本 `plot_microbench.py` 自己的公式(开销 = 耗时 − 基线,基线 5.15 微秒)从两份输入数据重算:Entry+Exit(tiny)6.25 → 6.06,(1.10−0.91)/1.10 = 17.3%;Exit probe(tiny)6.23 → 5.35,(1.08−0.20)/1.08 = 81.5%。

### E.7 行数的完整对照

复核文档 `asplos-27-rebuttal/loc-reconciliation.md` 的表格行原文:`C3 sequential 375 | extension/prefetch_adaptive_sequential.{bpf.c,c} | 233 | 340 | 573 | -198 | OFF BY 198`;它的 Suspect C 一节写:"Neither component alone (233, 340) nor the sum (573) equals 375"。文档头部第 7--8 行写:"The active draft now uses 573 for sequential prefetch, approximately 880 for 573+304, 1090 for 573+472+45, and 1334 for 472+454+408";第 123--129 行把四处标成 OFF BY 198。

稿子里 375 出现在 `tex-revision/eval.tex` 第 57、151、192、218 行,另有第 348 行在不参与编译的 `\begin{comment}` 块里。两个合计数:第 153 行的"约 680 LOC"(375+304)与第 218 行的"约 890 LOC"(375+472+45)。双租户那一处在第 308 行,"约 926 LOC,由 Quota LRU、Tree-based Prefetch 和 Dynamic Timeslice 组成";第 281--282 行给出 `Prefetch(lo,hi)` 454 LOC、`Evict(lo,hi)` 472 LOC,相加正好 926;注释掉的支持矩阵第 351--352 行给出 Tree-based Prefetch 454、Dynamic Timeslice 408,三者相加 1334。

一处限制:复核文档测量的源码树路径是 `/home/yunwei37/workspace/gpu/gpu_ext`,不在这个仓库里,所以 573 这个数没有被重新数过一遍,上面引的是复核文档自己记录的测量结果。

### E.8 同类的另外五处

- GPreempt 的三个数:正文在 `tex-revision/eval.tex` 第 439 行,图题在第 410 行,图渲染在 `main.pdf` 第 13 页。数据文件里 `gpreempt` 面板有三组:`100` 组 baseline 1.916555、原生 1.628926、gpubpf 1.636552;`200` 组 1.853529、1.624812、1.610963;`cont.` 组 1.795937、1.614817、1.610008。正文的 1.796/1.615/1.610 正是 `cont.` 组。发出去的图只有两组,按包围盒读 x 轴刻度只有旋转过的 "100" 和 "200",没有 "cont."。图所在目录的 README 写着"合并后的图保留了两个后台负载速率,并加入了 GPreempt 那一段用到的连续负载组",而那一组在发出去的 PDF 里不存在。
- 观测开销的 5.57%:正文在 `tex-revision/eval.tex` 第 483 行。数据文件 `tex-revision/img/results-raw/revision/obs-with-array-data.json` 里,配对实验 `rtx5090_table1`(每臂 10 对,基线 37586.322536 token/s)给出 gpubpf 侧 90.70508589245986、2.965308072740932、0.22081515830431692,NVBit 侧 99.62103038795733、10.350110279369137、8.795916384163416。正文里的 5.57% 来自另一个实验 `rtx5090_gpu_array`(5 对,自己的基线 37979.2560812,`independent_campaign` 为真,`storage` 为 `gpu-array-onevalue`,均值 5.572554166810581),该实验自己的备注写着这五对"没有与 table1 的 NVBit 臂或 gpubpf 环形缓冲臂交错运行,也没有与之配对"。同一份文件还记录这个配置的 `final_lookup_ms` 均值 10.379343,并注明它落在 prefill 计时窗口之外。
- 两张图仍标着 eBPF:`img/results-raw/llama.cpp/llama_uvm_combined_color.pdf` 渲染在第 9 页,最后一根柱子标 "UVM eBPF",而 `visbasic.py` 第 12 行已经写成 "UVM gpubpf";`img/results-raw/clc/microbench_combined.pdf` 有两根柱子标 "Host+Dev. Stride eBPF" 和 "Host Seq. eBPF",而 `plot_microbench_combined.py` 第 28 行附近已经写成 `Host+Dev.\nStride\ngpubpf` 与 `Host Seq.\ngpubpf`。柱子的数值与现行脚本一致,过时的只有标签,说明脚本改过之后图没有重新生成。vLLM、colocated、faiss 三张图已经重新生成过。`tex-revision/eval.tex` 里还留着一条尚未处理的批注,原文是 "its very weird that none of the bars in Figure 8 are labeled '\sys'--I think that UVM eBPF is supposed to be that configuration"。修法是重跑 `make figures`,至少重跑这两个脚本,再重新编译。
- Faiss 图例的颜色:`img/results-raw/faiss/plot_results.py` 第 55--60 行的 `config_colors` 里键写成 `"UVM gpubpf Prefetch": "tab:red"`,而第 44 行的 `parse_filename()` 对 prefetch_adaptive 文件返回的 config 是 `"UVM gpubpf"`,第 83 行 `color=config_colors.get(config, "tab:gray")` 因此永远取到灰色;第 152 行的图例是手工构造的 `Line2D(color='tab:red', label='UVM gpubpf')`。结果面板 (a) "Index Build Time" 里没有任何红色曲线,gpubpf 的两次运行画成两条分不开的灰线,读者既分不出哪条是 gpubpf,也分不出哪条属于哪个数据集。修法是把颜色表的键改成 `"UVM gpubpf"`。
- 摘要里 1.76 倍没有限定:`tex-revision/abstract.tex` 第 17 行写 "AI-generated policies improve throughput by $1.76\times$ over application-tuned baselines",复数、没有 "up to"、没有范围。全篇唯一的 1.76 倍在 `tex-revision/eval.tex` 第 102 行,是 llama.cpp 上 GPT-OSS-120B 在 RTX 5090 上 decode 一个阶段相对一种 hint 配置的比值。同一个实验的另一个阶段 gpubpf 是落后的(第 106 行:框架卸载 `ncmoe=32` 的 prefill 吞吐比 gpubpf 高 13%)。GNN 那个负载里应用自己插的 hint 更强:第 181 行 "Developers can pre-migrate pages via `cudaMemPrefetchAsync`, achieving 5.5$\times$ speedup",第 183 行 gpubpf 无需 hint 达到 2.65 倍。引言第 103 行和结论第 6 行的同一个数都写了 "up to",摘要是唯一没写的。

另有两处 minor 属于同一类,正文没有单列:Hummingbird 那一句的下端点写 5.9%,按数据算是 5.830%,应为 5.8%(其余三个端点都对);Figure 16 的图题说面板 (b) 是"经 PCIe 的 CPU map 访问延迟与 GPU 侧操作的对比",而面板 (b) 只有两根红色柱子 Array lookup 和 Array update,都标 34 毫秒、都是 CPU 侧,GPU 侧的数在面板 (a)。与之相关,正文说"经 PCIe 的 CPU map 访问比 GPU 侧操作慢 6000 倍",34 毫秒对面板 (a) 里 gpubpf 的柱子(array lookup 约 0.6 微秒、array update 约 1.8 微秒)是一万九千到五万七千倍,6000 倍对应的是 34 毫秒比 eGPU 式基线的 array update(约 6 微秒)。这个数是偏保守而不是夸大,但要说清它取自哪一对柱子。

## 附录 F:第五章的逐条细节

### F.1 LithOS 的三处归类

`tex-revision/background.tex` 第 88 行在标题为 `\paragraph{Driver-Level Policies.}`(标题在第 82 行)的段落内,原句是 "More recent work such as GPREEMPT~\cite{fan2025gpreempt} and GCAPS~\cite{wang2024gcaps} add priority-based preemption, and LithOS~\cite{coppock2025lithos} re-implements runtime stacks with OS-like abstractions";这一段第 90 行的收尾句是 "Despite improved performance, all these approaches require OS kernel or driver modifications to change policy: they are neither safe (bugs can crash the OS kernel)..."。

第 95 行在标题为 `\paragraph{Host User-Space Runtimes and Libraries.}` 的段落内,同一个引用键再次出现:"User-space frameworks~\cite{ng2023paella,gim2025pie,shen2025xsched,chen2025ktransformers,coppock2025lithos} offer programmability but face three limitations";这一段第 103 行的收尾句是这些框架"safe and dynamic but not full-stack"。

第三处在 `tex-revision/discussion.tex` 第 11 行:"Driver-level GPU resource managers~\cite{kato2011timegraph,kato2012gdev,kernelintercept,fan2025gpreempt,wang2024gcaps,coppock2025lithos} require unsafe OS kernel driver modifications and service interruptions to change policy";这一行里其余五个键的归类是对的。

原始论文依据(LithOS,SOSP '25,DOI 10.1145/3731569.3764818,预印本 arXiv 2504.15465):第 4.1 节 "LithOS runs on CPU cores and interposes at the driver level, providing a dynamically linked library, LibLithOS, that mimics the native CUDA library";第 6 节 "We implement a prototype of LithOS ... in ~5000 lines of Rust, excluding macro-generated code for interposing the entire CUDA Driver API ... we build on top of MPS"。论文里说的 "driver level" 指用户态的 CUDA Driver API,没有内核模块也没有驱动源码补丁。改法是删掉第 88 行和第 11 行里的 LithOS,同时改掉第 89 行的中文注释。

### F.2 四处交叉引用

- `tex-revision/eval.tex` 第 506 行的 `\S\ref{sec:background}`:`\label{sec:background}` 在 `tex-revision/background.tex` 第 3 行,`main.aux` 记为第 2 节,渲染成 "(§2)",在 `main.pdf` 第 14 页。对 background.tex 全文搜 `read-only`、`neutrino`、`egpu`、`nvbit`、`workshop` 无命中。支撑句在 `tex-revision/discussion.tex` 第 17 行("NVBit~\cite{villa2019nvbit} and Neutrino~\cite{neutrino} inject instrumentation into GPU binaries for device-side visibility, but lack safety guarantees and target offline profiling rather than online policy enforcement")与第 19 行("A prior workshop paper~\cite{egpu} extends eBPF to GPU instrumentation but remains limited to read-only observability")。`main.aux` 第 260 行给出 `sec:related` 为第 6 节、在第 14 页。一处严重性上的修正:验证代理指出第 6 节就在同一页往下十几行,读者并非完全找不到依据,所以这一条的等级是介于 minor 与 major 之间,而不是 major。
- `tex-revision/discussion.tex` 第 9 行的 `\S\ref{sec:design-interfaces}`:`main.aux` 第 88 行记为第 3.2 节 "Resource State Machines",正文只有四句、讲三个资源域;应当指向 `sec:exec-model`(`main.aux` 第 94 行,第 3.4 节 "Asynchronous Execution Model")。只改第 9 行和第 10 行的中文注释,不要改标签本身——`tex-revision/intro.tex` 第 59 行用的是同一个标签且用对了。
- `tex-revision/eval.tex` 第 115 行的 `\S\ref{sec:design-interfaces}`:这一句列的是三个程序(设备端 warp 入口访问计数、uprobe 驱动的主机预取、LFU 排序的逐出),描述它们的是第 3.6 节 "Example: MoE Expert Offloading",在 `tex-revision/design.tex` 第 248 行,该节没有 `\label`,所以现在引不了;第 261--267 行是三个程序的文字描述,第 276--303 行是图 7 的代码清单 `moe_observe` / `moe_prefetch` / `moe_evict`。改法是给第 3.6 节加一个标签再指过去,或者改成引图 7。同一个标签在 `tex-revision/eval.tex` 第 98 行也用了一次,两条验证意见不一致:一条认为第 98 行尚可、只有第 115 行错,另一条认为两处都错。
- `tex-revision/design.tex` 第 62 行的 `\S\ref{sec:arch-gpu}`:标签在 `tex-revision/background.tex` 第 6 行,那一节报的是缺页地址轨迹和 SM 不均衡,没有任何迁移延迟数字。同一份设计文件第 94 行的 "a uprobe on `cudaLaunchKernel` concurrently initiates a 6.6\,ms DMA prefetch" 里的 6.6 在全稿只出现这一次,`tex-revision/fig_exec_model.tex` 里也没有对应的数字标注,评估里没有报过任何 DMA 或迁移耗时。同一个"跨设备操作要几毫秒"的前提在 `tex-revision/intro.tex` 第 74 行也出现过一次,同样没有引用。

### F.3 59 条策略的证据

现行稿子的三处:`tex-revision/intro.tex` 第 105 行、第 119 行,`tex-revision/eval.tex` 第 83--85 行。第 83 行原句:"All 59 policies evaluated were produced via a fully automated generate-test-iterate loop. Over 20 days, the agent performed 974 benchmark runs and 244 code edits, exploring 59 distinct policies."

四月投稿 PDF(`asplos-27-rebuttal/asplos27-apr-paper1797 (1).pdf`)的抽取文本第 289、312、1674--1677 行有一字不差的同样句子。在同一份抽取文本里搜 MoE-Infinity、Hummingbird、POD-Attention、Expert Buffering、FineMoE、cuFile,只有 XSched 在参考文献里出现过一次,其余无命中,说明第 5.2.4 节与 cuFile 策略都是这一轮新增的。第 5.2.4 节(`tex-revision/eval.tex` 第 364--450 行)从头到尾没有用过 "agent" 这个词,用的说法是 "\sys{} implements ... as host-side programs"。`asplos-27-rebuttal/revision-comments.md` 第 16 行写的是 "we will implement the policy instead, as we already do for GPREEMPT's priority timeslicing"。

### F.4 图编号顺序

浮动体声明在 `tex-revision/eval.tex` 第 328--334 行,唯一的两处引用在第 500 和 504 行。`main.aux` 记录 `fig:microbench` 为图 16(第 211 行)、`fig:matched-ports` 为图 17(第 223 行)、`fig:obs-overhead` 为图 18(第 232 行)。PDF 里第一次提及的顺序:第 11 页 "Methodology. In Figure 17, we compare the workload";第 12 页是图 16 的图题;第 13 页 "with NVBit [48] (Figure 18)";第 13 页 "Figure 16(a) compares gpubpf's"。改法是把第 328--334 行的浮动体移到第 496 行附近。

### F.5 两处外部事实

机器配置在 `tex-revision/eval.tex` 第 21 行(第 22 行是对应的中文注释),渲染在 `main.pdf` 第 8 页。Intel 官方规格页对 Xeon Gold 6138(SKU 120476)写的是 Total Cores: 20、Total Threads: 40,双路即 40 核 80 线程;6138P 与 6138T 也都是 20 核 40 线程。Core Ultra 9 285K(SKU 241060)写的是 Total Cores: 24(8 个性能核加 16 个能效核)、Total Threads: 24,所以同一句里的 Server A 是对的。建议改成 "Server~B with dual Intel Xeon Gold 6138 (40 cores, 80 threads)"。

系统名大小写:`asplos-27-rebuttal/ref/gpreempt-atc25.pdf` 第 1 行的标题是 "GPreempt: GPU Preemptive Scheduling Made General and Efficient";稿子写成全大写的地方是 `tex-revision/background.tex`、`tex-revision/eval.tex` 三处、Table 2、Fig. 15 的面板 (g),以及 `tex-revision/cite.bib`。llama.cpp 的版本号稿子写 "version 7101",上游 tag 是 `b7101`,2025-11-19 发布。

### F.6 排版与用词

- UVM 展开两次:`tex-revision/intro.tex` 第 8 行与 `tex-revision/background.tex` 第 13 行,都写成 "Unified Virtual Memory (UVM)"。
- SIMT 展开两次:`tex-revision/background.tex` 第 15 行与 `tex-revision/design.tex` 第 169 行,都写成 "SIMT (Single Instruction, Multiple Threads)"。
- eBPF 展开太晚:摘要用 2 次、引言用 26 次、背景用 4 次之后,`tex-revision/design.tex` 第 15 行才展开成 "eBPF (extended Berkeley Packet Filter)"。这个会场上 eBPF 是通用词,可以选择首次出现处展开,也可以干脆不展开,但不要两头都不占。
- Unicode 弯撇号:`tex-revision/design.tex` 第 169 行 "eBPF’s scalar model" 用的是 U+2019,全稿其余撇号是 ASCII。能编译,只是不一致。
- 图题里的小写:`tex-revision/fig_exec_model.tex` 的 `\caption{Policy execution model: cpu policies vs \sys{}.}`,`cpu` 应为 `CPU`。
- 标题里缺空格:`tex-revision/cite.bib` 第 286 行 `title={{TimeGraph}:{GPU} Scheduling for {Real-Time}{Multi-Tasking} Environments}` 缺两处空格,第 1576 行 `title={Gdev:{First-Class}{GPU} Resource Management in the Operating System}` 缺两处空格,共四处。印出来是 "TimeGraph:GPU"、"Real-TimeMulti-Tasking"、"Gdev:First-ClassGPU",在 `main.pdf` 第 15 页。一处证据上的更正:纯 `pdftotext` 输出里 "Multi-Tasking" 的连字符也没了,加 `-layout` 之后可以看到连字符是在的,只是正好在行尾断行,所以少的空格是四处不是五处。
- 四个手册类条目重复印网址那一条,见附录 D.4。
- 有七个 `\label` 定义了从未被引用:`sec:motivation-agent`、`sec:conclusion`、`sec:related`、`sec:rq1-micro`、`sec:rq1-agent`、`sec:rq1-mt`、`tab:support-matrix`。其中 `sec:related` 零引用正是 F.2 第一条的另一半。
- 图 15 的面板字母:结果段只在正文里点名了面板 (b) 和 (f),面板 (a)、(c)、(d)、(e)、(g) 都只按系统名讨论、没有给面板指引,读者要自己把七个系统名对到七个没被点名的面板上。这不算错误,是一次可以顺手做掉的可读性改进。

## 附录 G:第六章的逐条细节

### G.1 SemiAnalysis 那条区分

承诺原文,`asplos-27-rebuttal/revision-comments.md` 第 22 行:"...and will distinguish our software co-location setting from the static partitioning the SemiAnalysis critique targets(Reviewer E)"。审稿意见原文,`asplos-27-rebuttal/review.txt`:"gpubpf compares itself to MIG GPU partitioning in 2.3, but SemiAnalysis reports that inferencing workloads do not really use it"。

现状:bib 条目 `semianalysis2025partitioning` 在 `tex-revision/cite.bib` 第 2083--2089 行,标题 "AMD Advancing AI: MI350X and MI400 UALoE72, MI500 UAL256"。从 `main.tex` 与 `tex-revision/*.tex` 抽出的 60 个引用键里没有它,也没有 `\nocite`,`main.bbl` 里没有这一条。全稿与分区有关的只有 `tex-revision/background.tex` 第 99 行("hardware partitioning such as MIG imposes fixed resource boundaries that cannot be dynamically rebalanced")和 `tex-revision/eval.tex` 第 315 行("The tenants share an unpartitioned GPU managed by a system-wide policy"),两句都没提那条批评。

### G.2 agent 的提示词与基准脚本

承诺出现三次:`asplos-27-rebuttal/rebuttal.md` 第 73 行 "We will release prompts and benchmark harnesses as a publicly available artifact.";`asplos-27-rebuttal/rebuttal-v3.md` 第 102 行 "Agent prompts and interaction logs will be released as publicly available artifacts.";`asplos-27-rebuttal/revision-comments.md` 第 22 行 "release the agent prompts and benchmark harnesses (Reviewer E)"。审稿意见原文:"more details are needed about the agent setup (prompts used for Claude, etc.)"。

现状:在 `tex-revision/*.tex` 与 `main.tex` 里搜 artifact、open source、available at、release、prompts、harness,只命中 `tex-revision/eval.tex` 第 81 行、第 306 行(那是 ShareGPT 的请求 prompt,不是 agent 提示词)和第 401 行。没有 `\appendix`,没有补充材料引用,`main.tex` 第 235--236 行的致谢只有一句话。被这条影响的正文句子是第 81 行:"We provided an AI coding agent (Claude Code with Opus 4.5) with \sys{}'s eBPF interfaces; the agent autonomously generated all policy logic without human review or guidance, while humans authored only the initial framework and benchmark harness."

### G.3 引言里的政策与机制分离

shepherd 的原话,`asplos-27-rebuttal/revision-comments.md` 第 40 行:"it would be good to explicitly discuss whether the headline improvement numbers throughout (especially in abstract and introduction) come from the policy or the mechanism"。元审稿意见,`asplos-27-rebuttal/review.txt`:"Please pay attention to Reviewer F's concern with distinguishing between policy improvements and mechanism improvements."

现状:`tex-revision/abstract.tex` 第 19 行有一句做了这个区分,引言没有。在 `tex-revision/intro.tex` 里搜 published、seven、prior work、native implementation、reproduc,只命中第 50 行那个引用。评估总结在第 101--104 行,只列了 "LLM inference, GNN training, vector search, and multi-tenant scenarios";贡献列表第 119 行仍是四月那一版的写法。区分只出现在第 5.2.4 节的方法段(`tex-revision/eval.tex` 第 417--420 行)。

### G.4 SASS 那一句

正文原句,`tex-revision/implementation.tex` 第 65 行:"For applications without PTX, host-side policies still operate through driver hooks, and a prototype built on NVBit~\cite{villa2019nvbit} inserts compiled eBPF code into SASS."

审稿意见原文,Reviewer A:"How does it work with workloads ship as SASS or binary? Is there a way to handle patching without relying on PTX?"

现状:在 `tex-revision/*.tex` 里搜 SASS 只命中这一行,没有规模、没有实验、没有例子、没有可用性声明;另外两处提到 NVBit 的地方,一处是评估里拿它当插桩基线比开销(第 473 行),一处是相关工作(`tex-revision/discussion.tex` 第 17 行)。仓库自己的进展记录 `asplos-27-rebuttal/revision-plan.md` 在标题为 "Active follow-up — 2026-09-07 UTC" 的一节第 252--258 行记的路径是:clang 编出 BPF ELF,经 PREVAIL 与 SIMT 验证,再由 eBPF 转 NVPTX,用 CUDA 12.9 的 ptxas 编到 sm_120,通过 CUDA Driver API 装载并启动。这条路径与稿子那句里的 NVBit 插桩不是同一条。

### G.5 配套修改说明文档

原句,`resubmission-changes.tex` 第 33 行:"The evaluation was restructured from 3 RQs to 4 RQs. Single-tenant (RQ1) and multi-tenant (now RQ3) retain the same experiments. Agent-driven exploration (RQ2) is entirely new. The programmability and overhead section (now RQ4) retains the existing NVBit comparison, device-side microbenchmarks, and ..." 同一份文档还写了一个新增的 SIMT 验证器正确性实验,18 个 GPU 程序、5 个不安全用例被正确拒绝。

现状:`tex-revision/eval.tex` 第 9--11 行只定义了两个研究问题,"RQ1 (Policy Expressibility and Benefits)" 与 "RQ2 (Mechanism Cost)",小节标题也只有第 41 行和第 452 行两个。在 `tex-revision/*.tex` 里搜 "correctly rejected"、"unsafe cases" 无命中;评估里唯一的 18 是第 87 行 50 起安全事件里的 "18 performance regressions"。273 毫秒那个数还在,位置是第 485 行。

已查实的三处不符,原文出处都在 `resubmission-changes.tex`:第 21 行 "This paper was previously submitted to OSDI'26 (Spring cycle) and rejected";第 16 行给的标题 "Safe and Programmable GPU Resource Management with eBPF",与稿子实际标题相比少了 OS-Level;\section{Evaluation Reorganization} 一节写 "The evaluation was restructured from 3 RQs to 4 RQs",并写 "a new SIMT verifier correctness evaluation (18 GPU programs tested, 5 unsafe cases correctly rejected)",而现稿的 `tex-revision/eval.tex` 只列 RQ1 和 RQ2,全文没有那个验证器实验。`Makefile` 第 39 行的 `all: $(PDF) $(RESUB_PDF)` 说明它仍在当前构建里。仍未确定的只有一件事:这次投稿要不要交这份文档,这是你的决定。

