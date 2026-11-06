import json
import os
import glob
import re
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

def normalize_street(text):
    """
    Podstawowa normalizacja: usuwa przedrostki typu ul./al./pl. i znaki specjalne.
    """
    if not text or pd.isna(text):
        return ""
    s = str(text).lower().strip()
    s = re.sub(r'^(ul\.|ulica|al\.|aleja|pl\.|plac)\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def remove_all_numbers(text):
    """
    Usuwa wszystkie cyfry z nazwy ulicy (np. 'Drukarska 39' -> 'Drukarska').
    """
    if not text or pd.isna(text):
        return ""
    s = str(text).lower().strip()
    s = re.sub(r'^(ul\.|ulica|al\.|aleja|pl\.|plac)\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\d+', '', s)
    s = re.sub(r'[^\w\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def load_address_mappings():
    """
    Wczytuje plik Adresy.xlsx i buduje słowniki automatycznego dopasowania:
    1. Dokładny / znormalizowany
    2. Bez cyfr
    3. Po ostatnim słowie ulicy
    """
    address_path = "Adresy.xlsx"
    if not os.path.exists(address_path):
        address_path = os.path.join(BRONZE_DIR, "Adresy.xlsx")
    
    if not os.path.exists(address_path):
        print("[Ostrzeżenie] Nie znaleziono pliku Adresy.xlsx.")
        return {}, {}, {}

    try:
        df_addr = pd.read_excel(address_path)
        
        def clean_delegatura(deg):
            if pd.isna(deg):
                return None
            deg_str = str(deg).replace("Wrocław-", "").replace("Wroclaw-", "").strip()
            return deg_str

        exact_map = {}
        no_num_map = {}
        last_word_map = {}

        for _, row in df_addr.iterrows():
            raw_st = row['ULICA_NAZWA']
            deg = clean_delegatura(row['GUS_TERC_DELEGATURA'])
            nei = row['RMWROC_OSIEDLE']
            info = {"district": deg, "neighborhood": nei}

            norm = normalize_street(raw_st)
            if norm and norm not in exact_map:
                exact_map[norm] = info

            no_num = remove_all_numbers(raw_st)
            if no_num and no_num not in no_num_map:
                no_num_map[no_num] = info

            words = norm.split()
            if words:
                last_word = words[-1]
                if len(last_word) > 3 and last_word not in last_word_map:
                    last_word_map[last_word] = info

        print(f"[Sukces] Wczytano bazę adresową EMUiA: {len(exact_map)} ulic.")
        return exact_map, no_num_map, last_word_map
    except Exception as e:
        print(f"[Błąd] Nie udało się przetworzyć pliku Adresy.xlsx: {e}")
        return {}, {}, {}

def parse_bronze_files():
    print("Rozpoczynam transformację danych z warstwy Bronze do Silver...")
    exact_map, no_num_map, last_word_map = load_address_mappings()
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
                    if "data_blocks" in block:
                        for b in block["data_blocks"]:
                            if "offers" in b and isinstance(b["offers"], dict):
                                offers_list.extend(b["offers"].get("offers", []))
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

                            district = None
                            neighborhood = None
                            
                            if street:
                                norm_st = normalize_street(street)
                                
                                # KROK 1: Dokładne dopasowanie po znormalizowanej ulicy
                                if norm_st in exact_map:
                                    district = exact_map[norm_st]["district"]
                                    neighborhood = exact_map[norm_st]["neighborhood"]
                                else:
                                    # KROK 2: Usunięcie cyfr z ulicy i ponowne szukanie
                                    no_num_st = remove_all_numbers(street)
                                    if no_num_st in no_num_map:
                                        district = no_num_map[no_num_st]["district"]
                                        neighborhood = no_num_map[no_num_st]["neighborhood"]
                                    else:
                                        # KROK 3: Szukanie po ostatnim słowie ulicy
                                        words = norm_st.split()
                                        if words:
                                            last_word = words[-1]
                                            if last_word in last_word_map:
                                                district = last_word_map[last_word]["district"]
                                                neighborhood = last_word_map[last_word]["neighborhood"]

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
                                "district": district,
                                "neighborhood": neighborhood,
                                "url": url,
                                "processed_at": datetime.now().isoformat()
                            })
                        except Exception as e:
                            continue

            except Exception as e:
                print(f"Błąd parsowania pliku {file_path}: {e}")

    df = pd.DataFrame(all_offers)
    
    if not df.empty:
        initial_count = len(df)
        df = df[df["price_per_m2"].notnull() & (df["price_per_m2"] > 0)]
        print(f"Odrzucono {initial_count - len(df)} ofert bez ceny za m2.")

        if "url" in df.columns:
            before_dedup = len(df)
            df = df.sort_values(by="processed_at", ascending=False)
            df = df.drop_duplicates(subset=["url"], keep="first")
            print(f"Usunięto duplikaty po URL: odrzucono {before_dedup - len(df)} powtórzonych ofert.")

    return df

if __name__ == "__main__":
    df_silver = parse_bronze_files()
    
    if not df_silver.empty:
        print(f"\n[Sukces] Po transformacji i deduplikacji zostało {len(df_silver)} unikalnych ofert.")
        print("\nRozkład ofert na oficjalne dzielnice:")
        print(df_silver["district"].value_counts(dropna=False))
        
        silver_csv_path = os.path.join(SILVER_DIR, "clean_real_estate.csv")
        df_silver.to_csv(silver_csv_path, index=False, encoding="utf-8-sig")
        print(f"\nZapisano tabelę warstwy Silver do: {silver_csv_path}")

        con = duckdb.connect("data/real_estate.db")
        con.execute("CREATE OR REPLACE TABLE silver_properties AS SELECT * FROM df_silver")
        print("Zapisano dane do bazy DuckDB (tabela: silver_properties).")
        con.close()
    else:
        print("Nie udało się wyciągnąć ofert z dostępnych plików Bronze.")