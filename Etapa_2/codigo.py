


# import 
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

ARQUIVO = "dataset_projeto.csv"
Path("tabelas").mkdir(exist_ok=True)
Path("figuras").mkdir(exist_ok=True)

# 2.1 Leitura e tratamento dos dados
df = pd.read_csv(ARQUIVO, dtype=str)

df = df.rename(columns={
    "Territorialidades": "territorio",
    "Esperança de vida ao nascer 2024": "esp_vida",
    "Mortalidade infantil 2024": "mort_inf",
    "Média de anos de estudo 2024": "anos_estudo",
    "Taxa de analfabetismo - 15 anos ou mais de idade 2024": "analfab",
    "Taxa de frequência líquida ao ensino médio 2024": "freq_liq_em",
    "% de 5 a 6 anos de idade na escola 2024": "pct_5a6_escola",
    "Renda per capita 2024": "renda_pc",
    "População total 2024": "populacao",
    "Subíndice de escolaridade - IDHM Educação 2024": "sub_escolaridade",
    "Subíndice de frequência escolar - IDHM Educação 2024": "sub_freq_escolar",
    "IDHM Educação 2024": "idhm_educ",
    "IDHM Longevidade 2024": "idhm_long",
    "IDHM Renda 2024": "idhm_renda",
    "IDHM 2024": "idhm",
})

for col in df.columns.drop("territorio"):
    df[col] = df[col].str.replace(",", ".").astype(float)

brasil = df[df["territorio"] == "Brasil"].iloc[0]
ufs = df[df["territorio"] != "Brasil"].reset_index(drop=True)

grupos = {
    "Norte": ["Acre", "Amapá", "Amazonas", "Pará", "Rondônia", "Roraima", "Tocantins"],
    "Nordeste": ["Alagoas", "Bahia", "Ceará", "Maranhão", "Paraíba", "Pernambuco",
                 "Piauí", "Rio Grande do Norte", "Sergipe"],
    "Centro-Oeste": ["Distrito Federal", "Goiás", "Mato Grosso", "Mato Grosso do Sul"],
    "Sudeste": ["Espírito Santo", "Minas Gerais", "Rio de Janeiro", "São Paulo"],
    "Sul": ["Paraná", "Rio Grande do Sul", "Santa Catarina"],
}
mapa_regiao = {uf: reg for reg, lista in grupos.items() for uf in lista}
ufs["regiao"] = ufs["territorio"].map(mapa_regiao)
ordem = list(grupos)

print("Valores ausentes:", ufs.isna().sum().sum())
print("UFs duplicadas:", ufs["territorio"].duplicated().sum())
print(ufs["regiao"].value_counts(), "\n")


# 2.2 Estatísticas de resumo
nomes = {
    "idhm": "IDHM",
    "idhm_educ": "IDHM Educação",
    "idhm_long": "IDHM Longevidade",
    "idhm_renda": "IDHM Renda",
    "renda_pc": "Renda per capita (R$)",
    "anos_estudo": "Anos de estudo (média)",
    "analfab": "Analfabetismo 15+ (%)",
    "esp_vida": "Esperança de vida (anos)",
    "mort_inf": "Mortalidade infantil (por mil)",
}

linhas = []
for col, nome in nomes.items():
    serie = ufs[col]
    linhas.append({
        "indicador": nome,
        "media": serie.mean(),
        "mediana": serie.median(),
        "minimo": serie.min(),
        "uf_minimo": ufs.loc[serie.idxmin(), "territorio"],
        "maximo": serie.max(),
        "uf_maximo": ufs.loc[serie.idxmax(), "territorio"],
        "brasil": brasil[col],
    })
resumo = pd.DataFrame(linhas).round(3)
resumo.to_csv("tabelas/resumo_estatistico.csv", index=False, encoding="utf-8-sig")
print(resumo.to_string(index=False))

print("\nUFs com IDHM abaixo do Brasil:", (ufs["idhm"] < brasil["idhm"]).sum(), "de 27")
print("Renda DF / Maranhão:", round(1465.10 / 481.46, 1))

