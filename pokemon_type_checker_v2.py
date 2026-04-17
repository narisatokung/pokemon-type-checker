import streamlit as st
import requests

# ==========================================
# SECTION 1: Core Logic (Gen 6+ Type Chart)
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

def get_defensive_effectiveness(def_types):
    results = {}
    for atk_type in ALL_TYPES:
        mult = 1.0
        for def_type in def_types:
            mult *= CHART.get(atk_type, {}).get(def_type, 1.0)
        results[atk_type] = mult
    return results

# ==========================================
# SECTION 2: UI Setup & CSS
# ==========================================
st.set_page_config(page_title="Pokemon Data Center", layout="wide")

st.markdown("""
    <style>
    .stat-table { width: 100%; border-collapse: collapse; }
    .offensive-card { 
        padding: 15px; 
        border-radius: 10px; 
        background-color: #f8f9fa; 
        border-left: 5px solid #ff4b4b;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Pokemon Comprehensive Database")

@st.cache_data
def get_all_pokemon_names():
    try:
        res = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1500").json()
        return [p['name'].capitalize() for p in res['results']]
    except:
        return []

poke_list = get_all_pokemon_names()
selected_name = st.selectbox("พิมพ์ชื่อโปเกมอนเพื่อค้นหา:", [""] + poke_list)

if selected_name:
    with st.spinner('กำลังดึงข้อมูล...'):
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{selected_name.lower()}")
        if response.status_code == 200:
            data = response.json()
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(data['sprites']['other']['official-artwork']['front_default'], use_container_width=True)
                st.header(selected_name)
                types = [t['type']['name'].capitalize() for t in data['types']]
                st.write(f"**ธาตุ:** {' / '.join(types)}")
                
                # --- Abilities พร้อมคำอธิบาย ---
                st.subheader("🧬 Abilities")
                for ab in data['abilities']:
                    ab_info = requests.get(ab['ability']['url']).json()
                    desc = next((s['short_effect'] for s in ab_info['effect_entries'] if s['language']['name'] == 'en'), "No description available.")
                    name_display = ab['ability']['name'].replace('-', ' ').title()
                    
                    if ab['is_hidden']:
                        st.markdown(f"**{name_display}** *(Hidden Ability)*")
                    else:
                        st.markdown(f"**{name_display}**")
                    st.caption(desc)
                    st.write("---")

            with col2:
                # --- Stats แบบตาราง ---
                st.subheader("📊 Base Stats")
                stat_df = [{"Stat": s['stat']['name'].upper().replace('-', ' '), "Value": s['base_stat']} for s in data['stats']]
                st.table(stat_df)

                # --- การแพ้ทาง (Defensive) ---
                st.subheader("🛡️ การป้องกัน (Defensive Weaknesses)")
                eff = get_defensive_effectiveness(types)
                w1, w2 = st.columns(2)
                
                weaks = {k: v for k, v in eff.items() if v > 1}
                resists = {k: v for k, v in eff.items() if v < 1}
                
                with w1:
                    st.markdown("**โดนโจมตีแรง (x2, x4):**")
                    for t, m in weaks.items():
                        st.write(f"🔴 {t} (x{m})")
                with w2:
                    st.markdown("**โดนโจมตีเบา/ไม่เข้า:**")
                    for t, m in resists.items():
                        st.write(f"🟢 {t} (x{m})")

            # --- ส่วนที่เพิ่มใหม่: จุดเด่นด้านการโจมตี (Offensive Strengths) ---
            st.divider()
            st.subheader("⚔️ จุดเด่นด้านการโจมตี (Offensive Strengths)")
            st.write("แสดงธาตุที่โปเกมอนตัวนี้สามารถทำความเสียหายได้รุนแรง (x2.0)")
            
            off_cols = st.columns(len(types))
            for i, t_name in enumerate(types):
                with off_cols[i]:
                    # ดึงข้อมูลจาก CHART ว่าธาตุนี้ชนะทางธาตุไหนบ้าง
                    atk_logic = CHART.get(t_name, {})
                    strong_against = [target for target, mult in atk_logic.items() if mult > 1.0]
                    
                    st.markdown(f"""
                        <div class="offensive-card">
                            <h4 style="margin:0;">ธาตุ {t_name}</h4>
                            <p style="font-size: 0.9em; color: #666;">โจมตีแรงขึ้นกับธาตุต่อไปนี้:</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if strong_against:
                        for s_type in strong_against:
                            st.write(f"🔥 **{s_type}** (x2.0)")
                    else:
                        st.write("*(ไม่มีธาตุที่ชนะทางเป็นพิเศษ)*")
        else:
            st.error("ไม่พบข้อมูลโปเกมอนตัวนี้ กรุณาลองใหม่อีกครั้ง")
