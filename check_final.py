with open("mapa_investimento_saude_pr_2024.html", "r", encoding="utf-8") as f:
    c = f.read()

print("Size:", len(c), "bytes")

head_end = c.find("</head>")
print("Title in head:", "<title>Investimento" in c[:head_end])

body_start = c.find("<body>")
body_end = c.find("</body>")

sidebar_pos = c.find('<div id="sidebar"')
print("Sidebar in body:", sidebar_pos > body_start and sidebar_pos < body_end)

wrapper_pos = c.find('<div id="map-wrapper"')
print("Wrapper in body:", wrapper_pos > body_start and wrapper_pos < body_end)

print("Has L.geoJson:", "L.geoJson" in c)
print("Has municipiosData:", "municipiosData" in c)

# Final check - div balance
body_content = c[body_start:body_end]
open_d = body_content.count("<div ")
close_d = body_content.count("</div>")
print("Body div balance:", open_d - close_d)

# Check a few lines near the beginning
print("\nFirst 5 lines after <body>:")
lines = c[body_start:body_start+500].split("\n")
for l in lines[:8]:
    print(l.strip()[:100])
