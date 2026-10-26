import os
import pandas as pd

SILVER_CSV = "data/silver/clean_real_estate.csv"

def run_quality_tests():
    print("--- ROZPOCZYNAM AUTOMATYCZNE TESTY JAKOŚCI DANYCH (WARSTWA SILVER) ---")
    
    if not os.path.exists(SILVER_CSV):
        raise FileNotFoundError(f"[BŁĄD KRYTYCZNY] Nie znaleziono pliku wynikowego warstwy Silver: {SILVER_CSV}. Uruchom najpierw transform.py!")
    
    df = pd.read_csv(SILVER_CSV)
    print(f"Wczytano do testów {len(df)} rekordów.\n")
    
    errors_found = 0

    # --- TEST 1: Kompletność kluczowych kolumn (Reguła: Kompletność) ---
    print("Test 1: Sprawdzanie kompletności (brak NaN w price_pln, area_m2, url)...")
    critical_cols = ["price_pln", "area_m2", "url"]
    for col in critical_cols:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            print(f"  [NIEPOWODZENIE] Kolumna '{col}' zawiera {null_count} pustych wartości!")
            errors_found += 1
        else:
            print(f"  [OK] Kolumna '{col}' jest kompletna.")

    # --- TEST 2: Unikalność adresów URL (Reguła: Unikalność) ---
    print("\nTest 2: Sprawdzanie unikalności ofert po URL...")
    if "url" in df.columns:
        duplicates_count = df.duplicated(subset=["url"]).sum()
        if duplicates_count > 0:
            print(f"  [NIEPOWODZENIE] Znaleziono {duplicates_count} zduplikowanych adresów URL!")
            errors_found += 1
        else:
            print(f"  [OK] Wszystkie adresy URL są unikalne.")

    # --- TEST 3: Poprawność zakresu cenowego (Reguła: Poprawność zakresu) ---
    print("\nTest 3: Sprawdzanie zakresu cenowego (price_pln > 0)...")
    if "price_pln" in df.columns:
        invalid_prices = (df["price_pln"] <= 0).sum()
        if invalid_prices > 0:
            print(f"  [NIEPOWODZENIE] Znaleziono {invalid_prices} ofert z ceną <= 0 PLN!")
            errors_found += 1
        else:
            print(f"  [OK] Wszystkie ceny są większe od 0.")

    # --- TEST 4: Poprawność zakresu powierzchni (Reguła: Poprawność zakresu) ---
    print("\nTest 4: Sprawdzanie zakresu powierzchni (10 m² <= area_m2 <= 1000 m²)...")
    if "area_m2" in df.columns:
        invalid_area = ((df["area_m2"] < 10) | (df["area_m2"] > 1000)).sum()
        if invalid_area > 0:
            print(f"  [NIEPOWODZENIE] Znaleziono {invalid_area} ofert z powierzchnią poza zakresem [10, 1000] m²!")
            errors_found += 1
        else:
            print(f"  [OK] Wszystkie powierzchnie mieszczą się w poprawnym zakresie.")

    # --- TEST 5: Poprawność dozwolonych wartości źródła (Reguła: Dozwolone wartości) ---
    print("\nTest 5: Sprawdzanie dozwolonych wartości źródła...")
    if "source" in df.columns:
        allowed_sources = {"otodom", "morizon"}
        invalid_sources = ~df["source"].isin(allowed_sources)
        invalid_count = invalid_sources.sum()
        if invalid_count > 0:
            print(f"  [NIEPOWODZENIE] Znaleziono {invalid_count} rekordów z nieznanym źródłem!")
            errors_found += 1
        else:
            print(f"  [OK] Wszystkie źródła należą do zdefiniowanej listy ({allowed_sources}).")

    print("\n" + "="*60)
    if errors_found > 0:
        print(f"[WYNIK TESTÓW] Testy zakończone NIEPOWODZENIEM. Wykryto {errors_found} błędów jakości danych.")
        exit(1) # Zwraca kod błędu widoczny dla systemu/automatyzacji
    else:
        print("[WYNIK TESTÓW] Sukces! Wszystkie testy jakości danych przeszły pomyślnie.")
        exit(0)

if __name__ == "__main__":
    run_quality_tests()