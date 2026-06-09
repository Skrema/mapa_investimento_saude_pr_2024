import pandas as pd
import json
import folium
from branca.colormap import linear
import urllib.request

with open("geojs-41-mun.json", encoding="utf-8") as f:
    geojson_data = json.load(f)

df_saude = pd.read_csv("dados_saude_pr_24.csv", sep=",", dtype={"CO_MUNICIPIO_IBGE": str})
df_saude["CO_MUNICIPIO_IBGE"] = df_saude["CO_MUNICIPIO_IBGE"].str.strip().str.replace(r"\.0$", "", regex=True)
df_saude["MUNICIPIO"] = df_saude["MUNICIPIO"].str.strip()
df_saude["Valor Liquido"] = pd.to_numeric(df_saude["Valor Liquido"], errors="coerce")

try:
    df_pop = pd.read_csv("populacao_pr_2024.csv", dtype={"IBGE_6": str})
except FileNotFoundError:
    from sidrapy import get_table
    df_pop = get_table(table_code="6579", territorial_level="6", ibge_territorial_code="all", variable="9324", period="2024")
    df_pop = df_pop.iloc[1:].copy()
    df_pop.columns = ["nivel_cod", "nivel_nome", "unidade_cod", "unidade_nome", "populacao",
                      "municipio_cod_7", "municipio_nome", "ano_cod", "ano", "variavel_cod", "variavel_nome"]
    df_pop = df_pop[df_pop["municipio_cod_7"].astype(str).str.startswith("41")].copy()
    df_pop["populacao"] = pd.to_numeric(df_pop["populacao"], errors="coerce")
    df_pop["IBGE_6"] = df_pop["municipio_cod_7"].astype(str).str[:6]
    df_pop.to_csv("populacao_pr_2024.csv", index=False, columns=["IBGE_6", "municipio_cod_7", "municipio_nome", "populacao"])

df = df_saude.merge(df_pop[["IBGE_6", "populacao"]], left_on="CO_MUNICIPIO_IBGE", right_on="IBGE_6", how="left")
df["investimento_per_capita"] = df["Valor Liquido"] / df["populacao"]

for feature in geojson_data["features"]:
    props = feature["properties"]
    geo_id = str(props["id"])
    props["id_6"] = geo_id[:6]

geo_id_to_data = df.set_index("CO_MUNICIPIO_IBGE")["Valor Liquido"].to_dict()
geo_id_to_nome = df.set_index("CO_MUNICIPIO_IBGE")["MUNICIPIO"].to_dict()
geo_id_to_pop = df.set_index("CO_MUNICIPIO_IBGE")["populacao"].to_dict()
geo_id_to_percap = df.set_index("CO_MUNICIPIO_IBGE")["investimento_per_capita"].to_dict()

valores_inv = []
for feature in geojson_data["features"]:
    props = feature["properties"]
    cid = props["id_6"]
    v = geo_id_to_data.get(cid)
    props["valor_investimento"] = v
    props["nome_municipio"] = geo_id_to_nome.get(cid, props["name"])
    props["populacao"] = geo_id_to_pop.get(cid)
    props["investimento_per_capita"] = geo_id_to_percap.get(cid)
    if v is not None:
        valores_inv.append(v)

vmin, vmax = min(valores_inv), max(valores_inv)
colormap = linear.YlOrRd_09.scale(vmin, vmax)
colormap.caption = "Valor L\u00edquido Investido (R$)"

def style_function(feature):
    v = feature["properties"]["valor_investimento"]
    if v is None:
        return {"fillColor": "#cccccc", "color": "#666666", "weight": 0.5, "fillOpacity": 0.7}
    return {"fillColor": colormap(v), "color": "#666666", "weight": 0.5, "fillOpacity": 0.7}

def highlight_function(feature):
    return {"fillColor": "#ffeda0", "color": "black", "weight": 2, "fillOpacity": 0.7}

