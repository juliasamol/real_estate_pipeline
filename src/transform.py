import json
import os
import glob
from datetime import datetime
import pandas as pd
import duckdb

BRONZE_DIR = "data/bronze"
SILVER_DIR = "data/silver"
os.makedirs(SILVER_DIR, exist_ok=True)

def map_rooms_to_numeric(rooms):
    """
    Mapuje słowne lub niestandardowe oznaczenia liczby pokoi na wartości numeryczne.
    """
    if rooms is None:
        return None
    if isinstance(rooms, (int, float)):
        return int(rooms)
    
    mapping = {
        "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5, "SIX": 6,
        "SEVEN": 7, "EIGHT": 8, "NINE": 9, "TEN": 10
    }
    
    if isinstance(rooms, str):
        cleaned = rooms.strip().upper()
        if cleaned in mapping:
            return mapping[cleaned]
        try:
            return int(float(cleaned))
        except ValueError:
            pass
            
    return None

def parse_bronze_files():
    """
    Odczytuje pliki JSON z warstwy Bronze dla obu platform (Otodom i Morizon),
    spłaszcza struktury i przygotowuje ujednolicony zbiór danych.
    """
    print("Rozpoczynam transformację danych z warstwy Bronze do Silver...")
    all_offers = []

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
                    offers_list = []
                    
                    # Morizon
                    if "data_blocks" in block:
                        for b in block["data_blocks"]:
                            if "offers" in b and isinstance(b["offers"], dict):
                                offers_list.extend(b["offers"].get("offers", []))
                    
                    # Otodom
                    if "offers" in block and isinstance(block["offers"], dict):
                        offers_list.extend(block["offers"].get("offers", []))

                    for offer in offers_list:
                        try:
                            name = offer.get("name")
                            price = float(offer.get("price", 0)) if offer.get("price") else None
                            url = offer.get("url")
                            
                            item_offered = offer.get("itemOffered", {})
                            rooms_raw = item_offered.get("numberOfRooms")
                            rooms = map_rooms_to_numeric(rooms_raw)
                            
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
    
    if not df.empty:
        # 1. Filtrowanie: pozostawiamy tylko oferty z poprawną ceną za m2
        initial_count = len(df)
        df = df[df["price_per_m2"].notnull() & (df["price_per_m2"] > 0)]
        print(f"Odrzucono {initial_count - len(df)} ofert bez ceny za m2.")

        # 2. Deduplikacja po unikalnym URL (zostawiamy najnowszy wpis)
        if "url" in df.columns:
            before_dedup = len(df)
            # Sortujemy po dacie przetworzenia, żeby drop_duplicates zachowało najświeższy rekord
            df = df.sort_values(by="processed_at", ascending=False)
            df = df.drop_duplicates(subset=["url"], keep="first")
            print(f"Usunięto duplikaty po URL: odrzucono {before_dedup - len(df)} powtórzonych ofert.")

    return df

if __name__ == "__main__":
    df_silver = parse_bronze_files()
    
    if not df_silver.empty:
        print(f"\n[Sukces] Po transformacji i deduplikacji zostało {len(df_silver)} unikalnych ofert.")
        print("\nRozkład unikalnych ofert według źródeł:")
        print(df_silver["source"].value_counts())
        
        # Zapis do pliku CSV (utf-8-sig dla poprawnych polskich znaków w Excelu)
        silver_csv_path = os.path.join(SILVER_DIR, "clean_real_estate.csv")
        df_silver.to_csv(silver_csv_path, index=False, encoding="utf-8-sig")
        print(f"\nZapisano tabelę warstwy Silver do: {silver_csv_path}")

        # Zapis do bazy DuckDB
        con = duckdb.connect("data/real_estate.db")
        con.execute("CREATE OR REPLACE TABLE silver_properties AS SELECT * FROM df_silver")
        print("Zapisano unikalne dane do bazy DuckDB (tabela: silver_properties).")
        con.close()
    else:
        print("Nie udało się wyciągnąć ofert z dostępnych plików Bronze.")