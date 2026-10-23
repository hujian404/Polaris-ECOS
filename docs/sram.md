# 真实 SRAM IP 集成：未闭合工作分支

本分支是可继续开发的缓存配置。**已完成逻辑集成、有限门级程序检查和布局；CTS 尚未闭合，没有本配置的最终 GDS。** `results/cacheless/` 是 main 的对照资料，不是本分支通过结果。

## 接口与工艺视图

| 上游接口 | 实现 | 数量/要点 |
|---|---|---|
| MEM_ext，128×74，1RW | ICS55 128×74 宏 | 4个，低有效 CEB/GWEB |
| MEM_2_ext，512×76，1RW | ICS55 512×76 宏 | 1个，每19位写掩码 |
| MEM_3_ext，4096×256，1RW | 4路 ICS55 4096×64 | 4个宏，每64位写掩码 |
| MEM_0_ext/MEM_1_ext，128×84/256×256 | 可综合软1R1W | 独立读写端口，不能用1RW宏直接替代 |

三个宏包名称为 `ics55_ecos_sram_128x74_m4`、`ics55_ecos_sram_512x76_m4`、`ics55_ecos_sram_4096x64_m4`，从 [ECOS Factory](https://factory.openecos.com/ip/sram) / [官方 SRAM 项目](https://github.com/openecos-projects/ics55_ecos_sram) 获取，放在本机 `ip/` 下。库文件、官方模型与 LEF 不随本仓库重新分发。当前选择包缺少晶体管级 GDS；即使 CTS 闭合，也必须另行解决宏版图视图才能主张完整宏版图交付。

配置将 H7CR/H7CL 标准单元与三类宏共同纳入逻辑/物理库，五组PVT覆盖十三个RC/PVT分析组合；模板见 `flow/sram-corners.toml.in`。`rtl/Polaris.v` 是实际缓存RTL的纯AXI端口规范化副本，`processor/` 中 ECOSMain 仍是无缓存生成入口，不能用它覆盖本分支冻结RTL。

## 使用

```sh
git switch sram-ip
python3 scripts/check_release.py
python3 sim/run_sram.py --sram-root /opt/ics55-sram --jobs 8
python3 flow/configure.py --bundle /opt/ecos-nightly-linux-x86_64 \
  --oss-cad /opt/oss-cad-suite --sram-root /opt/ics55-sram --out local/sram
```

Icarus Verilog用于三类宏接口随机检查；系统程序需要支持 `--no-timing` 的 Verilator 5。可以用 `--verilator /opt/oss-cad-suite/bin/verilator` 指定路径，`--only macros/mmio/memory` 单独运行。MMIO测试签名7；缓存存储/读取后相加测试签名12；各测试施加0/3/7等待。历史RTL及映射网表共六组系统检查通过，宏接口检查分别3635/4421/11550项。有限程序不覆盖完整缓存一致性或ISA。

原综合的2.568GB文本写gzip时发生计数宽度边界问题，不能把空gzip当成可用输出。Issue350附最小复现，`reproducers/gzip-overflow.cpp` 可独立检查。实验保留原始失败状态，从实际非空映射golden通过Yosys `rename -hide` 生成显式派生检查点；统计、端口、连接与宏数核对后再做有限门级验证。压缩后约63.5MB仍超过本仓库单文件策略，未进入Git。原始golden到派生输入的身份见 `results/sram/summary.json`；恢复输入不等于把原生综合流程标为Success。

## CTS 诊断与继续方向

映射规模2828964单元、面积约9.098mm²；低密度拥塞布局完成。原九宏聚类分支负载约0.407411pF，高于默认0.15pF；核对候选强驱动单元的全角上限后试验0.45pF预算。九宏缩小用例的优化偏斜0.057312ns低于0.08ns，但不是完整处理器CTS成功证据。

完整设计中589378个普通时钟汇点仍出现 `no_strict_boundary_feasible_solution_any_depth`。分支缓冲器、零根输入转换时间、强单元与解析模式均未取得通过。7µm规划模式关闭对应边界原语模式后，在特征化结束后无新增输出，外部12小时限制终止进程；保存原生Ongoing并单独记录外部终止，未伪造完成状态。完整问题与观察见 [ECC Issue357](https://github.com/openecos-projects/ecc/issues/357)。

九宏最小物理复现无需发布PDK：

```sh
python3 reproducers/materialize_sram_clock.py --pdk /opt/ecos/pdk \
  --sram /opt/ics55-sram --layermap /opt/ics55.layermap --out local/nine-macro
```

该用例保留真实宏位置和时钟负载，只用于工具诊断，不保留处理器数据通路。生成项目可用原生ECC运行CTS；继续工作应首先定位根边界候选与特征规划、数据库高扇出导入开销。通过CTS后仍须布线、DRC/LVS、布线后LEC、寄生提取和十三角STA；目前没有可发布的SRAM签核结论。

发布封装检查：接口随机检查在公开目录重新通过，带宏配置的原生 `ecc check` 通过；RTL系统测试与有限门级结果为先前实际运行证据，本次发布没有重跑大规模映射和物理流程。
