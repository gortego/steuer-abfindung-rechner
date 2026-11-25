# German tax and net-income comparison tool

A self-contained, single-file HTML calculator for comparing the annual tax,
social-insurance and private-insurance burden of two parents in Germany under:

- **Einzelveranlagung** — individual assessment using the *Grundtabelle*
- **Zusammenveranlagung** — joint assessment using the *Splittingtabelle*

The user interface and all results are in German, apart from the small
`by gortego` credit at the bottom of the page. The browser title and page
heading are `Abfindung, Steuerlast & Netto`. This document is in English.

## Files

| File | Purpose |
| --- | --- |
| `config.ini` | Single source of truth for defaults, limits, tax parameters, states, colours, chart geometry and notes. |
| `index.html` | The complete application. Open it in a browser; no server or runtime dependency is required. It contains the embedded config and tax tables. |
| `tabelle/*.pdf` | Source tax tables in 1,000 EUR steps for 2026 and 2027. Needed only for the build/verification steps, not at runtime. |
| `tools/generate_config.py` | Build-time helper that embeds `config.ini` as `const CONFIG` into `index.html`. |
| `tools/generate_tables.py` | Build-time helper that extracts the PDF tables from `tabelle/` into `index.html`. |
| `tools/verify_calculation.py` | Build-time helper that verifies the embedded tables against the PDFs in `tabelle/`. |
| `REQUIREMENTS.md` | Complete, human-readable list of all product requirements. |
| `AGENTS.md` | Agent/skills file: working rules, build commands and verification checklist. |

## Usage

1. Open `index.html` in any modern browser.
2. Select the tax year, enter both gross annual salaries (or drag the sliders
   underneath them), the number of children and the federal state. Number
   fields accept negative annual income down to `-1,000,000 EUR`; the sliders
   remain at `0`–`150,000 EUR`.
3. Tick **Privat versichert (PKV)** for a parent who is privately insured;
   leave it unticked for **gesetzlich (GKV)**. For PKV, expand
   **Erweiterte Annahmen** and enter the monthly private premiums, employer
   subsidy and children covered.
4. Tick the church-tax checkboxes where applicable.
5. Enter an optional one-off **Abfindung** for either parent (0 = none).
6. Optional: in **Erweiterte Annahmen** change the GKV supplementary rate or
   state whether all children are under 25.
7. Optional: use **Steueroptimierung im Abfindungsjahr** to enter real,
   documented expenses and tax-free wage replacement payments. The callout at
   the end of that section shows which requested amounts exceed the modelled
   caps.
8. All results update automatically as soon as any input changes; there is no
   separate calculate button.
9. Optional: click **speichern** to store the current inputs, optimization
   amounts and the selected dark/light design as new defaults in this browser.
   They are loaded on the next run. This uses local browser storage only;
   `config.ini` and the single HTML file are not modified. The ☀️/🌙 button in
   the header switches between the funky dark and light designs immediately;
   dark is the built-in default.

The built-in defaults are tax year 2026, gross salaries of `50,000 EUR` for
both partners, one child, federal state NW, GKV for both partners, no church
tax, Partner #1 Abfindung `100,000 EUR` and Partner #2 Abfindung `0 EUR`.
All optimization amounts default to `0 EUR`, and the built-in theme is dark.
Saved browser values override these defaults; click **speichern** again or
clear this site's data to apply the built-in values.

Results are shown as:

- a household summary,
- detailed tables for both assessment modes with columns **Partner #1**,
  **Partner #2** and **Beide (Haushalt)** — the last column is the sum of
  both partners; child benefit is shown there only,
- a direct comparison table,
- a dedicated **Abfindung** tab with a six-column household matrix
  (individual/joint × without severance / with severance / with severance plus
  Fünftelregelung), expandable per-parent detail tables and its own chart,
