package chipyard

import org.chipsalliance.cde.config.Config
import freechips.rocketchip.subsystem.{ExtMem, MBUS}

/**
 * Tapeout target based on the current chip-like Rocket configuration.
 *
 * Uses generic IO cells (inherited from AbstractConfig) and attaches a
 * behavioral I2C EEPROM at the physical pads in simulation.
 */
class TapeoutConfig extends Config(
  new freechips.rocketchip.subsystem.WithoutTLMonitors ++
  new WithTapeoutRocket ++
  new testchipip.soc.WithNoScratchpads ++
  new chipyard.clocking.WithNdmResetInSystemReset ++
  new WithTapeoutSingleClock(100) ++
  new chipyard.harness.WithSimTSIOverSerialTL(fast = true) ++
  new chipyard.harness.WithSimI2CEepromOnPads ++
  new WithSerialConnect ++
  new chipyard.iobinders.WithSPIIOCells ++
  new chipyard.iobinders.WithSimI2CIOCells ++
  new chipyard.config.WithUART(
    baudrate = 115200,
    address = 0x10020000,
    txEntries = 8,
    rxEntries = 8) ++
  new chipyard.config.WithNoUART ++
  new chipyard.config.WithSPI(address = 0x10031000) ++
  new chipyard.config.WithI2C(address = 0x10040000) ++
  new chipyard.config.WithGPIO(address = 0x10010000, width = 8) ++
  new chipyard.config.AbstractConfig)

/**
 * TapeoutConfig with pad-connected SPI flash and I2C EEPROM simulation models.
 * SPI flash requires +spiflash0=; the I2C EEPROM is preloaded with byte[i] = i.
 */
class TapeoutSimConfig extends Config(
  new chipyard.harness.WithSimSPIFlashOnPads ++
  new chipyard.iobinders.WithSimSPIIOCells ++
  new TapeoutConfig)

class WithTapeoutRocket extends Config(
  new freechips.rocketchip.rocket.WithL1ICacheSets(64) ++
  new freechips.rocketchip.rocket.WithL1ICacheWays(1) ++
  new freechips.rocketchip.rocket.WithL1DCacheSets(64) ++
  new freechips.rocketchip.rocket.WithL1DCacheWays(1) ++
  new freechips.rocketchip.subsystem.WithInclusiveCacheDirReg(true) ++
  new freechips.rocketchip.subsystem.WithInclusiveCacheSchedulerBypass(false) ++
  new freechips.rocketchip.subsystem.WithInclusiveCache(nWays = 8, capacityKB = 16) ++
  new freechips.rocketchip.rocket.WithNHugeCores(1)
)

class WithSerialConnect extends Config(
  new testchipip.serdes.WithSerialTLMem(size = BigInt("10000000", 16)) ++
  new testchipip.serdes.WithSerialTLPHYParams(
    testchipip.serdes.DecoupledExternalSyncSerialPhyParams(phitWidth = 4, flitWidth = 16)) ++
  new WithSerialTLBackingMemory ++
  new testchipip.soc.WithOffchipBusClient(MBUS) ++
  new testchipip.soc.WithOffchipBus
)

class WithSerialTLBackingMemory extends Config((site, here, up) => {
  case ExtMem => None
})

class WithTapeoutSingleClock(freqMHz: Int) extends Config(
  new chipyard.clocking.WithSingleClockBroadcastClockGenerator(freqMHz) ++
  new chipyard.config.WithTileFrequency(freqMHz.toDouble) ++
  new chipyard.config.WithUniformBusFrequencies(freqMHz.toDouble) ++
  new chipyard.harness.WithHarnessBinderClockFreqMHz(freqMHz.toDouble) ++
  new chipyard.harness.WithAbsoluteFreqHarnessClockInstantiator
)
