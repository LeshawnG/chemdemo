# Lab 4 Bench and Lab 4 Companion: sources (not published)

GitHub Pages deploys `main` only, so nothing on this branch is on the site.

## App (`app/`)
    mkdir npmtmp && cd npmtmp && npm init -y && npm install three@0.128.0 && cd ..
    python3 eht.py && python3 mkdata.py   # extended Hückel for NH3 -> mo.json (needs numpy, scipy)
    python3 build.py                      # -> out/lab4-bench.html (artifact) and out/github/lab4/ (Pages)
    node icons.js $PWD/icon.svg $PWD/out/github/lab4   # then resize to 192 and 180
Copy `out/github/lab4/*` to `main:lab4/`.

## Companion PDF (`pdf/`)
Needs IBM Plex Sans/Mono woff2 from @fontsource and a `fonts.css` pointing at them (see build.py).
    python3 build.py && node print.js $PWD/lab4.html $PWD/lab4.pdf
