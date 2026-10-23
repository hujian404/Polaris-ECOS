/* Course experiment adapter by Jian Hu, 2026-10-19.
 * The original TopMain/Settings and processor implementations are unchanged.
 * This is a distinct cacheless RV64 configuration, not the original cache-rich SoC.
 * Generated memories remain behavioral RTL for standard-cell synthesis.
 */
package top

import chisel3.stage.{ChiselGeneratorAnnotation, ChiselStage}
import PolarisCore.PolarisCoreConfig
import system.Polaris

object ECOSMain extends App {
  val overrides = Map[String, AnyVal](
    "HasL2cache" -> false,
    "HasPrefetch" -> false,
    "HasIcache" -> false,
    "HasDcache" -> false,
    "HasITLB" -> false,
    "HasDTLB" -> false,
    "IsRV32" -> false,
    "FPGAPlatform" -> true,
    "EnableILA" -> true,
    "EnableDebug" -> false
  )
  Settings.settings = DefaultSettings() ++ PynqSettings() ++ InOrderSettings() ++ overrides
  println("ECOS course experiment: RV64 cacheless, full Polaris IO, 2-way issue/SIMD/SNN")
  Settings.settings.toList.sortBy(_._1).foreach(println)
  (new ChiselStage).execute(args, Seq(
    ChiselGeneratorAnnotation(() => new Polaris()(PolarisCoreConfig()))
  ))
}
