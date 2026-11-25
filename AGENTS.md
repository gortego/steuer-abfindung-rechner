# Agent skills / working rules

This is the skills file for anyone modifying the Steuer-Abfindung-Rechner.
Read `REQUIREMENTS.md` first; it contains the full product requirement list.

## Quick orientation

| File | Role |
| --- | --- |
| `index.html` | Single-file app; embedded `CONFIG`, `TABLES`, UI, CSS and JS. |
| `config.ini` | Build-time source of truth. Do not edit embedded `CONFIG` directly. |
| `README.md` | English user/developer documentation. |
| `REQUIREMENTS.md` | Complete product requirements. |
| `tabelle/*.pdf` | Tax table sources for builds/verification only. |
| `tools/generate_config.py` | Embeds `config.ini` into `index.html`. |
| `tools/generate_tables.py` | Extracts PDF tables into `index.html`. |
| `tools/verify_calculation.py` | Verifies embedded tables against the PDFs. |

## Golden rules

1. Keep the UI fully German (apart from the requested `by gortego` credit) and
   the documentation fully English.
2. Keep `index.html` dependency-free at runtime.
3. Change configuration in `config.ini`, then run `tools/generate_config.py`.
4. Gross sliders stay at `150000` and Abfindung sliders at `500000`; number
   fields accept larger values. Chart axes zoom through
   `CONFIG.limits.gross.zoom_steps` up to `number_max`; keep the guard requiring
   `gross.slider_max == charts.abfWork.x_max == charts.netBrutto.axis_max`.
5. Do not reintroduce `Bedienung`, `Zurücksetzen`, `Berechnen` or
   `heatMetric`/`heat_metric`.
6. Use **Partner #1** / **Partner #2** everywhere; never “Mann”/“Frau”.
7. Work locally only; do not commit or push unless explicitly asked.

## Build and verification

After changing `config.ini`:

```powershell
py -3 tools/generate_config.py
py -3 tools/generate_tables.py
py -3 tools/verify_calculation.py
```

After changing JS/CSS, open a cache-busted URL in the browser, for example
`http://127.0.0.1:8765/index.html?v=52`, and check:

- no console errors,
- no `NaN` or `Infinity`,
- expected number of SVGs,
- theme toggle works and is persisted,
- **speichern** saves inputs plus theme,
- heatmap/3D scales show EUR and can dip and rise, with no `100 %` cap,
- the compact-curve point label is red for “weniger als ohne Gehalt”, green
  otherwise.

## Change checklist by area

### Heatmap

- Score is the best absolute household net in EUR, including Kindergeld and
  Abfindung; the scale label is `Bestes Netto/Jahr`.
- Nettoquote = score / (gross Partner #1 + gross Partner #2 + Abfindungen),
  with Kindergeld included in the numerator. It is `100 %` only when nothing is
  deducted and no child benefit is added; the requested example is `72,51 %`.
- A separate `baselineRatio` = score / best net at Partner #1 gross `0` is
  labelled `Quote vs. ohne Gehalt`; it dips below and rises above `100 %` like
  household net.
- Scale labels use `money()`; there is no `100 %` clamp.
- Hatching/border/winner colours come from the active palette.
- Crosshair label shows household net (including Kindergeld), the live
  Nettoquote and the baseline comparison.
- The four compact-curve sliders sit in one row between the 2D plot and the flat
  heatmap; the 3D surface has its own four-slider row.
- Abfindung slider movement changes fills and EUR scale labels.
- There is no Fünftelregelung checkbox: every cell evaluates all four cases
  (Einzel/Zusammen × mit/ohne Fünftelregelung) and uses the best one.
- `computeHeatmapData()` is the single source for both the flat map and the
  3D surface; `renderHeatmap()` passes the same data object to both renderers.
- 3D surface marks the best cell in green and the current input in white and
  has its own four linked sliders (both gross salaries, both Abfindungen).

### Charts

- AbfWork has four curves (Einzel/Zusammen × mit/ohne Fünftelregelung; mit is
  solid, ohne is dash-dot) and two dashed baselines (best treatment per mode).
- Break-even and worst-case markers remain visible; the worst case has a vertical
  dotted marker and a horizontal red dashed net-level line. A bracket shows the
  EUR gap. Note lines are separate for break-even, worst case and gap; the
  `Netto aus der Abfindung` line shows best net with the entered Abfindungen
  minus best net at the same salaries without Abfindungen (`0 €` when none are
  entered). The only prominent takeaway compares the current net with "ohne
  Gehalt" (red below break-even, green above). No `45000` example and no separate
  "Ohne Gehalt" line.
- Red area is clipped at break-even.
- Black dashed guides follow the current gross values.
- Partner #2 gross slider changes the current point and recalculates curves.
- Marginal-rate chart marks the start after the Grundfreibetrag, zone changes
  (~`24 %`, `42 %`) and `PARAMS[year].top_rate` (`45 %` in 2026) with dashed
  lines; X axis reaches `600000` zvE. Y-axis rates use `G`/`S` prefixes and are
  collision-shifted; short X-axis zvE amounts use three staggered rotated rows.
  Dark dashed guides are labelled `Aktuell` for both tariffs.
- Compact curve is titled `Absolutes Netto`; its Y axis is labelled
  `Bestes Netto/Jahr`.
- End-of-page card explains the Nettoquote formula with the fixed
  `50000 / 60000 / 200000` example; the old `72,51 %` example is gone.
- Flat heatmap draws break-even (purple dashed) and worst-case (red dotted)
  lines from the same per-row `rows` values; the legend names both.
- 3D surface draws the same two ridges plus a violet dashed cross-section for
  the current Partner #2 gross across all Partner #1 gross values.
- Gross and Abfindung number fields have `number_step = 1000`.

### Persistence

- Inputs key: `steuer-abfindung-rechner.defaults.v1`.
- Theme key: `steuer-abfindung-rechner.theme`.
- `collectDefaultsFromInputs()` must include `theme`.
- `initialTheme()` prefers the theme from saved defaults, then the theme key,
  then `CONFIG.general.theme`.
- Saved PKV defaults are per partner (`pkv_kv1`, `pkv_kv2`, ...).

### Theme

- Default theme is dark, from `CONFIG.general.theme`.
- Apply theme before `applyConfigToInputs()` in `init()`.
- Redraw charts after toggling so SVG colours follow `COLORS`.
- Bar-total labels use `COLORS.guide_text` with a `COLORS.halo` stroke; never
  hard-code `#17202a` in SVG text.
- Print styles must force a light, readable output.

## Known gotchas

- `tools/generate_config.py` must not turn numeric `0`/`1` into booleans.
- `loadSavedDefaults()` only accepts string/number/boolean values.
- Year change resets KV-Zusatz to defaults only when the year actually changes.
- `calculate()` already calls `syncChartSliders()`; the delegated chart-slider
  listener also calls it for immediate visual feedback while dragging.
- `refreshFromInputs()` deduplicates rapid events with `requestAnimationFrame`,
  so at most one full recalculation runs per frame.
- All linked ranges use `data-target`. The two top gross sliders inside
  `#inputCard` go through `handleLiveInput()`; chart sliders live outside it and
  use the delegated `#chartsCard` listener. Both call `syncLinkedSlider()`, which
  writes the linked main number input, syncs outputs and triggers recalculation.
- Every range must be initialised with `setRange()`; an unset `max` reads as
  `Number("") === 0` in `syncChartSliders()` and would pin the slider at zero.
- `updateGrossDomain()` runs inside `syncChartSliders()`; it changes only the
  chart axis max at configured nice steps with hysteresis. Sliders always use
  `gross.slider_max` / `slider_step`. `computeHeatmapData()` and
  `computeAbfWorkData()` cache their sweeps, so moving only the current gross
  marker does not recompute all cells; include any new input in the cache keys.
- Kindergeld must stay in the detailed net tables and summary, but must be
  excluded from the heatmap ratio.

## Definition of done

- Requirements updated in `REQUIREMENTS.md` if behaviour changed.
- `README.md` updated for user-visible changes.
- Config regenerated if `config.ini` changed.
- Verification scripts pass.
- Browser check passes with no errors.
