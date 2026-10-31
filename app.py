# ==========================================
# 1. นำเข้าไลบรารีที่จำเป็น
# ==========================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 2. ตั้งค่าหน้าเว็บ (Page Configuration)
# ==========================================
# กำหนดให้หน้าเว็บกว้างเต็มจอ และตั้งชื่อแท็บ
st.set_page_config(page_title="Logistics Map", layout="wide")

# ==========================================
# 3. การจัดการสถานะ (Session State)
# ==========================================
# ใช้สำหรับจำว่าตอนนี้ผู้ใช้กำลังเลือกดู "โซนไหน" อยู่ (ค่าเริ่มต้นคือ 'All' ดูทั้งหมด)
if 'selected_zone' not in st.session_state:
    st.session_state.selected_zone = 'All'

# ฟังก์ชันสำหรับเปลี่ยนโซนเมื่อมีการกดปุ่ม
def set_zone(zone_name):
    st.session_state.selected_zone = zone_name

# ==========================================
# 4. ข้อมูลจำลอง (Mock Data)
# ==========================================
# 4.1 ข้อมูลจุดหมายปลายทางต่างๆ (พิกัดจำลอง x, y เพื่อวาดกราฟ)
data = {
    'id': range(1, 20),
    'name': [
        'Amata Nakorn', 'Taisho Seiki', 'SAIC Motor', 'PJW Sriracha', 'Kasai Teck See', 'Supavut Industry', # โซน 1
        'SSK Plastic', 'Union Nifco', 'S.K.Auto Interior', 'Rayong', 'JT TECH ระยอง', # โซน 2
        'Thai Summit', 'Focus Plastic', 'Saha Charoen', 'Bangpoo Ind.', 'Ampas Ind.', 'Bangkok Metropolis Motor', # โซน 3
        'Hi-Tech Ayutthaya', 'Kumi (Saraburi)' # โซน 4
    ],
    'distance_km': [5, 8, 30, 45, 55, 60, 20, 40, 60, 90, 95, 60, 65, 70, 85, 90, 120, 130, 145],
    'zone': ['Zone 1 (Orange)'] * 6 + ['Zone 2 (Blue)'] * 5 + ['Zone 3 (Purple)'] * 6 + ['Zone 4 (Green)'] * 2,
    'x': [0, 0, -2, -2, -3, -1, 3, 8, 12, 16, 20, -5, -10, -15, -20, -25, -30, -4, -2],
    'y': [-3, -7, -12, -20, -28, -35, -1, -4, -8, -18, -25, 2, 1, 0, -5, -12, -20, 18, 35]
}
df = pd.DataFrame(data)

# 4.2 ข้อมูลจุดศูนย์กลาง (Hub)
hub = {'name': 'MEIYA POLYMERS<br>AMATA CITY HUB', 'x': 0, 'y': 0}

# 4.3 ตั้งค่าสีประจำโซน
zone_colors = {
    'Zone 1 (Orange)': '#FF8C00',
    'Zone 2 (Blue)': '#1E90FF',
    'Zone 3 (Purple)': '#9400D3',
    'Zone 4 (Green)': '#00FF00'
}

# ==========================================
# 5. สร้างส่วนแสดงผลด้านข้าง (Sidebar)
# ==========================================
with st.sidebar:
    # หัวข้อ
    st.markdown("<h2 style='color: #00BFFF; margin: 0;'>MEIYA POLYMERS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8898aa; font-size: 12px; font-weight: bold;'> (AMATA CITY) LOGISTICS MAP</p><br>", unsafe_allow_html=True)
    
    # กลุ่มปุ่มกดเลือกโซน
    st.markdown("<p style='color: #8898aa; font-size: 12px; font-weight: bold;'>SELECT ROUTE ZONE</p>", unsafe_allow_html=True)
    
    st.button("Show All Zones", use_container_width=True, on_click=set_zone, args=('All',))
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("Zone 1 (Orange)", use_container_width=True, on_click=set_zone, args=('Zone 1 (Orange)',))
        st.button("Zone 3 (Purple)", use_container_width=True, on_click=set_zone, args=('Zone 3 (Purple)',))
    with col2:
        st.button("Zone 2 (Blue)", use_container_width=True, on_click=set_zone, args=('Zone 2 (Blue)',))
        st.button("Zone 4 (Green)", use_container_width=True, on_click=set_zone, args=('Zone 4 (Green)',))

    st.markdown("---")
    
    # แสดงระยะทางรวม
    st.metric(label="All Delivery Routes (TOTAL HUB DISTANCE)", value="1,273 KM")
    
    st.markdown("---")
    
    # แสดงรายการสถานที่ (เรียงจากไกลสุดไปใกล้สุด)
    display_df = df.sort_values('distance_km', ascending=False)
    
    for _, row in display_df.iterrows():
        # ตรวจสอบว่าโซนของรายการนี้ตรงกับที่ผู้ใช้กดเลือกไว้หรือไม่
        is_selected = (st.session_state.selected_zone == 'All' or row['zone'] == st.session_state.selected_zone)
        # ถ้าไม่ได้ถูกเลือก ให้ทำภาพจางลง (opacity: 0.3)
        opacity = "1.0" if is_selected else "0.3" 
        color = zone_colors[row["zone"]]
        
        # วาดการ์ดแสดงรายการด้วย HTML/CSS
        html_card = f"""
        <div style="display: flex; align-items: center; justify-content: space-between;
                    background-color: #1a243a; padding: 12px; border-radius: 8px;
                    margin-bottom: 10px; border: 1px solid {color}; opacity: {opacity};">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="background-color: #2c3b59; color: white; width: 28px; height: 28px;
                            border-radius: 50%; display: flex; align-items: center; justify-content: center;
                            font-weight: bold; font-size: 12px;">{row['id']}</div>
                <span style="color: white; font-weight: bold; font-size: 14px;">{row['name']}</span>
            </div>
            <div style="text-align: right;">
                <span style="color: {color}; font-weight: bold; font-size: 18px;">{row['distance_km']}</span><br>
                <span style="color: #8898aa; font-size: 10px;">KM</span>
            </div>
        </div>
        """
        st.markdown(html_card, unsafe_allow_html=True)

