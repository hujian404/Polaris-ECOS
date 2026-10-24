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

## 后续受控试验

H7CR X8/X12/X16/X20替换原H7CL集合后，原生CTS仍为 `Incomplete`，阶段耗时26分01秒；九宏域finished，589378个普通汇点失败，深度1至7均在严格根边界闭合后无候选。此轮不是外部超时，没有进入布线。结果已回存并补充到Issue357。

源码 `SynthesisState.cc` 使用最小候选缓冲器实现汇点负载分组的拆分。新增独立对照保留原四种H7CL缓冲器，再加入X2/X4，已核验七个Liberty视图、LEF及实际生成配置。该对照已原生返回 `Incomplete`（28分20秒），九宏域finished，普通域在深度1至7均因根边界闭合后无候选失败；分段前沿增加至228262项，没有时钟树提交，也未进入布线。此轮不是外部超时。它只扩大候选集合，不放宽约束。复现时在独立项目的 `[params.cts]` 中使用：

```toml
buffer_type = ["BUFX2H7L", "BUFX4H7L", "BUFX8H7L", "BUFX12H7L", "BUFX16H7L", "BUFX20H7L"]
```

所查源码明确不将 `cap_steps` / `slew_steps` 暴露为外部配置，不能将它们写入JSON后当成生效参数；采样或筛选逻辑的进一步修改须有可验证的源码构建和独立验证。

## 根边界诊断补丁

重复对照均在同一根边界闭合位置失败。已整理 [仅增加诊断的补丁](../patches/cts-root-boundary-diagnostics.patch)，针对所查源码中的 `TopologyPruning.cc`，在候选被拒绝后打印输入/闭合/拒绝候选数，以及首个被拒绝项的补偿有效性、负载桶和转换时间桶信息。首个拒绝样本不能代表所有候选的原因。补丁不改变判据、前沿或约束；它是诊断建议，不是CTS修复。

该补丁已对记录的上游源码完成 `git apply --check`，**尚未编译，也未在原生ECC中运行**。原始源码快照树为 `321f878e94de68392a95a16878ee0ff8005eeb43`；套用其他版本前需重新检查，并按上游构建流程生成独立工具后验证。源码上下文来自ECC Tools/iEDA，保留其MulanPSL-2.0许可。

另核对了ECOS Installer的nightly.20261023发布清单，其ECC提交与本实验安装包相同；更新了Studio、Sizer和PDK，不足以据此认定CTS已有修复。当前暂无正在运行的SRAM物理任务。
