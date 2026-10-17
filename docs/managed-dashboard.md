# Default AlphaESS dashboard · v1.19.3b4 beta

The integration includes the dark Overview, Controls and Diagnostics frontend. It is a working frontend, not an image: HA supplies current state and recorder history. The public screenshots use an isolated local fixture with example data.

## Install and update

1. In HACS, open AlphaESS Modbus TCP from PlainSeer's fork.
2. Enable beta versions in the download/version selection and choose **v1.19.3b4**.
3. Restart Home Assistant, then fully refresh the browser or Companion App frontend.
4. Open **AlphaESS (Beta)** in the sidebar. It is admin-only by default, as are the existing beta's permissions.

No additional custom card, HACS frontend download, YAML paste or resource copy is required in storage mode. The integration serves three local JavaScript modules with a shared content hash and registers its loader through both the frontend and Lovelace resource APIs. It does not use the temporary inline prototype module.

## What installation changes

- With no dashboard at `dashboard-alphaess-native`, setup creates AlphaESS (Beta) there using HA's Lovelace registration APIs.
- With this fork's recognised Beta configuration—exactly three panel views named overview, controls and diagnostics, each containing one `custom:alphaess-beta-live` card—setup saves a targeted rollback record, then changes it to the packaged AlphaESS strategy. Metadata and sidebar permissions stay as they were.
- An existing AlphaESS strategy dashboard automatically uses the new dark design after frontend refresh.
- Other configurations at that path, YAML dashboards, additional cards/views and unrelated dashboards are left alone. The default personal HA landing page is not changed.
- A modified Beta configuration is deliberately not auto-migrated. Add a new dashboard using the AlphaESS strategy or review the customisations before replacing it. The exact minimal strategy is shown below.

```yaml
strategy:
  type: custom:alphaess-modbus
```

The targeted prior Beta config is saved by HA's storage helper under `alphaess_modbus.dashboard_migration`; do not hand-edit internal storage files. Retain an exported dashboard config if you want a separately accessible backup.

## Layout and interaction

Overview has two wide desktop columns. Battery/system and solar readings lead into Power Flow, then Energy Today and Battery Health; compact control summaries sit alongside. Diagnostics has its own grouped page, with no repeated right-hand diagnostics column on Overview. Native HA tabs provide navigation; there is no duplicate inner tab row. At 1000 pixels the overview stacks; at 600 pixels the paired panels and control groups stack; diagnostic panels stack below 700 pixels.

Rows and tiles are keyboard accessible and open the normal HA details dialog. No custom switch or slider sends commands directly. Opening the page, changing views, refreshing, reading history or clicking a row does not call an inverter service. Changing a setting inside the HA dialog remains a real action using the existing integration. Maintenance dialogs include real restart/reset controls; opening them does not activate them.

Entity discovery uses platform, config-entry ID, device ID and stable unique IDs. Renamed entities are supported and inverter groups stay separate. Every enabled sensor/binary sensor appears once in Diagnostics, including fault and warning values. Controls retains enabled switches, numbers, selects, time settings and maintenance buttons. Missing or unavailable readings are shown explicitly. An incomplete daily energy estimate is flagged. PV1 and PV2 stay visible at all times; PV3 and PV4 hide while zero, missing or unavailable and return when they report power. This is a display rule, not proof that a string is physically disconnected. Battery status numeric suffixes are removed from the display only. Grid and battery paths animate in the direction implied by signed power; zero or unavailable readings stop the animation.

The eight-hour solar chart needs recorder history and refreshes at most once every five minutes while HA updates reach the card.

## Loading and troubleshooting

A refresh is required after updating. The content hash changes for all three modules when any module changes. The previous diagnostic loader is retained; its diagnostics view is a hidden subview at `alphaess-loader-diagnostics`. This beta does **not** claim to resolve the intermittent iOS Companion App loading timeout.

If another dashboard occupies the target URL, it is not overwritten. In YAML resource mode, automatic resource registration is skipped, but the frontend extra-module loading path is retained. YAML dashboards remain user-managed. A headless instance skips the frontend entirely.

The old temporary inline prototype resource is no longer referenced by the packaged dashboard. It may remain registered after migration; it does not write settings or compete with inverter controls. This release leaves unrelated resources alone.

## Rollback

Select **v1.19.3b3** in HACS, restart HA and refresh the frontend. The saved AlphaESS strategy is compatible with that version and returns to its old dashboard design. The newly created sidebar dashboard can remain; remove it through HA dashboard settings if desired. A native static dashboard must be restored from its exported config if that specific layout is wanted.

## Verification and limits

Frontend tests cover entity renaming, inverter isolation, passive updates, details-only clicks, missing readings, diagnostic coverage and loader errors. Migration tests cover protected custom dashboards and backup-before-replace behaviour. Regression tests exercise the inherited integration code; they are not a physical inverter certification. Browser QA uses example data at desktop and phone widths, not commands on a connected inverter. No Modbus register, polling, PredBat, charging, discharge/export, Hold/Freeze, Hold for Car, EV charging or Demand/ECO control implementation changes are included.
