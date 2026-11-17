import streamlit as st
import pandas as pd
import plotly.express as px

# Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="Эрүүл Мэндийн Самбар", layout="wide", page_icon="📊")

st.title("📊 Эрүүл Мэндийн Хяналтын Цогц Самбар")

# ТАНЫ GOOGLE SHEET-ИЙН ЗӨВ ID БА ХОЛБООС
SHEET_ID = "1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=2)
def load_data(url):
    try:
        data = pd.read_csv(url)
        data.columns = data.columns.str.strip()
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        
        if 'LogDate' in data.columns:
            data['LogDate'] = data['LogDate'].astype(str).str.replace('.', '-', regex=False)
            data['LogDate'] = pd.to_datetime(data['LogDate'], errors='coerce', format='mixed')
            data = data.dropna(subset=['LogDate'])
            data = data.sort_values(by='LogDate').reset_index(drop=True)
            
        num_cols = ['Steps', 'BloodSugar', 'SysBP', 'DiaBP', 'Pulse', 'BMI', 'Waist', 'BodyFat']
        for col in num_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
                
        return data
    except Exception as e:
        st.error(f"Хүснэгтийг уншиж чадсангүй. Алдаа: {e}")
        return pd.DataFrame()

# Сүүлийн бодит утга болон 1 сар (30 хоног), N хоногийн дундаж тооцоолох функц
def get_stats(df, col_name, period_days=365):
    if col_name not in df.columns:
        return None, None, None
    valid = df[df[col_name].notna() & (df[col_name] > 0)].copy()
    if valid.empty:
        return None, None, None
    
    latest_val = valid.iloc[-1][col_name]
    
    # Ирээдүйн андуурсан огнооноос сэргийлж бодит сүүлийн огноог тооцох
    today = pd.Timestamp.now().normalize() + pd.Timedelta(days=1)
    past_valid = valid[valid['LogDate'] <= today]
    ref_date = past_valid['LogDate'].max() if not past_valid.empty else valid['LogDate'].max()
    
    avg_1m = valid[valid['LogDate'] >= (ref_date - pd.Timedelta(days=30))][col_name].mean()
    avg_long = valid[valid['LogDate'] >= (ref_date - pd.Timedelta(days=period_days))][col_name].mean()
    
    return latest_val, avg_1m, avg_long

# График дээр 2 дундаж зураас нэмэх туслах функц
def add_avg_lines(fig, avg_1m, avg_long, label_long="1 жилийн дундаж", fmt="{:.1f}"):
    if pd.notna(avg_1m):
        fig.add_hline(
            y=avg_1m,
            line_dash="dash",
            line_color="#0055ff",
            line_width=3,
            annotation_text=f"  1 сарын дундаж: {fmt.format(avg_1m)}  ",
            annotation_position="top left",
            annotation_font=dict(size=12, color="#0055ff", family="Arial Black"),
            annotation_bgcolor="rgba(255, 255, 255, 0.85)"
        )
    if pd.notna(avg_long):
        fig.add_hline(
            y=avg_long,
            line_dash="dot",
            line_color="#ff6600",
            line_width=3,
            annotation_text=f"  {label_long}: {fmt.format(avg_long)}  ",
            annotation_position="bottom right",
            annotation_font=dict(size=12, color="#ff6600", family="Arial Black"),
            annotation_bgcolor="rgba(255, 255, 255, 0.85)"
        )

df = load_data(csv_url)

