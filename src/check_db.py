import duckdb

def check_database():
    print("Łączenie z lokalną bazą DuckDB (data/real_estate.db)...")
    con = duckdb.connect("data/real_estate.db")

    # 1. Sprawdzenie dostępnych tabel
    print("\n--- DOSTĘPNE TABELE W BAZIE ---")
    tables_df = con.execute("SHOW TABLES;").fetchdf()
    print(tables_df)

    # 2. Sprawdzenie liczby wszystkich ofert
    print("\n--- STATYSTYKA OGÓLNA ---")
    count_df = con.execute("SELECT COUNT(*) AS total_offers FROM silver_properties;").fetchdf()
    print(count_df)

    # 3. Agregacja: Średnia cena za m² w podziale na dzielnice
    print("\n--- ŚREDNIA CENA ZA M² W PODZIALE NA DZIELNICE ---")
    summary_df = con.execute("""
        SELECT 
            locality, 
            COUNT(*) AS liczba_ofert, 
            ROUND(AVG(price_per_m2), 2) AS srednia_cena_m2,
            ROUND(AVG(price_pln), 2) AS srednia_cena_calkowita
        FROM silver_properties 
        GROUP BY locality 
        ORDER BY srednia_cena_m2 DESC;
    """).fetchdf()
    print(summary_df)

    # 4. Podgląd pierwszych 5 ofert
    print("\n--- PRZYKŁADOWE OFERTY (TOP 5) ---")
    sample_df = con.execute("""
        SELECT source, price_pln, area_m2, price_per_m2, number_of_rooms, locality 
        FROM silver_properties 
        LIMIT 5;
    """).fetchdf()
    print(sample_df)

    # Zamknięcie połączenia
    con.close()
    print("\nPołączenie z bazą zostało zamknięte.")

if __name__ == "__main__":
    check_database()