print("\nCorrelação com o IDHM:")
for col in ["renda_pc", "anos_estudo", "analfab", "esp_vida", "mort_inf"]:
    print(f"  {nomes[col]:32s} {ufs[col].corr(ufs['idhm']):+.2f}")

medias = ufs.groupby("regiao")[["idhm", "renda_pc", "analfab"]].mean().reindex(ordem).round(3)
medias.to_csv("tabelas/medias_por_regiao.csv", encoding="utf-8-sig")
print("\n", medias)


# 2.3 Gráficos
AZUL, LARANJA, CINZA = "#2a78d6", "#eb6834", "#52514e"

plt.rcParams.update({
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#c9c8c2",
    "axes.labelcolor": CINZA,
    "xtick.color": CINZA,
    "ytick.color": CINZA,
    "axes.grid": True,
    "grid.color": "#ecebe7",
    "axes.axisbelow": True,
})

def cor(regiao):
    return LARANJA if regiao in ("Norte", "Nordeste") else AZUL

def virgula(eixo, casas):
    eixo.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.{casas}f}".replace(".", ",")))

def titulo(ax, texto):
    ax.set_title(texto, loc="left", fontsize=11.5, fontweight="bold")

legenda = [Patch(color=AZUL, label="Sul, Sudeste e Centro-Oeste"),
           Patch(color=LARANJA, label="Norte e Nordeste")]


