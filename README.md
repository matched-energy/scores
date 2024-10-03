Overview
====================
- **Goal:** calculate temporally-matched scores for UK suppliers.
- **Context:** https://matched.energy/overview/how-renewable-is-our-electricity/
- **Methodology:** https://matched.energy/scores/methodology/

Quick start
====================

Download sample data
----------
https://www.dropbox.com/scl/fo/ej3kagc932mzpedqyf8m6/ADKutwWd1iYDwxhhfEY8m_E?rlkey=1914ovaujkyc2o1wv9ix372o7&st=iv218ufs&dl=0

Setup
----------
Edit and execute `env.sh`:
- `MATCHED_DATA` should point to the downloaded data

Run
----------
This will run the entire workflow for a few suppliers on a few days and output the results to `/tmp`:

`python workflow/run.py configuration/run_long_test.yaml`
