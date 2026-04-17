import streamlit as st
import requests
import pandas as pd

# --- ส่วน Logic เดิม (CHART และ get_effectiveness) คงไว้เหมือนเดิม ---
# [ก๊อปปี้ CHART และ get_effectiveness จากโค้ดเดิมมาวาง]

# ==========================================
# SECTION: UI & Functions
# ==========================================
st.set_page_config(page_title="Pokemon Master Tool", layout="wide")

st.title("🛡️ Pokemon Comprehensive Database")

@st.cache_data
def get_all_pokemon_names():
    try:
        res = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1500").json()
        return [p['name'].capitalize() for p in res['results']]
    except:
        return []

poke_list = get_all_pokemon_names()
selected_name = st.selectbox("ค้นหาชื่อโปเกมอน:", [""] + poke_list)

if selected_name:
    with st.spinner('กำลังโหลดข้อมูล...'):
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{selected_name.lower()}")
        if response.status_code == 200:
            data = response.json()
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(data['sprites']['other']['official-artwork']['front_default'], use_container_width=True)
                st.header(selected_name)
                types = [t['type']['name'].capitalize() for t in data['types']]
                st.write(f"**ธาตุ:** {' / '.join(types)}")
                
                # --- Ability & Description ---
                st.subheader("🧬 Abilities")
                for ab in data['abilities']:
                    ab_res = requests.get(ab['ability']['url']).json()
                    desc = next((s['short_effect'] for s in ab_res['effect_entries'] if s['language']['name'] == 'en'), "ไม่มีคำอธิบาย")
                    name = ab['ability']['name'].replace('-', ' ').title()
                    st.markdown(f"**{name}** {'*(Hidden)*' if ab['is_hidden'] else ''}")
                    st.caption(desc)

            with col2:
                # --- Stats Table (ปรับเป็นตารางตามโจทย์) ---
                st.subheader("📊 Base Stats")
                stats_list = [{"Status": s['stat']['name'].upper(), "Value": s['base_stat']} for s in data['stats']]
                st.table(pd.DataFrame(stats_list))

                # --- Effectiveness ---
                st.subheader("⚔️ Weaknesses")
                eff = get_effectiveness(types)
                w1, w2 = st.columns(2)
                with w1:
                    st.error("แพ้ทาง (x2, x4)")
                    for t, m in eff.items():
                        if m > 1: st.write(f"{t} (x{m})")
                with w2:
                    st.success("ต้านทาน (x0.5, x0)")
                    for t, m in eff.items():
                        if m < 1: st.write(f"{t} (x{m})")

            # --- 🔥 แก้ไขส่วน Move List (ใช้ DataFrame Styling) ---
            st.divider()
            st.subheader("🥋 Learnable Moves (ไฮไลท์ท่าที่นิยม)")
            
            # รายชื่อท่าที่นิยม
            popular_moves = ["Earthquake", "Thunderbolt", "Ice Beam", "Flamethrower", "Scald", "Toxic", "Recover", "Roost", "U-Turn", "Close Combat", "Surfing"]

            # สร้าง List ข้อมูล Move
            moves_data = []
            for m in data['moves']:
                m_name = m['move']['name'].replace('-', ' ').title()
                is_popular = "⭐ Popular" if m_name in popular_moves else "-"
                moves_data.append({"Move Name": m_name, "Status": is_popular})

            df_moves = pd.DataFrame(moves_data)

            # ฟังก์ชันสำหรับไฮไลท์ตัวหนังสือสีแดง
            def highlight_popular(row):
                if row['Status'] == "⭐ Popular":
                    return ['color: #ff4b4b; font-weight: bold;'] * len(row)
                return [''] * len(row)

            # แสดงตารางแบบ Interactive พร้อมไฮไลท์
            st.dataframe(
                df_moves.style.apply(highlight_popular, axis=1),
                use_container_width=True,
                height=400,
                hide_index=True
            )
        else:
            st.error("ไม่พบข้อมูลโปเกมอนตัวนี้")
