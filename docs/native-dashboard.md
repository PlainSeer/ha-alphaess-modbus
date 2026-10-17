# Native AlphaESS dashboard (beta)

This is a **static Home Assistant dashboard**, not a JavaScript strategy. The file `examples/native_dashboard.json` can be pasted into Home Assistant's Raw configuration editor (JSON is valid YAML syntax).

The layout contains Overview, Controls and Diagnostics and uses only built-in `sections`, `grid`, `entities` and `markdown` cards. It maps AlphaESS Modbus's default `alphaess_inverter_*` entity IDs; if entities are renamed or disabled, adjust/remove those entries before deploying. The native dashboard does not automatically discover newly enabled entities.

**Migration:** Keep the original standard dashboard. Create a new storage dashboard, copy in the native configuration, verify that all controls and readings render, then delete only the old `custom:alphaess-modbus` strategy dashboard. Do not delete the Modbus integration. Do not remove or disable control entities. Maintenance/reset/restart buttons are deliberately excluded from the beta's Controls page to avoid accidental taps; they remain accessible on the standard dashboard.

**Scope:** Presentation only. No register mappings, Modbus polling, inverter dispatch, PredBat or EV/AlphaESS automations are changed. Test with the user's actual enabled entities before tagging as a published beta release.
