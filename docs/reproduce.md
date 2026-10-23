> 当前为SRAM工作分支。下面的无缓存物理闭合配方属于main基线；本分支输入和CTS继续方法必须先读 [sram.md](sram.md)。

# 从输入到最终产物

## 固定输入与工具

默认 `rtl/Polaris.v` 是通过本实验程序检查、用于无缓存实现的实际输入。`processor/` 保存对应源快照，包含上游已有修改；`scripts/build_rtl.sh` 重新生成至 `generated/`，不会覆盖冻结输入。重新生成可能改变命名/注释，应重做行为检查。

历史工具：ECOS installer `v0.1.0-nightly.20261012.3`；ECC CLI 0.1.0a12，ecc_tools 0.1.0a13，DREAMPlace 0.1.0a7，Sizer 0.1.0-alpha，KLayout 0.30.2；OSS CAD Suite 20260827 / Yosys 0.68+132。请从官方获取，保持 ECC 与 PDK 配套：

- https://cnb.cool/ecoslab/ecos-installer/-/releases/tag/v0.1.0-nightly.20261012.3
- https://github.com/openecos-projects/icsprout55-pdk
- https://github.com/YosysHQ/oss-cad-suite-build

`configure.py` 要求实际 bundle、OSS CAD 和图层映射路径。优先使用 bundle 的映射；若该 nightly 缺失，请从官方 PDK 获取 `icsprout55.layermap` 并传 `--layermap`，见 Installer Issue35。环境配置写入被忽略的 `local/`，不会写死某台服务器。

## 综合与物理步骤

1. `bash sim/run.sh` 检查三种总线等待下真实存储签名；其他验证范围见 validation.md。
2. `flow/patch_yosys.py` 在明确指定的脚本上安装可选控制，备份原文件；默认行为保留。run.py 对本实验启用分层映射、避免重复通用 ABC、跳过已复现错误的 onehot，并选择 DELAY 0。
3. `flow/configure.py` 生成 `ecc.toml`、同一 50MHz SDC、RTL副本及环境配置。先运行独立 synthesis。
4. 检查映射网表非空、无未映射模块，并完成门级行为对照后，使用 `flow/handoff.py --source runs/synthesis --stage Synthesis_yosys --out local/physical --source-project local/cacheless` 创建映射网表项目。
5. `flow/run.py --project local/physical --workspace runs/physical --from preFloorplan --to drc`。核心利用率/目标密度均0.3，拥塞优化开启。步骤返回成功后仍须检查 DRC/LVS 数值。
6. 仅当 DRC/LVS 均0，交接 DRC 网表、DEF、golden 和原SDC到独立签核项目：`flow/handoff.py --source runs/physical --stage drc_ecc --out local/signoff --source-project local/physical --require-clean`；随后 `flow/run.py --project local/signoff --workspace runs/signoff --from postRouteLec --to Harden`。
7. 逐角检查 setup/hold WNS、TNS与违例数，检查当前 LEC 输入身份；另查看扇出/转换时间等电气统计。输出存在或阶段 Success 不代表质量通过。

SDC、LEF、LIB、DEF、SPEF 都有不同职责；不能把几何短路用网表等价证明放行。最终 GDS 是课程工具流程输出，不是晶圆厂制造签核。

## 历史两缓冲器 ECO

历史密度修正版尚有 MAX_125/Cworst 一条 setup 违例。末端 hold43545/hold43546：DLY4X2H7R → BUFX4H7R，同功能A、A/Y引脚、同高且更窄。`flow/eco.py` 接受明确的网表、DEF、SDC、golden、Liberty、LEF及输出目录，核对单元后替换并清除普通信号旧布线，保留电源特殊布线。

此 ECO 是**检查点相关**的技术配方，不能将实例名盲目用于任意重跑。脚本要求精确找到每个旧实例，失败即停止。重新布线、DRC/LVS、LEC、RCX、十三角 setup/hold 均必须重做；历史最差hold仅5ps。

## 原生工作区

```text
origin/                         当前输入与SDC
config/                         各工具JSON
home/flow.json                  原生步骤状态
place_dreamplace/output/         布局网表/DEF
CTS_ecc/output/                  时钟网络
timing_optimization_sizer/output/
route_ecc/output/                布线网表/DEF
drc_ecc/output/                  物理检查点
postRouteLec_kepler_formal/output/
RCX_ecc/output/                  SPEF
sta_ecc/feature/<PVT>/<RC>/       qor_summary / timing_paths
Harden_ecc/output/               GDS / LEF / LIB / PNG
```

实验实际使用分段工作区以保留失败证据和明确门禁。原机器约1.5TiB RAM；无缓存十三角STA峰值约208GiB，SRAM规模更大。小内存WSL上重跑大型步骤可能严重交换，不给固定耗时承诺。
