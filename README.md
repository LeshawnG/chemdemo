# Lab 3 Bench — sources (not published)

Build sources for `lab3/` on `main`. GitHub Pages deploys `main` only, so nothing here is on the site.

## Setup
    mkdir npmtmp && cd npmtmp && npm init -y && npm install three@0.128.0 @fontsource/ibm-plex-sans@5.0.8 @fontsource/ibm-plex-mono@5.0.8 && cd ..

## App
    python3 build.py          # → out/lab3-bench.html (artifact) and out/github/lab3/index.html (Pages)
`sheets.json` (if present) is baked in as "Lab sheets" in Part 2.

## Part 2 sheets → app + add-on PDF
    python3 findlattice.py photo.jpg            # prints primitive a, b (px) + overlay PNG; check by eye
    # write sheets_input.json (see part2_addon.py docstring; test_in.json is an example)
    python3 part2_addon.py sheets_input.json    # → sheets.json + out/addon.html
    python3 render_pdf.py out/addon.html out/Lab3_Part2_Addon.pdf
    python3 build.py                            # rebuild app with sheets → copy out/github/lab3/index.html to main:lab3/

## Companion PDF
    python3 gen_sym.py && python3 figs.py && python3 pdf_build.py && python3 render_pdf.py out/companion.html out/Lab3_Companion.pdf
