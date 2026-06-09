with open("mapa_investimento_saude_pr_2024.html", "r", encoding="utf-8") as f:
    c = f.read()

# Find sidebar
sidebar_pos = c.find("sidebar")
print("Sidebar first appears at position:", sidebar_pos)

# Find body
body_start = c.find("<body>")
body_end = c.find("</body>")
print("Body from", body_start, "to", body_end)

# Context around sidebar
print("\n--- Context around first 'sidebar' ---")
print(repr(c[max(0,sidebar_pos-100):sidebar_pos+200]))

# Check where title is
title_pos = c.find("<title>")
print("\n--- Title at", title_pos, "---")
print(repr(c[title_pos:title_pos+100]))

# Check head
head_end = c.find("</head>")
print("\n--- Head ends at", head_end, "---")
print(repr(c[max(0,head_end-100):head_end+50]))
