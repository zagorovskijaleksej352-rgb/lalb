import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# Konfiguracja połączenia (Dla GitHub/Streamlit Cloud użyj st.secrets)
DB_URL = "sqlite:///magazyn.db"
engine = create_engine(DB_URL)

# Funkcja inicjalizująca bazę danych zgodnie ze schematem
def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS kategorie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazwa TEXT NOT NULL
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS magazyn228 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nazwa TEXT NOT NULL,
                liczba INTEGER,
                cena NUMERIC,
                categorie INTEGER,
                FOREIGN KEY (categorie) REFERENCES kategorie (id)
            );
        """))
        conn.commit()

init_db()

st.title("📦 System Zarządzania Magazynem")

# --- SEKCJA 1: DODAWANIE KATEGORII ---
st.header("Dodaj Nową Kategorię")
with st.form("form_kategoria"):
    kat_nazwa = st.text_input("Nazwa kategorii")
    submit_kat = st.form_submit_button("Zapisz kategorię")
    
    if submit_kat and kat_nazwa:
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO kategorie (nazwa) VALUES (:n)"), {"n": kat_nazwa})
            conn.commit()
        st.success(f"Dodano kategorię: {kat_nazwa}")

---

# --- SEKCJA 2: DODAWANIE PRODUKTU ---
st.header("Dodaj Produkt do Magazynu")

# Pobranie aktualnych kategorii do rozwijanej listy
df_kat = pd.read_sql("SELECT * FROM kategorie", engine)
kategorie_dict = dict(zip(df_kat['nazwa'], df_kat['id']))

with st.form("form_produkt"):
    prod_nazwa = st.text_input("Nazwa produktu")
    prod_liczba = st.number_input("Liczba (int8)", step=1, value=0)
    prod_cena = st.number_input("Cena (numeric)", step=0.01, format="%.2f")
    prod_kat_name = st.selectbox("Wybierz kategorię", options=list(kategorie_dict.keys()))
    
    submit_prod = st.form_submit_button("Dodaj produkt")
    
    if submit_prod and prod_nazwa:
        kat_id = kategorie_dict[prod_kat_name]
        with engine.connect() as conn:
            query = text("""
                INSERT INTO magazyn228 (nazwa, liczba, cena, categorie) 
                VALUES (:n, :l, :c, :k)
            """)
            conn.execute(query, {"n": prod_nazwa, "l": prod_liczba, "c": prod_cena, "k": kat_id})
            conn.commit()
        st.success(f"Produkt {prod_nazwa} został dodany!")

---

# --- SEKCJA 3: PODGLĄD DANYCH ---
st.header("Aktualny Stan Magazynu")
query_view = """
    SELECT m.nazwa, m.liczba, m.cena, k.nazwa as kategoria 
    FROM magazyn228 m 
    LEFT JOIN kategorie k ON m.categorie = k.id
"""
df_view = pd.read_sql(query_view, engine)
st.dataframe(df_view, use_container_width=True)
