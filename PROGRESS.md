# Dziennik postępów

## Tydzień 1 (Zakończony)
- Instalacja środowiska i inicjalizacja repozytorium Git.
- Zdefiniowanie problemu biznesowego, grupy docelowej oraz 4 perspektyw projektowych.
- Zaprojektowanie koncepcji wieloźródłowego pozyskiwania danych.
- Napisanie i przetestowanie skryptu w Pythonie (`src/extract.py`) pobierającego dane w formacie JSON-LD z Otodom i Morizon.
- Skuteczne zapisywanie surowych paczek danych z metadanymi czasowymi w lokalnej warstwie **Bronze** (`data/bronze/`)

## Tydzień 2 (Oczekujący)
- **Transformacja i warstwa Silver:**
  - Napisanie skryptu parsowania i spłaszczania zagnieżdżonych struktur JSON-LD z warstwy Bronze (`src/transform.py`).
  - Implementacja walidacji danych (obsługa braków cen, zabezpieczenie przed dzieleniem przez zero).
  - Automatyczne obliczanie kluczowej metryki biznesowej: **stawki za 1 m² (`price_per_m2`)**.
  - Zapis oczyszczonych danych do formatu płaskiego (`data/silver/clean_real_estate.csv`) oraz relacyjnej bazy analitycznej **DuckDB** (`data/real_estate.db`, tabela `silver_properties`).
  - Pomyślne przetestowanie i weryfikacja poprawności transformacji (przetworzono pulę unikalnych ofert nieruchomości we Wrocławiu).