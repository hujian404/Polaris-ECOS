# 结果与验证边界

冻结结果来自实际源综合与完整物理实现，后续两单元ECO复用完成的综合/布局/CTS检查点，新执行4个物理和5个签核步骤。`results/cacheless/` 保存摘要和原始逐角QoR；不是一次为发布重新运行的全流程。

- 修订 RTL/映射网表在0、3、7等待下均完成签名7；另有16组依赖ADDI×2等待×RTL/门级，共64次对照。
- 密度修正版实际DRC网表同样通过3组程序与64次ADDI；最终ECO的新增证据是布线后LEC、零DRC/LVS及全部13角setup/hold，不把旧网表程序测试身份混作新ECO单独仿真。
- 50MHz、setup不确定度0.3ns、hold不确定度0.1ns，输入输出延迟0，输出负载0.001pF，最大扇出32。最终最差setup0.256ns、hold0.005ns；13角setup/hold违例计数及TNS均0。
- 原生QoR的design_statistics含1项fanout统计，不能声称所有电气规则已清零。DRC/LVS计数0与STA电气统计的口径不同。
- 默认活动功耗46.0981mW不是SNN应用实测功耗。未完成完整ISA/异常/浮点/类脑扩展验证。工具配套DRC/LVS不是晶圆厂签核。

main默认RTL无外部SRAM宏依赖；sram-ip含真实宏集成，CTS未闭合。不要在两个分支间直接作等功能PPA比较。
