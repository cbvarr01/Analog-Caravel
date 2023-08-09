from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
import cocotb
from cocotb.triggers import ClockCycles


@cocotb.test()
@report_test
async def mprj_por(dut):
    caravelEnv = await test_configure(dut,timeout_cycles=3346140)
    # Power supply for POR
    caravelEnv.drive_gpio_in(18, 0)
    await caravelEnv.reset()
    await cocotb.start(power_por(caravelEnv))
    await wait_status(caravelEnv, "01")
    check_bits = caravelEnv.monitor_discontinuous_gpios([27, 26, 12, 11])
    if check_bits != "1001":
        cocotb.log.error(f"[TEST] POR test failed expected 1001 got {check_bits}")
    else: 
        cocotb.log.info(f"[TEST] phase 1 passed seen 1001 at gpios 27 26 12 11")
    await wait_status(caravelEnv, "11")
    check_bits = caravelEnv.monitor_discontinuous_gpios([27, 26, 12, 11])
    if check_bits != "0101":
        cocotb.log.error(f"[TEST] POR test failed expected 0101 got {check_bits}")
    else:
        cocotb.log.info(f"[TEST] phase 2 passed seen 0101 at gpios 27 26 12 11")


async def wait_status(caravelEnv, val_to_wait):
    while True:
        if caravelEnv.monitor_discontinuous_gpios([25, 10]) == val_to_wait:
            break
        await ClockCycles(caravelEnv.clk, 1)
    await ClockCycles(caravelEnv.clk, 3)
    


async def power_por(caravelEnv):
    await caravelEnv.wait_mgmt_gpio(1)  # wait  configuration finished
    await ClockCycles(caravelEnv.clk, 10)
    caravelEnv.drive_gpio_in(18, 1)
