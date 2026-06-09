import pandas as pd
import json
import folium
from branca.colormap import linear

with open("geojs-41-mun.json", encoding="utf-8") as f:
    geojson_data = json.load(f)

df = pd.read_csv("dados_saude_pr_24.csv", sep=",", dtype={"CO_MUNICIPIO_IBGE": str})
df["CO_MUNICIPIO_IBGE"] = df["CO_MUNICIPIO_IBGE"].str.strip().str.replace(r"\.0$", "", regex=True)
df["MUNICIPIO"] = df["MUNICIPIO"].str.strip()
df["Valor Liquido"] = pd.to_numeric(df["Valor Liquido"], errors="coerce")

for feature in geojson_data["features"]:
    props = feature["properties"]
    geo_id = str(props["id"])
    props["id_6"] = geo_id[:6]

geo_id_to_data = df.set_index("CO_MUNICIPIO_IBGE")["Valor Liquido"].to_dict()
geo_id_to_nome = df.set_index("CO_MUNICIPIO_IBGE")["MUNICIPIO"].to_dict()

valores = []
for feature in geojson_data["features"]:
    props = feature["properties"]
    cid = props["id_6"]
    v = geo_id_to_data.get(cid)
    props["valor_investimento"] = v
    props["nome_municipio"] = geo_id_to_nome.get(cid, props["name"])
    if v is not None:
        valores.append(v)

vmin, vmax = min(valores), max(valores)
colormap = linear.YlOrRd_09.scale(vmin, vmax)
colormap.caption = "Valor Líquido Investido (R$)"

def style_function(feature):
    v = feature["properties"]["valor_investimento"]
    if v is None:
        return {"fillColor": "#cccccc", "color": "#666666", "weight": 0.5, "fillOpacity": 0.7}
    return {"fillColor": colormap(v), "color": "#666666", "weight": 0.5, "fillOpacity": 0.7}

def highlight_function(feature):
    return {"fillColor": "#ffeda0", "color": "black", "weight": 2, "fillOpacity": 0.7}

m = folium.Map(location=[-24.5, -51.5], zoom_start=7, tiles="CartoDB positron")

tooltip = folium.features.GeoJsonTooltip(
    fields=["nome_municipio", "valor_investimento"],
    aliases=["<b>Munic\u00edpio:</b>", "<b>Investimento (R$):</b>"],
    localize=True,
    sticky=False,
    labels=True,
    style="background-color: #F0EFEF; border: 1px solid black; border-radius: 3px; box-shadow: 3px; padding: 6px; font-size: 13px;",
    max_width=800,
)

popup = folium.features.GeoJsonPopup(
    fields=["nome_municipio", "valor_investimento"],
    aliases=["<b>Munic\u00edpio:</b>", "<b>Investimento (R$):</b>"],
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

title_overlay = """
<div style="
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    background: rgba(255,255,255,0.92);
    padding: 10px 24px;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    font-family: 'Segoe UI', Arial, sans-serif;
    text-align: center;
    pointer-events: none;
">
    <h2 style="margin: 0; font-size: 18px; color: #2c3e50;">Investimento em Sa\u00fade por Munic\u00edpio - Paran\u00e1 (2024)</h2>
    <p style="margin: 2px 0 0; font-size: 12px; color: #7f8c8d;">Repasses at\u00e9 junho de 2024 | Clique em um munic\u00edpio para detalhes</p>
</div>
"""

head_inject = """
<style>
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
    .leaflet-control-layers {
        max-height: 300px;
        overflow-y: auto;
    }
</style>
"""

js_inject = """
<script>
function formatCurrency(n) {
    if (n == null || n === undefined) return "N/A";
    return "R$ " + Number(n).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
}
var selectedLayer = null;
function getColorForValue(v, vmin, vmax) {
    if (v == null || v === undefined) return "#cccccc";
    var palette = ["#ffffcc","#ffeda0","#fed976","#feb24c","#fd8d3c","#fc4e2a","#e31a1c","#bd0026","#800026"];
    var ratio = (v - vmin) / (vmax - vmin);
    var idx = Math.min(palette.length - 1, Math.max(0, Math.round(ratio * (palette.length - 1))));
    return palette[idx];
}
document.addEventListener('DOMContentLoaded', function() {
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
                                weight: 0.5,
                                opacity: 1,
                                color: '#666666',
                                fillOpacity: 0.7
                            });
                        }
                        var v = layer.feature.properties.valor_investimento;
                        var nome = layer.feature.properties.nome_municipio || "Desconhecido";
                        layer.setStyle({
                            fillColor: "#1a9850",
                            weight: 2.5,
                            opacity: 1,
                            color: '#333333',
                            fillOpacity: 0.9
                        });
                        selectedLayer = layer;
                    }
                });
            }
        });
    }, 500);
});
</script>
</body>"""

html = html.replace("<head>", "<head><title>Investimento em Sa\u00fade - Paran\u00e1 2024</title>")
html = html.replace("</head>", head_inject + "\n</head>")
html = html.replace("</body>", title_overlay + "\n" + js_inject)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Mapa salvo em " + html_path)
