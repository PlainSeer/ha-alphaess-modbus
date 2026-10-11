# Optional Peak Shaving

Peak Shaving uses battery discharge to reduce grid import towards a chosen target. For example, 7 kW of house demand minus 1 kW of solar, with a 4 kW import target, requests approximately 2 kW from the battery. Battery availability and the inverter's limits still apply.

**Off by default, and always off after Home Assistant restarts.** Installing the feature or changing its settings while off does not start dispatch. This is an experimental, simulation-tested controller, not a hardware-validated grid limit. It cannot guarantee an import cap or prevent transient export when demand changes.

## Controls

| Entity | Purpose |
| --- | --- |
| Peak Shaving | Explicitly starts or stops this controller. |
| Peak Shaving Grid Import Limit | Desired grid import in kW; default 5, adjustable from zero to the configured AC limit. Choose a valid value before enabling if your AC limit is below 5 kW. |
| Peak Shaving Below SoC | Upper operating threshold; default 100%. At or above this level the controller pauses. This is not a charging target. |
| Peak Shaving Paused | Indicates that the enabled controller is waiting for its operating conditions. |

The existing **Discharging Cutoff SoC** supplies the lower battery boundary. The upper threshold must be greater than this lower boundary. This feature does not change either inverter register mappings or the meaning of existing controls.

The switch attributes show `reason`, `paused`, and `requested_battery_power_w`. The requested power is a command, not confirmation of measured battery output.

## Starting, stopping and other controls

Start only when you intend this feature to control battery dispatch. It refuses to start while another integration dispatch mode is active, while a previous command is pending, or without a fresh inactive inverter-dispatch reading. A stale reading may require waiting for the existing poll; an active dispatch must be stopped first.

Starting another force/dispatch mode stops Peak Shaving before the other mode begins. Dispatch Reset stops the controller as well as resetting dispatch. Turning Peak Shaving off drains any in-flight command before resetting it. It does not resume automatically after a restart.

External controllers that independently write inverter dispatch are not coordinated by this feature. Do not enable competing control loops at the same time. Existing Hold switches and the Dispatch PV Enabled preference retain their existing roles; they do not start Peak Shaving.

## Pause and recovery

- Invalid, missing or stale inputs, a failed poll, non-normal inverter mode, or reaching the lower discharge cutoff pauses control.
- Solar surplus or reaching the upper SoC threshold also pauses it; a 15-second grace period applies after an automatic resume.
- Pausing resets an outstanding dispatch once, rather than repeatedly sending reset commands.
- Automatic resume requires at least 15 seconds paused, 10 minutes of continuously observed normal inverter operation with valid inputs, no raw-PV surplus over filtered house demand, and SoC between the configured boundaries.
- A command failure turns the session off and attempts one reset. Re-enabling is manual.

While active, changed commands are at least five seconds apart, with a 50 W change threshold. Unchanged commands renew after four minutes using a five-minute inverter dispatch duration. If communication is lost and reset cannot reach the inverter, the previous command can remain until that duration expires.

## Calculations and Hillview relationship

Inspired by Axel Koegler's [Hillview AlphaESS package](https://projects.hillviewlodge.ie/alphaess/), including its Peak Shaving pause/resume approach. It uses already-polled raw power, SoC and operating-mode values, and the integration's existing dispatch/reset API. No new register addresses, mappings or polling are added. **When explicitly enabled, it does write commands through those existing controls.**

It preserves this fork's existing house-load and PV calculations, including the AC-PV contribution, and caps requested battery power at the configured AC limit. It uses private smoothing: 95% previous value plus 5% new value for each fresh power sample. Cached timer callbacks do not advance the filter; repeated fresh equal readings do. Existing displayed filtered sensors are unchanged.

This intentionally differs from a literal Hillview port. Simulations with staggered grid and battery readings required more conservative smoothing. Response is gradual and depends on polling speed; at two-second fresh samples, a step takes roughly two minutes to settle to 95%. An immediate reduction in house demand can temporarily leave too much discharge requested. This is not suitable as a fuse-protection mechanism or a guaranteed no-export limit.

Other deliberate differences include refusing takeover on enable, immediate lower-SoC/freshness checks, bounded dispatch leases, and serialized stop/start commands.

## Verification and limits

Isolated tests exercise default-off/restart behaviour, local settings, command contents, power limits, rate limiting, renewal, stale/missing data, pause/resume, write failures, in-flight stop/reset, other-mode takeover and unchanged existing-mode commands while disabled. Closed-loop simulations cover demand changes and delayed grid readings up to 20 seconds.

These simulations do not model every inverter, firmware, BMS or external controller. No connected inverter is used by the tests. Review behaviour on your installation before relying on it; automated tests are not hardware safety certification.
