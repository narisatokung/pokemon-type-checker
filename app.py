import streamlit as st
import requests
from rapidfuzz import process
import pandas as pd

# -----------------------------
# โหลดรายชื่อ Pokémon
# -----------------------------
@st.cache_data
def load_pokemon_list():
    url = "https://pokeapi.co/api/v2/pokemon?limit=1000"
    data = requests.get(url).json()
    return [p["name"] for p in data["results"]]

pokemon_list = load_pokemon_list()

# -----------------------------
# Fuzzy Search
# -----------------------------
def fuzzy_search(query, choices, limit=5):
    results = process.extract(query, choices, limit=limit)
    return [r[0] for r in results]

# -----------------------------
# Type Chart (simplified 18 types)
# -----------------------------
type_chart = {
    "fire": {"weak": ["water", "rock", "ground"], "strong": ["grass", "ice", "bug", "steel"], "immune": []},
    "water": {"weak": ["electric", "grass"], "strong": ["fire", "rock", "ground"], "immune": []},
    "electric": {"weak": ["ground"], "strong": ["water", "flying"], "immune": []},
    "grass": {"weak": ["fire", "ice", "poison", "flying", "bug"], "strong": ["water", "rock", "ground"], "immune": []},
    "ground": {"weak": ["water", "grass", "ice"], "strong": ["fire", "electric", "poison", "rock", "steel"], "immune": ["electric"]},
    "rock": {"weak": ["water", "grass", "fighting", "ground", "steel"], "strong": ["fire", "ice", "flying", "bug"], "immune": []},
    "ice": {"weak": ["fire", "fighting", "rock", "steel"], "strong": ["grass", "ground", "flying", "dragon"], "immune": []},
    "fighting": {"weak": ["psychic", "flying", "fairy"], "strong": ["normal", "ice", "rock", "dark", "steel"], "immune": []},
    "psychic": {"weak": ["bug", "ghost", "dark"], "strong": ["fighting", "poison"], "immune": []},
    "dark": {"weak": ["fighting", "bug", "fairy"], "strong": ["psychic", "ghost"], "immune": ["psychic"]},
    "ghost": {"weak": ["ghost", "dark"], "strong": ["psychic", "ghost"], "immune": ["normal", "fighting"]},
    "dragon": {"weak": ["ice", "dragon", "fairy"], "strong": ["dragon"], "immune": []},
    "steel": {"weak": ["fire", "fighting", "ground"], "strong": ["ice", "rock", "fairy"], "immune": ["poison"]},
    "fairy": {"weak": ["poison", "steel"], "strong": ["fighting", "dragon", "dark"], "immune": ["dragon"]},
    "poison": {"weak": ["ground", "psychic"], "strong": ["grass", "fairy"], "immune": []},
    "bug": {"weak": ["fire", "flying", "rock"], "strong": ["grass", "psychic", "dark"], "immune": []},
    "flying": {"weak": ["electric", "ice", "rock"], "strong": ["grass", "fighting", "bug"], "immune": ["ground"]},
    "normal": {"weak": ["fighting"], "strong": [], "immune": ["ghost"]},
}

def calculate_effectiveness(types):
    weaknesses, strengths, immunities = {}, {}, set()
    for t in types:
        chart = type_chart.get(t, {})
        for w in chart.get("weak", []):
            weaknesses[w] = weaknesses.get(w, 1) * 2
        for s in chart.get("strong", []):
            strengths[s] = strengths.get(s, 1) * 2
        for i in chart.get("immune", []):
            immunities.add(i)
    return weaknesses, strengths, immunities

# -----------------------------
# UI
# -----------------------------
st.title("🔍 Pokémon Fuzzy Search System")
st.markdown("[ไปหน้า Compare Pokémon ➡️](compare.py)")

query = st.text_input("ค้นหา Pokémon")
selected = None

if query:
    suggestions = fuzzy_search(query, pokemon_list)
    selected = st.selectbox("Suggestions", suggestions)

if selected:
    st.header(f"📖 {selected.capitalize()}")

    # ดึงข้อมูลจาก PokeAPI
    url = f"https://pokeapi.co/api/v2/pokemon/{selected}"
    data = requests.get(url).json()

    # -----------------------------
    # ข้อมูลพื้นฐาน
    # -----------------------------
    st.image(data["sprites"]["front_default"], width=150)
    types = [t["type"]["name"] for t in data["types"]]
    st.write("ประเภท:", ", ".join(types))

    # -----------------------------
    # Type Effectiveness
    # -----------------------------
    st.subheader("⚔️ Type Effectiveness")
    weaknesses, strengths, immunities = calculate_effectiveness(types)

    st.write("**แพ้ทาง (Weaknesses):**")
    for w, mult in weaknesses.items():
        st.markdown(f"- {w} ({mult}x)")

    st.write("**ชนะทาง (Strengths):**")
    for s, mult in strengths.items():
        st.markdown(f"- {s} ({mult}x)")

    if immunities:
        st.write("**ไม่โดน (Immunities):**")
        for i in immunities:
            st.markdown(f"- {i} (0x)")

    # -----------------------------
    # Stats (ตารางตัวเลข)
    # -----------------------------
    st.subheader("📊 Stats")
    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
    df_stats = pd.DataFrame(stats.items(), columns=["Stat", "Value"])
    st.table(df_stats)

    # -----------------------------
    # Ability
    # -----------------------------
    st.subheader("✨ Abilities")
    for ab in data["abilities"]:
        st.write(f"- {ab['ability']['name']} (คำอธิบาย: ... )")

    # -----------------------------
    # Moves
    # -----------------------------
    st.subheader("🎯 Moves")
    moves = [m["move"]["name"] for m in data["moves"]]
    st.write("**ทั้งหมด:**", ", ".join(moves[:30]))

    # Highlight Meta Moves (ตัวอย่าง mock)
    st.write("**Meta Moves:**")
    meta_moves = [
        {"name": "Thunderbolt", "reason": "ดาเมจสูง + ครอบคลุม Water"},
        {"name": "Earthquake", "reason": "ครอบคลุมหลายธาตุ + Physical"},
        {"name": "Dragon Dance", "reason": "Utility: เพิ่ม Attack + Speed"},
    ]
    for m in meta_moves:
        st.markdown(f"- {m['name']} → {m['reason']}")
