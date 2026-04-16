import streamlit as st
import requests

st.set_page_config(page_title="Pokédex Pro+", layout="centered")

# =========================
# TYPE CHART (FULL)
# =========================
TYPE_CHART = {
    "Normal": {"Rock":0.5,"Ghost":0,"Steel":0.5},
    "Fire":{"Fire":0.5,"Water":0.5,"Grass":2,"Ice":2,"Bug":2,"Rock":0.5,"Dragon":0.5,"Steel":2},
    "Water":{"Fire":2,"Water":0.5,"Grass":0.5,"Ground":2,"Rock":2,"Dragon":0.5},
    "Electric":{"Water":2,"Electric":0.5,"Grass":0.5,"Ground":0,"Flying":2,"Dragon":0.5},
    "Grass":{"Fire":0.5,"Water":2,"Grass":0.5,"Poison":0.5,"Ground":2,"Flying":0.5,"Bug":0.5,"Rock":2,"Dragon":0.5,"Steel":0.5},
    "Ice":{"Water":0.5,"Grass":2,"Ice":0.5,"Ground":2,"Flying":2,"Dragon":2,"Steel":0.5},
    "Fighting":{"Normal":2,"Rock":2,"Steel":2,"Ice":2,"Dark":2,"Ghost":0},
    "Poison":{"Grass":2,"Poison":0.5,"Ground":0.5,"Rock":0.5,"Steel":0},
    "Ground":{"Fire":2,"Electric":2,"Grass":0.5,"Flying":0,"Steel":2},
    "Flying":{"Grass":2,"Fighting":2,"Bug":2},
    "Psychic":{"Fighting":2,"Poison":2,"Dark":0},
    "Bug":{"Grass":2,"Psychic":2,"Dark":2},
    "Rock":{"Fire":2,"Ice":2,"Flying":2,"Bug":2},
    "Ghost":{"Ghost":2,"Psychic":2,"Normal":0},
    "Dragon":{"Dragon":2,"Fairy":0},
    "Dark":{"Ghost":2,"Psychic":2},
    "Steel":{"Rock":2,"Ice":2,"Fairy":2},
    "Fairy":{"Fighting":2,"Dragon":2,"Dark":2}
}

ALL_TYPES = list(TYPE_CHART.keys())

# =========================
# ABILITY SYSTEM
# =========================
def apply_ability(ability, atk_type, mult):
    if not ability:
        return mult

    a = ability.lower()

    if a == "levitate" and atk_type == "Ground":
        return 0.0

    if a in ["volt absorb", "lightning rod", "motor drive"] and atk_type == "Electric":
        return 0.0

    if a in ["water absorb", "storm drain"] and atk_type == "Water":
        return 0.0

    if a == "flash fire" and atk_type == "Fire":
        return 0.0

    if a == "sap sipper" and atk_type == "Grass":
        return 0.0

    if a == "thick fat" and atk_type in ["Fire", "Ice"]:
        return mult * 0.5

    return mult

# =========================
# CALC MULTIPLIER
# =========================
def calc_multiplier(atk, types, ability):
    mult = 1.0
    for t in types:
        mult *= TYPE_CHART.get(atk, {}).get(t, 1)
    mult = apply_ability(ability, atk, mult)
    return round(mult, 2)

# =========================
# FETCH DATA
# =========================
@st.cache_data
def fetch_pokemon(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    r = requests.get(url)
    if r.status_code != 200:
        return None

    data = r.json()

    types = [t["type"]["name"].capitalize() for t in data["types"]]
    abilities = [a["ability"]["name"] for a in data["abilities"]]

    stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

    moves = [m["move"]["name"] for m in data["moves"]]

    sprite = data["sprites"]["front_default"]

    return {
        "name": data["name"],
        "types": types,
        "abilities": abilities,
        "stats": stats,
        "moves": moves,
        "sprite": sprite
    }

# =========================
# UI MAIN
# =========================
st.title("📱 Pokédex Pro+")

# =========================
# SEARCH MODE
# =========================
st.header("🔍 Search Pokémon")

search_name = st.text_input("Enter Pokémon name")

if st.button("Search"):
    data = fetch_pokemon(search_name)

    if not data:
        st.error("Not found")
    else:
        st.subheader(data["name"].title())
        st.image(data["sprite"], width=120)

        st.write("**Type:**", ", ".join(data["types"]))

        st.write("### 📊 Stats")
        for k, v in data["stats"].items():
            st.write(f"{k.upper()}: {v}")

        st.write("### ✨ Abilities")
        st.write(", ".join(data["abilities"]))

        st.write("### ⚔️ Moves")
        st.write(", ".join(data["moves"][:15]))

# =========================
# COMPARE MODE
# =========================
st.markdown("---")
st.header("⚔️ Compare Mode")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Slot A")
    name_a = st.text_input("Pokemon A")
    data_a = fetch_pokemon(name_a) if name_a else None

    ability_a = None
    if data_a:
        ability_a = st.selectbox("Ability A", data_a["abilities"])

with col2:
    st.subheader("Slot B")
    name_b = st.text_input("Pokemon B")
    data_b = fetch_pokemon(name_b) if name_b else None

    ability_b = None
    if data_b:
        ability_b = st.selectbox("Ability B", data_b["abilities"])

# =========================
# TABLE
# =========================
if data_a and data_b:

    st.subheader("📊 Type Comparison")

    types_a = data_a["types"]
    types_b = data_b["types"]

    for atk in ALL_TYPES:
        mA = calc_multiplier(atk, types_a, ability_a)
        mB = calc_multiplier(atk, types_b, ability_b)

        colorA = "#a8f0a5" if mA < mB else ""
        colorB = "#a8f0a5" if mB < mA else ""

        c1, c2, c3 = st.columns([1,1,1])

        c1.write(atk)

        c2.markdown(
            f"<div style='background:{colorA};padding:4px'>{mA}x</div>",
            unsafe_allow_html=True
        )

        c3.markdown(
            f"<div style='background:{colorB};padding:4px'>{mB}x</div>",
            unsafe_allow_html=True
        )
