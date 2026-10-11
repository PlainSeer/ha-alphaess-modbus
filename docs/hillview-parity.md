# Hillview comparison — 29 September 2026

## Evidence and boundaries

GitHub MCP comparison found PlainSeer/main and senalse/main identical at
`3b944d6bbba8cae6ccc6f58ca99f2ec8a6e46563`; manifest version is 1.14.0.
The upstream PR search returned no results. This is not proof that no unindexed
work exists. HACS reports senalse v1.14.0 installed and available; running file
contents were not retrieved. This work does not deploy or validate live behavior.

Sources inspected:

- https://projects.hillviewlodge.ie/alphaess/
- https://projects.hillviewlodge.ie/_alphaess/integration_alpha_ess.txt
- https://projects.hillviewlodge.ie/_alphaess/integration_alpha_ess.yaml
- Fork sensor.py, binary_sensor.py, const.py, coordinator.py, switch.py,
  __init__.py, config_flow.py and upstream commit 656ca47.
- HA filter implementation: https://github.com/home-assistant/core/blob/dev/homeassistant/components/filter/sensor.py

Downloaded YAML identifies version 11.3 (2026-08-21); SHA256:
`82206b2cc34a760c62666ba44f183aaf7df30d3ace2bfaa335c8cc38a8d0fe2d`.

## Concrete gaps identified before implementation

| Feature | Existing behavior / gap | Treatment |
| --- | --- | --- |
| Filtered PV / house load | Fork has raw calculated sensors only. Hillview lowpass uses window 1, time constant 5. | Add separate passive entities using 0.8 previous + 0.2 new on source changes. Keep existing raw calculations. |
| Excess power | No exposed calculated entity. Hillview subtracts filtered house from filtered PV and clamps at zero. | Add passive entity, never wire into control. |
| House-load semantics | Hillview uses filtered PV and retains previous house value for nonpositive results. Fork uses raw PV and clamps at zero (except work mode 2). | Preserve fork semantics and existing consumers; new house filter smooths the existing raw calculation. This is intentionally not exact Hillview behavior. |
| Battery full | Hillview checks raw status 1 at 0x0103; fork formats 1 as Discharging. | Updated after Axel Koegler’s clarification: these flags describe charge/discharge permission. Battery Full now checks existing raw status 1, replacing the SoC-only condition while retaining its registry identity. Existing status text and all register access remain unchanged. |
| Total house load | Grid import - export - battery charge + discharge + DC PV + integrated AC PV. Fork lacks lifetime integrated AC PV. | Remaining gap: persistent AC-PV integration, restore and counter-reset handling must precede this entity. Omitting AC PV would undercount. |
| Today's house load | Fork already exposes five relevant daily totals, with AC PV included in today_pv_generation. | Remaining gap: combine those sources without double-counting AC PV; test midnight ordering, restart and missing-source behavior. |
| PV energy registers | Current Hillview YAML does not contain 0x08D0/0x08D2 or the previously claimed PV Inverter/System Total Energy entities. | Do not add based on the prior conversation. Verify manufacturer definitions/model support first. |
| Optional read isolation | Coordinator groups adjacent numeric registers and counts failed blocks toward aborting a refresh. Registry-disabled entities are still polled. | Any future optional reads need genuine opt-in polling and separate failure isolation; enabled_by_default=False alone is insufficient. |
| PV offset/calibration | Hillview provides helper and derived calibrated total. | Optional later addition; retain existing energy sources. |
| Peak shaving | Separate optional implementation, off by default, following later approval. | Uses existing dispatch API; see [behaviour and intentional differences](peak-shaving.md). Not part of the original passive tranche. |
| Force Import/Export | Fork uses a grid-error servo with gain 0.3, 80 W deadband, 60 s refresh. Commit 656ca47 explains the prior oscillation from battery-derived house-load feedback. | Retain. Copying Hillview's filtered load feedback would replace working control logic, not merely add sensors. |

## Hold monitoring comparison

Hillview YAML lines 4280–4349 trigger after battery power is strictly between
-50 and +50 W for 10 seconds. One of four force helpers must be on and its Hold
helper off. Force Export additionally requires integer SoC < integer export
cutoff + 2. It triggers the full dispatch-reset automation.

Fork switch.py `_start_battery_power_watcher` starts with each force operation,
checks abs(power) <= 50 on coordinator notifications, and stops that switch once
10 seconds have elapsed unless Hold is on. It does not check export SoC.
Missing battery power returns without clearing the elapsed-window start; cached
readings and update cadence also mean this is not proof of ten seconds of fresh
measurements. Hold toggling while power remains low can be re-evaluated on later
notifications, unlike Hillview's numeric-state threshold-entry trigger.

The export SoC guard is a concrete control difference: a balanced PV/load moment
can produce low battery power above cutoff. This is a source-supported mechanism,
not evidence that it happened on the user's inverter. A follow-up should test
above/at/below cutoff, zero-power starts, missing/stale readings, Hold toggles,
Force Import pauses and timer expiry before changing any dispatch-reset behavior.
No Hold/control change is authorized by this passive tranche.

## Data/control flow and compatibility

New sensors read existing calculated values from coordinator data. They publish
only their own states. Existing switches compute from raw coordinator registers;
they do not read the new entities. No new Modbus requests, writes, timers or
services are introduced. Domain, config-entry schema, existing unique IDs,
register maps and existing PredBat-facing entities remain unchanged.

Therefore this tranche adds no command path affecting battery-to-house,
PV-to-battery, grid charging, export/discharge, Hold/Freeze, Hold for Car,
EV charging or Demand/ECO. This is a repository dependency conclusion, not a live
regression test or an audit of external automations. No deployment was performed.

The new filters reset on unavailable/nonfinite input or reload and initialize
from the next valid value. They follow source-value changes, not every unrelated
coordinator notification. Repeated reads of native_value do not advance them.
They do not restore recorder history. Excess power is an estimate, not an export
command or an inverter capacity guarantee.

## First tranche validation

12 entity tests pass with Python 3.12.14, Home Assistant 2024.12.5 and pymodbus
3.7.4. These use real HA entity classes with an in-memory coordinator; they do
not start a full HA instance or connect to an inverter. Coverage includes source
changes, repeated callbacks, listener ordering, AC PV, source loss/recovery,
coordinator failure, nonfinite data, work mode 2 and unique IDs/setup.
The same test command is included in the PR workflow. This is not certification
against the user's current HA runtime. Existing HACS/hassfest workflows remain.

Run: `python -m pytest tests/test_filtered_power.py -q` after installing the pinned
dependencies in `.github/workflows/test.yml`. No release/version bump is included;
the branch is for review, not deployment. Revert the sensor commit to remove all
three additions without changing any existing control implementation.
