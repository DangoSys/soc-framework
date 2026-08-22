# soc-framework

Chipyard `DigitalTop` / config / IOBinder / harness layer extracted from [Chipyard](https://github.com/ucb-bar/chipyard) for DangoSys tapeout flows.

**TapeoutConfig** is the chip-like Rocket target: single 100 MHz clock, serial TileLink backing memory, and pad-level IO cells with a harness-attached I2C EEPROM model.

**TapeoutSimConfig** extends that with pad-connected SPI flash simulation (`+spiflash0=`) via `WithSimSPIFlashOnPads` and `WithSimSPIIOCells`. Use it as the pad-level VCS/Verilator sim target.

SystemVerilog pad models live in `src/main/resources/vsrc/` (`SimI2CEepromModel.sv`, `SimSPIFlashPadModel.sv`).
