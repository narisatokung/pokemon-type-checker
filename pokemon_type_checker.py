import streamlit as st
import requests

st.set_page_config(page_title="Pokédex Pro", layout="centered")

st.title("📱 Pokédex Pro")

name = st.text_input("🔍 Search Pokémon")

# -------------------------
# TYPE CHART (ครบขึ้น)
# -------------------------
TYPE_CHART = {
    "fire": {"water": 2, "rock": 2, "ground": 2},
    "water": {"electric": 2, "grass": 2},
    "grass": {"fire": 2, "ice": 2, "flying": 2, "bug": 2},
    "electric": {"ground": 2},
    "rock": {"water": 2, "grass": 2, "fighting": 2},
}

def get_weakness(types):
    result = {}
    for atk, targets in TYPE_CHART.items():
        mult = 1
        for t in types:
            if t in targets:
                mult *= targets[t]
        if mult > 1:
            result[atk] = mult
    return result

# -------------------------
# FETCH HELPERS
# -------------------------
def get_pokemon(name):
    return requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}").json()

def get_species(url):
    return requests.get(url).json()

def get_evolution(url):
    return requests.get(url).json()

# -------------------------
# MAIN
# -------------------------
if st.button("Search") and name:

    try:
        data = get_pokemon(name)

        # BASIC
        st.subheader(data["name"].title())
        st.image(data["sprites"]["front_default"], width=150)

        # TYPES
        types = [t["type"]["name"] for t in data["types"]]
        st.markdown(f"**Type:** {' / '.join(types)}")

        # WEAKNESS
        weak = get_weakness(types)
        if weak:
            st.markdown("**Weakness:**")
            for k, v in weak.items():
                st.write(f"- {k} ({v}x)")

        # STATS
        st.markdown("### 📊 Stats")
        for s in data["stats"]:
            st.write(f"{s['stat']['name'].upper()}: {s['base_stat']}")

        # ABILITIES
        st.markdown("### ✨ Abilities")
        for a in data["abilities"]:
            name = a["ability"]["name"]
            hidden = " (Hidden)" if a["is_hidden"] else ""
            st.write(f"- {name}{hidden}")

        # MOVES
        st.markdown("### ⚔️ Moves")
        moves = [m["move"]["name"] for m in data["moves"]]

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Top Moves:**")
            st.write(", ".join(moves[:10]))

        with col2:
            strong = [m for m in moves if any(x in m for x in ["beam","blast","punch","bolt"])]
            st.write("🔥 **Recommended:**")
            st.write(", ".join(strong[:10]))

        # EVOLUTION
        st.markdown("### 🌱 Evolution")

        species = get_species(data["species"]["url"])
        evo = get_evolution(species["evolution_chain"]["url"])

        def parse_chain(chain):
            result = []
            while chain:
                result.append(chain["species"]["name"])
                chain = chain["evolves_to"][0] if chain["evolves_to"] else None
            return result

        evo_list = parse_chain(evo["chain"])
        st.write(" → ".join(evo_list))

    except:
        st.error("Pokemon not found")