m = folium.Map(location=[-24.5, -51.5], zoom_start=7, tiles="CartoDB positron")

tooltip = folium.features.GeoJsonTooltip(
    fields=["nome_municipio", "valor_investimento", "populacao", "investimento_per_capita"],
    aliases=["<b>Munic\u00edpio:</b>", "<b>Investimento (R$):</b>", "<b>Popula\u00e7\u00e3o:</b>", "<b>Investimento per capita (R$):</b>"],
    localize=True,
    sticky=False,
    labels=True,
    style="background-color: #F0EFEF; border: 1px solid black; border-radius: 3px; box-shadow: 3px; padding: 6px; font-size: 13px;",
    max_width=800,
)

popup = folium.features.GeoJsonPopup(
    fields=["nome_municipio", "valor_investimento", "populacao", "investimento_per_capita"],
    aliases=["<b>Munic\u00edpio:</b>", "<b>Investimento (R$):</b>", "<b>Popula\u00e7\u00e3o:</b>", "<b>Investimento per capita (R$):</b>"],
    localize=True,
    style="background-color: #F0EFEF; border: 1px solid black; border-radius: 3px; box-shadow: 3px; padding: 8px; font-size: 14px;",
)

folium.features.GeoJson(
    data=geojson_data,
    name="Munic\u00edpios",
    tooltip=tooltip,
    popup=popup,
    style_function=style_function,
    highlight_function=highlight_function,
    smooth_factor=0.5,
).add_to(m)

colormap.add_to(m)

html_path = "mapa_investimento_saude_pr_2024.html"
m.save(html_path)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Build the ranking data as a JavaScript array
rankings_js = "var municipiosData = [\n"
for _, row in df.sort_values("Valor Liquido", ascending=False).iterrows():
    nome = row["MUNICIPIO"]
    valor = row["Valor Liquido"]
    ibge = row["CO_MUNICIPIO_IBGE"]
    pop = row["populacao"] if pd.notna(row["populacao"]) else "null"
    percap = row["investimento_per_capita"] if pd.notna(row["investimento_per_capita"]) else "null"
    if pd.notna(valor):
        rankings_js += f'  {{ibge:"{ibge}", nome:"{nome}", valor:{valor}, populacao:{pop}, percapita:{percap}}},\n'
rankings_js += "];\n"

