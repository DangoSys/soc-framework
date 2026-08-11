package firechip.chip

import org.chipsalliance.cde.config.{Config}
import chipyard.harness.HarnessClockInstantiatorKey

class WithFireSimConfigTweaks extends Config((site, here, up) => {
  case HarnessClockInstantiatorKey => () => new FireSimClockBridgeInstantiator
})
