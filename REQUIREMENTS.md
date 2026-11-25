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
  up/down arrows snap to multiples of `1000`. Gross number fields additionally
  accept negative annual income down to `number_min = -1000000`; the gross
  sliders remain at `0`–`150000`.
- Main number inputs, all sliders (main inputs, flat-heatmap sliders, 3D-surface
  sliders and AbfWork sliders), selects and checkboxes are linked and kept
  visually in sync; moving any slider updates all linked outputs immediately.
  The two top gross sliders under **Eingaben** therefore use `data-target` and
  write directly into `#gross1` / `#gross2`, just like the chart sliders.
- Recalculation from input changes is capped at one run per animation frame to
  keep slider dragging smooth. Sliders are capped at `150000` gross and
  `500000` Abfindung; number fields accept larger and negative gross values.
  Chart axes include a negative gross domain starting at `plot_min = -100000`
  (extending further for strongly negative typed values) and zoom on the positive
  side through configured nice steps with hysteresis (expand above `90 %`,
  shrink below `50 %`) and cached sweeps, so moving only the current gross
  marker does not rebuild every chart cell.
- Every gross-based plot draws a neutral dashed guide at gross `0` and labels it
  `0 €`. The flat heatmap and the 3D surface also draw the Partner #2 zero guide.
  The 3D surface has an explicit depth axis labelled as the Partner #2 gross
  salary.
- **speichern** stores the current inputs **and the selected dark/light design**
  locally in the browser. They are loaded on the next start.
- There is no **Zurücksetzen** button.
- Local-storage keys:
  - inputs: `steuer-abfindung-rechner.defaults.v1`
  - theme: `steuer-abfindung-rechner.theme`
- Saved PKV defaults use per-partner keys such as `pkv_kv1`, `pkv_kv2`.
- The generator must not coerce numeric `0`/`1` config values to booleans.

### Steueroptimierung im Abfindungsjahr

- A dedicated German section collects genuine cash outflows and income for the
  severance year: Weiterbildung and other Werbungskosten per partner,
  health-insurance prepayments, extra pension contributions, tax-free wage
  replacement payments (Arbeitslosengeld), donations, rental losses and
  business losses.
- All optimization fields are annual amounts with `100` spinner steps and a
  common configured range (`0`–`10000000`). Every field has a German hint with a
  statutory anchor or example, and a collapsed German details section explains
  § 10 EStG, § 10b EStG, § 32b EStG and § 15b EStG.
- Weiterbildung/other Werbungskosten are uncapped. Health-insurance prepayments
  are capped at `3 ×` the current-year KV/PV contributions per § 10 EStG; extra
  pension contributions at approximately `24.7 %` of `bbgRV` minus employee and
  employer RV; donations at `20 %` of the approximated total income per
  § 10b EStG; business losses at `10000` individual / `20000` joint; rental
  losses are uncapped. Household losses are split equally between partners.
  Every optimization input is clamped to its current Höchstbetrag before any
  calculation or save; the live callout shows the applied amounts and limits.
- Arbeitslosengeld is added tax-free to net income but raises the tax rate on
  the remaining income via the Progressionsvorbehalt (§ 32b EStG). Unused
  employee allowance reduces the progression amount. Its two fields are marked
  with a green `+ Einnahme` badge and green left border; every expense/loss
  field has a red `− Ausgabe` badge and red left border. The written badge
  carries the meaning, so colour is never the only cue.
- Optimization values affect all four severance cases, both assessment modes,
  the tables, the summary, the heatmap, the 3D surface and both AbfWork charts.
  They are part of the sweep cache keys.
- The section does not display a separate advisory callout; § 15b EStG remains
  explained in the collapsed German details.

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
  `Bestes Netto/Jahr`. It is **not** capped at 100 % or at zero; it must be able
  to show negative net, the dip below the “ohne Gehalt” baseline and the rise
  after break-even. The primary Nettoquote is undefined when the denominator
  (gross salaries plus Abfindungen) is zero or negative.
- The separate `baselineRatio` is labelled `Quote vs. ohne Gehalt`. It is
  `100 %` at Partner #1 gross zero, falls below `100 %` in the loss zone and
  rises above `100 %` after break-even. It follows the household-net U-shape
  but is **not** the Nettoquote. Both ratios appear in tooltips and markers.
