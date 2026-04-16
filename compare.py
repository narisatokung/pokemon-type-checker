import streamlit as st
import requests
import pandas as pd

@st.cache_data
def load_pokemon(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    return requests.get(url).json()

st.title("⚔️ Compare Pokémon")
st.markdown("[⬅️ กลับไปหน้า Search](app.py)")

col1, col2 = st.columns(2)

with col1:
    p1 = st.text_input("Pokémon ตัวที่ 1", "pikachu")
with col2:
    p2 = st.text_input("Pokémon ตัวที่ 2", "charizard")

if p1 and p2:
    data1 = load_pokemon(p1)
    data2 = load_pokemon(p2)

    st.subheader("📊 Stats Comparison")

    stats1 = {s["stat"]["name"]: s["base_stat"] for s in data1["stats"]}
    stats2 = {s["stat"]["name"]: s["base_stat"] for s in data2["stats"]}

    df_compare = pd.DataFrame({
        "Stat": list(stats1.keys()),
        p1.capitalize(): list(stats1.values()),
        p2.capitalize(): list(stats2.values())
    })

    st.table(df_compare)

    colA, colB = st.columns(2)
    with colA:
        st.image(data1["sprites"]["front_default"], width=150)
        st.write("ประเภท:", ", ".join([t["type"]["name"] for t in data1["types"]]))
    with colB:
        st.image(data2["sprites"]["front_default"], width=150)
        st.write("ประเภท:", ", ".join([t["type"]["name"] for t in data2["types"]]))
