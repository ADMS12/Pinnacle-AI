# Duc-TOS: Schwab trading pattern dashboard

Open **Trading-Dashboard.html** in a browser. It is self-contained (Chart.js loads from a CDN, so it needs internet the first time).

## Regenerate from a new Schwab export

1. In Schwab, export Order Status to CSV (same columns as the current file).
2. Drop the CSV in this folder.
3. Run:

```
python build_dashboard.py <new-export>.csv
```

That rewrites Trading-Dashboard.html. Pass a second argument to write somewhere else.

## Files

- `build_dashboard.py` - parses the CSV, pairs Buy to open / Sell to close fills FIFO into round trips, marks never-sold lots as expired worthless, and injects the data into the template.
- `dashboard_template.html` - the page: filters, scorecard, focus list, insights, charts, behavior tables, trade log. All aggregation runs in the browser, so filters re-compute everything.
- `Trading-Dashboard.html` - the built page. Do not edit by hand; edit the template and rebuild.

## Notes on the numbers

- P&L is before commissions and the SPX index-option fees.
- Stock sells in the export are not paired (their buys predate the export) and are excluded from P&L.
- Six option sells had no matching buy inside the export window and are excluded; they are listed at the bottom of the page.
