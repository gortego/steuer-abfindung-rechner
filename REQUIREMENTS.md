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
  - tax/social parameters for 2026, 2027 and 2028,
  - the fixed zvE shifts used to project the 2028 tax tables,
  - federal states,
  - light and dark colour palettes,
  - chart geometry, including both Grundtabelle timeline plots,
  - notes and default theme.
- `tools/generate_config.py` embeds `config.ini` into `index.html`.
- Never edit the embedded `const CONFIG` block directly; edit `config.ini` and
  regenerate.
- `tools/generate_tables.py` extracts the PDFs into embedded tables.
- `tools/verify_calculation.py` checks embedded tables against the PDFs.

## 4. Inputs and live behaviour

- Built-in defaults: tax year 2026, gross `50000` for both partners, `1` child,
  state NW, no church tax, `gkv_freiwillig` (freiwillig versichert, Auto on)
  for both partners, joint
  assessment enabled (`joint_allowed = true`), Partner #1 Abfindung `100000`
  and Partner #2 Abfindung `0`, both partners with `minijob_mode = none`,
  `minijob_gross = 0` and `minijob_rv_exempt = false`, voluntary-GKV bases of
  `0`, and all per-partner optimization fields at `0`.
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
- `joint_allowed` controls eligibility. When false, `body.single-mode` hides
  every `[data-partner="2"]` input and slider, `#surfaceSection`, the joint and
  compare tabs/panels, and sets Partner #2 to a neutral zero person in every
  calculation and sweep. Hidden DOM values are preserved for later re-enable.
  The flat heatmap collapses to one Partner #2 = 0 row with no Partner #2 axis,
  and the 3D surface is not rendered. No visible German text may mention
  `Partner #2`, `P2`, `Zusammenveranlagung`, `Splitting` or `Haushalt`,
  including hints, notes, chart legends, intros, result tables and the
  source-table filename; single-mode alternatives are supplied instead. The
  detailed result tables have only `Position` and `Partner #1`, with Kindergeld
  and the full net in that column. The worked Nettoquote example uses
  `jointAllowed: false` in single mode, with Partner #1 gross `50000` and
  Abfindung `200000`.
- Insurance status is an explicit, mutually exclusive radio choice per partner:
  `gkv` (pflichtversichert employee), `gkv_freiwillig` (freiwillig versichert)
  or `pkv`. There is no automatic detection of voluntary GKV.
- `gkv` calculates KV/PV from gross salary up to `bbgKVPV` with the employee
  share of KV and PV. `gkv_freiwillig` uses a separate annual `voluntary_base1`
  / `voluntary_base2` field capped at `bbgKVPV`, the full KV and PV rates and no
  employer share. `pkv` uses the entered monthly premiums and subsidy and keeps
  the existing GKV-equivalent deductible. The insurance mode and Auto flag are
  part of both sweep cache keys; a manual base is part of the keys, while an
  Auto base is derived per sampled salary inside `taxScenario()` so moving the
  current gross marker changes only the marker and not the cached curves.
- Each voluntary-GKV base has an **Auto** checkbox immediately to the right of
  the number field, so no extra page row is added. Auto is on by default. While
  on, the field is read-only and is recalculated from that partner's current
  gross salary, capped at `bbgKVPV`, on every relevant input change. Unticking
  Auto makes the field editable and uses the entered Bescheid value instead.
  The Auto flags are persisted with the other defaults and are part of the
  sweep cache keys; the derived base is computed per sampled salary.
- Old saved `insurance1` / `insurance2` checkboxes migrate on load: `true` →
  `pkv`, `false` → `gkv`. New saved data uses `insurance_mode1` /
  `insurance_mode2`.
- The generator must not coerce numeric `0`/`1` config values to booleans.

### PDF export

- A German **PDF herunterladen** button sits in the header immediately left of
  the light/dark toggle. It renders the report to canvases and downloads a valid
  PDF directly through an anchor; `window.print()` is not called. The embedded
  generator adds no external runtime library and makes no network request.
