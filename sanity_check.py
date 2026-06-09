with open("mapa_investimento_saude_pr_2024.html", "r", encoding="utf-8") as f:
    c = f.read()

checks = {
    "focusMunicipio com fitBounds": "fitBounds" in c,
    "updateSelectedInfo": "function updateSelectedInfo" in c,
    "click handler no mapa": "layer.on({" in c and "click" in c,
    "ranking onclick focusMunicipio": 'onclick="focusMunicipio' in c,
    "selected-info display": "display = 'block'" in c,
}
for name, ok in checks.items():
    print(f"  {name}: {'OK' if ok else 'FALTA'}")
