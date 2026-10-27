# AlphaESS Modbus TCP — PlainSeer fork

![AlphaESS icon](https://raw.githubusercontent.com/PlainSeer/ha-alphaess-modbus/main/custom_components/alphaess_modbus/brand/icon.png)

Local Home Assistant integration for AlphaESS inverters via Modbus TCP, without a cloud dependency.

## USE AT YOUR OWN RISK

Unofficial community-maintained software, supplied without warranty. The integration includes controls that write to your inverter. Incorrect settings can cause unexpected operation, financial loss or equipment damage. Keep a restorable backup. Passing tests does not certify hardware safety.

## About this fork

Continues Senalse's v1.14.0 integration, with passive sensors and optional controls inspired by Axel Koegler's Hillview package. Original authors retain full credit. This is not an official AlphaESS integration or full Hillview parity.

## Sensor overview

- **Current House Load Filtered / Current PV Production Filtered:** smooth the existing power calculations. These displayed values do not drive inverter controls.
- **Excess Power:** filtered PV minus filtered house load, clamped at zero; an estimate, not an export command.
- **Battery Full:** on when existing raw battery status is `1` (charging not permitted, discharging permitted), matching Hillview. Invalid, missing or unrecognised status makes it unavailable.
- **Today's House Energy:** a daily balance of import, export, PV and battery energy, including AC PV once. This estimate can decrease during the day.
- **House Energy Since Tracking:** accumulates from zero when first enabled; not lifetime consumption. Downtime can leave gaps.
- **House Load Energy Today (Accumulated):** integrates existing house-load power into kWh. Only increases within each day, resets at HA-local midnight and restores same-day totals after restart. Missing readings and downtime leave gaps.

These passive sensors use data already read by the integration, without adding register reads or writes or changing polling. They do not automatically replace existing helpers or automations. See the energy calculation notes below before using the estimates.

## Optional Peak Shaving

**Off by default and after restart.** Uses existing dispatch controls to reduce grid import towards a target when explicitly enabled. Simulation-tested, not yet tested on physical inverter hardware; it cannot guarantee a hard import cap or prevent transient export. See the [feature guide and limitations](https://github.com/PlainSeer/ha-alphaess-modbus/blob/main/docs/peak-shaving.md).

Hillview's Force Import pause/resume and Cutoff SoC Hold monitoring changes have not been adopted, and optional PV energy registers are not included.

## Default saved dashboard

**v1.20.0b1:** a saved Home Assistant dashboard with **Overview**, **Controls** and **Diagnostics**. Two-column panels stack on phones. Dashboard and view strategies are no longer used by the default dashboard.

Overview keeps the inverter centred between Solar/Grid and Battery/Load. The four-node flow uses solid tracks and smooth power-dependent dots, a grid pylon, compact units and direction labels. Tapping a value opens its entity details. Native panels show daily energy, solar strings, battery details and estimates.

![AlphaESS saved Overview — local preview with example data](https://raw.githubusercontent.com/PlainSeer/ha-alphaess-modbus/d60f174ac61c223c8e3406b492f4e60d8d88f211/docs/images/dashboard-overview.png)

<details>
<summary>Controls, Diagnostics and mobile previews</summary>

![AlphaESS Controls — local preview with example data](https://raw.githubusercontent.com/PlainSeer/ha-alphaess-modbus/d60f174ac61c223c8e3406b492f4e60d8d88f211/docs/images/dashboard-controls.png)

![AlphaESS Diagnostics — local preview with example data](https://raw.githubusercontent.com/PlainSeer/ha-alphaess-modbus/d60f174ac61c223c8e3406b492f4e60d8d88f211/docs/images/dashboard-diagnostics.png)

<img src="https://raw.githubusercontent.com/PlainSeer/ha-alphaess-modbus/d60f174ac61c223c8e3406b492f4e60d8d88f211/docs/images/dashboard-mobile.png" alt="Saved AlphaESS dashboard at 390 pixels — local preview with example data" width="390">

</details>

Images use a local preview of the production flow card and representative native panels with example readings; they are not screenshots of a connected inverter. Native card appearance follows your HA version and theme.

Update through HACS, restart HA and refresh the frontend. Setup creates **AlphaESS**, or backs up and migrates this fork's exact default strategy/recognised beta dashboard at its existing URL. Customised dashboards, YAML dashboards and unrelated dashboards are preserved. [Setup, migration and rollback](https://github.com/PlainSeer/ha-alphaess-modbus/blob/v1.20.0b1/docs/managed-dashboard.md).

## Documentation and installation

For requirements, setup, controls and limitations, see the [README](https://github.com/PlainSeer/ha-alphaess-modbus#readme), [energy calculation notes](https://github.com/PlainSeer/ha-alphaess-modbus/blob/main/docs/passive-house-energy.md) and [release history](https://github.com/PlainSeer/ha-alphaess-modbus/releases).

Version-specific changes, fixes and acknowledgements belong in the [GitHub release notes](https://github.com/PlainSeer/ha-alphaess-modbus/releases).

Existing installations should update through HACS and retain their configured integration and entities.

## Credits

Original Python integration: [Senalse](https://github.com/senalse/ha-alphaess-modbus). Original YAML package: [Axel Koegler / Hillview](https://projects.hillviewlodge.ie/alphaess/). AlphaESS artwork identifies supported hardware; it does not imply endorsement.
