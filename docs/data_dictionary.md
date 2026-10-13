# Słownik Danych  - tabela `silver_properties` (warstwa Silver)

| Nazwa kolumny | Typ danych | Opis / Znaczenie biznesowe                                                                        |
| :--- | :--- |:--------------------------------------------------------------------------------------------------|
| `source` | VARCHAR | Portal źródłowy ogłoszenia (`otodom` lub `morizon`).                                              |
| `title` | VARCHAR | Oryginalny tytuł ogłoszenia nieruchomości.                                                        |
| `price_pln` | DECIMAL | Całkowita cena nieruchomości w PLN.                                                               |
| `area_m2` | DECIMAL | Powierzchnia użytkowa nieruchomości w metrach kwadratowych ($m^2$).                               |
| `price_per_m2`| DECIMAL | Obliczona stawka za 1 $\text{m}^2$ (`price_pln / area_m2`), zaokrąglona do 2 miejsc po przecinku. |
| `number_of_rooms`| INTEGER | Liczba pokoi w oferowanym lokalu.                                                                 |
| `street` | VARCHAR | Ulica lub dokładny adres lokalizacji (jeśli podano w ofercie).                                    |
| `locality` | VARCHAR | Dzielnica / mikroregion we Wrocławiu (wzbogacona algorytmicznie w warstwie Silver).               |
| `url` | VARCHAR | Bezpośredni link do oryginalnego ogłoszenia w sieci.                                              |
| `processed_at` | TIMESTAMP | Znacznik czasu wykonania transformacji i zapisu rekordu.                                          |