import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

BRONZE_DIR = "data/bronze"
os.makedirs(BRONZE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.9"
}

def extract_otodom(max_pages=10):
    """
    Pobiera oferty z Otodom w sposób wielostronicowy.
    """
    all_offers = []
    print(f"\n[Otodom] Rozpoczynam pobieranie (max {max_pages} stron)...")

    for page in range(1, max_pages + 1):
        url = f"https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/dolnoslaskie/wroclaw/wroclaw/wroclaw?page={page}"
        print(f"[Otodom] Strona {page} -> {url}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                print(f"[Otodom] Strona {page} zwróciła kod {response.status_code}. Koniec.")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            script_tag = soup.find("script", id="__NEXT_DATA__")
            
            if script_tag and script_tag.string:
                json_data = json.loads(script_tag.string)
                
                page_props = json_data.get("props", {}).get("pageProps", {})
                ads = []
                if "data" in page_props and isinstance(page_props["data"], dict):
                    search_ads = page_props["data"].get("searchAds", {})
                    if isinstance(search_ads, dict):
                        ads = search_ads.get("items", [])
                
                if not ads and "searchAds" in page_props:
                    ads = page_props["searchAds"].get("items", [])

                if not ads:
                    print(f"[Otodom] Brak ofert na stronie {page}.")
                    break

                page_wrapper = {"source": "otodom", "page": page, "offers": {"offers": []}}
                for ad in ads:
                    location = ad.get("location", {}) or {}
                    address = location.get("address", {}) or {}
                    street_obj = address.get("street", {}) or {}
                    district_obj = address.get("district", {}) or {}
                    total_price = ad.get("totalPrice", {}) or {}

                    page_wrapper["offers"]["offers"].append({
                        "name": ad.get("title"),
                        "price": total_price.get("value"),
                        "url": f"https://www.otodom.pl/pl/oferta/{ad.get('slug')}",
                        "itemOffered": {
                            "numberOfRooms": ad.get("roomsNumber"),
                            # Używamy poprawionego pola odkrytego w strukturze JSON
                            "floorSize": {"value": ad.get("areaInSquareMeters")},
                            "address": {
                                "streetAddress": street_obj.get("name"),
                                "addressLocality": district_obj.get("name", "Wrocław")
                            }
                        }
                    })
                all_offers.append(page_wrapper)
                print(f"[Otodom] Sukces: pobrano {len(ads)} ofert ze strony {page}.")
            else:
                print(f"[Otodom] Brak znacznika __NEXT_DATA__ na stronie {page}.")
                break
        except Exception as e:
            print(f"[Otodom] Błąd na stronie {page}: {e}")
            break

    return all_offers

def extract_morizon_stable():
    """
    Pobiera dane z Morizon.
    """
    print(f"\n[Morizon] Rozpoczynam pobieranie ze źródła...")
    url = "https://www.morizon.pl/mieszkania/wroclaw/"
    
    all_records = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"[Morizon] Serwer zwrócił kod {response.status_code}.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        ld_scripts = soup.find_all("script", {"type": "application/ld+json"})
        
        page_data = {"source": "morizon", "page": 1, "data_blocks": []}
        block_count = 0
        for script in ld_scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    page_data["data_blocks"].append(data)
                    block_count += 1
            except:
                pass

        if block_count > 0:
            all_records.append(page_data)
            print(f"[Morizon] Sukces: pobrano {block_count} bloków ld+json.")
        else:
            print("[Morizon] Nie znaleziono bloków danych.")
            
    except Exception as e:
        print(f"[Morizon] Błąd podczas pobierania: {e}")

    return all_records

def save_to_bronze(data, source_name):
    if not data:
        print(f"[{source_name}] Brak danych do zapisu.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(BRONZE_DIR, f"raw_{source_name}_wroclaw_{timestamp}.json")
    
    payload = {
        "pipeline_layer": "bronze",
        "source_platform": source_name,
        "extracted_at": datetime.now().isoformat(),
        "total_records": len(data),
        "data": data
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    
    print(f"[Sukces] Zapisano plik Bronze dla '{source_name}': {file_path}")

if __name__ == "__main__":
    print("--- START KOMPLETNEJ EKSTRAKCJI (OTODOM + MORIZON) ---")
    
    # 1. Otodom wielostronicowy
    otodom_data = extract_otodom(max_pages=10)
    save_to_bronze(otodom_data, "otodom")
    
    print("\n" + "="*50 + "\n")
    
    # 2. Morizon stabilny
    morizon_data = extract_morizon_stable()
    save_to_bronze(morizon_data, "morizon")
    
    print("\n--- KONIEC EKSTRAKCJI ---")