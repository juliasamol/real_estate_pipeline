import json
import os
import glob
from datetime import datetime
import pandas as pd
import duckdb

BRONZE_DIR = "data/bronze"
SILVER_DIR = "data/silver"
os.makedirs(SILVER_DIR, exist_ok=True)

def parse_bronze_files():
    """
    Odczytuje surowe pliki JSON z warstwy Bronze, spłaszcza zagnieżdżone struktury
    i wyciąga poszczególne oferty mieszkań.
    """
    print("Rozpoczynam transformację danych z warstwy Bronze do Silver...")
    all_offers = []

    # Wyszukaj wszystkie pliki JSON w warstwie Bronze
    json_files = glob.glob(os.path.join(BRONZE_DIR, "*.json"))
    
    if not json_files:
        print("Brak plików w warstwie Bronze do przetworzenia.")
        return pd.DataFrame()

    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                content = json.load(f)
                source = content.get("source_platform") or content.get("source")
                data_blocks = content.get("data", [])

                for block in data_blocks:
                    # Sprawdzamy czy blok zawiera listę ofert (AggregateOffer lub @graph)
                    offers_list = []
                    
                    # Przypadek 1: Bezpośredni słownik z offers -> offers
                    if "offers" in block and isinstance(block["offers"], dict):
                        offers_list = block["offers"].get("offers", [])
                    
                    # Przypadek 2: Struktura @graph (często w Otodom)
                    if "@graph" in block:
                        for graph_item in block["@graph"]:
                            if "offers" in graph_item and isinstance(graph_item["offers"], dict):
                                offers_list.extend(graph_item["offers"].get("offers", []))

                    # Parsowanie pojedynczych ofert
                    for offer in offers_list:
                        try:
                            name = offer.get("name")
                            price = float(offer.get("price", 0)) if offer.get("price") else None
                            url = offer.get("url")
                            
                            item_offered = offer.get("itemOffered", {})
                            rooms = item_offered.get("numberOfRooms")
                            
                            # Obsługa liczby pokoi jeśli jest słownikiem (np. min/max)
                            if isinstance(rooms, dict):
                                rooms = rooms.get("minValue")
                            
                            floor_size = item_offered.get("floorSize", {})
                            if isinstance(floor_size, dict):
                                area = float(floor_size.get("value", 0)) if floor_size.get("value") else None
                            else:
                                area = None

                            address_obj = item_offered.get("address", {})
                            street = address_obj.get("streetAddress")
                            locality = address_obj.get("addressLocality")

                            if price and area and area > 0:
                                price_per_m2 = round(price / area, 2)
                            else:
                                price_per_m2 = None

                            all_offers.append({
                                "source": source,
                                "title": name,
                                "price_pln": price,
                                "area_m2": area,
                                "price_per_m2": price_per_m2,
                                "number_of_rooms": rooms,
                                "street": street,
                                "locality": locality,
                                "url": url,
                                "processed_at": datetime.now().isoformat()
                            })
                        except Exception as e:
                            continue

            except Exception as e:
                print(f"Błąd parsowania pliku {file_path}: {e}")

    df = pd.DataFrame(all_offers)
    return df

if __name__ == "__main__":
    df_silver = parse_bronze_files()
    
    if not df_silver.empty:
        print(f"\n[Sukces] Przetworzono i spłaszczono {len(df_silver)} unikalnych ofert nieruchomości.")
        print("\nPrzykładowe wiersze przekształconych danych:")
        print(df_silver[["source", "price_pln", "area_m2", "price_per_m2", "number_of_rooms", "locality"]].head(5))
        
        # Zapis do pliku CSV/Parquet w warstwie Silver oraz do bazy DuckDB
        silver_csv_path = os.path.join(SILVER_DIR, "clean_real_estate.csv")
        df_silver.to_csv(silver_csv_path, index=False, encoding="utf-8")
        print(f"\nZapisano tabelę warstwy Silver do: {silver_csv_path}")

        # Zapis do lokalnej bazy DuckDB
        con = duckdb.connect("data/real_estate.db")
        con.execute("CREATE OR REPLACE TABLE silver_properties AS SELECT * FROM df_silver")
        print("Zapisano dane do bazy DuckDB (tabela: silver_properties).")
        con.close()
    else:
        print("Nie udało się wyciągnąć ofert z dostępnych plików Bronze.")