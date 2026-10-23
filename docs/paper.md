# 配套论文

题目：**基于开源 ECOS 工具链的开源脑启发处理器全流程设计与验证**。

作者：胡健，中国科学院计算技术研究所；课程指导老师：沈海华，中国科学院大学计算机科学与技术学院。

课程背景：本工作是中国科学院大学计算机技术专业硕士专业研讨课《集成电路设计与验证》（2026 年秋季，沈海华老师）的课程大作业。课程得到 ECOS 开源 EDA 研究团队支持，谨致谢意。英文说明为 *UCAS MEng Computer Technology seminar course materials: Integrated Circuit Design and Verification*。完整课程标识及支持关系见 [仓库首页](../README.md#课程背景与致谢)。

论文围绕综合控制语义与高扇出驱动、密度/拥塞与物理可布线性、两缓冲器ECO和十三角时序复查展开，并分别讨论未闭合SRAM扩展。本文仓库提供对应源码、流程配置和结果数据，两个处理器上游必须同时引用：

1. https://github.com/ByeBeihai/Polaris
2. https://gitee.com/OpenBPU/OpenBPU2

main冻结通过范围，sram-ip记录尚未闭合的存储与CTS工作。课程文稿保存在原课程工程；其中第三方参考图未随本代码仓库重新分发或重新许可。本页及公开结果摘要可用于理解论文与代码的对应关系。
