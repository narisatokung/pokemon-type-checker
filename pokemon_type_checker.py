import streamlit as st
from dataclasses import dataclass
from typing import Callable

# =========================
# TYPE CHART
# =========================
CHART = {
    "Normal": {"Rock": 0.5, "Ghost": 0.0, "Steel": 0.5},
    "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0,
             "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0},
    "Water": {"Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0,
              "Rock": 2.0, "Dragon": 0.5},
    "Electric": {"Water": 2.0, "Electric": 0.5, "Grass": 0.5, "Ground": 0.0,
                 "Flying": 2.0, "Dragon": 0.5},
    "Grass": {"Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5,
              "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0,
              "Dragon": 0.5, "Steel": 0.5},
    "Ice": {"Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Ground": 2.0,
            "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5},
    "Fighting": {"Normal": 2.0, "Ice": 2.0, "Rock": 2.0, "Dark": 2.0, "Steel": 2.0},
    "Ground": {"Fire": 2.0, "Electric": 2.0, "Flying": 0.0, "Steel": 2.0},
    "Flying": {"Grass": 2.0, "Fighting": 2.0, "Bug": 2.0},
    "Psychic": {"Fighting": 2.0, "Poison": 2.0},
    "Rock": {"Fire": 2.0, "Ice": 2.0, "Flying": 2.0},
    "Ghost": {"Ghost": 2.0, "Psychic": 2.0},
    "Dragon": {"Dragon": 2.0},
    "Dark": {"Ghost": 2.0, "Psychic": 2.0},
    "Steel": {"Ice": 2.0, "Rock": 2.0},
    "Fairy": {"Dragon": 2.0, "Dark": 2.0},
}

ALL_TYPES = sorted(CHART.keys())

# =========================
# ABILITIES (FIXED)
# =========================
AbilityHandler = Callable[[str, float], float]

@dataclass
class Ability:
    name: str
    handler: AbilityHandler

def immune(t):
    return lambda atk, mult: 0.0 if atk == t else mult

def modify(t, factor):
    return lambda atk, mult: mult * factor if atk == t else mult

DEF_ABILITIES = {
    "Levitate": Ability("Levitate", immune("Ground")),
    "Volt Absorb": Ability("Volt Absorb", immune("Electric")),
    "Water Absorb": Ability("Water Absorb", immune("Water")),
    "Flash Fire": Ability("Flash Fire", immune("Fire")),
    "Thick Fat": Ability("Thick Fat", lambda atk, m: m*0.5 if atk in ["Fire","Ice"] else m),
    "Filter": Ability("Filter", lambda atk, m: m*0.75 if m>1 else m),
    "Solid Rock": Ability("Solid Rock", lambda atk, m: m*0.75 if m>1 else m),
}

ATK_ABILITIES = {
    "Scrappy": Ability("Scrappy", lambda atk, m: 1.0 if atk in ["Normal","Fighting"] and m==0 else m),
    "Tinted Lens": Ability("Tinted Lens", lambda atk, m: m*2 if m<1 else m),
}

# =========================
# CALC
# =========================
def get_mult(atk, d1, d2):
    m = CHART.get(atk, {}).get(d1, 1)
    if d2:
        m *= CHART.get(atk, {}).get(d2, 1)
    return m

def calc(d1, d2, def_ab, atk_ab):
    results = {}

    for atk in ALL_TYPES:
        mult = get_mult(atk, d1, d2)

        if atk_ab:
            mult = atk_ab.handler(atk, mult)

        if def_ab:
            mult = def_ab.handler(atk, mult)

        results[atk] = round(mult, 2)

    return results

# =========================
# UI
# =========================
st.set_page_config(page_title="Pokemon Type Checker", layout="centered")

st.title("⚡ Pokemon Type Checker (Mobile UI)")

col1, col2 = st.columns(2)

with col1:
    type1 = st.selectbox("Type 1", ALL_TYPES)

with col2:
    type2 = st.selectbox("Type 2 (optional)", ["None"] + ALL_TYPES)

def_ab = st.selectbox("Defender Ability", ["None"] + list(DEF_ABILITIES.keys()))
atk_ab = st.selectbox("Attacker Ability", ["None"] + list(ATK_ABILITIES.keys()))

if st.button("Calculate"):
    d2 = None if type2 == "None" else type2
    da = DEF_ABILITIES.get(def_ab)
    aa = ATK_ABILITIES.get(atk_ab)

    result = calc(type1, d2, da, aa)

    st.subheader("Result")

    buckets = {}
    for t, m in result.items():
        buckets.setdefault(m, []).append(t)

    order = [4,2,1,0.5,0.25,0]

    for m in order:
        if m in buckets:
            st.markdown(f"### {m}x")
            st.write(", ".join(buckets[m]))
