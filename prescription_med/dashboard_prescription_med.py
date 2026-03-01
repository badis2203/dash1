import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(
    page_title="Dashboard Prescription Médicamenteuses en France", layout="wide")

st.title("Dashboard Prescriptions Médicamenteuses En France")
st.caption("Sources : OpenMedic (prescriptions), INSEE (population via API), CARMF (médecins libéraux via web scraping), OpenStreetMap : pharmacies (web scraping + Overpass API) + projection simple.")


@st.cache_data
def load_data():
    df_atc1 = pd.read_csv(
        "data/processed/atc1_prescriptions_2014_2024.csv", sep=";")
    df_atc2 = pd.read_csv(
        "data/processed/atc2_prescriptions_2014_2024.csv", sep=";")
    df_dens = pd.read_csv(
        "data/processed/df_dens_med.csv", sep=";")
    df_pred = pd.read_csv(
        "data/processed/df_pred.csv", sep=";")
    df_atc2_plot = pd.read_csv(
        "data/processed/atc2_summary.csv", sep=";")
    df_pharma = pd.read_csv(
        "data/processed/pharma_density.csv", sep=";")
    return df_atc1, df_atc2, df_dens, df_pred, df_atc2_plot, df_pharma


df_atc1, df_atc2, df_dens, df_pred, df_atc2_plot, df_pharma = load_data()

df_atc1["boites_pour_1000"] = pd.to_numeric(
    df_atc1["boites_pour_1000"], errors="coerce")
df_atc1["l_atc1"] = df_atc1["l_atc1"].astype(str).str.strip()

df_2024 = df_dens[df_dens["annee"] == 2024]

total_boites = df_2024["boites"].sum()
moy_boites_1000 = df_2024["boites_pour_1000_hab"].mean()
moy_hab_med = df_2024["habitants_par_medecin"].mean()

region_map = {
    11: "Île-de-France",
    24: "Centre-Val de Loire",
    27: "Bourgogne-Franche-Comté",
    28: "Normandie",
    32: "Hauts-de-France",
    44: "Grand Est",
    52: "Pays de la Loire",
    53: "Bretagne",
    75: "Nouvelle-Aquitaine",
    76: "Occitanie",
    84: "Auvergne-Rhône-Alpes",
    93: "Provence-Alpes-Côte d'Azur",
    94: "Corse"}

