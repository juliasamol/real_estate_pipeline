import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Ścieżka do warstwy Bronze
BRONZE_DIR = "data/bronze"
os.makedirs(BRONZE_DIR, exist_ok=True)

# Nagłówki udające zwykłą przeglądarkę (zapobiegają natychmiastowemu odrzuceniu zapytania)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.9"
}

def extract_json_ld_from_url(url, source_name):
    """
    Pobiera stronę HTML z podanego adresu URL i wyciąga z niej 
    wszystkie ustrukturyzowane bloki danych JSON-LD (Schema.org).
    """
    print(f"[{source_name}] Łączę się z adresem: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            print(f"[{source_name}] Ostrzeżenie: Serwer zwrócił kod HTTP {response.status_code}. Strona mogła zablokować zapytanie.")
            return []

        # Parsowanie kodu HTML strony
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Wyszukiwanie znaczników <script type="application/ld+json">
        ld_scripts = soup.find_all("script", {"type": "application/ld+json"})
        print(f"[{source_name}] Znaleziono {len(ld_scripts)} bloków danych strukturalnych JSON-LD.")

        extracted_records = []
        for script in ld_scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    extracted_records.append(data)
            except json.JSONDecodeError:
                continue

        return extracted_records

    except Exception as e:
        print(f"[{source_name}] Wystąpił błąd krytyczny podczas pobierania: {e}")
        return []

def save_to_bronze(data, source_name):
    """
    Zapisuje pobrane surowe dane do warstwy Bronze w formacie JSON z metadanymi czasowymi.
    """
    if not data:
        print(f"[{source_name}] Brak danych do zapisu w warstwie Bronze.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(BRONZE_DIR, f"raw_{source_name}_wroclaw_{timestamp}.json")
    
    payload = {
        "pipeline_layer": "bronze",
        "source_platform": source_name,
        "extracted_at": datetime.now().isoformat(),
        "record_count": len(data),
        "data": data
    }
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)
    
    print(f"[Sukces] Zapisano dane ze źródła '{source_name}' do: {file_path}")

if __name__ == "__main__":
    print("--- ROZPOCZĘCIE PROCESU EKSTRAKCJI DANYCH (OTODOM & MORIZON) ---")
    
    # Adresy URL dla Wrocławia
    otodom_url = "https://www.otodom.pl/pl/wyniki/sprzedaz/mieszkanie/dolnoslaskie/wroclaw/wroclaw/wroclaw"
    morizon_url = "https://www.morizon.pl/mieszkania/wroclaw/"
    
    # 1. Ekstrakcja z Otodom
    otodom_data = extract_json_ld_from_url(otodom_url, "otodom")
    if otodom_data:
        print("\n--- PODGLĄD PIERWSZEGO REKORDU Z OTODOM ---")
        print(json.dumps(otodom_data[0], ensure_ascii=False, indent=4))
    save_to_bronze(otodom_data, "otodom")
    
    print("\n" + "="*50 + "\n")
    
    # 2. Ekstrakcja z Morizon
    morizon_data = extract_json_ld_from_url(morizon_url, "morizon")
    if morizon_data:
        print("\n--- PODGLĄD PIERWSZEGO REKORDU Z MORIZON ---")
        print(json.dumps(morizon_data[0], ensure_ascii=False, indent=4))
    save_to_bronze(morizon_data, "morizon")
    
    print("\n--- ZAKOŃCZONO ETAP EKSTRAKCJI ---")