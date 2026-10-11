# Local dashboard preview

Install the optional preview icons with `npm install --no-save --package-lock=false @mdi/font@7.4.47`.
Serve the repository root with a local static server and open
`/tools/dashboard-preview/`. This fixture imports the actual dashboard module,
uses invented entity data, and never connects to Home Assistant. HA supplies the
icon component in production; screenshot tooling supplies an MDI font locally.
It is a component preview, not a complete Home Assistant installation.

Use this to check both tabs, narrow layouts, dark appearance and label overflow.
Keep screenshots labelled as examples. Do not use screenshots of private live
entities in public documentation.