- All gross sliders stay at `0`–`150000`. Both chart axes start at
  `-100000 … 150000` and extend further down for strongly negative typed gross
  values. The positive maximum zooms through `150000 / 250000 / 500000 /
  1000000 / 2000000 / 5000000 / 10000000` when either gross exceeds `90 %` of
  the current maximum, shrinking back once both gross values fall below `50 %`.
  Tick steps are rounded so the sweep resolution stays readable.
- Orange hatching marks cells where individual assessment wins; smooth cells
  mean joint assessment wins. A fine light-red dashed border marks the winner
  boundary.
- “Vorteil Einzel” and “Vorteil Zusammen” are green.
- A live label at the crosshair shows the household net (including Kindergeld),
  the current Nettoquote and the baseline comparison.
- A purple dashed line traces the break-even for every Partner #2 gross. A red
  dotted line traces the worst case only where both salaries are positive;
  both use per-row values from the same heatmap cells and are identified in the
  legend. Negative cells remain visible and feed the break-even and scales.
- Two extra curves use the same cells and maximise the Nettoquote
  (`score / (gross salaries + Abfindungen)`), not absolute net: `Opt. P1 je P2`
  gives the best Partner #1 salary for every Partner #2 salary, and
  `Opt. P2 je P1` gives the best Partner #2 salary for every Partner #1 salary.
  Their drawing code is kept but disabled by
  `CONFIG.general.show_optimum_curves = false`; while hidden, neither curve,
  current-point marker nor legend entry is rendered. The optimum data still
  drives compact German readouts under every gross slider (input card, both
  chart slider rows and the Abfindungsjahr row) with the corresponding optimum
  and its Nettoquote.
- Changing Abfindung sliders must visibly change the fills and EUR scale.
- A second pure-SVG 3D surface shows the same computed cells, with height and
  colour encoding the best absolute net. It marks the highest net in the grid
  with both salaries, the amount, the Nettoquote and the baseline comparison,
  plus the current input point. A violet dashed cross-section line traces the
  best net for every Partner #1 salary at the currently selected Partner #2
  salary. Labelled purple dashed and red dotted ridges trace the break-even and
  the positive-salary worst case across Partner #2 salaries. The depth axis is
  explicitly drawn and labelled as the Partner #2 gross salary, and zero guides
  mark both gross axes. The cell data is computed once and shared by both views.
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
- Axis-limit drag zoom applies only to `Absolutes Netto` and `Haushaltsnetto
  gegen Gehalt von Partner #1`. Dragging a rectangle inside the plot defines new
  X/Y minimum and maximum values; the chart is redrawn at the same pixel size
  with those axis limits, so the SVG viewBox, line widths and cached sweep data
  are unchanged. `↺ Zoom aufheben` restores the configured limits. State is kept
  per chart in memory, survives recalculation and theme changes, and is not
  saved to local storage. The heatmap, 3D surface, bar charts, progression and
  marginal-rate chart have no drag zoom.

## 7. AbfWork chart — “Lohnt sich Arbeiten im Abfindungsjahr?”

- The detailed 2D chart heading is `Haushaltsnetto gegen Gehalt von Partner #1`
  (the former `2D: ` prefix is removed).
- Four net curves: individual and joint assessment, each with and without the
  Fünftelregelung, all **with** Partner #1 salary. Curves with Fünftelregelung
  are solid; curves without are dash-dot.
- Two horizontal dashed reference lines: the same assessments **without**
  Partner #1 salary, only Abfindung, using the better Fünftel treatment per
  assessment mode.
- Partner #2 gross has its own slider and stays constant while curves are
  sampled. The Partner #1 sweep starts at the configured negative plot minimum
  (extending for typed values below it) so negative income and negative net are
  visible; the dashed “ohne Gehalt P1” reference is still evaluated at gross
  `0`.
- Red area is clipped at the break-even.
- Purple dashed line: break-even. Red dotted vertical line at the worst-case
  gross plus a horizontal red dashed line at the worst-case net level. The
  worst case uses only positive salaries of both partners; negative gross stays
  in the plotted curves but cannot become the worst case. A neutral dashed guide
  marks gross `0`.
