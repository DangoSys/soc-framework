package sims.firesim

import org.chipsalliance.cde.config.Config
import freechips.rocketchip.devices.tilelink.BootROMLocated
import freechips.rocketchip.util.SystemFileName

class WithBootROM extends Config((site, here, up) => {
  case BootROMLocated(x) =>
    up(BootROMLocated(x)).map(_.copy(
      contentFileName = SystemFileName("src/main/resources/bootrom/bare/bootrom.rv64.img")
    ))
})
