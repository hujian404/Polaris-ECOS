# 公开反馈

| 问题 | 复现与影响 |
|---|---|
| [Installer35](https://github.com/openecos-projects/ecos-installer/issues/35) | 图层映射缺失但前置检查通过；配置官方映射恢复输出。 |
| [ECC347](https://github.com/openecos-projects/ecc/issues/347) | LEC收集器的预期路径与实际输入不一致；独立核对证明身份，不改写原清单。 |
| [ECC349](https://github.com/openecos-projects/ecc/issues/349) | onehot使请求握手/组合逻辑不等价；包含SAT最小复现，实验受控跳过。 |
| [ECC350](https://github.com/openecos-projects/ecc/issues/350) | 超过2GiB网表gzip写出为空及附加分析失败状态；提供整数边界复现。 |
| [ECC357](https://github.com/openecos-projects/ecc/issues/357) | SRAM时钟域严格根边界失败、解析式锚点超时、显式线长改变规划模式；独立九宏复现见sram-ip。 |

Issue由hujian404提交。提交不代表上游已经修复；实时状态请以原链接为准。
