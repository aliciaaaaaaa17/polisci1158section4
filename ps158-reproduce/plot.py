"""Plot the growth of AI lobbying: distinct clients per year whose LD-2 reports mention AI."""
from pathlib import Path
import datetime
import pandas as pd
import matplotlib.pyplot as plt

here = Path(__file__).parent
files = sorted((here / "data").glob("filings_ai_*.csv"))
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
df = df[df["mentions_phrase"] == True]          # exact phrase, not just word match

by_year = df.groupby("filing_year").agg(
    clients=("client_id", "nunique"),
    filings=("filing_uuid", "nunique"),
).reset_index()
print(by_year.to_string(index=False))
by_year.to_csv(here / "summary_by_year.csv", index=False)

cur = datetime.date.today().year
fig, ax = plt.subplots(figsize=(9, 5.5))
colors = ["#9fb7cf" if y == cur else "#1f4e79" for y in by_year["filing_year"]]
ax.bar(by_year["filing_year"], by_year["clients"], color=colors)
for x, v in zip(by_year["filing_year"], by_year["clients"]):
    ax.text(x, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
ax.set_ylabel("Clients lobbying on AI")
ax.set_xticks(by_year["filing_year"])
ax.set_title("The growth of AI lobbying", loc="left", fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
note = f"Lighter bar: {cur} is a partial year. " if cur in set(by_year["filing_year"]) else ""
fig.text(0.01, 0.01, note + "Distinct clients with an LD-2 report mentioning \"artificial intelligence\" "
         "in specific issues. Source: Lobbying Disclosure Act filings, lda.gov.",
         fontsize=7.5, color="gray")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(here / "figure.png", dpi=200)
print("saved figure.png")
