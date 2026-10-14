# PS158 reproduction: the growth of AI lobbying

**Figure:** Session 4 (politics track), growth of AI lobbying from congressional lobbying disclosure filings.

**Data:** Lobbying Disclosure Act LD-2 quarterly reports, downloaded by `get_data.py` from the
public REST API at https://lda.gov/api/v1/ (Senate Office of Public Records / House Clerk).
Filings are selected by the phrase "artificial intelligence" in the specific-issues text, 2015 to present.
Retrieval date is in `data/retrieved.txt`. Senate Office of Public Records cannot vouch for the data
or analyses derived from these data after the data have been retrieved from LDA.gov.

**Run:** `python get_data.py && python plot.py` (needs pandas, matplotlib).
Optional: `LDA_API_KEY` env var (free key from lda.gov) speeds up the download a lot.

**Measure:** distinct clients per year with at least one filing mentioning the phrase.
`summary_by_year.csv` also gives filing counts.

**How close:** NOTES - fill in after comparing with the slide (which measure it uses, years, shape of growth).
