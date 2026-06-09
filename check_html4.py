with open("mapa_investimento_saude_pr_2024.html", "r", encoding="utf-8") as f:
    c = f.read()

# Search for actual sidebar div
div_sidebar = c.find('<div id="sidebar"')
print("Div sidebar at:", div_sidebar)
body_start = c.find("<body>")
body_end = c.find("</body>")
print("In body:", div_sidebar > body_start and div_sidebar < body_end)

# Search for title
title_pos = c.find("<title>")
print("Title at:", title_pos)

# Check what's in head
head_content = c[:c.find("</head>")]
if "<title>" in head_content:
    print("Title is in head: YES")
else:
    print("Title is in head: NO")
    # Find title anywhere
    any_title = c.find("<title>")
    if any_title >= 0:
        print("Title found at", any_title, ":", repr(c[any_title:any_title+60]))

# Show all divs with id=sidebar
import re
for m in re.finditer(r'<div[^>]*id="sidebar"[^>]*>', c):
    print("Found sidebar div at", m.start())
    
# Show all divs with id=map-wrapper  
for m in re.finditer(r'<div[^>]*id="map-wrapper"[^>]*>', c):
    print("Found map-wrapper at", m.start())
