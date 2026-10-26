import streamlit as st
import pandas as pd
import duckdb
import os

# Konfiguracja strony
st.set_page_config(
    page_title="Wrocławski Detektor Okazji Nieruchomościowych",
    page_icon="🏠",
    layout="wide"
)

DB_PATH = "data/real_estate.db"

@st.cache_data
def load_data_from_duckdb():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        query = """
            SELECT 
                source,
                title,
                price_pln,
                area_m2,
                price_per_m2,
                number_of_rooms,
                street,
                locality,
                COALESCE(district, 'Nie sprecyzowano dzielnicy') AS district,
                COALESCE(neighborhood, 'Nie sprecyzowano osiedla') AS neighborhood,
                url,
                processed_at
            FROM silver_properties
        """
        df = con.execute(query).fetchdf()
    except Exception as e:
        st.error(f"Błąd podczas odczytu z bazy DuckDB: {e}")
        df = pd.DataFrame()
    finally:
        con.close()
    return df

df = load_data_from_duckdb()

# Główny nagłówek
st.title("🏠 Wrocławski Detektor Okazji Nieruchomościowych")
st.markdown("Inteligentny system analityczny rynku nieruchomości we Wrocławiu.")

if df.empty:
    st.warning("Brak danych w bazie DuckDB. Uruchom najpierw potok ETL (`python src/transform.py`).")
