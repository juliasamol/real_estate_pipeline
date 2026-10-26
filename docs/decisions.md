# Rejestr Decyzji Projektowycj

## Decyzjca 1: Metoda ekstrakcji danych (Web Scraping danych strukturalnych JSON-LD)
- **Data:** Tydzień 1
- **Wybór:** Zastosowanie celowanego pobierania danych strukturalnych (JSON-LD / Schema.org) bezpośrednio z kodu HTML publicznych stron ogłoszeniowych (Otodom i Morizon) w trybie cyklicznym.
- **Rozważane alternatywy:** 
  1. *Oficjalne API komercyjne* – odrzucone ze względu na brak darmowych interfejsów programistycznych dla zewnętrznych deweloperów nieruchomościowych.
  2. *Tradycyjny web scraping* – odrzucone ze względu na dużą niestabilność i podatność na częste zmiany w szacie graficznej portalu.
- **Uzasadnienie:** Standard JSON-LD dostarcza czyste, ustandaryzowane dane wprost od dostawcy (wymagane przez wyszukiwarki), co pozwala na niezawodne i powtarzalne budowanie warstwy surowej (Bronze) przy zachowaniu dobrych praktyk inżynierskich.

## Decyzja 2: Wybór lokalnej bazy danych DuckDB do warstwy Silver
- **Data:** Tydzeiń 2
- **Wybór:** Baza DuckDB
- **Uzasadnienie:** DuckDB doskonale integruje się z biblioteką Pandas, pozwala na szybkie zapytania SQL na lokalnym sprzęcie bez konieczności stawiania ciężkich silników bazodanowych, idealnie wspierając architekturę analityczną projektu.

## Decyzja 3: Strategia deduplikacji po adresie URL w warstwie Silver
- **Data:** Tydzień 3
- **Wybór:** Wprowadzenie deduplikacji w skrypcie `transform.py` oparty na unikalnym kluczu `url` z zachowaniem najnowszego rekordu (`keep="first"` po posortowaniu malejąco po `processed_at`).
- **Uzasadnienie:** Wielokrotne pobieranie danych w różnych dniach powoduje powtarzanie się tych samych aktywnych ofert w plikach warstwy Bronze. Warstwa Silver zawiera wyłącznie unikalne, aktualne rekordy, co zapobiega sztucznemu zaniżaniu/zawyżaniu liczności ofert w analizach analitycznych.

## Decyzja 4: Rezygnacja ze sztywnego słownika na rzecz pliku referencyjnego EMUiA
- **Data:** Tydzień 3
- **Decyzja:** Wykorzystanie urzędowego pliku `Adresy.xlsx` (EMUiA Wrocław) zawierającego ulice i odpowiadające im regiony do przypisania jednolitych regionów administracyjnych miasta do ulic podanych w ogłoszeniach.
- **Konsekwencje:** Pełna automatyzacja, zgodność z oficjalnym podziałem administracyjnym miasta.