- A bracket between the worst-case net and the break-even net shows the EUR gap
  that must be recovered; the same gap is written on its own line in the note.
- The note places break-even, worst case and the gap on separate lines. It also
  shows `Netto aus der Abfindung (bei den aktuellen Gehältern)`: the best net
  with the entered Abfindungen minus the best net at the same gross salaries
  with both Abfindungen set to zero, plus the total gross Abfindung and both net
  amounts. It is `0 €` when no Abfindung is entered.
- The highlighted key takeaway is `Bei aktuellem BruttoGehalt ... bringt Arbeiten ...
  weniger/mehr Netto als ohne Gehalt.` It compares current household net with
  the best net at Partner #1 gross zero. It is red below the break-even and
  green above it. The `45000` EUR example and the separate "Ohne Gehalt" line
  are removed; the `+1000` EUR marginal readout is no longer shown because a
  positive marginal gain can coexist with a loss relative to not working.
- A `<details>` section titled `Berechnung Schritt für Schritt` is collapsed by
  default beneath the note. It lists the inputs, the base net without Abfindung,
  all four current severance cases (including zvE, social contributions,
  additional expenses/losses, tax-free wage replacement payments, ESt, SolZu,
  KiSt, Kindergeld, Abfindung and net), the Abfindung net gain, the
  "ohne Gehalt P1" reference cases, the sweep interpolation for break-even, the
  worst case and the gap, and the current comparison. It uses German UI text.
- The marginal-rate chart marks the start after the Grundfreibetrag, the tariff
  zone changes at about `24 %` and `42 %`, and the top rate (`45 %` for 2026,
  `47 %` for the 2027 draft) with dashed lines. Its X axis reaches `600000` zvE
  so both tariffs' top-rate thresholds are visible. Y-axis rate labels use
  `G`/`S` prefixes and are shifted so Grund- and Splittingtarif do not overlap.
  Short zvE amounts are placed below the X axis in three staggered, rotated rows
  so nearby markers stay readable; current zvE amounts are bold.
  It also marks the current zvE of both tariffs with dark dashed guides, a
  circle, an `Aktuell` label and a labelled percentage.
- Black dashed guides connect the current “mit Gehalt” points to the Y axis.
- On the compact absolute-net curve, the moving current-point label is red when
  its text says `weniger als ohne Gehalt` and green otherwise.
- Text must say four curves plus two reference lines.

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
- Notes explain the absolute-net colour scale, the Nettoquote including
  Kindergeld, negative income/net ranges, the red/green moving label and the
  Abfindung handling.

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
- Negative gross salaries are allowed in number fields. Social-contribution
  bases are clamped to zero, while genuine expenses and losses may make the
  taxable income and the resulting household net negative. No chart scale is
  clamped at zero.
- The capped optimization expenses, household loss split and
  Progressionsvorbehalt described in section 4 apply to every scenario and all
  four Abfindung cases. Alg is added tax-free to net but is not part of the
  primary Nettoquote denominator.
- Break-even = last crossing of the negative-inclusive Partner #1 sweep where
  the best net reaches the best net at Partner #1 gross `0`. The value is
  computed from the current inputs; no fixed example is assumed.
- Worst case = sampled gross where the best net of the four cases is minimal,
  considering only samples with both Partner #1 and Partner #2 gross above `0`.
  Its salary and net come from the same sweep; negative samples remain plotted
  and feed break-even, but cannot win the minimum. No fixed example is assumed.

## 11. Verification

Run after relevant changes:

```powershell
py -3 tools/generate_config.py
py -3 tools/generate_tables.py
py -3 tools/verify_calculation.py
```

Expected: four tables, 1040 rows each, PDF-vs-HTML max diff `0.00e+00`.
Browser checks use a cache-busted URL, must show no console errors and no
`NaN`/`Infinity`, and must render nine SVGs. They also verify the dark default
and persisted theme toggle, **speichern** persistence, automatic cap clamping
and the cap callout, the zero guides and the labelled 3D depth axis, negative
Partner #1/Partner #2 salaries, negative net values in the scales and axes,
positive-only worst-case markers, and the red/green compact-curve comparison
label.
