import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import urllib.parse
import streamlit.components.v1 as components

# ==========================================
# 1. ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Logistics Map", layout="wide")

# ==========================================
# 2. การจัดการสถานะโซนที่เลือก
# ==========================================
if 'selected_zone' not in st.session_state:
    st.session_state.selected_zone = 'All'

def set_zone(zone_name):
    st.session_state.selected_zone = zone_name

# ==========================================
# 3. เตรียมข้อมูล
# ==========================================
data = {
    'id': range(1, 20),
    'name': [
        'Amata Nakorn', 'Taisho Seiki', 'SAIC Motor', 'PJW Sriracha', 'Kasai Teck See', 'Supavut Industry',
        'SSK Plastic', 'Union Nifco', 'S.K.Auto Interior', 'Rayong', 'JT TECH ระยอง', 
        'Thai Summit', 'Focus Plastic', 'Saha Charoen', 'Bangpoo Ind.', 'Ampas Ind.', 'Bangkok Metropolis Motor', 
        'Hi-Tech Ayutthaya', 'Kumi (Saraburi)' 
    ],
    'distance_km': [5, 8, 30, 45, 55, 60, 20, 40, 60, 90, 95, 60, 65, 70, 85, 90, 120, 130, 145],
    'zone': ['Zone 1 (Orange)'] * 6 + ['Zone 2 (Blue)'] * 5 + ['Zone 3 (Purple)'] * 6 + ['Zone 4 (Green)'] * 2,
    'x': [0, 0, -2, -2, -3, -1, 3, 8, 12, 16, 20, -5, -10, -15, -20, -25, -30, -4, -2],
    'y': [-3, -7, -12, -20, -28, -35, -1, -4, -8, -18, -25, 2, 1, 0, -5, -12, -20, 18, 35]
}
df = pd.DataFrame(data)

hub = {'name': 'MEIYA POLYMERS<br>AMATA CITY HUB', 'search_name': 'Amata City Chonburi', 'x': 0, 'y': 0}

zone_colors = {
    'Zone 1 (Orange)': '#FF8C00',
    'Zone 2 (Blue)': '#1E90FF',
    'Zone 3 (Purple)': '#9400D3',
    'Zone 4 (Green)': '#00FF00'
}

# ==========================================
# 4. ดึงข้อมูลจุดที่ถูกคลิกจาก Session State ก่อนวาดกราฟ
# ==========================================
selected_loc = None
selected_dist = None

# เมื่อกราฟถูกคลิก Streamlit จะเก็บค่าไว้ใน st.session_state["map_chart"]
if "map_chart" in st.session_state:
    map_event = st.session_state["map_chart"]
    try:
        # รองรับโครงสร้างข้อมูลที่ Streamlit ส่งกลับมา (Dictionary)
        if isinstance(map_event, dict):
            points = map_event.get("selection", {}).get("points", [])
            if points:
                selected_loc = points[0]["customdata"][0]
                selected_dist = points[0]["customdata"][1]
    except Exception:
        pass

# ==========================================
# 5. สร้างแถบเมนูด้านข้าง (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color: #00BFFF; margin: 0;'>MEIYA POLYMERS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8898aa; font-size: 12px; font-weight: bold;'> (AMATA CITY) LOGISTICS MAP</p><br>", unsafe_allow_html=True)
    
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
    
    # 🌟 อัปเดตตัวเลขระยะทางที่ Sidebar ทันทีหากมีการคลิก
    if selected_loc and selected_dist is not None:
        st.metric(label=f"Route Distance: Meiya ➔ {selected_loc}", value=f"{selected_dist} KM")
    else:
        st.metric(label="All Delivery Routes (TOTAL HUB DISTANCE)", value="1,273 KM")
        
    st.markdown("---")
    
    display_df = df.sort_values('distance_km', ascending=False)
    for _, row in display_df.iterrows():
        is_selected = (st.session_state.selected_zone == 'All' or row['zone'] == st.session_state.selected_zone)
        # เน้นเฉพาะจุดที่ถูกคลิก หรือโชว์ทั้งหมดถ้าไม่ได้คลิก
        opacity = "1.0" if (selected_loc == row['name'] or (is_selected and not selected_loc)) else "0.3" 
        color = zone_colors[row["zone"]]
        
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
# 6. สร้างแผนที่ (Main Area) พร้อมระบบเส้นทึบ/เส้นประ
# ==========================================
st.markdown("### 🗺️ แผนที่จำลองเส้นทาง (คลิกที่จุดปลายทางเพื่อดูเส้นทางและระยะทางจริง)")

if st.session_state.selected_zone == 'All':
    filtered_df = df
else:
    filtered_df = df[df['zone'] == st.session_state.selected_zone]

fig = go.Figure()

