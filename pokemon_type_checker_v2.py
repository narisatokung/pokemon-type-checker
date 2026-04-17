import streamlit as st
import requests

# ==========================================
# SECTION 1: Type Chart (Gen 6+) & Logic
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
# SECTION 2: Web UI with Streamlit
# ==========================================
st.set_page_config(page_title="Pokemon Master Tool", layout="wide")
st.title("🛡️ Pokemon Mastery Hub")

# 1. ค้นหาชื่อ (พร้อม Autocomplete)
all_pokes = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1000").json()['results']
poke_names = [p['name'].capitalize() for p in all_pokes]

search_col, _ = st.columns([1, 2])
with search_col:
    selected_name = st.selectbox("Search Pokémon Name:", [""] + poke_names)

if selected_name:
    data = requests.get(f"https://pokeapi.co/api/v2/pokemon/{selected_name.lower()}").json()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(data['sprites']['other']['official-artwork']['front_default'], width=300)
        st.subheader(f"Name: {selected_name}")
        types = [t['type']['name'].capitalize() for t in data['types']]
        st.write("Types: " + " / ".join(types))
        
        # Ability (ข้อ 1 & 5)
        st.markdown("### 🧬 Abilities")
        for ab in data['abilities']:
            st.write(f"- **{ab['ability']['name'].title()}** {'(Hidden)' if ab['is_hidden'] else ''}")

    with col2:
        # Stat (ข้อ 3)
        st.markdown("### 📊 Base Stats")
        stats = {s['stat']['name'].upper(): s['base_stat'] for s in data['stats']}
        st.bar_chart(stats)

        # Type Effectiveness (ข้อ 2)
        st.markdown("### ⚔️ Weaknesses & Resistances")
        eff = get_effectiveness(types)
        weak_col, res_col = st.columns(2)
        with weak_col:
            st.error("Super Effective (x2, x4)")
            for t, m in eff.items():
                if m > 1: st.write(f"**{t}** (x{m})")
        with res_col:
            st.success("Resistant (x0.5, x0)")
            for t, m in eff.items():
                if m < 1: st.write(f"**{t}** (x{m})")

    # Moves Table (ข้อ 6)
    st.markdown("### 🥋 Move List")
    popular_moves = ["Earthquake", "Thunderbolt", "Ice Beam", "Protect", "Surf"] # ตย. ท่ายอดนิยม
    move_data = []
    for m in data['moves']:
        m_name = m['move']['name'].title().replace("-", " ")
        status = "⭐ POPULAR" if m_name in popular_moves else ""
        move_data.append({"Move Name": m_name, "Popularity": status})
    
    st.dataframe(move_data, use_container_width=True, height=300)
