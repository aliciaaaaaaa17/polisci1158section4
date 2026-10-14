"""Download lobbying filings that mention "artificial intelligence".

Source: U.S. Senate Office of Public Records / House Clerk, Lobbying Disclosure Act
(LDA) LD-2 quarterly reports, via the public REST API at https://lda.gov/api/v1/
(the old lda.senate.gov address is being retired).

For each year it pages through filings whose "specific lobbying issues" text matches
"artificial intelligence" and saves one row per filing to data/filings_ai_<year>.csv.
Re-running skips years that are already saved (delete the file to refresh a year).

Optional: set LDA_API_KEY (free, from lda.gov) for a much higher rate limit.
Anonymous access works but is throttled, so the script sleeps and retries on HTTP 429.
"""
import csv, json, os, sys, time, datetime
import urllib.request, urllib.error, urllib.parse
from pathlib import Path

BASE = "https://lda.gov/api/v1/filings/"
PHRASE = "artificial intelligence"
FIRST_YEAR = 2015
LAST_YEAR = datetime.date.today().year
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)
KEY = os.environ.get("LDA_API_KEY")

FIELDS = ["filing_uuid", "filing_year", "filing_period", "filing_type", "client_id",
          "client_name", "registrant_name", "income", "expenses", "dt_posted",
          "issue_codes", "mentions_phrase"]


def fetch(url):
    headers = {"User-Agent": "ps158-class-project", "Accept": "application/json"}
    if KEY:
        headers["Authorization"] = f"Token {KEY}"
    for attempt in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(e.headers.get("Retry-After", "30")) + 1
                print(f"  rate limited, sleeping {wait}s", flush=True)
                time.sleep(wait)
            elif e.code >= 500:
                time.sleep(5 * (attempt + 1))
            else:
                raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"giving up on {url}")


def row(f):
    acts = f.get("lobbying_activities") or []
    text = " ".join((a.get("description") or "") for a in acts).lower()
    client, reg = f.get("client") or {}, f.get("registrant") or {}
    return {
        "filing_uuid": f.get("filing_uuid"), "filing_year": f.get("filing_year"),
        "filing_period": f.get("filing_period"), "filing_type": f.get("filing_type"),
        "client_id": client.get("id"), "client_name": client.get("name"),
        "registrant_name": reg.get("name"), "income": f.get("income"),
        "expenses": f.get("expenses"), "dt_posted": f.get("dt_posted"),
        "issue_codes": ";".join(sorted({a.get("general_issue_code") or "" for a in acts})),
        # the API search is word-based; record whether the exact phrase is present
        "mentions_phrase": PHRASE in text,
    }


for year in range(FIRST_YEAR, LAST_YEAR + 1):
    path = OUT / f"filings_ai_{year}.csv"
    if path.exists():
        print(f"{year}: already downloaded, skipping")
        continue
    q = urllib.parse.urlencode({"filing_year": year, "filing_specific_lobbying_issues": PHRASE, "page_size": 25})
    url, rows, total = f"{BASE}?{q}", [], None
    while url:
        data = fetch(url)
        total = data.get("count", total)
        rows += [row(f) for f in data.get("results", [])]
        url = data.get("next")
        print(f"{year}: {len(rows)}/{total}", end="\r", flush=True)
        time.sleep(0.5 if KEY else 4)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)
    print(f"\n{year}: saved {len(rows)} filings -> {path.name}")

(OUT / "retrieved.txt").write_text(
    f"Retrieved from lda.gov API on {datetime.date.today().isoformat()}. "
    "Senate Office of Public Records cannot vouch for the data or analyses derived "
    "from these data after the data have been retrieved from LDA.gov.\n")
