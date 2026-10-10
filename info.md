# AlphaESS Modbus TCP — PlainSeer fork

![AlphaESS icon](https://raw.githubusercontent.com/PlainSeer/ha-alphaess-modbus/main/custom_components/alphaess_modbus/brand/icon.png)

Local Home Assistant integration for AlphaESS inverters via Modbus TCP, without a cloud dependency.

## USE AT YOUR OWN RISK

Unofficial community-maintained software, supplied without warranty. The integration retains inherited controls that write to your inverter. Incorrect settings can cause unexpected operation, financial loss or equipment damage. Keep a restorable backup. Passing tests does not certify hardware safety.

## About this fork

Continues Senalse's v1.14.0 integration, with selected passive improvements inspired by Axel Koegler's Hillview package. Original authors retain full credit. This is not an official AlphaESS integration or full Hillview parity.

## Changes added by this fork

### v1.17.1

- Battery Full: uses existing raw battery status `1`, matching Hillview (charging not permitted, discharging permitted). Corrects the former SoC-only indicator in place, preserving its entity ID. No additional register reads or control changes.

### v1.15.0

- Current House Load Filtered: smooths the existing house-load value.
- Current PV Production Filtered: smooths the existing PV-production value.
- Excess Power: filtered PV minus filtered house load, clamped at zero; an estimate, not an export command.

### v1.17.0

- House Load Energy Today (Accumulated): a separate kWh counter integrating existing house-load power. Only increases within each day and resets at HA-local midnight. Restores same-day totals after restart; missing readings and downtime leave gaps. Existing comparison sensors and PredBat helpers are retained.

### v1.16.0

- Introduced the battery-full indicator, initially based on SoC; corrected above.
- Today's House Energy: existing daily import minus export plus PV minus battery charged plus discharged; AC PV included once.
- House Energy Since Tracking: accumulates from zero when first enabled; not lifetime consumption. Downtime can leave missing AC-PV history.

No Modbus register addresses, mappings, reads, writes or polling were changed by these additions. Existing entities and controls are preserved. Keep existing PredBat house-energy helpers while comparing the estimates; nothing migrates automatically.

Hillview 11.2 import pause/resume and 11.3 Cutoff SoC Hold monitoring changes are not adopted.

## Documentation and installation

For requirements, setup, controls and limitations, see the [README](https://github.com/PlainSeer/ha-alphaess-modbus#readme), [energy calculation notes](https://github.com/PlainSeer/ha-alphaess-modbus/blob/main/docs/passive-house-energy.md) and [release history](https://github.com/PlainSeer/ha-alphaess-modbus/releases).

Existing installations should update through HACS and retain their configured integration and entities.

## Credits

Original Python integration: [Senalse](https://github.com/senalse/ha-alphaess-modbus). Original YAML package: [Axel Koegler / Hillview](https://projects.hillviewlodge.ie/alphaess/). AlphaESS artwork identifies supported hardware; it does not imply endorsement.