st.markdown("""
<style>

/* style des liens sidebar */
section[data-testid="stSidebar"] ul li a {
    color: #E5E7EB !important;
    text-decoration: none !important;
    font-weight: 500;
}

/* hover */
section[data-testid="stSidebar"] ul li a:hover {
    color: #60A5FA !important;
}

/* espace lignes */
section[data-testid="stSidebar"] ul {
    list-style: none;
    padding-left: 0;
}

section[data-testid="stSidebar"] ul li {
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)


st.sidebar.markdown("""
### Navigation
---

<ul>
<li><a href="#kpi">KPI</a></li>
<li><a href="#evolution-atc1">Évolution ATC1</a></li>
<li><a href="#carte-prescriptions">Carte prescriptions</a></li>
<li><a href="#pharmacies-offre">Pharmacies & offre</a></li>
<li><a href="#detail-par-sous-classes-atc2">Détail par sous-classes ATC2</a></li>
<li><a href="#projection-atc1">Projection ATC1</a></li>
<li><a href="#donnees-methodologie">Données & Méthodologie</a></li>
</ul>
""", unsafe_allow_html=True)

st.markdown('<div id="kpi"></div>', unsafe_allow_html=True)

years_kpi = sorted(df_atc1["annee"].dropna().unique().astype(int).tolist())
year_kpi = st.selectbox("Année", options=years_kpi,
                        index=len(years_kpi) - 1, key="year_kpi")

df_year = df_atc1[df_atc1["annee"] == year_kpi].copy()
df_reg = df_year.groupby("region", as_index=False).agg(
    boites=("boites", "sum"),
    population=("population", "first"),)

df_reg["boites_pour_1000"] = (
    df_reg["boites"] / df_reg["population"] * 1000).round(0)

total_boites = df_reg["boites"].sum()
moy_boites_1000 = df_reg["boites_pour_1000"].mean()

df_prev = df_atc1[df_atc1["annee"] == (year_kpi - 1)].copy()
if not df_prev.empty:
    df_prev_reg = df_prev.groupby("region", as_index=False).agg(
        boites=("boites", "sum"),
        population=("population", "first"),)

    df_prev_reg["boites_pour_1000"] = (
        df_prev_reg["boites"] / df_prev_reg["population"] * 1000).round(0)

    total_boites_prev = df_prev_reg["boites"].sum()
    moy_boites_1000_prev = df_prev_reg["boites_pour_1000"].mean()

    delta_total = (total_boites - total_boites_prev) / \
        total_boites_prev * 100 if total_boites_prev else None
    delta_1000 = (moy_boites_1000 - moy_boites_1000_prev) / \
        moy_boites_1000_prev * 100 if moy_boites_1000_prev else None
else:
    delta_total = None
    delta_1000 = None

if year_kpi == 2024:
    df_kpi_dens = df_dens[df_dens["annee"] == 2024].copy()
    moy_hab_med = df_kpi_dens["habitants_par_medecin"].mean()
else:
    moy_hab_med = None

c1, c2, c3, c4 = st.columns(4)

c1.metric("Année", f"{year_kpi}")

c2.metric(
    "Total boîtes prescrites",
    f"{int(total_boites):,}".replace(",", " "),
    delta=f"{delta_total:+.1f} % vs {year_kpi-1}" if delta_total is not None else None,)

c3.metric(
    "Boîtes / 1000 habitants",
    f"{int(moy_boites_1000)}",
    delta=f"{delta_1000:+.1f} % vs {year_kpi-1}" if delta_1000 is not None else None,)

c4.metric(
    "Habitants / médecin",
    f"{int(moy_hab_med)}" if moy_hab_med is not None else "Dispo pour 2024",)

top_row = df_reg.sort_values("boites_pour_1000", ascending=False).iloc[0]
top_region = int(top_row["region"])
top_region_name = region_map.get(top_region, str(top_region))
top_val = int(top_row["boites_pour_1000"])

st.info(f"En {year_kpi}, la région la plus consommatrice est {top_region_name}, avec {top_val} boîtes pour 1000 habitants.")

st.markdown('<div id="evolution-atc1"></div>', unsafe_allow_html=True)

st.divider()
st.subheader("Évolution temporelle des prescriptions (ATC1)")

df_atc1["annee"] = pd.to_numeric(df_atc1["annee"], errors="coerce")
df_atc1["region"] = pd.to_numeric(df_atc1["region"], errors="coerce")
df_atc1["boites_pour_1000"] = pd.to_numeric(
    df_atc1["boites_pour_1000"], errors="coerce")
df_atc1["boites"] = pd.to_numeric(df_atc1["boites"], errors="coerce")
df_atc1["l_atc1"] = df_atc1["l_atc1"].astype(str).str.strip()

regions = sorted(df_atc1["region"].dropna().unique().astype(int).tolist())
atc1_codes = sorted(df_atc1["atc1"].dropna().unique().tolist())

atc1_map = df_atc1[["atc1", "l_atc1"]].drop_duplicates().set_index("atc1")[
    "l_atc1"].to_dict()

c1, c2, c3, c4 = st.columns([1, 1, 1, 2])

with c1:
    region_sel = st.selectbox(
        "Région",
        options=["France entière"] + regions,
        index=0,
        format_func=lambda x: x if isinstance(
            x, str) else region_map.get(x, str(x)),
        key="region_time")

with c2:
    mode = st.radio(
        "Affichage",
        ["Top 6", "Personnalisé"],
        horizontal=True,
        key="mode_time")

with c3:
    metric_mode = st.radio(
        "Métrique",
        ["Normalisé (pour 1000 hab)", "Volume brut (boîtes)"],
        horizontal=True,
        key="metric_time")

with c4:
    if mode == "Personnalisé":
        atc1_sel = st.multiselect(
            "Classes ATC1",
            options=atc1_codes,
            default=atc1_codes,
            format_func=lambda x: f"{x} : {atc1_map.get(x, '')}".strip(" :"),
            key="atc1_time")
    else:
        atc1_sel = atc1_codes

y_col = "boites_pour_1000" if metric_mode == "Normalisé (pour 1000 hab)" else "boites"
y_title = "Boîtes / 1000 hab" if y_col == "boites_pour_1000" else "Boîtes (volume brut)"

if region_sel == "France entière":
    df_base = df_atc1.groupby(["annee", "atc1", "l_atc1"], as_index=False)[
        y_col].sum()
else:
    df_base = df_atc1[df_atc1["region"] == int(region_sel)].copy()

df_base = df_base.dropna(subset=["annee", "l_atc1", y_col])

if mode == "Top 6":
    top_labels = (
        df_base.groupby("l_atc1")[y_col]
        .mean()
        .sort_values(ascending=False)
        .head(6)
        .index
        .tolist())
    df_plot = df_base[df_base["l_atc1"].isin(top_labels)].copy()
else:
    df_plot = df_base[df_base["atc1"].isin(atc1_sel)].copy()

zoom_x = alt.selection_interval(encodings=["x"])

chart = alt.Chart(df_plot).mark_line().encode(
    x=alt.X("annee:O", title="Année"),
    y=alt.Y(f"{y_col}:Q", title=y_title),
    color=alt.Color(
        "l_atc1:N",
        title="ATC1",
        legend=alt.Legend(orient="bottom", columns=2, labelLimit=400)
    ),
    tooltip=[
        alt.Tooltip("annee:O", title="Année"),
        alt.Tooltip("l_atc1:N", title="ATC1"),
        alt.Tooltip(f"{y_col}:Q", title=y_title, format=".0f")
    ]
).properties(height=380).interactive()

st.altair_chart(chart, use_container_width=True)

csv = df_plot.to_csv(index=False, sep=";").encode("utf-8")

st.download_button(
    label="Télécharger les données (CSV)",
    data=csv,
    file_name="evolution_atc1.csv",
    mime="text/csv")

st.markdown('<div id="carte-prescriptions"></div>', unsafe_allow_html=True)

st.divider()
st.subheader("Carte des prescriptions par région")

years = sorted(df_atc1["annee"].dropna().unique().astype(int).tolist())
year_sel = st.selectbox("Année", options=years, index=len(years) - 1)

atc1_for_map = st.selectbox(
    "Classe ATC1 (carte)",
    options=atc1_codes,
    index=0,
    format_func=lambda x: f"{x} : {atc1_map.get(x, '')}".strip(" :"))

df_map = df_atc1[(df_atc1["annee"] == year_sel) & (
    df_atc1["atc1"] == atc1_for_map)].copy()
df_map = df_map.groupby("region", as_index=False)["boites_pour_1000"].sum()

geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson"

chart_map = (alt.Chart(alt.Data(url=geo_url, format=alt.DataFormat(property="features", type="json")))
             .mark_geoshape(stroke="white")
             .encode(
    color=alt.Color(
        "boites_pour_1000:Q",
        title="Boîtes / 1000 hab",
        scale=alt.Scale(scheme="reds", reverse=False),
        legend=alt.Legend(labelLimit=300),),
    tooltip=[alt.Tooltip("properties.nom:N", title="Région"),
             alt.Tooltip("boites_pour_1000:Q", title="Boîtes / 1000", format=".0f")]).transform_lookup(
    lookup="properties.code",
    from_=alt.LookupData(df_map.assign(code=df_map["region"].astype(
        str)), key="code", fields=["boites_pour_1000"])).properties(height=420))

st.altair_chart(chart_map, use_container_width=True)

csv_map = df_map.to_csv(index=False, sep=";").encode("utf-8")

st.download_button(
    label="Télécharger les données de la carte (CSV)",
    data=csv_map,
    file_name=f"carte_{year_sel}_{atc1_for_map}.csv".replace(" ", "_"),
    mime="text/csv",)

st.markdown('<div id="pharmacies-offre"></div>', unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Densité de pharmacies par région")

    geo_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions.geojson"

    chart_pharma = (
        alt.Chart(
            alt.Data(
                url=geo_url,
                format=alt.DataFormat(property="features", type="json"))).mark_geoshape(stroke="white").encode(
            color=alt.Color("pharma_pour_100k:Q", title="Pharmacies / 100k hab",
                            scale=alt.Scale(scheme="reds", reverse=False),),
            tooltip=[
                alt.Tooltip("properties.nom:N", title="Région"),
                alt.Tooltip("pharma_pour_100k:Q",
                            title="Pharmacies / 100k", format=".0f"),],).transform_lookup(
            lookup="properties.code",
            from_=alt.LookupData(
                df_pharma.assign(code=df_pharma["region_code"].astype(str)),
                key="code",
                fields=["pharma_pour_100k"],),).properties(height=420))

    st.altair_chart(chart_pharma, use_container_width=True)

    top = df_pharma.sort_values("pharma_pour_100k", ascending=False).iloc[0]
    top_region = top.get("region", top.get("region_name", ""))
    st.info(
        f"La région la mieux dotée est {top_region} avec {int(top['pharma_pour_100k'])} pharmacies pour 100 000 habitants.")

with col2:
    st.markdown("### Offre pharmaceutique vs consommation")

    df_presc_2024 = df_atc1[df_atc1["annee"] == 2024].copy()

    df_presc_2024 = df_presc_2024.groupby("region", as_index=False).agg(
        boites=("boites", "sum"),
        population=("population", "first"))

    df_presc_2024["boites_pour_1000"] = (
        df_presc_2024["boites"] / df_presc_2024["population"] * 1000)

    df_scatter = df_presc_2024.merge(
        df_pharma[["region_code", "pharma_pour_100k"]],
        left_on="region",
        right_on="region_code",
        how="left")

    df_scatter["region_name"] = df_scatter["region"].map(region_map)

    chart_scatter = (alt.Chart(df_scatter).mark_circle(size=120).encode(
        x=alt.X("pharma_pour_100k:Q", title="Pharmacies / 100k habitants"),
        y=alt.Y("boites_pour_1000:Q", title="Boîtes / 1000 habitants"),
        tooltip=[
            alt.Tooltip("region_name:N", title="Région"),
            alt.Tooltip("pharma_pour_100k:Q",
                        title="Pharmacies / 100k", format=".0f"),
            alt.Tooltip("boites_pour_1000:Q",
                        title="Boîtes / 1000", format=".0f"),],).properties(height=420))

    st.altair_chart(chart_scatter, use_container_width=True)

    corr = df_scatter[["pharma_pour_100k",
                       "boites_pour_1000"]].corr().iloc[0, 1]
    st.metric("Corrélation", f"{corr:.2f}")

st.markdown('<div id="detail-par-sous-classes-atc2"></div>',
            unsafe_allow_html=True)

st.divider()
st.subheader("Détail par sous-classes ATC2")

df_atc2["annee"] = pd.to_numeric(df_atc2["annee"], errors="coerce")
df_atc2["region"] = pd.to_numeric(df_atc2["region"], errors="coerce")
df_atc2["boites_pour_1000"] = pd.to_numeric(
    df_atc2["boites_pour_1000"], errors="coerce")
df_atc2["l_atc2"] = df_atc2["l_atc2"].astype(str).str.strip()
df_atc2["atc2"] = df_atc2["atc2"].astype(str).str.strip()

if "atc1" not in df_atc2.columns:
    df_atc2["atc1"] = df_atc2["atc2"].str[0]

if "l_atc1" not in df_atc2.columns:
    atc1_ref = df_atc1[["atc1", "l_atc1"]].drop_duplicates()
    df_atc2 = df_atc2.merge(atc1_ref, on="atc1", how="left")

years_atc2 = sorted(df_atc2["annee"].dropna().unique().astype(int).tolist())
year_atc2 = st.selectbox("Année", options=years_atc2,
                         index=len(years_atc2) - 1, key="year_atc2")

atc1_codes_atc2 = sorted(df_atc2["atc1"].dropna().unique().tolist())
atc1_map_atc2 = (df_atc2[["atc1", "l_atc1"]].dropna(
).drop_duplicates().set_index("atc1")["l_atc1"].to_dict())

atc1_for_atc2 = st.selectbox(
    "Classe ATC1",
    options=atc1_codes_atc2,
    index=0,
    format_func=lambda x: f"{x} : {atc1_map_atc2.get(x, '')}".strip(" :"),
    key="atc1_for_atc2",)

regions_atc2 = sorted(df_atc2["region"].dropna().unique().astype(int).tolist())
region_atc2 = st.selectbox(
    "Région",
    options=["France entière"] + regions_atc2,
    index=0,
    format_func=lambda x: x if isinstance(
        x, str) else region_map.get(x, str(x)),
    key="region_atc2",)

top_n = st.slider("Nombre de sous-classes (Top N)", min_value=5,
                  max_value=20, value=10, step=1, key="topn_atc2")

df_atc2_f = df_atc2[(df_atc2["annee"] == year_atc2) &
                    (df_atc2["atc1"] == atc1_for_atc2)].copy()

if region_atc2 == "France entière":
    df_atc2_f = df_atc2_f.groupby(["atc2", "l_atc2"], as_index=False)[
        "boites_pour_1000"].sum()
else:
    df_atc2_f = df_atc2_f[df_atc2_f["region"] == int(region_atc2)].copy()
    df_atc2_f = df_atc2_f.groupby(["atc2", "l_atc2"], as_index=False)[
        "boites_pour_1000"].sum()

df_atc2_f = df_atc2_f.dropna(subset=["l_atc2", "boites_pour_1000"])
df_atc2_f = df_atc2_f.sort_values(
    "boites_pour_1000", ascending=False).head(top_n)

chart_atc2 = (alt.Chart(df_atc2_f).mark_bar().encode(
    x=alt.X("boites_pour_1000:Q", title="Boîtes / 1000 hab"),
    y=alt.Y("l_atc2:N", sort="-x", title=None),
    tooltip=[
        alt.Tooltip("atc2:N", title="ATC2"),
        alt.Tooltip("l_atc2:N", title="Libellé"),
        alt.Tooltip("boites_pour_1000:Q",
                    title="Boîtes / 1000", format=".0f"),],).properties(height=380))

st.altair_chart(chart_atc2, use_container_width=True)

csv_atc2 = df_atc2_f.to_csv(index=False, sep=";").encode("utf-8")
st.download_button(
    "Télécharger (Top ATC2)",
    data=csv_atc2,
    file_name=f"top_atc2_{year_atc2}_{atc1_for_atc2}.csv",
    mime="text/csv",
    key="dl_top_atc2",)

st.markdown('<div id="projection-atc1"></div>', unsafe_allow_html=True)

st.divider()
st.subheader("Projection tendancielle simple (ATC1)")

df_pred["annee"] = pd.to_numeric(df_pred["annee"], errors="coerce")
df_pred["boites_pour_1000"] = pd.to_numeric(
    df_pred["boites_pour_1000"], errors="coerce")
df_pred["atc1"] = df_pred["atc1"].astype(str).str.strip()
df_pred["l_atc1"] = df_pred["l_atc1"].astype(str).str.strip()

atc1_sel_pred = st.selectbox(
    "Classe ATC1",
    options=sorted(df_pred["atc1"].dropna().unique().tolist()),
    format_func=lambda x: f"{x} : {atc1_map.get(x, '')}".strip(" :"),
    key="atc1_pred")

df_tmp = df_pred[df_pred["atc1"] == atc1_sel_pred].copy()
hist = df_tmp[df_tmp["boites_pour_1000"].notna()].copy()

x = hist["annee"].astype(float).values
y = hist["boites_pour_1000"].astype(float).values

slope, intercept = np.polyfit(x, y, 1)
y_hat = slope * x + intercept
resid_std = np.std(y - y_hat, ddof=1)

future_years = np.array([2025, 2026, 2027], dtype=float)
y_pred = slope * future_years + intercept

band = 1.96 * resid_std
df_fut = pd.DataFrame({
    "annee": future_years.astype(int),
    "pred": y_pred,
    "low": y_pred - band,
    "high": y_pred + band, })

chart_hist = alt.Chart(hist).mark_line().encode(
    x=alt.X("annee:O", title="Année"),
    y=alt.Y("boites_pour_1000:Q", title="Boîtes / 1000 hab"),
    tooltip=[alt.Tooltip("annee:O", title="Année"),
             alt.Tooltip("boites_pour_1000:Q", title="Historique", format=".0f"),],)

chart_band = alt.Chart(df_fut).mark_area(opacity=0.25).encode(
    x=alt.X("annee:O", title="Année"),
    y=alt.Y("low:Q", title="Boîtes / 1000 hab"),
    y2="high:Q",
    tooltip=[alt.Tooltip("annee:O", title="Année"),
             alt.Tooltip("low:Q", title="Borne basse", format=".0f"),
             alt.Tooltip("high:Q", title="Borne haute", format=".0f"),],)

chart_pred = alt.Chart(df_fut).mark_line(strokeDash=[6, 4]).encode(
    x=alt.X("annee:O", title="Année"),
    y=alt.Y("pred:Q", title="Boîtes / 1000 hab"),
    tooltip=[alt.Tooltip("annee:O", title="Année"),
             alt.Tooltip("pred:Q", title="Projection", format=".0f"),],)

st.caption(
    "Projection linéaire sur 3 ans avec bande d’incertitude (approximation via résidus).")

st.altair_chart((chart_hist + chart_band +
                chart_pred).properties(height=320), use_container_width=True)

st.markdown('<div id="donnees-methodologie"></div>', unsafe_allow_html=True)

st.divider()

min_year = int(df_atc1["annee"].min())
max_year = int(df_atc1["annee"].max())
nb_regions = df_atc1["region"].nunique()
nb_atc1 = df_atc1["atc1"].nunique()
nb_atc2 = df_atc2["atc2"].nunique()

st.markdown(
    f"""
<div style="color: #6c757d; font-size: 0.95rem; line-height: 1.6">

<h3 style="color: #6c757d; margin-bottom: 0.5rem;">Données & Méthodologie</h3>

<b>Couverture des données :</b> {min_year}–{max_year} • {nb_regions} régions • {nb_atc1} classes ATC1 • {nb_atc2} sous-classes ATC2

<br><br>

<b>Sources :</b><br>
OpenMedic : données de prescriptions remboursées<br>
INSEE : population régionale via API<br>
CARMF : médecins libéraux (web scraping)<br>
OpenStreetMap : pharmacies (web scraping + Overpass API)

<br><br>

<b>Traitements réalisés :</b><br>
Agrégation par classe ATC1 / ATC2<br>
Calcul de ratios par habitant<br>
Calcul densité médicale régionale<br>
Calcul densité pharmaceutique régionale<br>
Nettoyage et harmonisation des régions

<br><br>

<b>Prédictions :</b><br>
Régression linéaire simple par classe ATC1<br>
Projection sur 3 ans uniquement<br>
Interprétation prudente des tendances

</div>
""",
    unsafe_allow_html=True
)
