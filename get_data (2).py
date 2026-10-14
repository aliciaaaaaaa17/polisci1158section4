"""Download Census Historical Income Table H-5 (households by median and mean income,
by race and Hispanic origin of householder).

Source: U.S. Census Bureau, Current Population Survey Annual Social and Economic
Supplement (CPS ASEC), Historical Income Tables: Households
https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html

The script reads that page, finds the link to table H-5, and downloads the file. If the
page layout changes and it can't find the link, it falls back to the usual file address.
"""
import re, urllib.request
from pathlib import Path
from urllib.parse import urljoin

PAGE = "https://www.census.gov/data/tables/time-series/demo/income-poverty/historical-income-households.html"
FALLBACK = "https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income-households/h05.xlsx"
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)
HDR = {"User-Agent": "Mozilla/5.0 (ps158 class project)"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=90) as r:
        return r.read()


url = FALLBACK
try:
    html = get(PAGE).decode("utf-8", "ignore")
    links = re.findall(r'href="([^"]+h05\.xlsx?)"', html, flags=re.I)
    if links:
        url = urljoin(PAGE, links[0])
except Exception as e:
    print("could not read the Census page, using fallback link:", e)

print("downloading", url)
body = get(url)
ext = ".xls" if url.lower().endswith(".xls") else ".xlsx"
(OUT / f"h05{ext}").write_bytes(body)
(OUT / "source.txt").write_text(f"Downloaded from {url}\nPage: {PAGE}\n")
print(f"saved data/h05{ext} ({len(body):,} bytes)")
