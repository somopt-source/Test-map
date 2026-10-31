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
# 2. การจัดการสถานะ (Session State)
# ==========================================
if 'selected_zone' not in st.session_state:
    st.session_state.selected_zone = 'All'

def set_zone(zone_name):
    st.session_state.selected_zone = zone_name

# ==========================================
# 3. เตรียมข้อมูล (Data Preparation)
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
# 4. สร้างแถบเมนูด้านข้าง (Sidebar)
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
    
    # 🌟 สร้างพื้นที่ว่าง (Placeholder) ไว้สำหรับใส่ตัวเลขระยะทางที่จะอัปเดตทีหลัง
    distance_placeholder = st.empty() 
    
    st.markdown("---")
    
    display_df = df.sort_values('distance_km', ascending=False)
    for _, row in display_df.iterrows():
        is_selected = (st.session_state.selected_zone == 'All' or row['zone'] == st.session_state.selected_zone)
        opacity = "1.0" if is_selected else "0.3" 
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
# 5. สร้างแผนที่จำลอง (Main Area)
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
    
    x_coords = [hub['x']] + list(zone_data['x'])
    y_coords = [hub['y']] + list(zone_data['y'])
    
    fig.add_trace(go.Scatter(
        x=x_coords, y=y_coords,
        mode='lines',
        line=dict(color=color, width=4, dash='dash'),
        hoverinfo='none', 
        showlegend=False
    ))
    
    # 🌟 ซ่อนข้อมูลทั้ง "ชื่อ" และ "ระยะทาง" ไว้ใน customdata
    custom_data_list = [[row['name'], row['distance_km']] for _, row in zone_data.iterrows()]
    
    fig.add_trace(go.Scatter(
        x=zone_data['x'], y=zone_data['y'],
        mode='markers+text',
        marker=dict(size=12, color=color, line=dict(width=2, color='white')),
        text=[f"{row['name']}<br>{row['distance_km']} km" for _, row in zone_data.iterrows()],
        customdata=custom_data_list, # <--- อัปเดตตรงนี้
        textposition="top center",
        textfont=dict(color='white', size=10),
        hoverinfo='text',
        showlegend=False
    ))

fig.add_trace(go.Scatter(
    x=[hub['x']], y=[hub['y']],
    mode='markers+text',
    marker=dict(size=18, color='white', symbol='square', line=dict(width=2, color='#00BFFF')),
    text=[hub['name']],
    customdata=[[hub['search_name'], 0]], # <--- จุด Hub ระยะทางเป็น 0
    textposition="top center",
    textfont=dict(color='white', size=14, family='Arial Black'),
    hoverinfo='text',
    showlegend=False
))

fig.update_layout(
    plot_bgcolor='#0b1325', 
    paper_bgcolor='#0b1325', 
    margin=dict(l=0, r=0, t=0, b=0),
    xaxis=dict(showgrid=True, gridcolor='#1a243a', zeroline=False, showticklabels=False, range=[-35, 25]),
    yaxis=dict(showgrid=True, gridcolor='#1a243a', zeroline=False, showticklabels=False, range=[-40, 40]),
    dragmode='pan',
    height=600,
    clickmode='event+select' 
)

# จับค่า Event เมื่อมีการคลิกบนแผนที่
event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")

# ==========================================
# 6. อัปเดตระยะทางที่ Sidebar และแสดง Google Maps
# ==========================================
st.markdown("---")
st.subheader("📍 เส้นทางจริงบน Google Maps")

selected_location_name = None
selected_distance_km = None

# ตรวจสอบว่ามีการคลิกจุดบนแผนที่หรือไม่
if event and len(event.selection.points) > 0:
    clicked_point = event.selection.points[0] 
    
    if 'customdata' in clicked_point:
        # ดึงข้อมูลจาก customdata ที่เราซ่อนไว้ (index 0 คือชื่อ, index 1 คือระยะทาง)
        selected_location_name = clicked_point['customdata'][0]
        selected_distance_km = clicked_point['customdata'][1]
        
        # แสดงเส้นทางบน Google Maps
        origin_query = f"{hub['search_name']} Thailand"
        destination_query = f"{selected_location_name} Thailand"
        
        encoded_origin = urllib.parse.quote(origin_query)
        encoded_destination = urllib.parse.quote(destination_query)
        
        gmap_url = f"https://maps.google.com/maps?saddr={encoded_origin}&daddr={encoded_destination}&ie=UTF8&output=embed"
        
        st.success(f"กำลังแสดงเส้นทางจาก **MEIYA (Amata City)** ไปยัง **{selected_location_name}**")
        components.iframe(gmap_url, height=500, scrolling=True)
else:
    st.info("👆 กรุณาคลิกที่จุด (วงกลม) บนแผนที่ด้านบน เพื่อดูเส้นทาง")

# 🌟 นำข้อมูลระยะทางกลับไปแสดงใน Sidebar (ที่ Placeholder ที่เราจองพื้นที่ไว้)
if selected_location_name and selected_distance_km is not None:
    # ถ้ามีการคลิกจุด ให้แสดงระยะทางของจุดนั้น
    distance_placeholder.metric(
        label=f"Route Distance: Meiya ➔ {selected_location_name}", 
        value=f"{selected_distance_km} KM"
    )
else:
    # ถ้ายังไม่ได้คลิกจุดใดเลย ให้แสดงผลรวม 1,273 KM เหมือนเดิม
    distance_placeholder.metric(
        label="All Delivery Routes (TOTAL HUB DISTANCE)", 
        value="1,273 KM"
    )