if not df.empty:
    # Бүх үзүүлэлтийн статистикийг бодох
    st_lat, st_1m, st_1y = get_stats(df, 'Steps', 365)
    su_lat, su_1m, su_3m = get_stats(df, 'BloodSugar', 90)
    sys_lat, sys_1m, sys_1y = get_stats(df, 'SysBP', 365)
    dia_lat, dia_1m, dia_1y = get_stats(df, 'DiaBP', 365)
    pu_lat, pu_1m, pu_1y = get_stats(df, 'Pulse', 365)
    bmi_lat, bmi_1m, bmi_1y = get_stats(df, 'BMI', 365)
    wa_lat, wa_1m, wa_1y = get_stats(df, 'Waist', 365)
    fat_lat, fat_1m, fat_1y = get_stats(df, 'BodyFat', 365)

    # --- ХЭСЭГ 1: БҮХ ҮЗҮҮЛЭЛТИЙН СҮҮЛИЙН БА ДУНДАЖ УТГУУД ---
    st.subheader("📌 Бүх Үзүүлэлтийн Сүүлийн Утга ба Дундаж")

    # 1. Алхалт ба Сахар
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🏃‍♂️ Сүүлийн Алхалт", f"{int(st_lat):,}" if st_lat else "Байхгүй")
    with c2:
        st.metric("📅 Алхалт (1 сар / 1 жил)", 
                  f"{int(round(st_1m)):,} / {int(round(st_1y)):,}" if pd.notna(st_1m) and pd.notna(st_1y) else "Байхгүй")
    with c3:
        st.metric("🩸 Сүүлийн Сахар", f"{su_lat:.1f} mmol/L" if su_lat else "Байхгүй")
    with c4:
        st.metric("📅 Сахар (1 сар / 3 сар)", 
                  f"{su_1m:.2f} / {su_3m:.2f}" if pd.notna(su_1m) and pd.notna(su_3m) else "Байхгүй")

    # 2. Даралт ба Пульс
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric("❤️ Сүүлийн Даралт", f"{int(sys_lat)}/{int(dia_lat)}" if sys_lat and dia_lat else "Байхгүй")
    with c6:
        st.metric("📅 Даралт (1 сар / 1 жил)", 
                  f"{int(round(sys_1m))}/{int(round(dia_1m))} | {int(round(sys_1y))}/{int(round(dia_1y))}" if pd.notna(sys_1m) and pd.notna(sys_1y) else "Байхгүй")
    with c7:
        st.metric("🫀 Сүүлийн Пульс", f"{int(pu_lat)} цох/мин" if pu_lat else "Байхгүй")
    with c8:
        st.metric("📅 Пульс (1 сар / 1 жил)", 
                  f"{int(round(pu_1m))} / {int(round(pu_1y))}" if pd.notna(pu_1m) and pd.notna(pu_1y) else "Байхгүй")

    # 3. БЖИ, Өөхний хувь, Хэвлийн тойрог
    c9, c10, c11 = st.columns(3)
    with c9:
        st.metric("⚖️ БЖИ (Сүүлийн | 1сар / 1жил)", 
                  f"{bmi_lat:.1f}  |  {bmi_1m:.1f} / {bmi_1y:.1f}" if bmi_lat and pd.notna(bmi_1m) else "Байхгүй")
    with c10:
        st.metric("📉 Өөх % (Сүүлийн | 1сар / 1жил)", 
                  f"{fat_lat:.1f}%  |  {fat_1m:.1f}% / {fat_1y:.1f}%" if fat_lat and pd.notna(fat_1m) else "Байхгүй")
    with c11:
        st.metric("📏 Тойрог см (Сүүлийн | 1сар / 1жил)", 
                  f"{wa_lat:.1f}  |  {wa_1m:.1f} / {wa_1y:.1f}" if wa_lat and pd.notna(wa_1m) else "Байхгүй")

    st.markdown("---")

    # --- ХЭСЭГ 2: ГРАФИКУУД ---
    df_chart = df.copy()
    if 'LogDate' in df_chart.columns:
        df_chart['LogDate_Str'] = df_chart['LogDate'].dt.strftime('%Y-%m-%d')

        # МӨР 1: Алхалт ба Сахар
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            df_steps = df_chart[df_chart['Steps'].notna() & (df_chart['Steps'] > 0)]
            if not df_steps.empty:
                st.subheader("🏃 Алхалтын Түүхэн Хөдөлгөөн")
                fig_steps = px.line(df_steps, x='LogDate_Str', y='Steps', markers=True, title="Өдрийн алхалт ба Дундаж")
                fig_steps.update_traces(line_color='#2ca02c', line_width=2)
                add_avg_lines(fig_steps, st_1m, st_1y, "1 жилийн дундаж", "{:,.0f}")
                fig_steps.update_layout(xaxis_title="Огноо", yaxis_title="Алхалт", xaxis_type='category')
                st.plotly_chart(fig_steps, use_container_width=True)
                
        with g_col2:
            df_sugar = df_chart[df_chart['BloodSugar'].notna() & (df_chart['BloodSugar'] > 0)]
            if not df_sugar.empty:
                st.subheader("🩸 Цусны Сахарын Өөрчлөлт")
                fig_sugar = px.line(df_sugar, x='LogDate_Str', y='BloodSugar', markers=True, title="Сахарын хяналт ба Дундаж")
                fig_sugar.update_traces(line_color='#d62728', line_width=2)
                add_avg_lines(fig_sugar, su_1m, su_3m, "3 сарын дундаж", "{:.2f}")
                fig_sugar.update_layout(xaxis_title="Огноо", yaxis_title="mmol/L", xaxis_type='category')
                st.plotly_chart(fig_sugar, use_container_width=True)

        # МӨР 2: Даралт ба Пульс
        g_col3, g_col4 = st.columns(2)
        with g_col3:
            df_bp = df_chart[df_chart['SysBP'].notna() & df_chart['DiaBP'].notna() & (df_chart['SysBP'] > 0)]
            if not df_bp.empty:
                st.subheader("❤️ Цусны Даралтын Түүх")
                fig_bp = px.line(df_bp, x='LogDate_Str', y=['SysBP', 'DiaBP'], markers=True, title="Даралт ба Дээд даралтын дундаж")
                add_avg_lines(fig_bp, sys_1m, sys_1y, "1 жилийн дундаж (Дээд)", "{:.0f}")
                fig_bp.update_layout(xaxis_title="Огноо", yaxis_title="Даралт (mmHg)", xaxis_type='category')
                st.plotly_chart(fig_bp, use_container_width=True)
                    
        with g_col4:
            df_pulse = df_chart[df_chart['Pulse'].notna() & (df_chart['Pulse'] > 0)]
            if not df_pulse.empty:
                st.subheader("🫀 Зүрхний Цохилтын Түүх (Пульс)")
                fig_pulse = px.line(df_pulse, x='LogDate_Str', y='Pulse', markers=True, title="Пульс ба Дундаж")
                fig_pulse.update_traces(line_color='#ff7f0e')
                add_avg_lines(fig_pulse, pu_1m, pu_1y, "1 жилийн дундаж", "{:.0f}")
                fig_pulse.update_layout(xaxis_title="Огноо", yaxis_title="Цохилт/мин", xaxis_type='category')
                st.plotly_chart(fig_pulse, use_container_width=True)

        st.markdown("### 📊 Биеийн бүтэц ба хэмжээний өөрчлөлтүүд")
        
        # МӨР 3: BMI, BodyFat, Waist ГРАФИКУУД
        g_col5, g_col6, g_col7 = st.columns(3)
        with g_col5:
            df_bmi = df_chart[df_chart['BMI'].notna() & (df_chart['BMI'] > 0)]
            if not df_bmi.empty:
                st.subheader("⚖️ БЖИ (BMI) Хяналт")
                fig_bmi = px.line(df_bmi, x='LogDate_Str', y='BMI', markers=True, title="БЖИ ба Дундаж")
                fig_bmi.update_traces(line_color='#9467bd')
                add_avg_lines(fig_bmi, bmi_1m, bmi_1y, "1 жилийн дундаж", "{:.1f}")
                fig_bmi.update_layout(xaxis_title="Огноо", yaxis_title="БЖИ", xaxis_type='category')
                st.plotly_chart(fig_bmi, use_container_width=True)

        with g_col6:
            df_fat = df_chart[df_chart['BodyFat'].notna() & (df_chart['BodyFat'] > 0)]
            if not df_fat.empty:
                st.subheader("📉 Өөхний Хувийн Түүх")
                fig_fat = px.line(df_fat, x='LogDate_Str', y='BodyFat', markers=True, title="Өөхний хувь ба Дундаж")
                fig_fat.update_traces(line_color='#e377c2')
                add_avg_lines(fig_fat, fat_1m, fat_1y, "1 жилийн дундаж", "{:.1f}%")
                fig_fat.update_layout(xaxis_title="Огноо", yaxis_title="Өөх (%)", xaxis_type='category')
                st.plotly_chart(fig_fat, use_container_width=True)

        with g_col7:
            df_waist = df_chart[df_chart['Waist'].notna() & (df_chart['Waist'] > 0)]
            if not df_waist.empty:
                st.subheader("📏 Хэвлийн Тойргийн Түүх")
                fig_waist = px.line(df_waist, x='LogDate_Str', y='Waist', markers=True, title="Хэвлийн тойрог ба Дундаж")
                fig_waist.update_traces(line_color='#17becf')
                add_avg_lines(fig_waist, wa_1m, wa_1y, "1 жилийн дундаж", "{:.1f}")
                fig_waist.update_layout(xaxis_title="Огноо", yaxis_title="Тойрог (см)", xaxis_type='category')
                st.plotly_chart(fig_waist, use_container_width=True)

    st.markdown("---")
    
    # --- ХЭСЭГ 3: ХҮСНЭГТ ---
    st.subheader("📋 Бүх бүртгэгдсэн өгөгдлийн сан")
    df_display = df.copy()
    if 'LogDate' in df_display.columns:
        df_display['LogDate'] = df_display['LogDate'].dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(df_display.sort_values(by='LogDate', ascending=False), use_container_width=True)
else:
    st.warning("Хүснэгтээс өгөгдөл уншиж чадсангүй.")
