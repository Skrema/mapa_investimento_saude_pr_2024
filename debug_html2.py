with open("mapa_investimento_saude_pr_2024.html", "r", encoding="utf-8") as f:
    c = f.read()

body_start = c.find("<body>")
body_end = c.find("</body>")
print("body_start:", body_start)
print("body_end:", body_end)

map_div_start = c.find('<div class="folium-map"')
print("map_div_start:", map_div_start)

# Content around body
start = max(0, body_start - 50)
end = min(len(c), body_start + 200)
print("\nAround <body>:")
print(c[start:end])
