import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from thefuzz import process

# --- 1. ตั้งค่าและ Data Dictionaries ---
st.set_page_config(page_title="Pokémon Pokedex", page_icon="🔴", layout="wide")

# พจนานุกรมแปล Ability (ตัวอย่าง)
ABILITY_THAI_DICT = {
    "overgrow": "เพิ่มพลังท่าธาตุพืชเมื่อ HP เหลือน้อยกว่า 1/3",
    "blaze": "เพิ่มพลังท่าธาตุไฟเมื่อ HP เหลือน้อยกว่า 1/3",
    "torrent": "เพิ่มพลังท่าธาตุน้ำเมื่อ HP เหลือน้อยกว่า 1/3",
    "intimidate": "เมื่อลงสนาม จะลดพลังโจมตี (Attack) ของคู่ต่อสู้ลง 1 ระดับ"
}

# ท่ายอดนิยม (Meta Moves - ตัวอย่าง)
META_MOVES = {
    "charizard": {"roost": "ใช้ฟื้นฟู HP ได้ดี", "flare-blitz": "ท่าโจมตีหลักที่รุนแรงมาก"},
    "pikachu": {"volt-tackle": "ท่าเฉพาะที่รุนแรงที่สุด", "fake-out": "ใช้ขัดจังหวะศัตรูในเทิร์นแรก"}
}

# --- 2. ฟังก์ชันดึงข้อมูล (Cache เพื่อความเร็ว) ---
@st.cache_data
def get_all_pokemon_names():
    url = "https://pokeapi.co/api/v2/pokemon?limit=1000"
    res = requests.get(url).json()
    return [p['name'] for p in res['results']]

@st.cache_data
def get_pokemon_data(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    return None

# --- 3. UI Component: Search & Detail View ---
st.title("🔴 Pokémon Dex: Fuzzy Search")

pokemon_list = get_all_pokemon_names()
search_query = st.text_input("🔍 พิมพ์ชื่อ Pokémon (พิมพ์ผิดนิดหน่อยก็หาเจอ เช่น Pika, Charzard)", "")

selected_pokemon = None

# Fuzzy Search Logic
if search_query:
    # หาชื่อที่ใกล้เคียงที่สุด 5 อันดับแรก
    matches = process.extract(search_query.lower(), pokemon_list, limit=5)
    
    # แสดง Dropdown ให้ผู้ใช้คลิกเลือก
    match_names = [m[0] for m in matches if m[1] > 50] # เอาเฉพาะที่ความเหมือน > 50%
    if match_names:
        selected_pokemon = st.selectbox("💡 คุณหมายถึงตัวไหน?", match_names)
    else:
        st.warning("❌ ไม่พบ Pokémon ที่ใกล้เคียง")

# หากมีการเลือก Pokémon
if selected_pokemon:
    with st.spinner('Loading Pokémon Data...'):
        data = get_pokemon_data(selected_pokemon)
        
    if data:
        # --- จัด Layout เป็น 2 คอลัมน์ ---
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # 2.1 ข้อมูลพื้นฐาน
            st.image(data['sprites']['other']['official-artwork']['front_default'], width=300)
            st.subheader(data['name'].capitalize())
            types = [t['type']['name'].capitalize() for t in data['types']]
            st.write(f"**Type:** {' / '.join(types)}")
            
            # 2.2 ธาตุที่แพ้ทาง (Simplified Example)
            # หมายเหตุ: การคำนวณแพ้ธาตุจริงๆ ต้องดึง Type Chart มาไขว้กัน
            st.write("**⚠️ Weaknesses (ตัวอย่าง):**")
            st.info("Water (2x), Ground (2x), Rock (4x)") 
            
        with col2:
            # 2.3 ค่าสถานะ (Stats) - Radar Chart
            st.write("### 📊 Base Stats")
            stats_data = {s['stat']['name']: s['base_stat'] for s in data['stats']}
            
            # สร้าง Radar Chart ด้วย Plotly
            df = pd.DataFrame(dict(
                r=list(stats_data.values()),
                theta=['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
            ))
            fig = px.line_polar(df, r='r', theta='theta', line_close=True)
            fig.update_traces(fill='toself', line_color='#FF4B4B')
            st.plotly_chart(fig, use_container_width=True)

        st.divider()
        
        # 2.4 Ability
        st.write("### ⭐ Abilities")
        for ab in data['abilities']:
            ab_name = ab['ability']['name'].lower()
            is_hidden = " (Hidden)" if ab['is_hidden'] else ""
            thai_desc = ABILITY_THAI_DICT.get(ab_name, "อยู่ระหว่างการแปล...")
            
            st.markdown(f"- **{ab_name.capitalize()}{is_hidden}**: {thai_desc}")

        st.divider()
        
        # 2.5 Moves
        st.write("### ⚔️ Moves")
        meta_moves_dict = META_MOVES.get(selected_pokemon, {})
        
        if meta_moves_dict:
            st.success("**🔥 Current Meta Moves (ท่าที่นิยมใช้)**")
            for move, reason in meta_moves_dict.items():
                st.write(f"- **{move.capitalize()}**: {reason}")

        # Expanders สำหรับท่าทั้งหมดเพื่อไม่ให้รกหน้าจอ
        with st.expander("ดูท่าทั้งหมด (All Moves)"):
            all_moves = [m['move']['name'] for m in data['moves']]
            st.write(", ".join(all_moves))
