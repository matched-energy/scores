Goal
====================

Calculate time-matched scores for UK suppliers.

Methodology
====================

### Determine monthly generation for each supplier
- From REGO registry
- `supplier_monthly_generation.py`

### Calculate half-hourly generation for each supplier
- By fitting monthly profile to half-hourly historic grid mix
- `grid_monthly_generation.py`
- function _calculate_supplier_generation_ in  `supplier_time_matched_scores.py` (to be moved)

### Determine half-hourly load for each supplier
- From Elexon S0142 files
- `supplier_hh_load_by_day.py`
- `supplier_hh_load_concatenated.py`

### Calculate time-matched scores
- `supplier_time_matched_scores.py`

Data Sources
====================

#### REGOS
https://renewablesandchp.ofgem.gov.uk/Public/ReportViewer.aspx?ReportPath=/DatawarehouseReports/CertificatesExternalPublicDataWarehouse&ReportVisibility=1&ReportCategory=2

#### BM Units
https://bmrs.elexon.co.uk/api-documentation/endpoint/reference/bmunits/all

#### Historic grid mix
https://www.nationalgrideso.com/data-portal/historic-generation-mix

#### Elexon S0142
https://www.elexonportal.co.uk/scripting?cachebust=i2dnjkr3ui


Preliminary results
====================
For year ending 03/2023:
- Good Energy ~90%
- Octopus ~70%
- So Energy ~70%

Outstanding Issues
====================
- Underestimating annual matching scores by ~6% for Good Energy and Octopus
- Could/should improve estimation of half-hourly generation (i.e. AB's approach)
- Code needs to be much improved!
