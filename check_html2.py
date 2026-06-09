with open("mapa_investimento_saude_pr_2024.html", "r", encoding="utf-8") as f:
    c = f.read()

print("Size:", len(c), "bytes")

# Check structure
print("\n--- Structure checks ---")
print("Starts with DOCTYPE:", c.startswith("<!DOCTYPE html>"))
print("Has <title> in <head>:", "<title>" in c[:c.find("</head>")])
print("Has map-wrapper after <body>:", c.find('<div id="map-wrapper">') > c.find("<body>"))
print("Has sidebar:", "sidebar" in c)
print("Has L.geoJson:", "L.geoJson" in c)
print("Has municipiosData:", "municipiosData" in c)

# Check for common problems
print("\n--- Problem checks ---")
print("First 100 chars:", repr(c[:100]))

# Check body structure
body_start = c.find("<body>")
body_end = c.find("</body>")
body_content = c[body_start:body_end+7]

# Count div tags to check balance
open_divs = body_content.count("<div")
close_divs = body_content.count("</div>")
print("Body open <div>:", open_divs)
print("Body close </div>:", close_divs)
print("Body div balance:", open_divs - close_divs)

# Check if sidebar is inside body
print("\nSidebar position relative to body:", c.find("sidebar") > body_start and c.find("sidebar") < body_end)
