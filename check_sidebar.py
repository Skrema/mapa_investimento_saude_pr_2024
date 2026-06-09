with open("mapa_investimento_saude_pr_2024.html", "r", encoding="utf-8") as f:
    c = f.read()

idx = c.find('id="selected-info"')
print("selected-info found:", idx >= 0)
if idx >= 0:
    print(c[idx:idx+300])
