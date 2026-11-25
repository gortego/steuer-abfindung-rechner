# German tax and net-income comparison tool

A self-contained, single-file HTML calculator for comparing the annual tax,
social-insurance and private-insurance burden of two parents in Germany under:

- **Einzelveranlagung** — individual assessment using the *Grundtabelle*
- **Zusammenveranlagung** — joint assessment using the *Splittingtabelle*

The user interface and all results are in German, apart from the small
`by gortego` credit at the bottom of the page. The browser title and page
heading are `Abfindung, Steuerlast & Brutto`. This document is in English.

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
   underneath them), the number of children and the federal state.
3. Tick **Privat versichert (PKV)** for a parent who is privately insured;
   leave it unticked for **gesetzlich (GKV)**. For PKV, expand
   **Erweiterte Annahmen** and enter the monthly private premiums, employer
   subsidy and children covered.
4. Tick the church-tax checkboxes where applicable.
5. Enter an optional one-off **Abfindung** for either parent (0 = none).
6. Optional: in **Erweiterte Annahmen** change the GKV supplementary rate or
   state whether all children are under 25.
7. All results update automatically as soon as any input changes; there is no
   separate calculate button.
8. Optional: click **speichern** to store the current inputs and the selected
   dark/light design as new defaults in this browser. They are loaded on the
   next run. This uses local browser storage only; `config.ini` and the single
   HTML file are not modified. The ☀️/🌙 button in the header switches between
   the funky dark and light designs immediately.

