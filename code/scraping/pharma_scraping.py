import requests
import pandas as pd
import time

regions = [
    "Auvergne-Rhône-Alpes",
    "Bourgogne-Franche-Comté",
    "Bretagne",
    "Centre-Val de Loire",
    "Corse",
    "Grand Est",
    "Hauts-de-France",
    "Île-de-France",
    "Normandie",
    "Nouvelle-Aquitaine",
    "Occitanie",
    "Pays de la Loire",
    "Provence-Alpes-Côte d'Azur"]


def scrape_pharmacies():
    all_dfs = []
    url = "http://overpass-api.de/api/interpreter"

    for region in regions:
        query = f"""
        [out:json][timeout:300];
        area["name"="{region}"]["admin_level"="4"]->.searchArea;
        (
          node["amenity"="pharmacy"](area.searchArea);
          way["amenity"="pharmacy"](area.searchArea);
          relation["amenity"="pharmacy"](area.searchArea););out center;"""

        response = requests.post(url, data={"data": query}, timeout=310)

        if response.status_code == 200:
            data = response.json()
            elements = data.get("elements", [])

            temp_list = []

            for e in elements:
                lat = e.get("lat")
                lon = e.get("lon")

                if "center" in e:
                    lat = e["center"].get("lat")
                    lon = e["center"].get("lon")

                temp_list.append({
                    "osm_id": f"{e.get('type')}_{e.get('id')}",
                    "nom": e.get("tags", {}).get("name"),
                    "ville": e.get("tags", {}).get("addr:city"),
                    "cp": e.get("tags", {}).get("addr:postcode"),
                    "region": region,
                    "lat": lat,
                    "lon": lon})

            df_temp = pd.DataFrame(temp_list)
            all_dfs.append(df_temp)

        time.sleep(10)

    df_final = pd.concat(all_dfs, ignore_index=True)
    df_final = df_final.drop_duplicates(subset="osm_id")
    df_final.to_csv("pharmacies_france_FINAL.csv",
                    index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    scrape_pharmacies()
