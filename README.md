# *Wieloźródłowy system wykrywania okazji na rynku nieruchomości*

## Opis i cel projektu

Projekt adresowany jest do inwestorów na rynku nieruchomości, którzy każdego dnia tracą cenne godziny na ręcznym przeszukiwaniu setek nowych ogłoszeń w poszukiwaniu atrakcyjnych ofert. Głównym celem systemu jest automatyczne i błyskawiczne wyłapywanie tzw. „perełek inwestycyjnych” – czyli mieszkań, których cena za metr kwadratowy jest znacząco niższa od rynkowej średniej w danej lokalizacji.

Dzięki automatycznej integracji danych z wielu różnych portali ogłoszeniowych, narzędzie samodzielnie pobiera oferty, standaryzuje je, przelicza mediany cenowe i w czasie rzeczywistym wskazuje te, które najbardziej opłaca się kupić pod kątem szybkiego flipu lub wynajmu. Całość wspierana jest przez potok danych (data pipeline) dbający o ich jakość oraz interaktywną aplikację analityczną w Streamlit, która w przejrzysty sposób prezentuje gotowe okazje biznesowe. Proces został zrealizowany w architekturze medalionowej (Bronze -> Silver -> Gold), a jego jakość zapewniają testy.

## Struktura repozytorium
- `src/` - skrypty Pythona odpowiedzialne za ekstrakcję oraz transformacje,
- `data/` - warstwowy magazyn danych (Bronze, Silver, Gold),
- `docs/` - dokumentacja projektowa (perspektywy, architektura, słownik danych, rejestr decyzji),
- `tests/` - automatyczne testy jakości danych.

## Instrukcja uruchomienia krok po kroku
*(Instrukcja zostanie uzupełniona w kolejnych tygodniach)*

## Wykorzystanie AI
Asystenci AI zostali wykorzystani w projekcie do wsparcia przy projektowaniu architektury potoku, pisaniu skryptów transformujących dane oraz strukturze testów jakości. Wszelkie decyzje projektowe i kod zostały zweryfikowane przez autora.