"""Writes SERVICES.md from the live catalog (https://agentsvc.io/api/v1/services). Run: python3 gen_services.py"""
import json
import urllib.request

CAT = {"web": "Web reading and crawling", "visual": "Screenshots, images, charts", "text": "Text and AI",
       "data": "Data and lookups", "finance": "Crypto, DeFi and finance", "utility": "Validation and utilities"}
with urllib.request.urlopen("https://agentsvc.io/api/v1/services") as r:
    services = json.load(r)["data"]
out = [f"# All {len(services)} services", "",
       "Generated from the live catalog at https://agentsvc.io/api/v1/services. Prices in USDC per call. "
       "Each service has a free sample with its example input at `/api/v1/try/<slug>`.", ""]
for key, title in CAT.items():
    rows = sorted((s for s in services if s["category"] == key), key=lambda s: s["slug"])
    if not rows:
        continue
    out += [f"## {title}", "", "| Service | Price | What it does |", "|---|---|---|"]
    for s in rows:
        desc = s["description"].split(". ")[0].replace("|", "/").replace("\n", " ")
        out.append(f"| [`{s['slug']}`]({s['page_url'] if s.get('page_url') else 'https://agentsvc.io'}) | {s['price_usdc']:g} | {desc} |")
    out.append("")
open("SERVICES.md", "w").write("\n".join(out))
print(len(services))