- The download filename is `Abfindung-Steuerlast-Netto-<year>-<date>.pdf`.
- Before generating, the app builds a German `#pdfInputs` table containing every
  current input and its hint, including hidden Minijob, voluntary-GKV and PKV
  fields and the selected theme. In single mode Partner #2 fields stay hidden so
  no forbidden Partner #2 wording appears.
- All `<details>` blocks (input notes, optimization notes, severance tables and
  step-by-step calculation) are temporarily opened, and every result panel is
  included, so the PDF contains all comments, all information and all SVG plots.
- Pages are light, readable A4 landscape canvases. SVGs are rasterised from their
  own serialized markup so their exact colours survive.
- The document title is temporarily set to a dated filename suggestion; the
  previous title and details state are restored after generation and on
  `afterprint` for manual browser printing. Print CSS still forces a light,
  readable A4 landscape report, hides buttons/tabs/sliders and wraps wide tables.

### Minijobs

- Each partner has a per-partner Minijob selector with `none`, `pauschal` and
  `individuell` modes. Selecting a mode reveals that partner's annual gross
  field; the pension-exemption checkbox appears only for `pauschal`. `none`
  hides the detail block while preserving the stored values.
- Minijob gross uses `limits.minijob` (`0`–`10000`, step `1`) and is additionally
  clamped to the selected year's `minijob_annual`: `7236` for 2026 and `7596`
  for the 2027 draft. Invalid or over-cap values are clamped before calculation
  and save. The mode, gross amount and exemption flag are persisted per partner.
- A pauschal Minijob stays outside progressive `zvE` and outside the regular
  social-contribution bases. The employee pension contribution is
  `minijob_rv_employee` (`3.6 %`) and is omitted when the exemption is checked.
  The employer pension contribution is `minijob_rv_employer` (`15 %`) on at
  least `minijob_rv_min_month × 12`; employer KV/PV for GKV partners uses
  `minijob_kv_employer` (`13 %` / `17.5 %` draft) and `minijob_pv_employer`
  (`0 %`), with no employer KV/PV for PKV. The employer-paid Pauschsteuer uses
  `minijob_pauschsteuer` (`2 %` / `5 %` draft). Employer contributions and
  Pauschsteuer are informational only and never reduce employee net.
- An individual Minijob is added to taxable gross and to the RV/AV/KV/PV bases;
  it uses ordinary employee contributions and the donation cap, with no
  Pauschsteuer. The exemption flag does not alter the regular pension base.
- Minijob gross is included in `effectiveGross` for net, in the Nettoquote
  denominator and in the Auto voluntary-GKV base up to `bbgKVPV`. Kindergeld
  remains in the numerator only. All three Minijob inputs per partner are part
  of both sweep cache keys and of the fixed-example neutral person.
- The German detail tables, hints and notes list the active Minijob, gross,
  employee RV, employer RV/KV/PV and Pauschsteuer information; the composition
  chart counts salary plus Minijob gross as income.

### Steueroptimierung im Abfindungsjahr

- A dedicated German section collects genuine cash outflows and income for the
  severance year **per partner**: Weiterbildung and other Werbungskosten,
  health-insurance prepayments, extra pension contributions, grouped tax-free
  wage replacement benefits, donations, rental losses, rental profits, business
  losses and interest. No household amount is split 50/50.
- All optimization fields are annual amounts with `100` spinner steps and a
  common configured range (`0`–`10000000`). Every field has a German hint that
  states how its maximum is calculated, and a collapsed German details section
  explains § 10 EStG, § 10b EStG, § 32b EStG and § 15b EStG.
- Weiterbildung/other Werbungskosten are uncapped. Health-insurance prepayments
  are capped at `3 ×` the current-year KV/PV contributions per § 10 EStG: from
  gross salary for `gkv`, from the entered voluntary contribution base for
  `gkv_freiwillig`, and from the GKV-equivalent deductible for `pkv`. Extra
  pension contributions are capped at `30826` individual / `61652` joint in
  2026 and `32308` / `64616` in 2027, reduced by twice the modelled employee RV.
  Business losses are capped at `10000` individual / `20000` joint. Rental
  losses and rental profits are uncapped.