else:
    # Układ zakładek z elementami wizualnymi
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Przegląd i średnie ceny",
        "🎯 Radar Okazji Cenowych", 
        "⚖️ Rozpiętość rynkowa",
        "🛏️ Analiza mikrorynku (pokoje)"
    ])

    # --- ZAKŁADKA 1: Średnie ceny w formie wizualnej ---
    with tab1:
        st.subheader("Aktualne stawki za metr kwadratowy w podziale na dzielnice")
        
        district_stats = df.groupby("district").agg(
            liczba_ofert=("price_per_m2", "count"),
            srednia_m2=("price_per_m2", "mean"),
            mediana_m2=("price_per_m2", "median")
        ).reset_index().sort_values(by="srednia_m2", ascending=False)

        # Prezentacja w postaci kart (kodu wizualnego) dla top 3 najdroższych dzielnic
        cols = st.columns(3)
        for i, col in enumerate(cols):
            if i < len(district_stats):
                row = district_stats.iloc[i]
                col.metric(
                    label=f"📍 {row['district']}",
                    value=f"{row['srednia_m2']:.0f} PLN/m²",
                    delta=f"{int(row['liczba_ofert'])} ofert w bazie"
                )

        st.markdown("---")
        
        # Wykres i tabela obok siebie
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("##### Średnia cena za m² (Wykres)")
            st.bar_chart(district_stats.set_index("district")["srednia_m2"])
        with c2:
            st.markdown("##### Szczegółowe zestawienie tabelaryczne")
            st.dataframe(
                district_stats.rename(columns={
                    "district": "Dzielnica",
                    "liczba_ofert": "Oferty",
                    "srednia_m2": "Średnia PLN/m²",
                    "mediana_m2": "Mediana PLN/m²"
                }).style.format({"Średnia PLN/m²": "{:.1f}", "Mediana PLN/m²": "{:.1f}"}),
                use_container_width=True,
                hide_index=True
            )

    # --- ZAKŁADKA 2: Radar Okazji (Najważniejsza część z linkami) ---
    with tab2:
        st.subheader("Wykrywacz Okazji Inwestycyjnych")
        st.markdown("Oferty z ceną za m² **znacząco niższą** od średniej rynkowej w danej lokalizacji.")

        discount_threshold = st.slider("Wymagany poziom dyskonta względem średniej w dzielnicy (%):", 5, 40, 15, 5)

        district_avg = df.groupby("district")["price_per_m2"].mean().reset_index().rename(columns={"price_per_m2": "district_avg_m2"})
        df_merged = pd.merge(df, district_avg, on="district")
        df_merged["discount_pct"] = ((df_merged["district_avg_m2"] - df_merged["price_per_m2"]) / df_merged["district_avg_m2"]) * 100
        deals_df = df_merged[df_merged["discount_pct"] >= discount_threshold].sort_values(by="discount_pct", ascending=False)

        if deals_df.empty:
            st.info("Brak ofert spełniających tak wysoki próg dyskonta. Spróbuj zmniejszyć wymagany procent na suwaku.")
        else:
            st.success(f"Znaleziono **{len(deals_df)}** atrakcyjnych okazji spełniających kryteria!")
            
            for _, row in deals_df.iterrows():
                # Użycie ekspanderów lub ładnych ramek dla ofert z linkami
                with st.expander(f"🔥 {row['district']} | {int(row['price_pln']):,} PLN | Taniej o {row['discount_pct']:.1f}% ({row['price_per_m2']} PLN/m²)"):
                    c_left, c_right = st.columns([3, 1])
                    with c_left:
                        st.markdown(f"**Tytuł ogłoszenia:** {row['title']}")
                        st.markdown(f"📍 **Lokalizacja:** Ulica: `{row['street'] if pd.notna(row['street']) else 'Nie podano'}`")
                        st.markdown(f"📐 **Powierzchnia:** {row['area_m2']} m² | **Pokoje:** {row['number_of_rooms']} | **Źródło:** {row['source'].capitalize()}")
                    with c_right:
                        st.markdown(f"### [{row['source'].upper()} 🔗]({row['url']})")
                        st.caption("Kliknij, aby przejść do oferty")

    # --- ZAKŁADKA 3: Rozpiętość Rynkowa ---
    with tab3:
        st.subheader("Dysproporcje i zróżnicowanie cenowe w dzielnicach")
        st.markdown("Analiza rozpiętości między najtańszymi a najdroższymi nieruchomościami w obrębie tej samej jednostki administracyjnej.")

        spread_df = df.groupby("district").agg(
            min_m2=("price_per_m2", "min"),
            max_m2=("price_per_m2", "max"),
            srednia_m2=("price_per_m2", "mean")
        ).reset_index()
        spread_df["rozpietosc_zl"] = spread_df["max_m2"] - spread_df["min_m2"]
        spread_df = spread_df.sort_values(by="rozpietosc_zl", ascending=False)

        st.dataframe(
            spread_df.rename(columns={
                "district": "Dzielnica",
                "min_m2": "Min PLN/m²",
                "max_m2": "Max PLN/m²",
                "srednia_m2": "Średnia PLN/m²",
                "rozpietosc_zl": "Rozpiętość (Max - Min)"
            }).style.format({"Min PLN/m²": "{:.1f}", "Max PLN/m²": "{:.1f}", "Średnia PLN/m²": "{:.1f}", "Rozpiętość (Max - Min)": "{:.1f}"}),
            use_container_width=True,
            hide_index=True
        )

    # --- ZAKŁADKA 4: Wpływ pokoi ---
        with tab4:
            st.subheader("Wpływ liczby pokoi na stawkę za m²")
            
            sel_dist = st.selectbox("Wybierz dzielnicę do analizy mikrorynku pokoi:", sorted(df["district"].unique()))
            sub_df = df[df["district"] == sel_dist]

            if sub_df.empty:
                st.warning("Brak danych dla wybranej dzielnicy.")
            else:
                room_agg = sub_df.groupby("number_of_rooms").agg(
                    oferty=("price_per_m2", "count"),
                    srednia_m2=("price_per_m2", "mean")
                ).reset_index().sort_values(by="number_of_rooms")

                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.bar_chart(room_agg.set_index("number_of_rooms")["srednia_m2"])
                with col_b:
                    st.dataframe(
                        room_agg.rename(columns={
                            "number_of_rooms": "Pokoje",
                            "oferty": "Liczba ofert",
                            "srednia_m2": "Średnia PLN/m²"
                        }).style.format({
                            "Pokoje": "{:.0f}",                  
                            "Liczba ofert": "{:.0f}",        
                            "Średnia PLN/m²": "{:.1f}"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )