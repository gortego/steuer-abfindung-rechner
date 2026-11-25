# Product requirements — Steuer-Abfindung-Rechner

This file is the complete requirement list for the project. User-facing text is
German; documentation is English.

## 1. Purpose

Provide a dependency-free HTML calculator that compares, for two partners:

- income tax, Soli and church tax,
- GKV/PKV contributions,
- child benefit and child allowance,
- Abfindung (severance) treatments,
- individual vs. joint assessment,
- annual/monthly net income and net-to-gross ratios.

## 2. Delivery and runtime

- The complete application is a single `index.html`.
- No external runtime dependency, no server and no network request at runtime.
- Python scripts are build-time/verification tools only.
- `tabelle/*.pdf` are build/verification inputs only; they are not needed to
  open `index.html`.

## 3. Source of truth

- `config.ini` is the build-time source of truth for:
  - defaults,
  - input limits,
  - tax/social parameters for 2026 and 2027,
  - federal states,
  - light and dark colour palettes,
  - chart geometry,
  - notes and default theme.
- `tools/generate_config.py` embeds `config.ini` into `index.html`.
- Never edit the embedded `const CONFIG` block directly; edit `config.ini` and
  regenerate.
- `tools/generate_tables.py` extracts the PDFs into embedded tables.
- `tools/verify_calculation.py` checks embedded tables against the PDFs.

## 4. Inputs and live behaviour

- Built-in defaults: tax year 2026, gross `50000` for both partners, `1` child,
  state NW, no church tax, GKV for both, Partner #1 Abfindung `100000` and
  Partner #2 Abfindung `0`.
- All inputs recalculate automatically on any change; there is no separate
  **Berechnen** button.
- Gross salary and Abfindung number fields use `1000` spinner steps, so the
  up/down arrows snap to multiples of `1000`.
- Main number inputs, all sliders (main inputs, flat-heatmap sliders, 3D-surface
  sliders and AbfWork sliders), selects and checkboxes are linked and kept
  visually in sync; moving any slider updates all linked outputs immediately.
  The two top gross sliders under **Eingaben** therefore use `data-target` and
  write directly into `#gross1` / `#gross2`, just like the chart sliders.
- Recalculation from input changes is capped at one run per animation frame to
  keep slider dragging smooth. Gross zoom uses configured nice steps with
  hysteresis (expand above `90 %`, shrink below `50 %`) and cached sweeps, so
  moving only the current gross marker does not rebuild every chart cell.
- **speichern** stores the current inputs **and the selected dark/light design**
  locally in the browser. They are loaded on the next start.
- There is no **Zurücksetzen** button.
- Local-storage keys:
  - inputs: `steuer-abfindung-rechner.defaults.v1`
  - theme: `steuer-abfindung-rechner.theme`
- Saved PKV defaults use per-partner keys such as `pkv_kv1`, `pkv_kv2`.
- The generator must not coerce numeric `0`/`1` config values to booleans.

## 5. Naming and layout

- Overall partner names are **Partner #1** and **Partner #2**.
- No use of “Mann” or “Frau”.
- Results include a household summary, per-partner tables, a comparison table
  and a dedicated **Abfindung** tab.
- A small, muted `by gortego` credit appears below the main content.

## 6. Heatmap — bestes Netto/Jahr

- No metric dropdown; `heatMetric` / `heat_metric` are fully removed.
- There is **no Fünftelregelung checkbox** and no `heat_fuenftel` default.
- Every cell and the current-input readout evaluate all four cases:
  Einzel/Zusammen × mit/ohne Fünftelregelung. The best absolute net determines
  the score, the winner hatching and the “Bestes Netto/Jahr” line, which names
  both the assessment mode and the Fünftel treatment. Tooltips list all four
  net amounts.
- The heatmap shows the **best** result of Einzel- and Zusammenveranlagung.
- Score definition:

  ```text
  score         = best(individual net, joint net; with/without Fünftelregelung)
                  // includes Kindergeld and Abfindung; unit is EUR
  quote         = score / (gross Partner #1 + gross Partner #2 + total Abfindung)
  baselineRatio = score / best net at Partner #1 gross = 0
                  // same Partner #2 gross and Abfindungen
  ```

- The primary Nettoquote follows the requested definition, including
  Kindergeld in the numerator. It is `100 %` only when nothing is deducted and
  no child benefit is added; with Kindergeld it can exceed `100 %`.
- The colour scale encodes absolute EUR net and is labelled
  `Bestes Netto/Jahr`. It is **not** capped at 100 %; it must be able to show
  the dip below the “ohne Gehalt” baseline and the rise after break-even.
- The separate `baselineRatio` is labelled `Quote vs. ohne Gehalt`. It is
  `100 %` at Partner #1 gross zero, falls below `100 %` in the loss zone and
  rises above `100 %` after break-even. It follows the household-net U-shape
  but is **not** the Nettoquote. Both ratios appear in tooltips and markers.
- Both axes start at `0`–`150000` and zoom together with all gross sliders.
  The domain grows through `150000 / 250000 / 500000 / 1000000 / 2000000 /
  5000000 / 10000000` when either gross exceeds `90 %` of the current maximum,
  and shrinks back once both gross values fall below `50 %`. Tick steps are
  rounded so the slider and sweep resolution stay roughly constant.
- Orange hatching marks cells where individual assessment wins; smooth cells
  mean joint assessment wins. A fine light-red dashed border marks the winner
  boundary.
- “Vorteil Einzel” and “Vorteil Zusammen” are green.
- A live label at the crosshair shows the household net (including Kindergeld),
  the current Nettoquote and the baseline comparison.
- A purple dashed line traces the break-even and a red dotted line the worst
  case for every Partner #2 gross. Both use per-row values from the same heatmap
  cells and are identified in the legend.
- Changing Abfindung sliders must visibly change the fills and EUR scale.
- A second pure-SVG 3D surface shows the same computed cells, with height and
  colour encoding the best absolute net. It marks the highest net in the grid
  with both salaries, the amount, the Nettoquote and the baseline comparison,
  plus the current input point. A violet dashed cross-section line traces the
  best net for every Partner #1 salary at the currently selected Partner #2
  salary. Labelled purple dashed and red dotted ridges trace the break-even and
  worst case across all Partner #2 salaries. The cell data is computed once and
  shared by both views.
- The compact curve is titled `Absolutes Netto` and its Y axis is labelled
  `Bestes Netto/Jahr`. It sweeps Partner #1 while Partner #2 stays at its
  selected value.
- The four linked sliders for that compact curve sit in one row between the
  curve and the flat heatmap: Brutto Partner #1, Brutto Partner #2, Abfindung
  Partner #1 and Abfindung Partner #2. They write the main number inputs and
  drive both charts.
- A card at the end of the page explains the Nettoquote formula in German and
  shows a worked example using Partner #1 gross `50000`, Partner #2 gross
  `60000` and Partner #1 Abfindung `200000` (Partner #2 Abfindung `0`). The
  numerator is computed from the current year, children, state and insurance
  settings; the former supplied `72,51 %` example is removed. It distinguishes
  the primary quote from the separate “Quote vs. ohne Gehalt”.
- The 3D surface has its own four linked sliders: Brutto Partner #1, Brutto
  Partner #2, Abfindung Partner #1 and Abfindung Partner #2. They write the main
  number inputs, so both diagrams and all tables update together.

## 7. AbfWork chart — “Lohnt sich Arbeiten im Abfindungsjahr?”

- The detailed 2D chart heading is `Haushaltsnetto gegen Gehalt von Partner #1`
  (the former `2D: ` prefix is removed).
- Two solid net curves: individual and joint assessment **with** Partner #1
  salary.
- Two horizontal dashed reference lines: the same assessments **without**
  Partner #1 salary, only Abfindung.
- Partner #2 gross has its own slider and stays constant while curves are
  sampled.
- Red area is clipped at the break-even.
- Purple dashed line: break-even. Red dotted vertical line at the worst-case
  gross plus a horizontal red dashed line at the worst-case net level.
- A bracket between the worst-case net and the break-even net shows the EUR gap
  that must be recovered; the same gap is written on its own line in the note.
- The note places break-even, worst case and the gap on separate lines. The
  highlighted key takeaway is `Bei aktuellem BruttoGehalt ... bringt Arbeiten ...
  weniger/mehr Netto als ohne Gehalt.` It compares current household net with
  the best net at Partner #1 gross zero. It is red below the break-even and
  green above it. The `45000` EUR example and the separate "Ohne Gehalt" line
  are removed; the `+1000` EUR marginal readout is no longer shown because a
  positive marginal gain can coexist with a loss relative to not working.
- The marginal-rate chart marks the start after the Grundfreibetrag and the
  tariff zone changes at about `24 %` and `42 %` with dashed lines. Y-axis rate
  labels use `G`/`S` prefixes and are shifted so Grund- and Splittingtarif do not
  overlap. Short zvE amounts are placed below the X axis in three staggered,
  rotated rows so nearby markers stay readable; current zvE amounts are bold.
  It also marks the current zvE of both tariffs with dark dashed guides, a
  circle, an `Aktuell` label and a labelled percentage.
- Black dashed guides connect the current “mit Gehalt” points to the Y axis.
- On the compact absolute-net curve, the moving current-point label is red when
  its text says `weniger als ohne Gehalt` and green otherwise.
- Text must say two curves plus two reference lines, not four curves.

## 8. Themes

- Funky **dark** theme is the default; funky light theme is also available.
- The header button toggles the design immediately.
- Choice is stored locally and also saved by **speichern**.
- Dark and light colours come from `config.ini` (`colors` / `colors_dark`).
- SVGs must be redrawn with the active palette. Bar-total labels in
  `Wofür das Brutto verbraucht wird` use `COLORS.guide_text` with a
  `COLORS.halo` stroke, never a hard-coded dark colour.

## 9. Notes

- Notes section ends with the **Diagramme und Abfindung:** block.
- The **Bedienung:** block has been removed.
- Notes explain the absolute-net colour scale, the Nettoquote excluding
  Kindergeld, the red/green moving label and the Abfindung handling.

## 10. Calculation rules

- ESt, SolZu and KiSt come from embedded 1000 €-step PDF tables with linear
  interpolation.
- Both assessment modes are always computed. Joint Splitting tax is allocated
  by `zvE` share.
- 2027 values are a draft and are clearly marked as such.
- Fünftelregelung:

  ```text
  ESt_total = 5 × ESt(zvE + A/5) − 4 × ESt(zvE)
  ```

- Both the Fünftelregelung and the ordinary tariff variant are always computed
  for each assessment mode; the user selects nothing, the more favourable net
  result is used everywhere. The detailed **Abfindung** tab still lists all
  three treatments (ohne Abfindung / mit Fünftel / ohne Fünftel).
- Abfindung has no social contributions.
- SolZu is derived from the resulting ESt by inverse table lookup so the
  Freigrenze and Anstiegsklausel remain exact.
- Church tax is `ESt × 8 %/9 %` depending on the federal state.
- Break-even = last crossing where
  `max(mit) >= max(ohne)`. Built-in default: `31.775 €`.
- Worst case = sampled Partner #1 gross where `max(mit)` is minimal. Built-in
  default: `17.500 € → 124.221 €`.

## 11. Verification

Run after relevant changes:

```powershell
py -3 tools/generate_config.py
py -3 tools/generate_tables.py
py -3 tools/verify_calculation.py
```

Expected: four tables, 1040 rows each, PDF-vs-HTML max diff `0.00e+00`.
Browser checks must show no console errors and no `NaN`/`Infinity`.
