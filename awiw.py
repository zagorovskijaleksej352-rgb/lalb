import streamlit as st
import pandas as pd
from supabase import create_client

# =========================
# SUPABASE CONFIG
# =========================
st.set_page_config(page_title="Magazyn Pro", layout="wide")

SUPABASE_URL = ["https://cggcehsanonhhkpweokk.subapase.co"]
SUPABASE_KEY = ["sb_publishable_Rslbdu7bwIoOgFSDnfe7xQ_wFR2L5oN"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# UI
# =========================
st.title("📦 System Zarządzania Magazynem (Supabase PUBLIC)")

# =========================
# STATYSTYKI
# =========================
st.subheader("📊 Podsumowanie Magazynu")

data = supabase.table("magazyn228").select("liczba, cena").execute().data
df_stats = pd.DataFrame(data)

if not df_stats.empty:
    total_items = int(df_stats["liczba"].sum())
    total_value = (df_stats["liczba"] * df_stats["cena"]).sum()

    col1, col2 = st.columns(2)
    col1.metric("Suma produktów", f"{total_items} szt.")
    col2.metric("Wartość magazynu", f"{total_value:,.2f} PLN")
else:
    st.info("Magazyn jest pusty.")

st.divider()

# =========================
# DODAWANIE
# =========================
col_kat, col_prod = st.columns(2)

# --- KATEGORIE ---
with col_kat:
    st.header("➕ Dodaj kategorię")

    with st.form("form_kategoria", clear_on_submit=True):
        kat_nazwa = st.text_input("Nazwa kategorii")
        submit_kat = st.form_submit_button("Zapisz")

        if submit_kat:
            if kat_nazwa.strip() == "":
                st.error("Podaj nazwę kategorii")
            else:
                try:
                    supabase.table("kategorie").insert(
                        {"nazwa": kat_nazwa.strip()}
                    ).execute()
                    st.success(f"Dodano kategorię: {kat_nazwa}")
                    st.rerun()
                except Exception:
                    st.warning("Taka kategoria już istnieje")

# --- PRODUKTY ---
with col_prod:
    st.header("➕ Dodaj produkt")

    kat_data = supabase.table("kategorie").select("*").order("nazwa").execute().data
    df_kat = pd.DataFrame(kat_data)

    if df_kat.empty:
        st.warning("Najpierw dodaj kategorię")
    else:
        kategorie_dict = dict(zip(df_kat["nazwa"], df_kat["id"]))

        with st.form("form_produkt", clear_on_submit=True):
            prod_nazwa = st.text_input("Nazwa produktu")
            prod_liczba = st.number_input("Ilość", min_value=0, step=1)
            prod_cena = st.number_input("Cena (PLN)", min_value=0.0, step=0.01)
            prod_kat_name = st.selectbox(
                "Kategoria",
                list(kategorie_dict.keys())
            )

            submit_prod = st.form_submit_button("Dodaj")

            if submit_prod:
                if prod_nazwa.strip() == "":
                    st.error("Podaj nazwę produktu")
                else:
                    supabase.table("magazyn228").insert({
                        "nazwa": prod_nazwa.strip(),
                        "liczba": int(prod_liczba),
                        "cena": float(prod_cena),
                        "categorie": kategorie_dict[prod_kat_name],
                    }).execute()

                    st.success(f"Dodano produkt: {prod_nazwa}")
                    st.rerun()

st.divider()

# =========================
# PODGLĄD + USUWANIE
# =========================
st.header("🔍 Stan magazynu")

response = supabase.table("magazyn228").select(
    "id, nazwa, liczba, cena, kategorie(nazwa)"
).execute()

rows = []
for r in response.data:
    rows.append({
        "id": r["id"],
        "nazwa": r["nazwa"],
        "liczba": r["liczba"],
        "cena": r["cena"],
        "kategoria": r["kategorie"]["nazwa"] if r["kategorie"] else None
    })

df_view = pd.DataFrame(rows)

if df_view.empty:
    st.info("Brak produktów w magazynie")
else:
    st.dataframe(
        df_view.drop(columns="id"),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("🗑️ Usuń produkt")

    product_map = {
        f"{row.nazwa} | {row.kategoria} | ID {row.id}": row.id
        for _, row in df_view.iterrows()
    }

    selected = st.selectbox(
        "Wybierz produkt",
        list(product_map.keys())
    )

    if st.button("Usuń", type="primary"):
        supabase.table("magazyn228").delete().eq(
            "id", product_map[selected]
        ).execute()

        st.warning("Produkt usunięty")
        st.rerun()
