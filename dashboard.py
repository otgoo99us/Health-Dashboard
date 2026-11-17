import streamlit as st
import pandas as pd
import plotly.express as px

# Хуудасны үндсэн тохиргоо
st.set_page_config(page_title="Эрүүл Мэндийн Самбар", layout="wide", page_icon="📊")

st.title("📊 Эрүүл Мэндийн Хяналтын Цогц Самбар")

# ТАНЫ GOOGLE SHEET-ИЙН ЗӨВ ID БА ХОЛБООС
SHEET_ID = "1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc"
csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=2) # 2 секунд тутамд датаг шинэчилнэ
def load_data(url):
    try:
        data = pd.read_csv(url)
        data.columns = data.columns.str.strip()
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        
        # Огнооны хөрвүүлэлт
        if 'LogDate' in data.columns:
            data['LogDate'] = data['LogDate'].astype(str).str.replace('.', '-', regex=False)
            data['LogDate'] = pd.to_datetime(data['LogDate'], errors='coerce', format='mixed')
            data = data.dropna(subset=['LogDate'])
            data = data.sort_values(by='LogDate').reset_index(drop=True)
            
        # Тоон утгуудыг цэвэрлэх
        num_cols = ['Steps', 'BloodSugar', 'SysBP', 'DiaBP', 'Pulse', 'BMI', 'Waist', 'BodyFat']
        for col in num_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
                
        return data
    except Exception as e:
        st.error(f"Хүснэгтийг уншиж чадсангүй. Алдаа: {e}")
        return pd.DataFrame()

# Тухайн баганын хамгийн сүүлийн бодит утгыг олох туслах функц
def get_latest_valid(df, col_name):
    if col_name in df.columns:
        valid = df[df[col_name].notna() & (df[col_name] > 0)]
        if not valid.empty:
            return valid.iloc[-1][col_name]
    return None

# Датаг ачааллах
df = load_data(csv_url)

