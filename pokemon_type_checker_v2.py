# 6. Moves Table พร้อมไฮไลท์ตัวหนังสือ
        st.subheader("🥋 Learnable Moves")
        # รายชื่อท่าที่นิยม
        popular_moves = ["Earthquake", "Thunderbolt", "Ice Beam", "Flamethrower", "Scald", "Toxic", "Recover", "Roost", "U-Turn", "Close Combat"]
        
        # เริ่มสร้าง HTML String
        table_body = ""
        for m in data['moves']:
            m_name = m['move']['name'].replace('-', ' ').title()
            is_popular = m_name in popular_moves
            
            # ใช้ CSS Class 'meta-move' ที่คุณประกาศไว้ใน Section 2
            text_style = 'class="meta-move"' if is_popular else ''
            status_text = "⭐ Popular" if is_popular else "-"
            
            table_body += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">
                        <span {text_style}>{m_name}</span>
                    </td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">{status_text}</td>
                </tr>
            """
        
        move_list_html = f"""
        <div style="max-height: 400px; overflow-y: auto; border: 1px solid #f0f2f6; border-radius: 5px;">
            <table style="width:100%; border-collapse: collapse;">
                <thead style="background-color: #f0f2f6; sticky top: 0;">
                    <tr>
                        <th style="padding: 10px; text-align: left;">Move Name</th>
                        <th style="padding: 10px; text-align: left;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {table_body}
                </tbody>
            </table>
        </div>
        """
        
        # แสดงผลตาราง
        st.markdown(move_list_html, unsafe_allow_html=True)
