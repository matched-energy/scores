Overview
====================
- **Goal:** calculate temporally-matched scores for UK suppliers.
- **Context:** https://matched.energy/overview/how-renewable-is-our-electricity/
- **Methodology:** https://matched.energy/scores/methodology/

Quick start
====================

Download data
----------
https://www.dropbox.com/scl/fo/5ito3kxb9njrop9u0wct6/ANkfP39_z8FPmm4FF_jK3wU?rlkey=sd2o4suyihzpt2q5tsi3992g7&st=jgolydim&dl=0

Setup
----------
Edit and execute `env.sh`:
- `MATCHED_DATA` should point to the downloaded data

Run
----------
This will run the entire workflow for a few suppliers on a few days and output the results to `/tmp`:

`python workflow/run.py configuration/run_long_test.yaml`