# G1 Ranking do IDHM
rank = ufs.sort_values("idhm").reset_index(drop=True)
fig, ax = plt.subplots(figsize=(8, 8))
ax.barh(rank["territorio"], rank["idhm"], color=rank["regiao"].map(cor), height=0.7)
for i, v in enumerate(rank["idhm"]):
    ax.text(v + 0.002, i, f"{v:.3f}".replace(".", ","), va="center", fontsize=8, color=CINZA,
            zorder=4, bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
ax.axvline(brasil["idhm"], color="black", ls="--", lw=1, zorder=3)
linha_br = Line2D([0], [0], color="black", ls="--", lw=1, label="Brasil (0,805)")
ax.legend(handles=legenda + [linha_br], loc="lower right", frameon=False, fontsize=9)
ax.set_xlim(0.70, 0.89)
ax.set_xlabel("IDHM 2024")
virgula(ax.xaxis, 3)
ax.grid(axis="y", visible=False)
titulo(ax, "Norte e Nordeste concentram os menores IDHM do país")
fig.tight_layout()
fig.savefig("figuras/ranking_idhm.png", dpi=160, facecolor="white")
plt.close(fig)


# G2 IDHM por região
fig, ax = plt.subplots(figsize=(8, 4.8))
ax.boxplot([ufs.loc[ufs["regiao"] == r, "idhm"] for r in ordem], tick_labels=ordem,
           widths=0.5, patch_artist=True, showfliers=False,
           boxprops=dict(facecolor="#d6e4f7", edgecolor="#9db7d5"),
           medianprops=dict(color="black", lw=1.6),
           whiskerprops=dict(color="#9db7d5"), capprops=dict(color="#9db7d5"))
rng = np.random.default_rng(42)
for i, r in enumerate(ordem, start=1):
    y = ufs.loc[ufs["regiao"] == r, "idhm"]
    ax.scatter(i + rng.uniform(-0.12, 0.12, len(y)), y, s=26, color=cor(r),
               edgecolor="white", linewidth=0.8, zorder=3)
ax.axhline(brasil["idhm"], color="black", ls="--", lw=1)
ax.text(5.45, brasil["idhm"] + 0.002, "Brasil", fontsize=8.5, ha="right")
ax.set_ylabel("IDHM 2024")
virgula(ax.yaxis, 2)
ax.grid(axis="x", visible=False)
titulo(ax, "O IDHM é mais baixo no Norte e no Nordeste")
fig.tight_layout()
fig.savefig("figuras/idhm_por_regiao.png", dpi=160, facecolor="white")
plt.close(fig)


# G3 Renda per capita x IDHM
fig, ax = plt.subplots(figsize=(8, 5.4))
for rotulo, c in (("Sul, Sudeste e Centro-Oeste", AZUL), ("Norte e Nordeste", LARANJA)):
    sel = ufs["regiao"].map(cor) == c
    ax.scatter(ufs.loc[sel, "renda_pc"], ufs.loc[sel, "idhm"], s=48, color=c,
               edgecolor="white", linewidth=0.9, label=rotulo, zorder=3)
b, a = np.polyfit(ufs["renda_pc"], ufs["idhm"], 1)
x = np.linspace(ufs["renda_pc"].min(), ufs["renda_pc"].max(), 50)
ax.plot(x, a + b * x, color="#8a8984", lw=1.2, zorder=2)
destaques = {"Distrito Federal": (-8, 8, "right"), "São Paulo": (6, -3, "left"),
             "Maranhão": (6, -3, "left"), "Alagoas": (6, -9, "left"),
             "Santa Catarina": (-6, 6, "right")}
for uf, (dx, dy, ha) in destaques.items():
    linha = ufs[ufs["territorio"] == uf].iloc[0]
    ax.annotate(uf, (linha["renda_pc"], linha["idhm"]), xytext=(dx, dy),
                textcoords="offset points", fontsize=8.5, color=CINZA, ha=ha)
r = ufs["renda_pc"].corr(ufs["idhm"])
ax.set_xlabel("Renda per capita (R$)")
ax.set_ylabel("IDHM 2024")
virgula(ax.yaxis, 2)
ax.legend(frameon=False, loc="lower right", fontsize=9)
titulo(ax, f"Quanto maior a renda, maior o IDHM (r = {r:.2f})".replace(".", ","))
fig.tight_layout()
fig.savefig("figuras/renda_vs_idhm.png", dpi=160, facecolor="white")
plt.close(fig)


# G4 Analfabetismo por região
analf = ufs.groupby("regiao")["analfab"].mean().reindex(ordem)
fig, ax = plt.subplots(figsize=(8, 4.6))
ax.bar(analf.index, analf.values, color=[cor(r) for r in analf.index], width=0.6)
for i, v in enumerate(analf.values):
    ax.text(i, v + 0.2, f"{v:.1f}%".replace(".", ","), ha="center", fontsize=9.5, color=CINZA)
ax.axhline(brasil["analfab"], color="black", ls="--", lw=1)
ax.text(4.45, brasil["analfab"] + 0.2, "Brasil: 5,3%", ha="right", fontsize=8.5)
ax.set_ylabel("Analfabetismo, 15 anos ou mais (%)")
ax.set_ylim(0, 13.5)
ax.grid(axis="x", visible=False)
titulo(ax, "O analfabetismo no Nordeste é mais de 4× o do Sul")
fig.tight_layout()
fig.savefig("figuras/analfabetismo_regiao.png", dpi=160, facecolor="white")
plt.close(fig)


# 2.4 Tabelas de frequência
ufs["faixa_analfab"] = pd.cut(ufs["analfab"], [0, 5, 10, 100], right=False,
                              labels=["Menos de 5%", "5% a 10%", "10% ou mais"])
freq = pd.crosstab(ufs["regiao"], ufs["faixa_analfab"]).reindex(ordem)
freq["Total"] = freq.sum(axis=1)
freq.loc["Total (27 UFs)"] = freq.sum()
freq.to_csv("tabelas/frequencia_analfabetismo_regiao.csv", encoding="utf-8-sig")
print("\n", freq)

ufs["faixa_idhm"] = pd.cut(ufs["idhm"], [0, 0.700, 0.800, 1], right=False,
                           labels=["Médio", "Alto", "Muito alto"])
freq_idhm = pd.crosstab(ufs["regiao"], ufs["faixa_idhm"]).reindex(ordem)
freq_idhm["Total"] = freq_idhm.sum(axis=1)
freq_idhm.loc["Total (27 UFs)"] = freq_idhm.sum()
freq_idhm.to_csv("tabelas/frequencia_idhm_regiao.csv", encoding="utf-8-sig")
print("\n", freq_idhm)