# ==========================================
# 6. สร้างส่วนแสดงแผนที่หลัก (Main Map Area)
# ==========================================
# 6.1 กรองข้อมูลเฉพาะโซนที่เลือก
if st.session_state.selected_zone == 'All':
    filtered_df = df
else:
    filtered_df = df[df['zone'] == st.session_state.selected_zone]

# 6.2 เริ่มสร้างกราฟ Plotly
fig = go.Figure()

# 6.3 วาดเส้นทางและจุดปลายทางทีละโซน
for zone_name in filtered_df['zone'].unique():
    # เลือกข้อมูลเฉพาะโซนนั้น และเรียงตามระยะทางเพื่อให้เส้นลากต่อกันอย่างสมูท
    zone_data = filtered_df[filtered_df['zone'] == zone_name].sort_values('distance_km')
    color = zone_colors[zone_name]
    
    # เพิ่มจุดศูนย์กลาง (Hub) เข้าไปเป็นจุดเริ่มต้นของเส้น
    x_coords = [hub['x']] + list(zone_data['x'])
    y_coords = [hub['y']] + list(zone_data['y'])
    
    # วาดเส้นประ (Dashed Lines)
    fig.add_trace(go.Scatter(
        x=x_coords, y=y_coords,
        mode='lines',
        line=dict(color=color, width=4, dash='dash'),
        hoverinfo='none', # ไม่ต้องแสดงข้อมูลตอนเอาเมาส์ชี้ที่เส้น
        showlegend=False
    ))
    
    # วาดจุดวงกลมปลายทาง (Markers) และชื่อสถานที่
    fig.add_trace(go.Scatter(
        x=zone_data['x'], y=zone_data['y'],
        mode='markers+text',
        marker=dict(size=12, color=color, line=dict(width=2, color='white')),
        text=[f"{row['name']}<br>{row['distance_km']} km" for _, row in zone_data.iterrows()],
        textposition="top center",
        textfont=dict(color='white', size=10),
        hoverinfo='text',
        showlegend=False
    ))

# 6.4 วาดจุดศูนย์กลาง (Hub) เป็นสี่เหลี่ยมขนาดใหญ่ตรงกลาง
fig.add_trace(go.Scatter(
    x=[hub['x']], y=[hub['y']],
    mode='markers+text',
    marker=dict(size=18, color='white', symbol='square', line=dict(width=2, color='#00BFFF')),
    text=[hub['name']],
    textposition="top center",
    textfont=dict(color='white', size=14, family='Arial Black'),
    hoverinfo='text',
    showlegend=False
))

# 6.5 ตกแต่งหน้าตากราฟให้เป็นธีมมืด (Dark Theme) แบบคล้ายในภาพ
fig.update_layout(
    plot_bgcolor='#0b1325', # สีพื้นหลังกราฟ
    paper_bgcolor='#0b1325', # สีขอบนอกกราฟ
    margin=dict(l=0, r=0, t=0, b=0), # ลดขอบ
    xaxis=dict(showgrid=True, gridcolor='#1a243a', zeroline=False, showticklabels=False, range=[-35, 25]),
    yaxis=dict(showgrid=True, gridcolor='#1a243a', zeroline=False, showticklabels=False, range=[-40, 40]),
    dragmode='pan', # ให้ลากแพนหน้าจอได้
    height=800 # ความสูงของแผนที่
)

# 6.6 นำกราฟที่สร้างเสร็จมาแสดงใน Streamlit
st.plotly_chart(fig, use_container_width=True)
