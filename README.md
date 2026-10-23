# Polaris-ECOS

基于开源 **ECOS** 工具链，对开源脑启发处理器 **OpenBPU2 / Polaris** 进行 RTL 到 GDS 实现、验证和技术复现。

> **处理器来自上游，不是本项目重新设计：**
> [ByeBeihai/Polaris](https://github.com/ByeBeihai/Polaris) ·
> [OpenBPU/OpenBPU2](https://gitee.com/OpenBPU/OpenBPU2)
>
> 本仓库保存 ASIC 实现适配、流程配置、验证程序、关键诊断和结果摘要；许可证与版权说明见 [NOTICE](NOTICE.md) 和 [LICENSE](LICENSE)。

## 课程背景与致谢

本项目是中国科学院大学计算机技术专业硕士**专业研讨课《集成电路设计与验证》**的课程大作业，在**沈海华**老师指导下，由学生**胡健**完成。

- **课程归属**：中国科学院大学 · 计算机技术 · 专业研讨课
- **开课学期**：2026 年秋季
- **课程名称**：集成电路设计与验证
- **课程完整标识**：中国科学院大学-计算机技术-专业研讨课-2026年秋-集成电路设计与验证-沈海华
- **英文说明**：UCAS MEng Computer Technology seminar course materials: Integrated Circuit Design and Verification

本课程得到 **ECOS 开源 EDA 研究团队**的支持，谨向团队致谢。本项目基于其开源工具链开展处理器全流程实现与验证，整理课程实践中的方法、结果与问题反馈，供学习与复现参考。本仓库由学生个人维护，记录课程实践成果及后续拓展。

## 分支与冻结状态

| 分支/标签 | 默认配置 | 已完成范围 |
|---|---|---|
| `main` / `v1.0.0-cacheless` | 无外部 SRAM 宏的无缓存 RV64 Polaris | 综合、布局布线、零 DRC/LVS、布线后 LEC、50 MHz 十三角 setup/hold、GDS 导出 |
| [`sram-ip`](https://github.com/hujian404/Polaris-ECOS/tree/sram-ip) | 九个硬宏和两类软 1R1W 阵列的缓存候选 | 宏接口/有限门级程序、布局；**CTS 未闭合，无该配置最终 GDS** |

`main` 冻结的是已记录的验证结果；新的工具版本、不同机器或重新运行仍须重新检查，不能继承本仓库的通过结论。`sram-ip` 作为可继续开发的工作分支，不能替代已完成基线。

## 已验证的无 SRAM 主实验

目标 50 MHz，十三个 RC/PVT 角建立/保持违例数与 TNS 均为零；最差 setup **+0.256 ns**，hold **+0.005 ns**。DRC/LVS 计数为零，布线后 LEC 为 `proven`。版图面积约 5.623 mm²。默认活动模型总功耗约 46.0981 mW；不是应用实测能效。

原生 STA 汇总同时报告一项 fanout/电气统计（见逐角 JSON 的 `design_statistics`）；本仓库的时序通过结论明确指 setup/hold，不声称全部电气检查或晶圆厂签核完成。有限程序检查不等于完整 ISA、缓存一致性或 SNN 指令验证。

![最终无缓存布局输出](results/cacheless/final-layout.png)

完整数据入口：[结果摘要](results/cacheless/summary.json)、[十三角表](results/cacheless/corners.csv)、[验证范围](docs/validation.md)。大型 GDS、SPEF 和工艺相关网表未进入 Git 历史；最终 GDS 的文件身份和边界记录于结果摘要，以便与持有该交付物的副本核对。

## 快速开始

Linux / WSL Ubuntu 22.04，Python 3.10+、Verilator、C++ 编译器；重新生成 Chisel 另需 JDK 11 和 mill 0.9.10。可直接使用已冻结的 `rtl/Polaris.v`，不依赖 Chisel 下载才能检查 RTL。

```sh
git clone https://github.com/hujian404/Polaris-ECOS.git
cd Polaris-ECOS
python3 scripts/check_release.py
bash sim/run.sh
```

获取 ECOS 指定集成包及配套 PDK 后，按 [复现说明](docs/reproduce.md) 设置本机工具路径、安装可选综合控制，生成项目配置并按阶段运行。**不要将占位路径当作已安装工具。**

```sh
python3 flow/configure.py --bundle /opt/ecos-nightly-linux-x86_64 \
  --oss-cad /opt/oss-cad-suite --out local/cacheless
python3 flow/patch_yosys.py --script /opt/ecos-nightly-linux-x86_64/ecc/_internal/chipcompiler/tools/yosys/scripts/yosys_synthesis.tcl
python3 flow/run.py --project local/cacheless --workspace runs/synthesis --from synthesis --to synthesis
```

完整复现需要重新执行功能门禁和各阶段检查；公开流程封装经过配置/结构与 RTL 功能检查，**没有为了发布再次重跑多日物理流程**。历史通过数据与新封装的验证范围分别记录。

## 工程组织

```text
processor/      实际 Chisel 源码快照、原版权和构建元数据
rtl/            当前分支冻结的 Polaris RTL
sim/            真实总线握手的程序测试
flow/           SDC、参数化项目配置/运行/交接/ECO
patches/        处理器旁路修复说明
results/        已记录的摘要、逐角指标和原生图片
reproducers/    独立工具问题复现
docs/           构建、验证边界、Issues 与维护规则
```

中后端文件关系：网表与同阶段 DEF 配套；布线后网表用于 LEC，DEF/工艺用于连接检查和寄生提取，SPEF/SDC/Liberty 共同决定最终时序。详见 [复现说明](docs/reproduce.md)。

## 社区反馈与论文

本工作提交的 ECOS 问题见 [Issues 清单](docs/issues.md)：Installer 35、ECC 347/349/350/357。处理器来源和本仓库贡献边界也在配套课程论文中区分，论文介绍见 [docs/paper.md](docs/paper.md)。

作者：胡健，hujian26e@ict.ac.cn。请保留上游来源与许可证；不要将未闭合分支描述为已完成 SRAM 芯片实现。
