# Cardiac MRI Reference Converter

### ▶ [**Open the live tool**](https://nethahussain.github.io/cardiac-mri-reference-converter/)

**Use it now in your browser — no install:** https://nethahussain.github.io/cardiac-mri-reference-converter/

(Or download `Cardiac-MRI-Reference-Converter.html` and open it locally — it works fully offline.)

---

A single-file, offline web tool that converts cardiac MRI (CMR) measurements into
age-, sex-, and ethnicity-specific reference comparisons, using the reference ranges
published by the **Healthy Hearts Consortium** (Raisi-Estabragh et al., *JACC
Cardiovascular Imaging*, 2024).

Enter a patient's volumes and masses, and the tool
computes the derived metrics, indexes them to body size, and flags every value as
**low / normal / high** against the matching published reference range — then produces
a clean, copy-ready report.

> **For clinical decision support and education only.** This is not a medical device.
> Always verify against local guidelines and the original publication.

---

## Features

- **Four chambers** — left ventricle (LV), right ventricle (RV), left atrium (LA), right atrium (RA).
- **Three segmentation methods** — *smooth*, *papillary*, and *anatomical* (selectable; the reference ranges switch accordingly).
- **Two body-size corrections** — body surface area (BSA, Mosteller) and height.
- **30 parameters** — volumes (EDV, ESV, SV) and their indexed forms, ejection fraction, cardiac output, and systolic & diastolic myocardial mass for the ventricles, plus maximal/end-systolic volumes and ejection fraction for the atria.
- **Automatic derivation** — stroke volume, ejection fraction, cardiac output, BSA/height indexing, and atrial ejection fraction are all computed for you.
- **Visual gauges** — every parameter is shown on a gauge marking the normal band and the patient's position.
- **Copy-ready report** — a formatted, editable text report for pasting into a radiology system.
- **Editable reference values** — a password-protected workspace lets you adjust the stored reference ranges (saved locally in the browser).
- **Fully offline** — one self-contained HTML file. No server, no tracking, no data leaves the browser.

---

## Usage

1. Open the tool — **online** at https://nethahussain.github.io/cardiac-mri-reference-converter/, or download **`Cardiac-MRI-Reference-Converter.html`** and open it locally (works fully offline).
2. Enter the patient's **sex, ethnicity, date of birth, weight, height**, and (optionally) **heart rate**.
3. Choose the **segmentation method** and **indexing** that match how your measurements were obtained.
4. Type the **measurements** for each chamber (left & right atrium are optional).
5. Read the **results & reference comparison**, and click **Copy report to clipboard**.

No installation, build step, or internet connection is required.

---

## Reference data & method

All reference ranges are the **95% prediction intervals** from:

> Raisi-Estabragh Z, et al. *Cardiovascular Magnetic Resonance Reference Ranges From the
> Healthy Hearts Consortium.* JACC Cardiovasc Imaging. 2024.
> [doi:10.1016/j.jcmg.2024.01.009](https://www.jacc.org/doi/epdf/10.1016/j.jcmg.2024.01.009)

The consortium pooled 9,088 CMR studies and modelled smooth reference ranges across age,
stratified by sex and ethnicity, for three predefined segmentation protocols and two
body-size corrections. The reference values are released under
[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).

- **`cmr_reference_ranges.json`** — the complete extracted dataset used by the tool:
  5 ethnicities × 2 sexes × 3 segmentations × 2 indexings × 4 chambers × up to 6 age groups.
- **`smooth_bsa_reference_ranges.json`** — the smooth + BSA subset, used to validate the extraction.
- **`extract_refs.py`** — extracts every reference table from the publication's supplemental
  appendix and validates the smooth+BSA subset against the file above (1,317 cells, 0 mismatches).

Because some ethnicity groups had limited data, certain younger age bands are not available
for every ethnicity; the tool shows measured values without a comparison in those cases and
states this explicitly.

---

## Calculations (summary)

| Quantity | Formula |
|---|---|
| Body surface area (Mosteller) | √(weight_kg × height_cm / 3600) |
| Stroke volume (SV) | EDV − ESV |
| Ejection fraction (EF) | (SV / EDV) × 100 |
| Cardiac output (CO) | SV × heart rate / 1000 |
| BSA-indexed value | value / BSA |
| Height-indexed value | value / height_m |
| Atrial ejection fraction | (V_max − V_min) / V_max × 100 |

Full details are in **`docs/Calculations_Documentation.docx`**, and the complete reference
tables are in **`docs/Reference_Values.docx`**.

---

## Project structure

```
Cardiac-MRI-Reference-Converter.html   The tool (English) — open this in a browser
Hjart-MR-Referensomvandlare.html       Original Swedish version
cmr_reference_ranges.json              Full extracted reference dataset (CC0)
smooth_bsa_reference_ranges.json       Smooth + BSA subset (extraction validation source)
extract_refs.py                        Reference-table extraction & validation script
docs/Calculations_Documentation.docx   Formulas & methods
docs/Reference_Values.docx             Complete reference tables
README.md
LICENSE
```

---

## Data & privacy

This repository contains **no patient data**. Example CMR segmentation XML files and the
publisher's copyrighted article PDF/appendix are deliberately **excluded** and listed in
`.gitignore`. Only the tool, the CC0 reference values, and the documentation are included.

---

## Credits

Developed by **Caroline Berntsson** and **Netha Hussain**.
Questions or error reports: netha.hussain@vgregion.se

## License

The Healthy Hearts Consortium reference values are released under
[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). See `LICENSE`.
