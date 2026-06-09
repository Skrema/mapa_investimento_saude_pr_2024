with open("mapa_investimento_saude_pr_2024.html", "r", encoding="utf-8") as f:
    c = f.read()

print("Has L.geoJson:", "L.geoJson" in c)
print("Has L.geoJSON:", "L.geoJSON" in c)
print("Has folium GeoJson:", "folium" in c and "GeoJson" in c)

import re
geo_matches = re.findall(r"L\.geo\w+", c)
print("Geo methods found:", geo_matches[:5])

# Check the structure around the map
idx = c.find('<div class="folium-map"')
if idx >= 0:
    print("\nfolium-map div found at position", idx)
    # Show surrounding context
    start = max(0, idx - 200)
    end = min(len(c), idx + 400)
    print("Context around folium-map:")
    print(c[start:end])
