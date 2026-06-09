# Mapa Interativo - Investimento em Saúde no Paraná (2024)

Visualização interativa do total de investimento em saúde por município do Paraná, considerando os repasses até junho de 2024.

## Funcionalidades

- **Mapa coroplético** com escala de cores (YlOrRd) por valor investido
- **Tooltip ao passar o mouse**: nome do município, valor do investimento, população e valor per capita
- **Popup ao clicar** no município com os mesmos detalhes
- **Destaque visual** (cor verde) no município selecionado
- **Painel lateral** com:
  - Busca por nome do município
  - Ranking dos 10 maiores e menores investimentos
  - Informações detalhadas do município selecionado (investimento, população, per capita)
- **Botão "Limpar Seleção"** para remover o destaque
- **Legenda** com escala de valores

## Arquivos

| Arquivo | Descrição |
|---|---|
| `geojs-41-mun.json` | GeoJSON com os polígonos dos 399 municípios do PR |
| `dados_saude_pr_24.csv` | Dados de repasses financeiros em saúde (até junho/2024) |
| `populacao_pr_2024.csv` | Estimativa populacional dos municípios (IBGE 2024) |
| `gerar_mapa.py` | Script Python para gerar o mapa |
| `mapa_investimento_saude_pr_2024.html` | Mapa interativo (abrir no navegador) |

## Como usar

1. Abra o `mapa_investimento_saude_pr_2024.html` em qualquer navegador
2. Passe o mouse sobre os municípios para ver nome, valor, população e per capita
3. Clique em um município para fixar a seleção (destacado em verde)
4. Use a busca no painel lateral para localizar um município
5. Consulte o ranking de maiores/menores investimentos
6. Clique em "Limpar Seleção" para remover o destaque

## Requisitos (para gerar o mapa)

- Python 3.14+
- pandas, folium, sidrapy

```bash
pip install pandas folium sidrapy
python gerar_mapa.py
```
