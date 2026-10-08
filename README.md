# *Wieloźródłowy system wykrywania okazji na rynku nieruchomości*

## 1. Opis i cel projektu

Projekt ma na celu stworzenie zautomatyzowanego systemu wspierającego podejmowanie decyzji inwestycyjnych na rynku nieruchomości w segmencie mieszkaniowym we Wrocławiu. Jest on adresowany do inwestorów na rynku nieruchomości, którzy każdego dnia tracą cenne godziny na ręcznym przeszukiwaniu setek nowych ogłoszeń w poszukiwaniu atrakcyjnych ofert. Głównym celem systemu jest automatyczne i błyskawiczne wyłapywanie tzw. „perełek inwestycyjnych” – czyli mieszkań, których cena za metr kwadratowy jest znacząco niższa od rynkowej średniej w danej lokalizacji.

Dzięki automatycznej integracji danych z wielu różnych portali ogłoszeniowych, narzędzie samodzielnie pobiera oferty, standaryzuje je, przelicza mediany cenowe i w czasie rzeczywistym wskazuje te, które najbardziej opłaca się kupić pod kątem szybkiego flipu lub wynajmu. Całość wspierana jest przez potok danych (data pipeline) dbający o ich jakość oraz interaktywną aplikację analityczną w Streamlit, która w przejrzysty sposób prezentuje gotowe okazje biznesowe. Proces został zrealizowany w architekturze medalionowej (Bronze -> Silver -> Gold), a jego jakość zapewniają testy.

* **Konkretny odbiorca:** inwestor indywidualny / tzw. "flipper" poszukujący okazyjnych ofert mieszkań poniżej wartości rynkowej z potencjałem na szybką odsprzedaż lub wynajem.
* **Potrzeba informacyjna i proces decyzyjny:** odbiorca potrzebuje bieżącej identyfikacji niedoszacowanych ofert w konkretnych dzielnicach Wrocławia na tle średnich cen rynkowych, aby szybko podjąć decyzję o kontakcie ze sprzedającym lub zakupie nieruchomości.

## 2. Kluczowe pytania analityczne
Zbierane i przetwarzane w potoku dane muszą umożliwić odpowiedź na następujące pytania badawcze:
1. Jakie są aktualne średnie ceny za metr kwadratowy (m²) mieszkań w poszczególnych dzielnicach Wrocławia?
2. Które konkretne oferty aktywne na portalach (Otodom, Morizon) charakteryzują się ceną za m² znacząco niższą (np. o 15% lub więcej) od średniej rynkowej w danej lokalizacji?
3. Gdzie we Wrocławiu występują największe dysproporcje cenowe między rynkiem wtórnym a nowym budownictwem w ramach tej samej dzielnicy?
4. Jak liczba pokoi oraz powierzchnia użytkowa wpływają na stawkę za m² w ujęciu mikroregionalnym?

## 3. Źródła danych i metodologia
* **Źródła danych:** Komercyjne portale ogłoszeniowe dla Wrocławia (Otodom, Morizon).
* **Metoda ekstrakcji:** cykliczny import  ustrukturyzowanych danych z formatu **JSON-LD (Schema.org)** osadzanego w kodzie stron, co zapewnia czystość pobieranych rekordów i zgodność z architekturą warstwową (Bronze -> Silver -> Gold).

## 4. Stos technologiczny
* **Język:** Python (requests, BeautifulSoup)
* **Przechowywanie i przetwarzanie:** DuckDB
* **Transformacje:** dbt (data build tool)
* **Prezentacja / Wizualizacja:** Streamlit

## 5. Struktura repozytorium
- `src/` - skrypty Pythona odpowiedzialne za ekstrakcję oraz transformacje,
- `data/` - warstwowy magazyn danych (Bronze, Silver, Gold),
- `docs/` - dokumentacja projektowa (perspektywy, architektura, słownik danych, rejestr decyzji),
- `tests/` - automatyczne testy jakości danych.

## 6. Instrukcja uruchomienia krok po kroku
*(Instrukcja zostanie uzupełniona w kolejnych tygodniach)*

## Wykorzystanie AI
Asystenci AI zostali wykorzystani w projekcie do wsparcia przy projektowaniu architektury potoku, pisaniu skryptów transformujących dane oraz strukturze testów jakości. Wszelkie decyzje projektowe i kod zostały zweryfikowane przez autora.