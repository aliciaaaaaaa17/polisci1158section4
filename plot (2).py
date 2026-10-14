"""Plot real median household income by race and Hispanic origin of householder,
from Census table H-5 (data/h05.xlsx)."""
import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

here = Path(__file__).parent
f = next((here / "data").glob("h05.xls*"))
raw = pd.read_excel(f, header=None, sheet_name=0)

GROUPS = {
    "ALL RACES": "All races",
    "WHITE ALONE, NOT HISPANIC": "White, not Hispanic",
    "BLACK ALONE": "Black",
    "ASIAN ALONE": "Asian",
    "HISPANIC (ANY RACE)": "Hispanic (any race)",
}
COLORS = {"All races": "#444444", "White, not Hispanic": "#1f4e79", "Black": "#c0392b",
          "Asian": "#2e8b57", "Hispanic (any race)": "#e08a00"}


def norm(s):
    s = str(s).strip().upper()
    s = re.sub(r"\s*\(\d+\)", "", s)          # footnote markers like "(21)"
    return re.sub(r"\s+", " ", s).strip()


def year_of(v):
    m = re.match(r"^\s*(\d{4})\b", str(v))
    return int(m.group(1)) if m else None


# first data row = first row whose first cell starts with a 4-digit year
first = next(i for i in range(len(raw)) if year_of(raw.iat[i, 0]))
# build one text label per column from the header rows above it (fill merged cells rightwards)
hdr = raw.iloc[:first].copy().astype(object).where(raw.iloc[:first].notna(), None)
hdr = hdr.ffill(axis=1)
labels = {c: " ".join(str(x) for x in hdr[c] if x is not None).lower() for c in raw.columns}
cands = []
for c, t in labels.items():
    m = re.findall(r"(20\d\d) dollars", t)
    if "median" in t and "mean" not in t.split("median")[0] and m:
        cands.append((int(m[-1]), "estimate" in t, c))
if not cands:
    print(raw.head(20).to_string())
    raise SystemExit("Could not find the 'median income, <year> dollars' column. "
                     "Send me the rows printed above and I will fix the parser.")
year_dollars, _, col = sorted(cands, key=lambda x: (x[0], x[1]))[-1]
print(f"Using column {col}: {labels[col]!r}")

rows, group = [], None
for i in range(len(raw)):
    a = raw.iat[i, 0]
    if year_of(a) is None:
        n = norm(a)
        if n in GROUPS:
            group = GROUPS[n]
        elif n and n not in ("NAN",) and not n.startswith("NOTE") and group and len(n) < 60 and n.isupper():
            group = None                       # a different block we are not plotting
        continue
    if group is None:
        continue
    v = pd.to_numeric(raw.iat[i, col], errors="coerce")
    if pd.notna(v):
        rows.append((group, year_of(a), float(v)))

df = pd.DataFrame(rows, columns=["group", "year", "median_income"])
df = df.drop_duplicates(["group", "year"], keep="last")   # years re-listed after method changes: keep latest
df.to_csv(here / "median_income_by_race.csv", index=False)
print(df.groupby("group")["year"].agg(["min", "max", "count"]))

fig, ax = plt.subplots(figsize=(9.5, 5.8))
for g, d in df.groupby("group"):
    d = d.sort_values("year")
    ax.plot(d["year"], d["median_income"], lw=2.2, color=COLORS.get(g), label=g)
    ax.annotate(f"${d['median_income'].iloc[-1]:,.0f}", (d["year"].iloc[-1], d["median_income"].iloc[-1]),
                xytext=(5, 0), textcoords="offset points", fontsize=8, va="center", color=COLORS.get(g))
ax.set_ylabel(f"Median household income ({year_dollars} dollars)")
ax.yaxis.set_major_formatter(lambda v, p: f"${v:,.0f}")
ax.set_title("Median household income by race and Hispanic origin of householder", loc="left", fontweight="bold")
ax.legend(frameon=False, loc="upper left")
ax.spines[["top", "right"]].set_visible(False)
ax.margins(x=0.08)
fig.text(0.01, 0.01, "Source: U.S. Census Bureau, CPS ASEC, Historical Income Tables, Table H-5.",
         fontsize=8, color="gray")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(here / "figure.png", dpi=200)
print("saved figure.png")