- Donations are capped at `20 %` of the **Gesamtbetrag der Einkünfte** before
  Sonderausgaben (§ 10b EStG), never at gross salary and never at post-
  Sonderausgaben zvE. The modelled amount is gross pay plus Abfindung after the
  employee allowance and actual Werbungskosten and after rental/business
  results, but before Vorsorge, KV prepayments, extra RV, tax-free wage
  replacement benefits and interest. The cap is per partner in individual
  assessment and shared in joint assessment.
- Interest uses an Abgeltungsteuer-style model: `25 %` on the amount above a
  `1000 EUR` Sparer-Pauschbetrag per partner, outside progressive zvE and
  outside the KV/PV base, with Soli and church tax where applicable and no
  Günstigerprüfung.
- Every visible optimization input is clamped to its current Höchstbetrag before
  any calculation or save. Hidden Partner #2 inputs are neither validated nor
  clamped. Field hints show the concrete current Höchstbetrag inline instead of
  referring to another box; the live callout shows the clamped amount, the
  current maximum and the formula used to derive it as a bulleted list. Older
  saved household keys `donations`, `rentalLoss` and `businessLoss` are split
  equally into the new per-partner keys on load only when no per-partner value
  was saved.
- German acronyms in static and generated UI text (for example `PKV`, `GKV`,
  `KV`, `PV`, `RV`, `EStG`, `zvE`, `bAV`, `BBG`, `JAEG`) are annotated with
  `<abbr>` elements. Hovering or focusing them shows a visible tooltip with the
  German meaning; native `title` text is used as a fallback. SVG text, scripts,
  styles and existing `<abbr>` elements are skipped, and the annotation is
  reapplied to generated content after each calculation.
- Tax-free wage replacement benefits are grouped in one field per partner and
  labelled `Steuerfreie Lohnersatzleistungen`. The group covers § 32b Abs. 1
  Satz 1 Nr. 1 EStG benefits such as Arbeitslosengeld I, Teilarbeitslosengeld,
  Kurzarbeitergeld, Insolvenzgeld, Übergangsgeld, Qualifizierungsgeld,
  Krankengeld/Kinderkrankengeld, Mutterschaftsgeld, Verletztengeld, Elterngeld
  variants, steuerfreie Altersteilzeit-Aufstockung and IfSG-Verdienstausfall.
  Bürgergeld/Arbeitslosengeld II, Wohngeld, Pflegegeld, Kindergeld, BAföG,
  private Krankentagegeld, pauschal versteuerte Minijobs and foreign/treaty
  income are excluded. The amounts are added tax-free to net but raise the tax
  rate on remaining income via the Progressionsvorbehalt. Unused employee
  allowance reduces the progression amount. Income fields carry a green
  `+ Einnahme` badge and green left border; every expense/loss field has a red
  `− Ausgabe` badge and red left border. The written badge carries the meaning,
  so colour is never the only cue.
- Optimization values affect all four severance cases, both assessment modes,
  the tables, the summary, the heatmap, the 3D surface and both AbfWork charts.
  They are part of the sweep cache keys.
- The section does not display a separate advisory callout; § 15b EStG remains
  explained in the collapsed German details.

## 5. Naming and layout

- Overall partner names are **Partner #1** and **Partner #2**.
- No use of “Mann” or “Frau”.
- Results include a household summary, per-partner tables, a comparison table
  and a dedicated **Abfindung** tab. In single mode the per-partner tables omit
  the redundant total column and show only `Partner #1`.
- A small, muted `by gortego` credit appears below the main content.

### Visible scope notice

- A visible German notice sits at the top of `main`, before the input card.
- It states that the page is **KEINE Steuerberatung**, does not replace
  individual tax advice, and returns only a simplified comparison estimate.
