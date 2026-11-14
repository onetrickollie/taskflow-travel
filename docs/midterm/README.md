# Midterm report source

LaTeX source for the CSCI 566 midterm report (ICML 2026 two-column format,
`preprint` option, numeric citations).

## Build

```
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

or upload this folder to Overleaf (compiler: pdfLaTeX). A self-contained
alternative is `tectonic -X compile main.tex`.

## Notes

- `icml2026.sty` is the course-provided ICML 2026 style with **one local
  patch**: the mandatory-corresponding-author error branch inside
  `\printAffiliationsAndNotice` was removed (course reports carry no
  correspondence footnote; with the stock style the footer would print
  `AUTHORERR: Missing \icmlcorrespondingauthor`). Keep this patched copy if
  you rebuild.
- Citations are forced back to numeric (`\setcitestyle{numbers,square,...}`
  in `main.tex`, after the style file sets author-year).
- `figures/pareto.png` is regenerated from `metrics.json` (repo git
  `50777f0`) with `tools/redraw_pareto.py`:

  ```
  python tools/redraw_pareto.py metrics.json figures/pareto.png
  ```

  The original auto-generated figure had colliding per-point labels in the
  top-left cluster. All plotted values are read from `metrics.json` directly.
- `figures/error_vs_step.png` and `figures/recovery.png` are the committed
  repo figures, unmodified.
- Numbers in the tables come from `results/REPORT.md` / the referenced
  `results/runs/*` reports at git `50777f0`; `metrics.json` here is a copy
  of `results/metrics.json` at that commit, kept so the figure rebuilds
  without a full evaluation run.