if not df.empty:
    max_date = df['LogDate'].max()
    
    # --- ДУНДАЖ ҮЗҮҮЛЭЛТҮҮДИЙГ ТООЦООЛОХ ---
    # 1. Алхалтын дундаж (1 сар = 30 хоног, 1 жил = 365 хоног)
    df_steps_valid = df[df['Steps'].notna() & (df['Steps'] > 0)] if 'Steps' in df.columns else pd.DataFrame()
    steps_1m_avg = df_steps_valid[df_steps_valid['LogDate'] >= (max_date - pd.Timedelta(days=30))]['Steps'].mean() if not df_steps_valid.empty else None
    steps_1y_avg = df_steps_valid[df_steps_valid['LogDate'] >= (max_date - pd.Timedelta(days=365))]['Steps'].mean() if not df_steps_valid.empty else None

    # 2. Сахарын дундаж (1 сар = 30 хоног, 3 сар = 90 хоног)
    df_sugar_valid = df[df['BloodSugar'].notna() & (df['BloodSugar'] > 0)] if 'BloodSugar' in df.columns else pd.DataFrame()
    sugar_1m_avg = df_sugar_valid[df_sugar_valid['LogDate'] >= (max_date - pd.Timedelta(days=30))]['BloodSugar'].mean() if not df_sugar_valid.empty else None
    sugar_3m_avg = df_sugar_valid[df_sugar_valid['LogDate'] >= (max_date - pd.Timedelta(days=90))]['BloodSugar'].mean() if not df_sugar_valid.empty else None

    # Сүүлийн бодит утгууд
    latest_steps = get_latest_valid(df, 'Steps')
    latest_sugar = get_latest_valid(df, 'BloodSugar')
    latest_sys = get_latest_valid(df, 'SysBP')
    latest_dia = get_latest_valid(df, 'DiaBP')
    latest_pulse = get_latest_valid(df, 'Pulse')
    latest_bmi = get_latest_valid(df, 'BMI')
    latest_waist = get_latest_valid(df, 'Waist')
    latest_fat = get_latest_valid(df, 'BodyFat')

    # --- ХЭСЭГ 1: АЛХАЛТ БА САХАРЫН ОНЦЛОХ ДУНДАЖ КАРТУУД ---
    st.subheader("📌 Алхалт ба Сахарын Дундаж Үзүүлэлтүүд")
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.metric(
            label="🏃‍♂️ Сүүлийн Алхалт", 
            value=f"{int(latest_steps):,} алхам" if latest_steps else "0 алхам"
        )
    with m_col2:
        st.metric(
            label="📅 Алхалт (1 сарын дундаж)", 
            value=f"{int(round(steps_1m_avg)):,} алхам" if pd.notna(steps_1m_avg) else "Байхгүй"
        )
    with m_col3:
        st.metric(
            label="🗓️ Алхалт (1 жилийн дундаж)", 
            value=f"{int(round(steps_1y_avg)):,} алхам" if pd.notna(steps_1y_avg) else "Байхгүй"
        )

    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        st.metric(
            label="🩸 Сүүлийн Цусны Сахар", 
            value=f"{latest_sugar:.1f} mmol/L" if latest_sugar else "Байхгүй"
        )
    with s_col2:
        st.metric(
            label="📅 Сахар (1 сарын дундаж)", 
            value=f"{sugar_1m_avg:.2f} mmol/L" if pd.notna(sugar_1m_avg) else "Байхгүй"
        )
    with s_col3:
        st.metric(
            label="📊 Сахар (3 сарын дундаж)", 
            value=f"{sugar_3m_avg:.2f} mmol/L" if pd.notna(sugar_3m_avg) else "Байхгүй"
        )

    st.markdown("---")

    # --- БУСАД ҮЗҮҮЛЭЛТҮҮД ---
    o_col1, o_col2, o_col3, o_col4, o_col5 = st.columns(5)
    with o_col1:
        st.metric(label="❤️ Цусны Даралт", value=f"{int(latest_sys)} / {int(latest_dia)}" if latest_sys and latest_dia else "Байхгүй")
    with o_col2:
        st.metric(label="🫀 Пульс", value=f"{int(latest_pulse)} цохилт/мин" if latest_pulse else "Байхгүй")
    with o_col3:
        st.metric(label="⚖️ БЖИ (BMI)", value=f"{latest_bmi:.1f}" if latest_bmi else "Байхгүй")
    with o_col4:
        st.metric(label="📏 Хэвлийн Тойрог", value=f"{latest_waist} см" if latest_waist else "Байхгүй")
    with o_col5:
        st.metric(label="📉 Өөхний Хувь", value=f"{latest_fat:.1f}%" if latest_fat else "Байхгүй")

    st.markdown("---")

    # --- ХЭСЭГ 2: ГРАФИКУУД ---
    df_chart = df.copy()
    if 'LogDate' in df_chart.columns:
        df_chart['LogDate_Str'] = df_chart['LogDate'].dt.strftime('%Y-%m-%d')

        # МӨР 1: Алхалт ба Цусны сахар (ТОД ДУНДАЖ ЗУРААСТАЙ)
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            if 'Steps' in df_chart.columns:
                df_steps = df_chart.dropna(subset=['Steps'])
                df_steps = df_steps[df_steps['Steps'] > 0]
                if not df_steps.empty:
                    st.subheader("🏃 Алхалтын Түүхэн Хөдөлгөөн")
                    fig_steps = px.line(df_steps, x='LogDate_Str', y='Steps', markers=True, title="Өдрийн алхалт ба Дундаж шугамууд")
                    fig_steps.update_traces(line_color='#2ca02c', line_width=2)
                    
                    # 1 сарын дундаж тод зураас
                    if pd.notna(steps_1m_avg):
                        fig_steps.add_hline(
                            y=steps_1m_avg, 
                            line_dash="dash", 
                            line_color="#0055ff", 
                            line_width=3,
                            annotation_text=f"  1 сарын дундаж: {int(round(steps_1m_avg)):,}  ",
                            annotation_position="top left",
                            annotation_font=dict(size=13, color="#0055ff", family="Arial Black"),
                            annotation_bgcolor="rgba(255, 255, 255, 0.85)"
                        )
                    # 1 жилийн дундаж тод зураас
                    if pd.notna(steps_1y_avg):
                        fig_steps.add_hline(
                            y=steps_1y_avg, 
                            line_dash="dot", 
                            line_color="#ff6600", 
                            line_width=3,
                            annotation_text=f"  1 жилийн дундаж: {int(round(steps_1y_avg)):,}  ",
                            annotation_position="bottom right",
                            annotation_font=dict(size=13, color="#ff6600", family="Arial Black"),
                            annotation_bgcolor="rgba(255, 255, 255, 0.85)"
                        )
                        
                    fig_steps.update_layout(xaxis_title="Огноо", yaxis_title="Алхалт", xaxis_type='category')
                    st.plotly_chart(fig_steps, use_container_width=True)
                
        with g_col2:
            if 'BloodSugar' in df_chart.columns:
                df_sugar = df_chart.dropna(subset=['BloodSugar'])
                df_sugar = df_sugar[df_sugar['BloodSugar'] > 0]
                if not df_sugar.empty:
                    st.subheader("🩸 Цусны Сахарын Өөрчлөлт")
                    fig_sugar = px.line(df_sugar, x='LogDate_Str', y='BloodSugar', markers=True, title="Сахарын хяналт ба Дундаж шугамууд")
                    fig_sugar.update_traces(line_color='#d62728', line_width=2)
                    
                    # 1 сарын дундаж тод зураас
                    if pd.notna(sugar_1m_avg):
                        fig_sugar.add_hline(
                            y=sugar_1m_avg, 
                            line_dash="dash", 
                            line_color="#0055ff", 
                            line_width=3,
                            annotation_text=f"  1 сарын дундаж: {sugar_1m_avg:.2f}  ",
                            annotation_position="top left",
                            annotation_font=dict(size=13, color="#0055ff", family="Arial Black"),
                            annotation_bgcolor="rgba(255, 255, 255, 0.85)"
                        )
                    # 3 сарын дундаж тод зураас
                    if pd.notna(sugar_3m_avg):
                        fig_sugar.add_hline(
                            y=sugar_3m_avg, 
                            line_dash="dot", 
                            line_color="#ff6600", 
                            line_width=3,
                            annotation_text=f"  3 сарын дундаж: {sugar_3m_avg:.2f}  ",
                            annotation_position="bottom right",
                            annotation_font=dict(size=13, color="#ff6600", family="Arial Black"),
                            annotation_bgcolor="rgba(255, 255, 255, 0.85)"
                        )
                        
                    fig_sugar.update_layout(xaxis_title="Огноо", yaxis_title="mmol/L", xaxis_type='category')
                    st.plotly_chart(fig_sugar, use_container_width=True)

        # МӨР 2: Даралт ба Пульс
        g_col3, g_col4 = st.columns(2)
        with g_col3:
            if 'SysBP' in df_chart.columns and 'DiaBP' in df_chart.columns:
                df_bp = df_chart.dropna(subset=['SysBP', 'DiaBP'])
                df_bp = df_bp[(df_bp['SysBP'] > 0) & (df_bp['DiaBP'] > 0)]
                if not df_bp.empty:
                    st.subheader("❤️ Цусны Даралтын Түүх")
                    fig_bp = px.line(df_bp, x='LogDate_Str', y=['SysBP', 'DiaBP'], markers=True, title="Артерийн даралтын өөрчлөлт")
                    fig_bp.update_layout(xaxis_title="Огноо", yaxis_title="Даралт (mmHg)", xaxis_type='category')
                    st.plotly_chart(fig_bp, use_container_width=True)
                    
        with g_col4:
            if 'Pulse' in df_chart.columns:
                df_pulse = df_chart.dropna(subset=['Pulse'])
                df_pulse = df_pulse[df_pulse['Pulse'] > 0]
                if not df_pulse.empty:
                    st.subheader("🫀 Зүрхний Цохилтын Түүх (Пульс)")
                    fig_pulse = px.line(df_pulse, x='LogDate_Str', y='Pulse', markers=True, title="Минутанд цохих зүрхний давтамж")
                    fig_pulse.update_traces(line_color='#ff7f0e')
                    fig_pulse.update_layout(xaxis_title="Огноо", yaxis_title="Цохилт/мин", xaxis_type='category')
                    st.plotly_chart(fig_pulse, use_container_width=True)

        st.markdown("### 📊 Биеийн бүтэц ба хэмжээний өөрчлөлтүүд")
        
        # МӨР 3: BMI, BodyFat, Waist ГРАФИКУУД
        g_col5, g_col6, g_col7 = st.columns(3)
        with g_col5:
            if 'BMI' in df_chart.columns:
                df_bmi = df_chart.dropna(subset=['BMI'])
                df_bmi = df_bmi[df_bmi['BMI'] > 0]
                if not df_bmi.empty:
                    st.subheader("⚖️ БЖИ (BMI) Хяналт")
                    fig_bmi = px.line(df_bmi, x='LogDate_Str', y='BMI', markers=True, title="Биеийн жингийн индекс")
                    fig_bmi.update_traces(line_color='#9467bd')
                    fig_bmi.update_layout(xaxis_title="Огноо", yaxis_title="БЖИ", xaxis_type='category')
                    st.plotly_chart(fig_bmi, use_container_width=True)

        with g_col6:
            if 'BodyFat' in df_chart.columns:
                df_fat = df_chart.dropna(subset=['BodyFat'])
                df_fat = df_fat[df_fat['BodyFat'] > 0]
                if not df_fat.empty:
                    st.subheader("📉 Өөхний Хувийн Түүх")
                    fig_fat = px.line(df_fat, x='LogDate_Str', y='BodyFat', markers=True, title="Биеийн өөхний эзлэх хувь")
                    fig_fat.update_traces(line_color='#e377c2')
                    fig_fat.update_layout(xaxis_title="Огноо", yaxis_title="Өөх (%)", xaxis_type='category')
                    st.plotly_chart(fig_fat, use_container_width=True)

        with g_col7:
            if 'Waist' in df_chart.columns:
                df_waist = df_chart.dropna(subset=['Waist'])
                df_waist = df_waist[df_waist['Waist'] > 0]
                if not df_waist.empty:
                    st.subheader("📏 Хэвлийн Тойргийн Түүх")
                    fig_waist = px.line(df_waist, x='LogDate_Str', y='Waist', markers=True, title="Хэвлийн тойргийн хэмжээ")
                    fig_waist.update_traces(line_color='#17becf')
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
