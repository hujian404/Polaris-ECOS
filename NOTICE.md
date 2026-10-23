# 来源、修改与许可说明

本仓库是 **胡健（hujian404）的 ECOS 中后端实验与复现工程**，不是 OpenBPU/Polaris 上游官方发布。

必须同时引用的处理器上游：

- Polaris：[ByeBeihai/Polaris](https://github.com/ByeBeihai/Polaris)
- OpenBPU 二代：[OpenBPU/OpenBPU2](https://gitee.com/OpenBPU/OpenBPU2)

`processor/` 来自本实验实际使用的 OpenBPU2 工作快照，包含既有工作区修改和本次旁路适配；不是两个上游仓库的完整镜像或未修改 checkout。上游基线为 Gitee release 的 f7bab85。原始源码与 difftest 支持代码中的版权、许可证和免责声明保留。`processor/UPSTREAM-README.md` 是原项目介绍；其命令/图片路径属于上游布局，不替代本仓库首页。

处理器及本仓库新增流程代码按根目录 MulanPSL-2.0 条款分发，原有权利归原贡献者。新增流程、配置、测试和文档贡献 Copyright (c) 2026 胡健。第三方组件保留自身许可，不能将整个工具链、PDK 或 IP 的许可视为由本仓库重新授予。

修改范围：新增直接 Polaris 顶层的无缓存生成入口；标量旁路向量字段初始化和 MMIO 唯一来源修复；可选综合控制；低密度/拥塞布局配置；有门禁的布线后 ECO；真实 SRAM 接口适配（见 sram-ip 分支）。未将原处理器整体设计主张为本仓库作者原创。

工具来源：ECOS ECC、ECOS Studio、ECC Tools、Yosys/OSS CAD Suite。工艺来源：ICsprout55 PDK。SRAM 来源：ECOS Factory/ICS55 ECOS SRAM。工具二进制、标准单元库、SRAM 官方模型/LEF/Liberty 和内部运行环境均不随 Git 源码分发；请从原项目获取并遵守各自条款。

公开图片为本实验生成的 EDA 输出。课程报告中的第三方参考图未在此仓库另行分发；论文引用仍分别注明来源。

`flow/patch_yosys.py` 中引用的 Tcl 上下文来自 Efabless/OpenLane 派生综合脚本，Copyright 2020 Efabless Corporation，按 Apache-2.0 分发；见 `LICENSES/Apache-2.0.txt`。新增 Python 封装按 MulanPSL-2.0 分发。