- It states that the model is intended for couples where the partners are
  sozialversicherungspflichtig beschäftigt or have a Minijob (for example
  employees or Minijob holders, but no self-employment). It explains that unticking
  `Zusammenveranlagung ist möglich` calculates only Partner #1 and individual
  assessment.
- It names the main excluded cases: betriebliche Altersvorsorge or capital
  income as a KV/PV contribution base, wage-replacement benefits outside the
  grouped § 32b benefits, and a Kindergeld/Kinderfreibetrag Günstigerprüfung
  that accounts for the Abfindung.
- The notice stays readable in the dark theme, the light theme and print output.

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
  quote         = score / (gross Partner #1 + gross Partner #2
                  + Minijob gross Partner #1 + Minijob gross Partner #2
                  + total Abfindung)
  baselineRatio = score / best net at Partner #1 gross = 0
                  // same Partner #2 gross, Minijobs and Abfindungen
  ```

- The primary Nettoquote follows the requested definition, including
  Kindergeld in the numerator. It is `100 %` only when nothing is deducted and
  no child benefit is added; with Kindergeld it can exceed `100 %`.
- The colour scale encodes absolute EUR net and is labelled
  `Bestes Netto/Jahr`. It is **not** capped at 100 % or at zero; it must be able
  to show negative net, the dip below the “ohne Gehalt” baseline and the rise
  after break-even. The primary Nettoquote is undefined when the denominator
  (gross salaries, Minijob-Bruttos and Abfindungen) is zero or negative.
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
  (`score / (gross salaries + Minijob-Bruttos + Abfindungen)`), not absolute net:
  `Opt. P1 je P2`
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
- In single mode (`jointAllowed === false`) `computeHeatmapData()` uses `ny = 1`
  and Partner #2 gross `0` for all cells, the flat map centres that row and
  suppresses Partner #2 ticks and axis title, the surface renderer is skipped,
  and `#heatModeNote` explains the reduced view. All sweep cache keys include
  `jointAllowed`, every per-person optimization field and the per-person Minijob
  mode, gross amount and pension-exemption flag.
- The compact curve is titled `Absolutes Netto` and its Y axis is labelled
  `Bestes Netto/Jahr`. It sweeps Partner #1 while Partner #2 stays at its
  selected value. In single mode the Partner #2 slider is hidden.
- The four linked sliders for that compact curve sit in one row between the
  curve and the flat heatmap: Brutto Partner #1, Brutto Partner #2, Abfindung
  Partner #1 and Abfindung Partner #2. They write the main number inputs and
  drive both charts; only the two Partner #1 sliders remain visible in single
  mode.
- A card at the end of the page explains the Nettoquote formula in German. With
  joint assessment it shows a worked example using Partner #1 gross `50000`,
  Partner #2 gross `60000` and Partner #1 Abfindung `200000` (Partner #2
  Abfindung `0`); in single mode it uses Partner #1 gross `50000` and Abfindung
  `200000` only. That example explicitly forces Minijob mode `none` and Minijob
  gross `0` for both partners, so saved Minijob inputs cannot change it. The
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
- A bracket inside the plot connects the worst-case net and the break-even net.
  The EUR gap that must be recovered is labelled `Differenz` with
  `Worst case → Break-even` in the right margin; a dashed arrow leads from the
  bracket midpoint to that label. The same gap is written on its own line in the
  note.
- Marker labels are placed outside the plotted rectangle: break-even and
  worst-case salary labels above it, and `Einzel ohne Gehalt`,
  `Zusammen ohne Gehalt`, `Worst case Netto` and the gap label in the right
  margin with short leader lines. Close right-margin labels are staggered with
  enough room for the gap label's second line. In single mode only the individual
  baseline label appears, and no worst-case or gap labels are drawn.
