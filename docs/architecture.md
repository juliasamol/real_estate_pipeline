# Architektura Potoku Danych – Wrocławski Detektor Okazji Nieruchomicowych

## Warstwy Przetwarzania (Medallion Architecture)

1. **Warstwa Bronze (`data/bronze/`):**
   - **Format:** Surowe pliki JSON ze znacznikami czasowymi (`raw_<source>_wroclaw_<timestamp>.json`).
   - **Cel:** Pełne archiwum historyczne zrzutów z portali. Otodom pobierany jest wielostronicowo przez parsowanie Next.js (`__NEXT_DATA__`), natomiast Morizon poprzez bloki `ld+json`.
2. **Warstwa Silver (`data/silver/` i `data/real_estate.db`):**
   - **Format:** Plik CSV (`clean_real_estate.csv` z kodowaniem `utf-8-sig`) oraz tabela relacyjna w **DuckDB** (`silver_properties`).
   - **Zadania ETL (`src/transform.py`):**
     - Normalizacja schematów z różnych źródeł.
     - Konwersja typów danych (np. mapowanie słownych liczby pokoi na int).
     - Czyszczenie danych (odrzucanie ofert bez ceny za m²).
     - Deduplikacja: Usuwanie duplikatów po unikalnym adresie `url` (priorytetyzacja najnowszego wpisu bazująca na `processed_at`).
     - Warstwa Silver (`src/transform.py`) korzysta z lokalnego pliku referencyjnego `Adresy.xlsx` (oficjalna baza EMUiA Wrocław).
     - Do ulic pobranych z platform z ogłoszeniami dodano dzielnicę i osiedle ze słownika `Adresy.xlsx`.
     - Rekordy z nierozpoznaną ulicą zachowują puste wartości pól administracyjnych do późniejszego oznaczenia w interfejsie aplikacji (np. "Nie sprecyzowano dzielnicy").
3. **Warstwa Gold (Planowana):**
   - Agregacje analityczne, wykrywanie anomalii cenowych, wskaźniki rynkowe i detekcja "okazji" inwestycyjnych przy użyciu zapytań SQL w DuckDB.