The built-in defaults are tax year 2026, gross salaries of `50,000 EUR` for
both partners, one child, federal state NW, GKV for both partners, no church
tax, Partner #1 Abfindung `100,000 EUR` and Partner #2 Abfindung `0 EUR`.
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
- eight SVG charts:
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
     Abfindung year, with independent gross sliders for both partners, two net
     curves (Einzel/Zusammen with the salary of Partner #1), two dashed
     "Abfindung only" baselines and a red band (up to the break-even) where
     working *reduces* net income. A purple dashed line marks the break-even, a
     red dotted line (plus a horizontal red dashed net-level line) the worst
     case, and black dashed guides follow the two current "mit Gehalt" points
     to the Y axis; all four values are labelled at the current salary. A
     bracket shows the net difference from the worst case to the break-even.
     Break-even, worst case and gap are on separate lines in the callout; the
     highlighted key takeaway compares current net with "ohne Gehalt" (red below
     break-even, green above),
  5. individual vs. joint assessment,
  6. household net income as the gross salary of Partner #1 varies,
  7. approximate marginal tax rates for the Grund- and Splittingtabelle, with
     dashed lines at the start after the Grundfreibetrag and the zone changes
     (~24 %, 42 %), non-overlapping `G`/`S` rate labels on the Y axis, short zvE
     labels in three staggered rows below the X axis, and `Aktuell ...` markers
     with dark dashed guides for both tariffs,
  8. severance impact on household net income and total tax burden.

Everything is rendered from local data. The page loads no scripts, fonts or
styles from the internet.

## Inputs

| Input | Notes |
| --- | --- |
| Tax year | `2026` (final values) or `2027` (draft government proposal). |
| Gross annual salary | One number field with `1,000` spinner steps plus a linked slider (`0`–`150,000` EUR, step `1,000`) per parent. Moving a slider updates the field and recalculates immediately; larger typed values are clamped in the slider only. |
| Insurance type | Checkbox per parent: unticked = GKV, ticked = PKV. |
| PKV monthly KV premium | Private health premium for the employee. |
| PKV monthly PV premium | Private care-insurance premium for the employee. |
| PKV child premium | Monthly premium per child in that private policy (KV + PV combined). |
| PKV children | Number of children in that policy; must not exceed total children. |
| PKV employer subsidy | Monthly employer contribution towards private premiums; capped at the GKV employer share. |
| Number of children | Used for child allowance, child benefit and pension/care contributions. |
| Federal state | Determines the church-tax rate (8% in BY/BW, 9% elsewhere) and the Saxony-specific GKV care-insurance split. |
| Church tax | Per-parent checkbox. |
| Abfindung | One-off gross severance per parent with `1,000` spinner steps; default `360,000` EUR for Partner #1 and `0` for Partner #2. Drives the **Abfindung** report. |
| KV-Zusatzbeitrag | GKV supplementary rate; default 2.9%. |
| Children under 25 | Only then do additional children reduce the GKV care-insurance contribution. |

The initial scenario is: tax year **2026**, Partner #1 **120,000 EUR**, Partner #2
**65,000 EUR**, federal state **Nordrhein-Westfalen**, **3** children, church
tax only for **Partner #2**, and an Abfindung of **360,000 EUR** for Partner #1.
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

Contributions above the respective ceilings are not charged. The
*Jahresarbeitsentgeltgrenze* is shown in the notes, but the tool continues to
calculate statutory health-insurance contributions above it; private
insurance is not modelled.

### Taxable income (`zvE`)

A simplified taxable income is computed as:

```text
zvE = gross salary
      − employee pension contribution
      − employee health contribution
      − employee care contribution
      − employee allowance (Arbeitnehmer-Pauschbetrag)
      − special-expenses allowance (Sonderausgaben-Pauschbetrag)
      − child allowance, if favourable
```

The unemployment-insurance contribution is **not** part of the simplified
Vorsorgepauschale used here. Further deductions such as actual work expenses,
private insurance, company pensions and special tax rules are not included.

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

### Net income

```text
net = gross salary
      − employee social contributions
      − income tax
      − solidarity surcharge
      − church tax
```

Household net income adds the remaining child benefit. In the severance
scenarios, `abfindung` is added to net income as a one-off payment; the
per-month figures shown there are only an even annualisation for orientation.

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
added; with Kindergeld it can exceed `100 %`. There is no metric selector any
more. The colour scale is labelled `Bestes Netto/Jahr` and shows EUR, so it can
dip and rise again instead of being capped at `100 %`. This makes the U-shape of
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
  line traces the worst case (lowest best net). Both are computed from the same
  sampled row cells and appear in the legend.

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
#1 and Abfindung Partner #2. Gross ranges are `0`–`150,000` EUR and Abfindung
ranges `0`–`500,000` EUR (step `1,000`); all write the number fields in
**Eingaben**. Because the Abfindung changes the absolute net, moving either
Abfindung slider changes the cell colours and the EUR scale labels immediately.
There is no Fünftelregelung switch: all four cases
(individual/joint × with/without the privileged calculation
`5 × ESt(zvE + A/5) − 4 × ESt(zvE)`) are evaluated and the best net result wins.
The **Bestes Netto/Jahr** readout names the winning mode and Fünftel treatment
and lists all four net amounts.

Every cell tooltip lists Partner #1 and Partner #2 gross, all four net figures,
which mode and Fünftel treatment win, the advantage, the Nettoquote, the separate
quote versus "ohne Gehalt" and the Abfindung. Both axes start at 0–150,000 EUR
and zoom together with the gross sliders through 250k, 500k, 1M, 2M, 5M and
10M EUR. The scale expands only when a salary passes 90 % of the current
maximum and contracts when both salaries drop below 50 %; tick steps are
rounded so the resolution stays readable. A dashed crosshair marks the current
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
currently selected Partner #2 salary. Two further labelled ridges trace the
break-even (purple dashed, `Break-even`) and the worst case (red dotted,
`Worst case`) across all Partner #2 salaries. Four dedicated sliders directly above the
surface — Brutto Partner #1, Brutto Partner #2, Abfindung Partner #1 and
Abfindung Partner #2 — write the same main inputs, so both diagrams and all
tables stay in sync. The cell data is computed only once per recalculation.

### On-page quote explanation

A card at the end of the page repeats the Nettoquote formula in German and shows
a fixed worked example with Partner #1 gross `50,000`, Partner #2 gross
`60,000` and Partner #1 Abfindung `200,000` (Partner #2 Abfindung `0`). The best
net is computed with the current year, children, state and insurance settings;
the old supplied `72.51 %` example has been removed. The card also explains the
separate "Quote vs. ohne Gehalt".

The compact curve is titled **Absolutes Netto**. Both salaries and both
Abfindungen are controlled by the four linked sliders; the curve sweeps Partner
#1 while Partner #2 stays at its selected value, and its Y axis is labelled
`Bestes Netto/Jahr` in EUR.

### "Lohnt sich Arbeiten im Abfindungsjahr?"

This chart sweeps the gross salary of Partner #1 across the X axis. It has a
second gross slider for **Partner #2 im Abfindungsjahr**, linked to the main
Partner #2 gross input; that salary stays constant while the curves are sampled.
An additional slider sets the Abfindung of Partner #1 for this view. At each
sampled Partner #1 salary it computes individual and joint net **with** and
**without** the salary of Partner #1, always choosing the better of the two
assessment modes.

- **Break-even** (purple dashed line): the last sampled crossing where the best
  "with salary" net again reaches the best "without salary" net. Below it,
  working reduces household net because of the Fünftelregelung interaction; the
  red band is clipped there. With the built-in defaults this is `31,775 EUR`.
- **Worst case** (vertical red dotted line plus a horizontal red dashed line at
  its net level): the sampled gross salary where the best "with salary" net is
  lowest. With the built-in defaults this is `17,500 EUR` (`124,221 EUR` net).
- A bracket between the worst-case and break-even levels shows the EUR gap the
  household net must recover.
- The callout puts break-even, worst case and the gap on separate lines. The
  highlighted key takeaway is `Bei aktuellem BruttoGehalt ... bringt Arbeiten ...
  weniger/mehr Netto als ohne Gehalt.` It is red below the break-even (working
  reduces household net) and green above it. The former EUR `45,000` example and
  the separate "Ohne Gehalt" line have been removed; the `+1,000 EUR` marginal
  readout is no longer shown because a positive marginal gain can coexist with
  a net loss relative to not working.
- Black dashed guides run horizontally from the two current "mit Gehalt"
  points to the Y axis. They move with the Partner #1 salary slider; changing
  the Partner #2 slider moves the current point and recalculates all curves.

### Grenzsteuersatz

The marginal-rate chart uses dashed lines to mark where each tariff changes
zone: the start after the Grundfreibetrag, the change into the second
progression zone (~`24 %`) and the entry into the flat top zone (`42 %`). The
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

The generator checks that the initial gross-salary slider maximum matches both
the Abfindungsjahr chart maximum and the heatmap axis maximum (currently
`150,000 EUR`). `zoom_steps` then defines the shared zoom domain up to
`number_max`; the chart and slider maxima are only the starting window, not a
hard cap.

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

## Disclaimer

The 2027 values are based on a draft law and may change. This tool is a
simplified estimate for comparison purposes only. It is not tax advice. For a
binding calculation, consult a tax adviser.