- The note places break-even, worst case and the gap on separate lines. It also
  shows `Netto aus der Abfindung (bei den aktuellen Gehältern)`: the best net
  with the entered Abfindungen minus the best net at the same gross salaries
  with both Abfindungen set to zero, plus the total gross Abfindung and both net
  amounts. It is `0 €` when no Abfindung is entered. The `bestes Netto mit Abfindung` value must be visibly highlighted
  as the key amount in both the callout and the step-by-step calculation.
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
  its text says `weniger als ohne Gehalt` and green otherwise. Its plot height is
  `150` px (`230` px SVG height, `y0 = 30`) so the Y axis stays readable.
  Break-even and worst-case salary labels sit above the plot; `Ohne Gehalt` and
  `Worst case Netto` sit in the right margin with leader lines.
- Text must say four curves plus two reference lines when joint assessment is
  enabled. In single mode only the two individual-assessment curves and one
  reference line are drawn; the Partner #2 slider is hidden, the worst-case
  marker is omitted, the legend and live intro text are reduced, and
  `renderAbfWorkSteps()` lists only the two available cases.

## 8. Themes

- Funky **light** theme is the default; funky dark theme is also available.
- The header button label names the design it switches to and toggles the design
  immediately. Toggling stores the new theme in the saved defaults as well as in
  the theme key, so it survives a reload.
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
  Abfindung handling. A separate German Minijob list states the per-partner
  modes, annual ceiling, employee/employer RV, employer KV/PV, Pauschsteuer,
  the individual-taxation treatment and the Minijob share of the Nettoquote
  denominator and voluntary-GKV Auto base. Pauschal versteuerte Minijobs are no
  longer listed as an excluded wage-replacement benefit.

## 10. Calculation rules

- ESt, SolZu and KiSt come from embedded 1000 €-step PDF tables with linear
  interpolation.
- When joint assessment is enabled, both assessment modes are computed and the
  better net result is used; when disabled, only individual assessment is
  computed. Joint Splitting tax is allocated by `zvE` share.
- 2027 values are a draft and are clearly marked as such.
- A pauschal Minijob adds gross to `effectiveGross` but not to `taxGross`, the
  regular RV/AV/KV/PV bases or progressive `zvE`. It deducts only the separate
  employee RV from net, unless the exemption is set. Employer RV, employer
  KV/PV and employer-paid Pauschsteuer are displayed as information and never
  deducted from net.
- An individual Minijob adds its gross to both `effectiveGross` and `taxGross`,
  so it enters progressive `zvE`, the Vorsorgepauschale and the pre-Sonderausgaben
  donation cap; it has no Pauschsteuer and uses ordinary employee contributions.
- The Nettoquote denominator is gross salaries plus Minijob-Bruttos plus
  Abfindungen; Kindergeld remains in the numerator only.
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
- The per-partner optimization values, capped where applicable, and the grouped
  Progressionsvorbehalt described in section 4 apply to every scenario and all
  available Abfindung cases. Tax-free wage replacement benefits are added to
  net but are not part of the primary Nettoquote denominator. Interest is
  taxed separately at `25 %` after the per-partner Sparer-Pauschbetrag and
  stays outside progressive zvE and KV/PV. Donations are deducted from zvE only
  up to `20 %` of the pre-Sonderausgaben Gesamtbetrag der Einkünfte as described
  in section 4.
- Break-even = last crossing of the negative-inclusive Partner #1 sweep where
  the best net reaches the best net at Partner #1 gross `0`. The value is
  computed from the current inputs; no fixed example is assumed.
- Worst case = sampled gross where the best net of the four cases is minimal,
  considering only samples with both Partner #1 and Partner #2 gross above `0`.
  Its salary and net come from the same sweep; negative samples remain plotted
  and feed break-even, but cannot win the minimum. No fixed example is assumed.

### Tax years and 2028 projection

- The year selector contains exactly `2026 (endgültige Werte)`,
  `2027 (Regierungsentwurf)` and `2028 (Prognose)`. Tables for 2021–2025 are
  embedded only for the timeline and verification; they are not selectable.
