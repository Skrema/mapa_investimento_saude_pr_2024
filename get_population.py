import pandas as pd

url = "https://raw.githubusercontent.com/VictorTechrb/estrutura-de-dados/main/POPULACAO%20-%20MUNICIPIOS%20-%202024.csv"
df = pd.read_csv(url, header=None, names=["UF", "cod_estado", "cod_municipio", "nome", "populacao"])

df_pr = df[df["UF"] == "PR"].copy()
print("PR records:", len(df_pr))

df_pr["IBGE_6"] = df_pr["cod_estado"].astype(str).str.zfill(2) + df_pr["cod_municipio"].astype(str).str.zfill(4)
print(df_pr.head(3).to_string())
print("...")

df_pr.to_csv("populacao_pr_2024.csv", index=False)
print("Saved populacao_pr_2024.csv")