head_inject = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    #map-wrapper { position: relative; width: 100%; height: 100vh; display: flex; }
    #map-container { flex: 1; height: 100vh; }
    #map-container .folium-map { width: 100% !important; height: 100vh !important; }
    #sidebar {
        width: 340px; min-width: 340px; height: 100vh; overflow-y: auto;
        background: #fff; border-left: 2px solid #ddd;
        font-family: 'Segoe UI', Arial, sans-serif; z-index: 1000;
        display: flex; flex-direction: column;
    }
    #sidebar-header {
        padding: 16px; background: #2c3e50; color: white; text-align: center;
    }
    #sidebar-header h2 { font-size: 16px; margin: 0 0 4px; }
    #sidebar-header p { font-size: 11px; opacity: 0.8; margin: 0; }
    #search-box {
        padding: 10px 12px; border-bottom: 1px solid #eee;
    }
    #search-box input {
        width: 100%; padding: 8px 10px; border: 1px solid #ccc;
        border-radius: 4px; font-size: 13px;
    }
    #search-box input:focus { outline: none; border-color: #3498db; }
    #search-results {
        max-height: 180px; overflow-y: auto; display: none;
        position: absolute; width: 316px; background: white;
        border: 1px solid #ccc; border-radius: 0 0 4px 4px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); z-index: 9999;
    }
    #search-results div {
        padding: 6px 10px; cursor: pointer; font-size: 12px; border-bottom: 1px solid #f0f0f0;
    }
    #search-results div:hover { background: #e8f4fd; }
    .panel-section { padding: 10px 12px; border-bottom: 1px solid #eee; }
    .panel-section h3 { font-size: 13px; color: #2c3e50; margin-bottom: 6px; }
    .ranking-item {
        display: flex; justify-content: space-between; align-items: center;
        padding: 4px 0; font-size: 12px; border-bottom: 1px solid #f5f5f5; cursor: pointer;
    }
    .ranking-item:hover { background: #f9f9f9; }
    .ranking-item .pos { color: #7f8c8d; width: 24px; font-weight: bold; }
    .ranking-item .name { flex: 1; margin: 0 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .ranking-item .value { font-weight: bold; color: #2c3e50; text-align: right; white-space: nowrap; }
    .ranking-item .value.green { color: #27ae60; }
    .ranking-item .value.red { color: #e74c3c; }
    .tab-bar { display: flex; border-bottom: 1px solid #ddd; }
    .tab-bar button {
        flex: 1; padding: 8px; border: none; background: #f8f9fa;
        cursor: pointer; font-size: 12px; font-weight: bold; color: #555;
        transition: all 0.2s;
    }
    .tab-bar button.active { background: #fff; color: #2c3e50; border-bottom: 2px solid #2c3e50; }
    .tab-bar button:hover { background: #eee; }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    #btn-clear-selection {
        display: block; width: calc(100% - 24px); margin: 10px 12px; padding: 8px;
        background: #e74c3c; color: white; border: none; border-radius: 4px;
        cursor: pointer; font-size: 13px; font-weight: bold;
    }
    #btn-clear-selection:hover { background: #c0392b; }
    .legend {
        position: absolute !important;
        bottom: 30px !important;
        left: 12px !important;
        right: auto !important;
        top: auto !important;
        z-index: 1000 !important;
        background: white !important;
        padding: 8px !important;
        border-radius: 4px !important;
        box-shadow: 0 1px 5px rgba(0,0,0,0.2) !important;
    }
    .leaflet-control-layers { max-height: 300px; overflow-y: auto; }
    #selected-info {
        padding: 8px 12px; background: #e8f8f5; border-bottom: 1px solid #ddd;
        display: none; font-size: 12px;
    }
</style>
"""

title_overlay = """
<div style="
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    background: rgba(255,255,255,0.92);
    padding: 8px 20px;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    font-family: 'Segoe UI', Arial, sans-serif;
    text-align: center;
    pointer-events: none;
">
    <h2 style="margin: 0; font-size: 16px; color: #2c3e50;">Investimento em Sa\u00fade por Munic\u00edpio - Paran\u00e1 (2024)</h2>
    <p style="margin: 2px 0 0; font-size: 11px; color: #7f8c8d;">Repasses at\u00e9 junho de 2024 | Clique em um munic\u00edpio para detalhes</p>
</div>
"""

# Build the full HTML with sidebar layout
html = html.replace(
    '<style>',
    '<style>\n    html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; }\n'
)

# Wrap the map in a flex container
html = html.replace(
    '<div class="folium-map"',
    '<div id="map-wrapper"><div id="map-container"><div class="folium-map"'
)

# Close the wrapper after the map div ends and add sidebar
# Find the closing </div> for the map div and inject sidebar before script tags
html = html.replace(
    '</head>',
    head_inject + '\n</head>'
)

html = html.replace(
    '<head>',
    '<head><title>Investimento em Sa\u00fade - Paran\u00e1 2024</title>'
)

# Find the last script tag and inject sidebar before maps scripts
# We'll inject the sidebar after 'var map_'

# Inject sidebar HTML and JS before the closing </div> of the map
sidebar_html = """
</div> <!-- close map-container -->
<div id="sidebar">
    <div id="sidebar-header">
        <h2>Investimento em Sa\u00fade - PR</h2>
        <p>Repasses at\u00e9 junho de 2024</p>
    </div>
    <div id="search-box">
        <input type="text" id="search-input" placeholder="Buscar munic\u00edpio..." autocomplete="off">
        <div id="search-results"></div>
    </div>
    <div id="selected-info">
        <strong id="selected-name"></strong><br>
        Investimento: <span id="selected-valor"></span><br>
        Popula\u00e7\u00e3o: <span id="selected-pop"></span><br>
        Per capita: <span id="selected-percap"></span>
    </div>
    <div style="flex:1; overflow-y:auto;">
        <div class="panel-section">
            <h3>Ranking</h3>
            <div class="tab-bar">
                <button class="tab-btn active" onclick="switchTab('maiores')">Maiores Investimentos</button>
                <button class="tab-btn" onclick="switchTab('menores')">Menores Investimentos</button>
            </div>
            <div id="tab-maiores" class="tab-content active"></div>
            <div id="tab-menores" class="tab-content"></div>
        </div>
    </div>
    <button id="btn-clear-selection">Limpar Sele\u00e7\u00e3o</button>
</div>
</div> <!-- close map-wrapper -->
"""

# Append our sidebar HTML and JS before the main scripts
# Find the position of the first folium script
script_pos = html.find('<script src="https://cdn.jsdelivr.net/npm/leaflet')
html = html[:script_pos] + sidebar_html + html[script_pos:]

# Add the JavaScript with all functionality
js_extra = """
<script>
""" + rankings_js + """
function formatCurrency(n) {
    if (n == null || n === undefined) return "N/A";
    return "R$ " + Number(n).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}
function formatNumber(n) {
    if (n == null || n === undefined) return "N/A";
    return Number(n).toLocaleString('pt-BR');
}

var selectedLayer = null;
var municipiosIndex = {};
municipiosData.forEach(function(d) { municipiosIndex[d.ibge] = d; });

function getColorForValue(v, vmin, vmax) {
    if (v == null || v === undefined) return "#cccccc";
    var palette = ["#ffffcc","#ffeda0","#fed976","#feb24c","#fd8d3c","#fc4e2a","#e31a1c","#bd0026","#800026"];
    var ratio = (v - vmin) / (vmax - vmin);
    var idx = Math.min(palette.length - 1, Math.max(0, Math.round(ratio * (palette.length - 1))));
    return palette[idx];
}

function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('active'); });
    document.querySelectorAll('.tab-content').forEach(function(c) { c.classList.remove('active'); });
    if (tab === 'maiores') {
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
        document.getElementById('tab-maiores').classList.add('active');
    } else {
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
        document.getElementById('tab-menores').classList.add('active');
    }
}

function buildRankings() {
    var sorted = municipiosData.slice().sort(function(a, b) { return b.valor - a.valor; });
    var top10 = sorted.slice(0, 10);
    var bottom10 = sorted.slice(-10).reverse();
    
    var maioresHtml = '';
    top10.forEach(function(d, i) {
        maioresHtml += '<div class="ranking-item" onclick="focusMunicipio(\\'' + d.ibge + '\\')">' +
            '<span class="pos">' + (i+1) + '</span>' +
            '<span class="name">' + d.nome + '</span>' +
            '<span class="value green">' + formatCurrency(d.valor) + '</span></div>';
    });
    document.getElementById('tab-maiores').innerHTML = maioresHtml;
    
    var menoresHtml = '';
    bottom10.forEach(function(d, i) {
        menoresHtml += '<div class="ranking-item" onclick="focusMunicipio(\\'' + d.ibge + '\\')">' +
            '<span class="pos">' + (i+1) + '</span>' +
            '<span class="name">' + d.nome + '</span>' +
            '<span class="value red">' + formatCurrency(d.valor) + '</span></div>';
    });
    document.getElementById('tab-menores').innerHTML = menoresHtml;
}

function focusMunicipio(ibge) {
    var mapId = document.querySelector('.folium-map').id;
    var map = window[mapId];
    if (!map) return;
    
    map.eachLayer(function(layer) {
        if (layer.feature && layer.feature.properties) {
            var props = layer.feature.properties;
            if (props.id_6 === ibge) {
                if (selectedLayer && selectedLayer !== layer) {
                    var oldV = selectedLayer.feature.properties.valor_investimento;
                    selectedLayer.setStyle({
                        fillColor: getColorForValue(oldV, """ + str(vmin) + """, """ + str(vmax) + """),
                        weight: 0.5, opacity: 1, color: '#666666', fillOpacity: 0.7
                    });
                }
                layer.setStyle({fillColor: "#1a9850", weight: 2.5, opacity: 1, color: '#333333', fillOpacity: 0.9});
                selectedLayer = layer;
                map.fitBounds(layer.getBounds(), {maxZoom: 10});
                updateSelectedInfo(props.id_6);
            }
        }
    });
}

function updateSelectedInfo(ibge) {
    var d = municipiosIndex[ibge];
    if (!d) return;
    document.getElementById('selected-info').style.display = 'block';
    document.getElementById('selected-name').textContent = d.nome;
    document.getElementById('selected-valor').textContent = formatCurrency(d.valor);
    document.getElementById('selected-pop').textContent = formatNumber(d.populacao);
    document.getElementById('selected-percap').textContent = formatCurrency(d.percapita);
}

function clearSelection() {
    if (selectedLayer) {
        var oldV = selectedLayer.feature.properties.valor_investimento;
        selectedLayer.setStyle({
            fillColor: getColorForValue(oldV, """ + str(vmin) + """, """ + str(vmax) + """),
            weight: 0.5, opacity: 1, color: '#666666', fillOpacity: 0.7
        });
        selectedLayer = null;
    }
    document.getElementById('selected-info').style.display = 'none';
}

function initSearch() {
    var input = document.getElementById('search-input');
    var results = document.getElementById('search-results');
    
    input.addEventListener('input', function() {
        var q = this.value.toLowerCase().trim();
        if (q.length < 2) { results.style.display = 'none'; return; }
        
        var matches = municipiosData.filter(function(d) {
            return d.nome.toLowerCase().indexOf(q) !== -1;
        }).slice(0, 15);
        
        if (matches.length === 0) { results.style.display = 'none'; return; }
        
        results.innerHTML = '';
        matches.forEach(function(d) {
            var div = document.createElement('div');
            div.textContent = d.nome + ' - ' + formatCurrency(d.valor);
            div.onclick = function() { focusMunicipio(d.ibge); results.style.display = 'none'; input.value = d.nome; };
            results.appendChild(div);
        });
        results.style.display = 'block';
    });
    
    document.addEventListener('click', function(e) {
        if (!e.target.closest('#search-box')) results.style.display = 'none';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    buildRankings();
    initSearch();
    document.getElementById('btn-clear-selection').addEventListener('click', clearSelection);
    
    setTimeout(function() {
        var mapId = document.querySelector('.folium-map').id;
        var map = window[mapId];
        if (!map) return;
        
        map.eachLayer(function(layer) {
            if (layer.feature && layer.feature.properties) {
                layer.on({
                    click: function(e) {
                        if (selectedLayer && selectedLayer !== layer) {
                            var oldV = selectedLayer.feature.properties.valor_investimento;
                            selectedLayer.setStyle({
                                fillColor: getColorForValue(oldV, """ + str(vmin) + """, """ + str(vmax) + """),
                                weight: 0.5, opacity: 1, color: '#666666', fillOpacity: 0.7
                            });
                        }
                        var props = layer.feature.properties;
                        layer.setStyle({fillColor: "#1a9850", weight: 2.5, opacity: 1, color: '#333333', fillOpacity: 0.9});
                        selectedLayer = layer;
                        updateSelectedInfo(props.id_6);
                    }
                });
            }
        });
    }, 500);
});
</script>
</body>"""

html = html.replace("</body>", js_extra)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Mapa salvo em " + html_path)