- 2028 is always labelled as a non-official prognosis. Its tax tables are
  generated from 2027 by shifting the Grundtabelle `250 EUR` and the
  Splittingtabelle `500 EUR` to the right in zvE. The other parameters are
  carried forward from the 2027 draft.
- The fixed shift is explained in German: for zvE between `80,000` and
  `200,000 EUR`, 2026 ESt is `106 EUR` higher than 2027; at the `42 %` marginal
  rate that is about `250 EUR` of right shift. The Splittingtabelle step is
  about twice as large. This keeps the 2028 curve parallel to the recent annual
  offsets instead of fanning out with income.

### Grundtabelle timeline

- A card before the notes contains two pure-SVG timeline plots: absolute
  ESt over zvE (`0`–`300,000 EUR` on X, `0`–`140,000 EUR` on Y) and tax relief
  against 2021 (`tax 2021 − tax year`, with a `0`–`3,000 EUR` Y axis).
- Both plots show the historical Grundtabellen 2021–2027 plus a dashed, clearly
  labelled `2028 Prognose` curve. The second plot makes the small yearly gaps
  visible.
- Both Y-axis labels are rotated vertically and remain readable. The charts use
  the active palette, redraw on theme changes, contain no joint-assessment
  wording and stay visible in single mode.
- The German note states the fixed-shift assumption and the `106 EUR / 42 %`
  derivation, and says that earlier years are not in the year selector.

## 11. Verification

Run after relevant changes:

```powershell
py -3 tools/generate_config.py
py -3 tools/generate_tables.py
py -3 tools/verify_calculation.py
```

Expected: fourteen PDF tables plus the two generated 2028 projections, 1040
rows each; PDF-vs-HTML max diff `0.00e+00`. Browser checks use a cache-busted
URL, must show no console errors or warnings and no `NaN`/`Infinity`, and must
render eleven SVGs with joint assessment enabled and nine in single mode. They
check the three-option year selector, two timeline plots with eight curves each,
vertical timeline Y labels, the dashed `2028 Prognose` curve and the header PDF
button immediately left of the theme toggle.
After clearing local storage they confirm that the joint-assessment checkbox is
ticked and Partner #2 Abfindung is `0`. They verify that break-even and
worst-case labels sit above both net plots, that the baseline and worst-case-net
labels sit in the right margin, and that the compact plot is 150 px high. They
also verify the light default, `gkv_freiwillig` for both partners as the
built-in insurance default, the persisted theme toggle, the voluntary-base
Auto checkbox following gross salary and the manual override when unticked,
**speichern** persistence, automatic cap clamping and the cap callout, the zero
guides and the labelled 3D depth axis, negative Partner #1/Partner #2 salaries,
negative net values in the scales and axes, positive-only worst-case markers,
and the red/green compact-curve comparison label. With joint assessment unticked,
they verify that Partner #2 fields/sliders, the joint/compare tabs and the 3D
surface disappear, the heatmap has one centred row without a Partner #2 axis,
the AbfWork chart has only individual curves, and hidden Partner #2 DOM values
survive a mode toggle. They also check that fresh defaults show no Minijob and
hidden detail blocks, that pauschal gross stays outside `zvE` with only employee
RV deducted while employer RV/KV/PV and Pauschsteuer remain informational, that
the exemption removes exactly that employee RV and is hidden outside the
pauschal mode, that individual gross enters `taxGross` and regular RV without a
Pauschsteuer or employer lump sum, that over-cap amounts clamp to the selected
year's annual ceiling, that the Nettoquote denominator and both sweep caches
include Minijob inputs, that the voluntary-GKV Auto base follows salary plus
Minijob gross, and that saved defaults and the theme toggle include Minijob
mode, amount and exemption. They also click **PDF herunterladen** with printing
stubbed, confirm that `window.print()` is never called, that a direct anchor
download produces a valid `%PDF-1.4` file, that a full input/hint snapshot is
built, all details open and the dated title is restored afterwards, and verify
that moving Partner #1's gross under voluntary-GKV Auto leaves both sweep cache
keys and cached data unchanged while updating the base and the current point.
