with open("mapa_investimento_saude_pr_2024.html", "r", encoding="utf-8") as f:
    c = f.read()
print("Size:", len(c), "bytes")
checks = [
    ("municipiosData", "ranking data"),
    ("initSearch", "search function"),
    ("focusMunicipio", "focus function"),
    ("clearSelection", "clear selection"),
    ("updateSelectedInfo", "update info panel"),
    ("sidebar", "sidebar"),
    ("switchTab", "tab switching"),
    ("investimento_per_capita", "per capita"),
    ("ranking-item", "ranking items"),
    ("search-input", "search input"),
    ("btn-clear-selection", "clear button"),
]
for term, desc in checks:
    found = "OK" if term in c else "MISSING"
    print(f"  {desc}: {found}")
