# Submission checklist

## Files
- [x] `paper-en-anon.docx` — anonymized manuscript (no author names, affiliations, emails, ORCID or repository URL)
- [x] `title-page.docx` — author details and declarations (uploaded separately)
- [x] `cover-letter.md` — cover letter
- [x] `figures/` — five figures at 300 dpi
- [x] `REPRODUCE.md` — table/figure to script mapping

## Before upload
- [ ] Confirm whether the journal uses double-blind review; if single-blind, use `paper-en.docx` instead
- [ ] Reference style converted to the journal's required format (currently numbered, Springer Basic-like)
- [ ] Declarations moved to the journal's required position (some templates place them before References)
- [ ] Page count and abstract length checked against the author guidelines (abstract is 263 words)
- [ ] Data availability statement: decide between the repository link (single-blind) and "available upon acceptance" (double-blind)
- [ ] ORCID and affiliation verified in the submission system
- [ ] Run `python scripts/audit_numbers.py` once more after any edit

## Known limitations to acknowledge (already stated in the manuscript)
- Adaptive-RAG and CRAG are behavioural approximations, not exact reproductions (Appendix C)
- The synthetic corpus is small; real-corpus results are retrieval-level (Section 8)
- The BEIR gain fails on the adversarial arguana subset (Section 6.9)
- Order-dependent costs break the theoretical guarantee (Section 6.15)
- Per-query thresholding does not improve on a global threshold (Section 6.17)