for zone_name in filtered_df['zone'].unique():
    zone_data = filtered_df[filtered_df['zone'] == zone_name].sort_values('distance_km')
    color = zone_colors[zone_name]
    
    # 🌟 ตรวจสอบว่า "จุดที่ถูกคลิก" อยู่ในโซนนี้หรือไม่
    is_selected_zone = (selected_loc in zone_data['name'].values)
    
    if is_selected_zone:
        # แบ่งข้อมูลเป็น 2 ส่วน: ตั้งแต่ต้นจนถึงจุดที่คลิก (เส้นทึบ) และ หลังจากนั้น (เส้นประ)
        solid_df = zone_data[zone_data['distance_km'] <= selected_dist]
        dashed_df = zone_data[zone_data['distance_km'] >= selected_dist]
        
        # 1. วาดเส้นทึบ (Solid Line) จาก Hub ถึงจุดที่เลือก
        fig.add_trace(go.Scatter(
            x=[hub['x']] + list(solid_df['x']),
            y=[hub['y']] + list(solid_df['y']),
            mode='lines',
            line=dict(color=color, width=6), # เส้นทึบหนา 6
            hoverinfo='none', showlegend=False
        ))
        
        # 2. วาดเส้นประ (Dashed Line) สำหรับจุดที่เหลือในโซน (ถ้ามี)
        if len(dashed_df) > 1:
            fig.add_trace(go.Scatter(
                x=list(dashed_df['x']),
                y=list(dashed_df['y']),
                mode='lines',
                line=dict(color=color, width=4, dash='dash'),
                hoverinfo='none', showlegend=False
            ))
            
    else:
        # ถ้าไม่มีจุดที่ถูกคลิกในโซนนี้ ให้วาดเส้นประตามปกติ
        fig.add_trace(go.Scatter(
            x=[hub['x']] + list(zone_data['x']),
            y=[hub['y']] + list(zone_data['y']),
            mode='lines',
            line=dict(color=color, width=4, dash='dash'),
            hoverinfo='none', showlegend=False
        ))
    
    # ซ่อนข้อมูล name และ distance_km ไว้ใน customdata ของหมุด
    custom_data_list = [[row['name'], row['distance_km']] for _, row in zone_data.iterrows()]
    
    # วาดหมุดวงกลม (Markers)
    fig.add_trace(go.Scatter(
        x=zone_data['x'], y=zone_data['y'],
        mode='markers+text',
        marker=dict(size=12, color=color, line=dict(width=2, color='white')),
        text=[f"{row['name']}<br>{row['distance_km']} km" for _, row in zone_data.iterrows()],
        customdata=custom_data_list, 
        textposition="top center",
        textfont=dict(color='white', size=10),
        hoverinfo='text',
        showlegend=False
    ))

# วาดจุด Hub (จุดศูนย์กลาง)
fig.add_trace(go.Scatter(
    x=[hub['x']], y=[hub['y']],
    mode='markers+text',
    marker=dict(size=18, color='white', symbol='square', line=dict(width=2, color='#00BFFF')),
    text=[hub['name']],
    customdata=[[hub['search_name'], 0]], 
    textposition="top center",
    textfont=dict(color='white', size=14, family='Arial Black'),
    hoverinfo='text',
    showlegend=False
))

fig.update_layout(
    plot_bgcolor='#0b1325', paper_bgcolor='#0b1325', margin=dict(l=0, r=0, t=0, b=0),
    xaxis=dict(showgrid=True, gridcolor='#1a243a', zeroline=False, showticklabels=False, range=[-35, 25]),
    yaxis=dict(showgrid=True, gridcolor='#1a243a', zeroline=False, showticklabels=False, range=[-40, 40]),
    dragmode='pan', height=600, clickmode='event+select' 
)

# 🌟 ใส่ key="map_chart" เพื่อให้ค่าการคลิกถูกบันทึกลง Session State ทันที
st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points", key="map_chart")

# ==========================================
# 7. แสดง Google Maps ด้านล่างเมื่อคลิก
# ==========================================
st.markdown("---")
st.subheader("📍 เส้นทางจริงบน Google Maps")

if selected_loc and selected_dist != 0:
    origin_query = f"{hub['search_name']} Thailand"
    destination_query = f"{selected_loc} Thailand"
    
    encoded_origin = urllib.parse.quote(origin_query)
    encoded_destination = urllib.parse.quote(destination_query)
    
    gmap_url = f"https://maps.google.com/maps?saddr={encoded_origin}&daddr={encoded_destination}&ie=UTF8&output=embed"
    
    st.success(f"กำลังแสดงเส้นทางจาก **MEIYA (Amata City)** ไปยัง **{selected_loc}** (ระยะทาง {selected_dist} km)")
    components.iframe(gmap_url, height=500, scrolling=True)
else:
    st.info("👆 กรุณาคลิกที่จุด (วงกลม) บนแผนที่ด้านบน เพื่อดูเส้นทางแบบเส้นทึบ และเปิดแผนที่จริง")
