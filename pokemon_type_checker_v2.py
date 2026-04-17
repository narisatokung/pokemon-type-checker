import streamlit as st
import requests
import pandas as pd

# ==========================================
# SECTION 1: Core Logic
# ==========================================
CHART = {
    "Normal":   {"Rock": 0.5, "Ghost": 0.0, "Steel": 0.5},
    "Fire":     {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0},
    "Water":    {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0, "Dragon": 0.5},
    "Electric": {"Water": 2.0, "Electric": 0.5, "Grass": 0.5, "Ground": 0.0, "Flying": 2.0, "Dragon": 0.5},
    "Grass":    {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5, "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0, "Dragon": 0.5, "Steel": 0.5},
    "Ice":      {"Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5},
    "Fighting": {"Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0, "Dark": 2.0, "Steel": 2.0, "Fairy": 0.5},
    "Poison":   {"Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0, "Fairy": 2.0},
    "Ground":   {"Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Poison": 2.0, "Flying": 0.0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0},
    "Flying":   {"Electric": 0.5, "Grass": 2.0, "Fighting": 2.0, "Bug": 2.0, "Rock": 0.5, "Steel": 0.5},
    "Psychic":  {"Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Dark": 0.0, "Steel": 0.5},
    "Bug":      {"Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Flying": 0.5, "Psychic": 2.0, "Ghost": 0.5, "Dark": 2.0, "Steel": 0.5, "Fairy": 0.5},
    "Rock":     {"Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5, "Flying": 2.0, "Bug": 2.0, "Steel": 0.5},
    "Ghost":    {"Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5},
    "Dragon":   {"Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0},
    "Dark":     {"Fighting": 0.5, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5, "Fairy": 0.5},
    "Steel":    {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0, "Rock": 2.0, "Steel": 0.5, "Fairy": 2.0},
    "Fairy":    {"Fire": 0.5, "Fighting": 2.0, "Poison": 0.5, "Dragon": 2.0, "Dark": 2.0, "Steel": 0.5},
}

ALL_TYPES = sorted(CHART.keys())

def get_effectiveness(def_types):
    results = {}
    for atk_type in ALL_TYPES:
        mult = 1.0
        for def_type in def_types:
            mult *= CHART.get(atk_type, {}).get(def_type, 1.0)
        results[atk_type] = mult
    return results

# ==========================================
# UI Setup
# ==========================================
st.set_page_config(page_title="Pokemon Data Center", layout="wide")

st.title("🔍 Pokemon Comprehensive Database")

# ==========================================
# Data
# ==========================================
@st.cache_data
def get_all_pokemon_names():
    res = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1500").json()
    return [p['name'].capitalize() for p in res['results']]

@st.cache_data
def get_ability_info(url):
    return requests.get(url).json()

poke_list = get_all_pokemon_names()
selected_name = st.selectbox("พิมพ์ชื่อโปเกมอนเพื่อค้นหา:", [""] + poke_list)

# ==========================================
# Display
# ==========================================
if selected_name:
    with st.spinner('กำลังดึงข้อมูล...'):
        data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{selected_name.lower()}").json()

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(data['sprites']['other']['official-artwork']['front_default'], use_container_width=True)
            st.header(selected_name)

            types = [t['type']['name'].capitalize() for t in data['types']]
            st.write("ธาตุ: " + " / ".join(types))

            st.subheader("🧬 Abilities")
            for ab in data['abilities']:
                ab_info = get_ability_info(ab['ability']['url'])
                desc = next((s['short_effect'] for s in ab_info['effect_entries'] if s['language']['name'] == 'en'), "No description available.")

                name_display = ab['ability']['name'].replace('-', ' ').title()
                st.markdown(f"**{name_display}**{' *(Hidden)*' if ab['is_hidden'] else ''}")
                st.caption(desc)
                st.write("---")

        with col2:
            st.subheader("📊 Base Stats")
            stat_data = [{"Stat": s['stat']['name'].upper(), "Value": s['base_stat']} for s in data['stats']]
            st.table(stat_data)

            st.subheader("⚔️ การแพ้ทาง")
            eff = get_effectiveness(types)

            weaks = {k: v for k, v in eff.items() if v > 1}
            resists = {k: v for k, v in eff.items() if v < 1}

            st.write("🔴 Weak:", weaks)
            st.write("🟢 Resist:", resists)

        # ==========================================
        # Learnable Moves (เสถียร)
        # ==========================================
        st.subheader("🥋 Learnable Moves")

        popular_moves = ["Earthquake", "Thunderbolt", "Ice Beam", "Flamethrower", "Scald", "Toxic", "Recover", "Roost", "U-Turn"]

        search_move = st.text_input("🔎 ค้นหาท่า")

        move_data = []

        for m in data['moves']:
            m_name = m['move']['name'].replace('-', ' ').title()

            if search_move and search_move.lower() not in m_name.lower():
                continue

            status = "⭐ Popular" if m_name in popular_moves else "-"

            move_data.append({
                "Move Name": m_name,
                "Status": status
            })

        df = pd.DataFrame(move_data)

        def highlight(val):
            return "color:red; font-weight:bold" if "⭐" in str(val) else ""

        st.dataframe(
            df.style.applymap(highlight, subset=["Status"]),
            use_container_width=True,
            height=400
        )