- nine SVG charts:
  1. where the gross income goes (social contributions, taxes, net pay, child benefit),
     with dashed reference lines at the gross-income levels for comparison,
  2. a heatmap of the best absolute household net across both salaries, with a
     crosshair at the current inputs, four linked gross/Abfindung sliders placed
     between the compact net curve and the map, hatching to show which assessment
     mode wins, and a readout of all four annual net figures
     (individual/joint × with/without Fünftelregelung); the Nettoquote and the
     separate baseline-relative quote stay in the tooltip and crosshair label,
     and purple dashed/red dotted lines mark break-even and worst case,
  3. the same absolute net as a 3D surface over both salaries, with the best
     combination and the current input marked, break-even and worst-case ridges
     drawn across both salaries, and its own four linked sliders for both gross
     salaries and both Abfindungen,
  4. a 2D view of household net versus the salary of Partner #1 in the
     Abfindung year, with independent gross sliders for both partners, four
     net curves (Einzel/Zusammen × mit/ohne Fünftelregelung, all with the
     Partner #1 salary), two dashed "Abfindung only" baselines and a red band
     (up to the break-even) where working *reduces* net income. Solid curves
     use the Fünftelregelung, dash-dot curves do not. A purple dashed line
     marks the break-even, a red dotted line (plus a horizontal red dashed
     net-level line) the worst case, and black dashed guides follow the two
     best current points to the Y axis. A bracket shows the net difference from
     the worst case to the break-even.
     Break-even, worst case and gap are on separate lines in the callout; the
     highlighted key takeaway compares current net with "ohne Gehalt" (red below
     break-even, green above),
  5. a compact **Absolutes Netto** curve with a `Bestes Netto/Jahr` Y axis, a
     red/green label for the current comparison with "ohne Gehalt", and four
     linked sliders for both gross salaries and both Abfindungen,
  6. individual vs. joint assessment,
  7. household net income as the gross salary of Partner #1 varies,
  8. approximate marginal tax rates for the Grund- and Splittingtabelle, with
     dashed lines at the start after the Grundfreibetrag, the zone changes
     (~24 %, 42 %) and the top rate (45 % for 2026, 47 % for the 2027 draft),
     non-overlapping `G`/`S` rate labels on the Y axis, short zvE labels in
     three staggered rows below the X axis, and `Aktuell ...` markers with dark
     dashed guides for both tariffs,
  9. severance impact on household net income and total tax burden.

The current optimum Partner #1 salary for the selected Partner #2 salary, and
the optimum Partner #2 salary for the selected Partner #1 salary, are shown as
compact German readouts under every gross slider (input card, both chart slider
rows and the Abfindungsjahr row). The corresponding optimum curves remain
implemented behind `CONFIG.general.show_optimum_curves`, which is currently
false, so they are hidden from both charts and both legends.

Only the compact **Absolutes Netto** curve and **Haushaltsnetto gegen Gehalt von
Partner #1** support axis-limit zoom. Drag a rectangle inside one of those plots
to set new X/Y limits and redraw the chart at the same pixel size; `↺ Zoom
aufheben` restores the configured limits. The SVG viewBox is never scaled, line
widths stay unchanged, and the heatmap, 3D surface, bar charts, progression and
marginal-rate chart have no drag zoom. State is per chart in memory, survives
recalculation and theme changes, and is not saved to local storage.

Everything is rendered from local data. The page loads no scripts, fonts or
styles from the internet.

## Inputs

| Input | Notes |
| --- | --- |
| Tax year | `2026` (final values) or `2027` (draft government proposal). |
| Gross annual salary | One number field with `1,000` spinner steps plus a linked slider (`0`–`150,000` EUR, step `1,000`) per parent. Number fields accept negative annual income down to `-1,000,000 EUR` and large positive values; only the slider clamps to its fixed range. Moving a slider updates the field and recalculates immediately. |
| Insurance type | Checkbox per parent: unticked = GKV, ticked = PKV. |
| PKV monthly KV premium | Private health premium for the employee. |
| PKV monthly PV premium | Private care-insurance premium for the employee. |
| PKV child premium | Monthly premium per child in that private policy (KV + PV combined). |
| PKV children | Number of children in that policy; must not exceed total children. |
| PKV employer subsidy | Monthly employer contribution towards private premiums; capped at the GKV employer share. |
| Number of children | Used for child allowance, child benefit and pension/care contributions. |
| Federal state | Determines the church-tax rate (8% in BY/BW, 9% elsewhere) and the Saxony-specific GKV care-insurance split. |
| Church tax | Per-parent checkbox. |
| Abfindung | One-off gross severance per parent with `1,000` spinner steps; default `100,000` EUR for Partner #1 and `0` for Partner #2. Drives the **Abfindung** report. |
| KV-Zusatzbeitrag | GKV supplementary rate; default 2.9%. |
| Children under 25 | Only then do additional children reduce the GKV care-insurance contribution. |
| Weiterbildung / other Werbungskosten | Annual deductible expenses per parent; uncapped in this model. |
| KV prepayments | Annual health/care-insurance prepayments per parent, capped at three times the current-year statutory contributions (or the modelled PKV deductible). |
| Extra RV contributions | Annual pension contributions per parent beyond the employee contribution, capped at roughly `24.7 %` of the RV contribution ceiling minus modelled employee and employer contributions. |
| Arbeitslosengeld | Annual tax-free wage replacement payment per parent; added to net and applied through the Progressionsvorbehalt. |
| Donations | Household annual donations, capped at `20 %` of the approximated total income. |
| Rental losses | Household annual rental losses, split equally and not capped here. |
| Business losses | Household annual business losses, split equally and capped at `10,000 EUR` for individual assessment or `20,000 EUR` for joint assessment. |

All optimization fields are annual EUR amounts with `100` spinner steps and a
common `0`–`10,000,000 EUR` range. Values above a field's current Höchstbetrag
are clamped automatically before calculation or **speichern**. The German
section explains the statutory anchors in its collapsed details and shows the
applied amounts and limits live; it does not display a separate advisory callout.

The initial scenario is: tax year **2026**, Partner #1 **50,000 EUR**, Partner #2
**50,000 EUR**, federal state **Nordrhein-Westfalen**, **1** child, no church
tax, and an Abfindung of **100,000 EUR** for Partner #1.
These values apply until **speichern** stores a different set locally.

## Calculation rules

### Social contributions

Employee-side contributions are calculated with the annual contribution
ceilings (`BBG`) for the selected year:

- Pension insurance (RV): 18.6%, split equally between employee and employer.
- Unemployment insurance (AV): 2.6%, split equally.
- Health insurance (KV): 14.6% plus the selected supplementary rate, split equally.
- Care insurance (PV): 3.6% total. Employee share is 1.8% (2.3% in Saxony),
  childless employees pay a 0.6% surcharge, and from the second child onwards
  the employee share is reduced by 0.25% per child, capped at 1.0%.

Contributions above the respective ceilings are not charged. Negative gross
income produces no social contributions because the contribution bases are
clamped to zero. The *Jahresarbeitsentgeltgrenze* is shown in the notes, but the
tool continues to calculate statutory health-insurance contributions above it;
private insurance is not modelled.

### Taxable income (`zvE`)

A simplified taxable income is computed as:

```text
zvE = max(0, gross salary
      − employee pension contribution
      − employee health contribution
      − employee care contribution
      − employee allowance (Arbeitnehmer-Pauschbetrag)
      − special-expenses allowance (Sonderausgaben-Pauschbetrag)
      − optimisation expenses and split losses
      − child allowance, if favourable)
```

The unemployment-insurance contribution is **not** part of the simplified
Vorsorgepauschale used here. The optimization section adds the modelled real
expenses and losses; other deductions and special tax rules remain outside this
simplified estimate.

### Income tax, solidarity surcharge and church tax

Income tax is **not** calculated from a formula. The four supplied PDF tables
are embedded in `index.html` as JSON. Each row contains:

```text
zvE | ESt | SolZu | KiSt 8% | KiSt 9%
```

The app uses linear interpolation between the 1,000 EUR steps. Below the first
step the tax is zero; above the last step the slope of the final segment is
continued. The user-selected 1,000 EUR accuracy requirement is therefore met
while avoiding visible jumps between table rows.

- Individual assessment: each parent's `zvE` is looked up in the Grundtabelle.
- Joint assessment: the summed `zvE` is looked up in the Splittingtabelle. The
  joint ESt, SolZu and KiSt are allocated to the two parents in proportion to
  their `zvE`.
- Church tax comes directly from the table's 8%/9% column for individual
  assessment. For joint assessment it is calculated from the allocated ESt;
  because the table columns are exactly `ESt × rate`, the household total
  agrees with the table.

A SolZu of `0 €` is not an error: the embedded table already applies the
Freigrenze and the Anstiegsklausel. The detailed tables show the `zvE` and ESt
for each parent, and the comparison table shows the household `zvE` for both
assessment modes. A callout explicitly explains zero SolZu values.

### Children

For each child the tool compares:

- the annual child benefit (`Kindergeld`), and
- the tax saving from the child allowance (`Kinderfreibetrag`, half per parent
  and child in individual assessment; full allowance in joint assessment).

The child allowance is applied only while it is more favourable than child
benefit. Children also affect the care-insurance rate as described above.

### Optimization inputs in the severance year

The German **Steueroptimierung im Abfindungsjahr** section models genuine cash
outflows that reduce taxable income in the selected year:

- Weiterbildung and other Werbungskosten are added per parent without an
  additional cap in this tool.
- Health-insurance prepayments are limited to three times the modelled
  KV/PV contributions (§ 10 EStG).
- Extra pension contributions are limited to about `24.7 %` of the annual RV
  contribution ceiling minus the modelled employee and employer contributions.
- Donations are limited to `20 %` of the approximated total income
  (§ 10b EStG).
- Rental losses are uncapped here; business losses are capped at `10,000 EUR`
  for individual assessment and `20,000 EUR` for joint assessment. Household
  losses are split equally between the partners.
- Arbeitslosengeld is added tax-free to net income. It raises the tax rate on
  the remaining income through the Progressionsvorbehalt (§ 32b EStG); unused
  employee allowance reduces the progression amount. Its two fields carry a
  green `+ Einnahme` badge and green left border, while every expense/loss
  field carries a red `− Ausgabe` badge and red left border; the written badge
  means the distinction does not rely on colour alone.

Every cap is evaluated from the current year, salaries, insurance settings and
assessment mode. Over-cap inputs are replaced by the allowed amount; the live
callout shows the applied amounts and limits. These values affect all four
severance cases, both assessment modes, the tables, the summary, the heatmap,
the 3D surface and both AbfWork charts. The separate advisory callout has been
removed.

### Net income

```text
net = gross salary
      − employee social contributions
      − optimisation expenses and split losses
      − income tax
      − solidarity surcharge
      − church tax
      + tax-free wage replacement payments
```

Household net income adds the remaining child benefit. In the severance
scenarios, `abfindung` is added to net income as a one-off payment; the
per-month figures shown there are only an even annualisation for orientation.
Negative gross salaries and large expenses can produce negative net values;
none of the charts clamps those values at zero.

### Best-absolute-net heatmap

The second chart samples both salaries on an 18 × 14 grid (all other inputs
fixed). Each cell computes all four cases — individual/joint assessment with
and without the Fünftelregelung — including any Abfindung. The encoded score is
the **best absolute household net**, including Kindergeld:

```text
score         = best(individual net, joint net; with/without Fünftelregelung)
quote         = score / (gross Partner #1 + gross Partner #2 + total Abfindung)
baselineRatio = score / best net at Partner #1 gross = 0
                // same Partner #2 gross and Abfindungen
```

The score and the primary quote both include Kindergeld in the numerator. The
quote is therefore `100 %` only when nothing is deducted and no child benefit is
added; with Kindergeld it can exceed `100 %`. It is undefined when the
denominator (salaries plus Abfindungen) is zero or negative and is shown as `–`.
There is no metric selector any more. The colour scale is labelled
`Bestes Netto/Jahr` and shows EUR, so it can dip below zero and rise again
instead of being capped at `100 %`. This makes the U-shape of
the Abfindung year visible: at low salaries the net falls below the "ohne
Gehalt" baseline, then recovers after the break-even.

The separate `baselineRatio` is shown as **Quote vs. ohne Gehalt**. It is
`100 %` at a Partner #1 salary of zero, falls below `100 %` in the loss zone and
rises above `100 %` once the break-even is passed. It follows the household-net
U-shape but is not the Nettoquote. For decisions about a raise or a severance
payment, the marginal-rate chart remains the right tool.

The winner is encoded by the fill style:

- **Smooth** cells: joint assessment (`Zusammenveranlagung`) gives the higher net.
- **Orange hatched** cells: individual assessment (`Einzelveranlagung`) gives
  the higher net.
- A thin light-red dashed line marks each edge where adjacent cells switch
  between the two winners.
- A purple dashed line traces the break-even (best net with Partner #1 salary
  equals the best net without it) for every Partner #2 salary. A red dotted
  line traces the worst case only where both salaries are positive; negative
  cells still feed break-even and the colour scale. Both come from the same
  sampled row cells and appear in the legend. Neutral dashed guides mark gross
  `0` on both axes.

A readout above the chart always shows the best annual net at the current
salaries, both individual and joint net, and the advantage of the better mode.
Internally it uses the sign convention `joint net − individual net` to decide
which mode to name, but the displayed **advantage is always green**: whether
the winner is `Vorteil Zusammen` or `Vorteil Einzel`, the amount is a benefit
and is not styled as a loss. Joint assessment can reduce net income for some
salary/children/severance combinations; with the default Abfindung and
Fünftelregelung, individual assessment can win. The corresponding **difference in tax burden**
(`joint tax − individual tax`) has the opposite sign.

The four linked sliders sit in one row between the compact **Absolutes Netto**
curve and the flat map: Brutto Partner #1, Brutto Partner #2, Abfindung Partner
#1 and Abfindung Partner #2. Gross sliders are fixed at `0`–`150,000` EUR and
Abfindung sliders at `0`–`500,000` EUR (step `1,000`); all write the number
fields in
**Eingaben**. Because the Abfindung changes the absolute net, moving either
Abfindung slider changes the cell colours and the EUR scale labels immediately.
There is no Fünftelregelung switch: all four cases
(individual/joint × with/without the privileged calculation
`5 × ESt(zvE + A/5) − 4 × ESt(zvE)`) are evaluated and the best net result wins.
The **Bestes Netto/Jahr** readout names the winning mode and Fünftel treatment
and lists all four net amounts.

Every cell tooltip lists Partner #1 and Partner #2 gross, all four net figures,
which mode and Fünftel treatment win, the advantage, the Nettoquote, the separate
quote versus "ohne Gehalt" and the Abfindung. The sliders stay at 0–150,000 EUR
for gross and 0–500,000 EUR for Abfindung, but both chart axes start at
`-100,000 EUR` so negative salaries and net values are visible. They extend
further down for strongly negative typed values and zoom on the positive side
through 250k, 500k, 1M, 2M, 5M and 10M EUR. The positive scale expands only when
a salary passes 90 % of the current maximum and contracts when both salaries
drop below 50 %; tick steps are rounded so the resolution stays readable. A dashed crosshair marks the current
inputs, and the household net (including Kindergeld) together with the current
Nettoquote and baseline comparison is labelled beside the moving point. All
sliders are linked to the input fields and to each other through one delegated
listener; outputs update immediately, recalculation is capped at one animation
frame, and the expensive heatmap/AbfWork sweeps are cached, so dragging remains
smooth while the heatmap updates.

The compact curve also follows the Partner #1 slider. Its moving point label is
coloured red when it says `weniger als ohne Gehalt` and green otherwise, so the
loss zone is readable at a glance.

### 3D best-net surface

Directly below the flat heatmap, the same computed cells are drawn as a pure-SVG
isometric surface. Height and colour both encode the best absolute net in EUR,
so the best combinations form visible peaks. The green marker labels the highest
net in the current grid with both salaries, the amount, the Nettoquote and the
baseline comparison; the white marker shows the current inputs. A violet dashed
cross-section line traces the best net for every Partner #1 salary at the
currently selected Partner #2 salary. The depth edge is drawn as an explicit
axis and labelled `Tiefe: Bruttojahresgehalt Partner #2 →`; neutral dashed
guides mark gross `0` on both gross axes. Two further labelled ridges trace the
break-even (purple dashed, `Break-even`) and the worst case (red dotted,
`Worst case`) only where both salaries are positive. Four dedicated sliders
directly above the surface — Brutto Partner #1, Brutto Partner #2, Abfindung
Partner #1 and Abfindung Partner #2 — write the same main inputs, so both
diagrams and all tables stay in sync. The cell data is computed only once per
recalculation.

### On-page quote explanation

A card at the end of the page repeats the Nettoquote formula in German and shows
a fixed worked example with Partner #1 gross `50,000`, Partner #2 gross
`60,000` and Partner #1 Abfindung `200,000` (Partner #2 Abfindung `0`). The best
net is computed with the current year, children, state and insurance settings;
the old supplied `72.51 %` example has been removed. The card also explains the
separate "Quote vs. ohne Gehalt".

The compact curve is titled **Absolutes Netto**. Both salaries and both
Abfindungen are controlled by the four linked sliders; the curve sweeps Partner
#1 on the X axis while Partner #2 stays at its selected value, and moving the
Partner #2 slider recalculates the whole curve. Its Y axis is labelled
`Bestes Netto/Jahr` in EUR.

### "Lohnt sich Arbeiten im Abfindungsjahr?"

This chart sweeps the gross salary of Partner #1 across the X axis, starting at
`-100,000 EUR` and extending for more negative typed values. It has a second
gross slider for **Partner #2 im Abfindungsjahr**, linked to the main
Partner #2 gross input; that salary stays constant while the curves are sampled.
The dashed "ohne Gehalt" references are still evaluated at gross `0`, and a
neutral dashed guide marks that zero position. An additional slider sets the
Abfindung of Partner #1 for this view. At each
sampled Partner #1 salary it draws four nets: individual and joint assessment,
each **with and without the Fünftelregelung**. Solid curves use the
Fünftelregelung, dash-dot curves do not. Break-even, worst case and the current
markers still use the best of all four variants at each salary.

- **Break-even** (purple dashed line): the last sampled crossing where the best
  "with salary" net again reaches the best net at Partner #1 gross `0`. Below
  it, working reduces household net; the red band is clipped there. The value
  is recalculated from the current inputs, including negative salaries.
- **Worst case** (vertical red dotted line plus a horizontal red dashed line at
  its net level): the sampled gross salary with the lowest best "with salary"
  net, considering only samples where both partners' gross salaries are above
  zero. Negative gross stays in the curves and feeds break-even, but cannot
  become the worst case. No fixed example is assumed; if Partner #2 is not
  positive, the marker and gap are omitted.
- A bracket between the worst-case and break-even levels shows the EUR gap the
  household net must recover.
- The callout puts break-even, worst case and the gap on separate lines. It also
  reports `Netto aus der Abfindung (bei den aktuellen Gehältern)`: the best net
  with the entered Abfindungen minus the best net at the same salaries with both
  Abfindungen set to zero, together with the gross Abfindung and both net
  amounts. With no Abfindung it shows `0 €`.
- The highlighted key takeaway is `Bei aktuellem BruttoGehalt ... bringt Arbeiten ...
  weniger/mehr Netto als ohne Gehalt.` It is red below the break-even (working
  reduces household net) and green above it. The former EUR `45,000` example and
  the separate "Ohne Gehalt" line have been removed; the `+1,000 EUR` marginal
  readout is no longer shown because a positive marginal gain can coexist with
  a net loss relative to not working.
- A collapsed **Berechnung Schritt für Schritt** section below the callout
  explains every displayed value: inputs, the base scenarios without Abfindung,
  all four current severance cases with tax/Soli/church tax/social contributions,
  additional expenses/losses and tax-free payments, the Abfindung net gain, the
  "ohne Gehalt P1" reference, the negative-inclusive sweep formulas for
  break-even/worst case/gap and the current comparison.
- Black dashed guides run horizontally from the two current "mit Gehalt"
  points to the Y axis. They move with the Partner #1 salary slider; changing
  the Partner #2 slider moves the current point and recalculates all curves.

### Grenzsteuersatz

The marginal-rate chart uses dashed lines to mark where each tariff changes
zone: the start after the Grundfreibetrag, the change into the second
progression zone (~`24 %`), the entry into the `42 %` zone and the start of the
top rate (`45 %` for 2026). The X axis reaches `600,000 EUR` zvE so the 45 %
threshold is visible for both the Grundtarif and the Splittingtarif. The
matching rate is written on the Y axis as `G ...` (Grundtarif) or `S ...`
(Splittingtarif), with overlapping labels shifted apart. The corresponding zvE
values are written as short amounts in three staggered, rotated rows below the
X axis, so nearby markers stay readable. Dark dashed guides and circles labelled
`Aktuell ...` mark the current values of both tariffs; their zvE amounts are
bold in the axis labels.

### Abfindung and Fünftelregelung

Each severance amount is treated as a one-off gross payment in the selected
tax year. No social contributions are charged on it. Two treatments are shown
for both assessment modes:

- **Regular (mit Abfindung):** the full amount is added to `zvE` and the tax
  comes directly from the Grundtabelle (individual) or Splittingtabelle (joint).
- **Fünftelregelung (§ 34 EStG):** the tax attributable to the severance is

  ```text
  ESt_total = 5 × ESt(zvE + A/5) − 4 × ESt(zvE)
  ```

  For joint assessment, the sum of both severance payments is added to the
  joint `zvE`, and the resulting joint tax is allocated by income share.

Because the tax is modified, SolZu is derived from the resulting ESt by an
inverse lookup in the same embedded table, so the Freigrenze and
Anstiegsklausel remain exactly as in the PDF. Church tax is `ESt × 8%/9%` as
usual. The child-allowance decision and social contributions are taken from
the scenario without severance; this is a deliberate simplification.

The report always shows all six combinations. In reality the Fünftelregelung
may only be used when it is more favourable (§ 34 Abs. 1 Satz 5 EStG) and only
if the statutory conditions apply — neither is checked by this tool. A
callout compares the regular and fifth-based tax for each assessment mode.

## Parameters and sources

### 2026 (final)

- RV/AV ceiling: 101,400 EUR/year
- KV/PV ceiling: 69,750 EUR/year
- Jahresarbeitsentgeltgrenze: 77,400 EUR/year
- Employee allowance: 1,230 EUR
- Child allowance: 9,756 EUR per child
- Child benefit: 259 EUR/month per child

### 2027 (draft)

- RV/AV ceiling: 106,200 EUR/year
- KV/PV ceiling: 76,500 EUR/year
- Jahresarbeitsentgeltgrenze: 84,150 EUR/year
- Employee allowance: 1,430 EUR
- Child allowance: 10,056 EUR per child
- Child benefit: 267 EUR/month per child
- Contribution rates and supplementary rates are assumed unchanged where the
  draft does not specify otherwise.

Sources:

- Supplied 1,000 EUR overview tables in `tabelle/`
  (`grundtabelle-*-ueberblick-klein.pdf`,
  `splittingtabelle-*-ueberblick-klein.pdf`, finanz-tools.de).
- 2027 draft: Regierungsentwurf EStReformG 2027, cabinet decision
  02.09.2026, status 06.11.2026 (BT-Drs. 21/8235).
  <https://www.bundesfinanzministerium.de/Content/DE/Pressemitteilungen/Finanzpolitik/2026/09/2026-09-02-einkommensteuerreform.html>
- Social-insurance parameters: AOK contribution and calculation values.
  <https://www.aok.de/fk/tools/weitere-inhalte/beitraege-und-rechengroessen-der-sozialversicherung/sv-werte/>

## Configuration

`config.ini` is the single source of truth for configurable values. It defines
the default scenario, number/slider limits, tax parameters, federal states,
colours, chart geometry and note text. The HTML file must not be edited by hand
for these values: after changing the `.ini`, run `tools/generate_config.py` to
embed it between the `CONFIG_START` / `CONFIG_END` markers. The browser never
reads `config.ini`, so `index.html` remains dependency-free at runtime.

The generator checks that the fixed gross slider maximum matches both the
initial Abfindungsjahr chart maximum and the heatmap axis maximum (currently
`150,000 EUR`). Sliders stay at that cap; number fields accept larger and
negative values. `plot_min` sets the negative chart domain (`-100,000 EUR` by
default, extended for strongly negative typed values), while `zoom_steps`
defines the positive chart-only zoom domain up to `number_max`. The configured
default theme is `dark`.

## Regenerating and verifying the tables

Python is only needed for development, not for using the HTML file.

```bash
py -3 -m pip install pypdf
py -3 tools/generate_config.py
py -3 tools/generate_tables.py
py -3 tools/verify_calculation.py
```

`generate_config.py` replaces the JSON between the `CONFIG_START` /
`CONFIG_END` markers. `generate_tables.py` replaces the JSON between the
`TABLES_START` and `TABLES_END` markers in `index.html` and reads the four PDFs
from `tabelle/`. `verify_calculation.py` checks that:

- every one of the 1,040 rows in each of the four PDFs is present in
  `index.html` with identical values,
- the 1,000 EUR steps are consecutive,
- exact table rows, interpolation midpoints and extrapolation beyond the last
  row are reproduced by the Python mirror of the JavaScript `lookup()`,
- the church-tax columns equal `ESt × 8%` / `ESt × 9%`.

Current verification result: all four tables pass with a maximum difference of
`0.00e+00` between PDF and embedded values. A browser-side check of the actual
JavaScript `lookup()` covered 8,316 row and midpoint values with a maximum
floating-point error of `3.6e-15`; 512 tax-scenario combinations and 1,280
`zvE` checks also passed. A dedicated browser check of the severance logic
covered 6,912 assertions across both years, three federal states, several
salary/children/severance combinations and both assessment modes: the regular
and fifth-based ESt formulas, the SolZu inverse lookup, the income-expense
decomposition and the zero-severance identity with the base scenarios all
passed (maximum floating-point error `2.9e-11`).

The current cache-busted browser check (`?v=107`) rendered nine SVGs with no
console errors and no `NaN`/`Infinity`. It verified the dark default and
persisted theme toggle, **speichern** persistence for inputs, optimization
amounts and theme, automatic cap clamping and the cap callout, zero guides in
all gross plots, the labelled 3D depth axis, positive-only worst-case markers
in both AbfWork and the heatmap/3D ridges, negative Partner #1 and Partner #2
salaries with negative net values and axis/scale labels, the red/green
compact-curve comparison label, the income/expense badges and field borders,
the absence of the separate advisory callout, the optimum-value readouts under
all eight gross sliders while the two optimum curves stay hidden, and
axis-limit drag zoom on only the two named line charts: the SVG viewBox and
stroke widths stay unchanged, the axis labels change, heatmap data is
untouched, the German `↺ Zoom aufheben` button restores the limits, and zoom
state survives recalculation and theme changes without being saved.

## Disclaimer

The 2027 values are based on a draft law and may change. This tool is a
simplified estimate for comparison purposes only. It is not tax advice. For a
binding calculation, consult a tax adviser.
