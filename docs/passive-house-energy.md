# Passive house-energy and battery-full indicators

These additions use data already present in the coordinator. They make no Modbus requests and issue no inverter commands. Existing entities, daily calculations, PredBat helpers and controls are unchanged.

## Battery Full (SoC)

On means reported SoC equals 100%; off means a valid lower percentage. Missing, non-finite or out-of-range data is unavailable. This deliberately does not interpret battery status flags as BMS charge completion or completion of balancing.

## Today's House Energy

Calculation: daily grid import − grid export + PV − battery charge + battery discharge, in kWh. Reuses existing daily entities, including their AC-PV contribution exactly once. Those five daily source entities must remain enabled and have valid same-day baselines. The new sensor waits while baselines are missing or dates disagree at startup/midnight; a counter below its baseline makes it unavailable rather than treating a reset as zero consumption.

It inherits source rounding, baseline timing, AC-PV integration and restore limitations. A first installation partway through a day does not recover the earlier hours. Source dates use the existing integration's date handling; an HA/host timezone mismatch can keep this estimate unavailable. No existing daily logic has been changed.

## House Energy Since Tracking

Starts at zero, using counter deltas from the start of tracking; it is not a historical lifetime total. All five counter timestamps must advance before a new counter balance is accepted. Positive AC-PV power is integrated using the previous successful sample for intervals up to 60 seconds. Negative AC power contributes zero.

The accumulated value and counter snapshot restore after restart. Counter deltas can recover during outages, but AC-PV generation during downtime cannot be reconstructed. Gaps longer than 60 seconds are skipped and `ac_energy_gap` records that history is incomplete. This flag also becomes true after restoration. If any counter decreases, all counter baselines are rebased and `counter_resets` increments; energy in that interval is unknowable and omitted.

Both energy entities are estimates: asynchronous readings, counter resolution and energy-conversion losses can cause differences from integration of house-load power. Small decreases (including a small negative initial value) are possible, so state class is `total`, not `total_increasing`. Do not use these as billing measurements.

## Existing setup and rollout

Keep the existing PredBat house-energy integration helper and daily utility meter. No configuration is migrated, no automation consumes these new entities, and installing this release does not migrate PredBat to these sensors. Compare recorded values over complete days before separately deciding whether to change any consumer. The battery indicator does not control charging, Hold/Freeze, EV charging, export or Demand/ECO.

Tests exercise the real HA sensor classes with an in-memory coordinator: counter balance/reset, partial refresh, invalid inputs, AC-PV accounting/gaps, restore precision, midnight baselines and SoC boundaries. They do not connect to an inverter or certify live operation.
