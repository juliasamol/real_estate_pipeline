# Rejestr Decyzji Projektowycj

## Decyzjca 1: Metoda ekstrakcji danych (Web Scraping danych strukturalnych JSON-LD)
- **Data:** Tydzień 1
- **Wybór:** Zastosowanie celowanego pobierania danych strukturalnych (JSON-LD / Schema.org) bezpośrednio z kodu HTML publicznych stron ogłoszeniowych (Otodom i Morizon) w trybie cyklicznym.
- **Rozważane alternatywy:** 
  1. *Oficjalne API komercyjne* – odrzucone ze względu na brak darmowych interfejsów programistycznych dla zewnętrznych deweloperów nieruchomościowych.
  2. *Tradycyjny web scraping* – odrzucone ze względu na dużą niestabilność i podatność na częste zmiany w szacie graficznej portalu.
- **Uzasadnienie:** Standard JSON-LD dostarcza czyste, ustandaryzowane dane wprost od dostawcy (wymagane przez wyszukiwarki), co pozwala na niezawodne i powtarzalne budowanie warstwy surowej (Bronze) przy zachowaniu dobrych praktyk inżynierskich.