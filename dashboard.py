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
        data.columns = data.columns.str.strip() # Баганы нэрний хоосон зайг цэвэрлэнэ
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')] # Илүүдэл багануудыг устгана
        
        # Огнооны хөрвүүлэлт
        if 'LogDate' in data.columns:
            data['LogDate'] = data['LogDate'].astype(str).str.replace('.', '-', regex=False)
            data['LogDate'] = pd.to_datetime(data['LogDate'], errors='coerce', format='mixed')
            data = data.dropna(subset=['LogDate'])
            data = data.sort_values(by='LogDate').reset_index(drop=True)
        return data
    except Exception as e:
        st.error(f"Хүснэгтийг уншиж чадсангүй. Алдаа: {e}")
        return pd.DataFrame()

# Датаг ачааллах
df = load_data(csv_url)

if not df.empty:
    # Хамгийн сүүлийн бодит мөрийн утгыг олох
    valid_data = df.dropna(subset=['Steps', 'SysBP', 'BloodSugar', 'BMI', 'Waist'], how='all')
    if not valid_data.empty:
        latest = valid_data.iloc[-1]
    else:
        latest = df.iloc[-1]

    # --- ХЭСЭГ 1: ТОМ КАРТУУД (ДЭЭД МӨР) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        steps = latest.get('Steps', 0)
        st.metric(label="🏃‍♂️ Сүүлийн Алхалт", value=f"{int(steps):,} алхам" if pd.notna(steps) and steps > 0 else "0 алхам")
    with col2:
        sys = latest.get('SysBP', 0)
        dia = latest.get('DiaBP', 0)
        st.metric(label="❤️ Цусны Даралт", value=f"{int(sys)} / {int(dia)}" if pd.notna(sys) and pd.notna(dia) else "Байхгүй")
    with col3:
        sugar = latest.get('BloodSugar', 0)
        st.metric(label="🩸 Цусны Сахар", value=f"{sugar} mmol/L" if pd.notna(sugar) and sugar > 0 else "Байхгүй")
    with col4:
        pulse = latest.get('Pulse', 0)
        st.metric(label="🫀 Пульс (Зүрхний цохилт)", value=f"{int(pulse)} цохилт/мин" if pd.notna(pulse) and pulse > 0 else "Байхгүй")
        
    # --- БЖИ БА ХЭВЛИЙН ТОЙРӨГ (ДООД МӨР) ---
    col5, col6, col7 = st.columns(3)
    with col5:
        bmi = latest.get('BMI', 0)
        st.metric(label="⚖️ Биеийн Жингийн Индекс (БЖИ)", value=f"{bmi:.1f}" if pd.notna(bmi) and bmi > 0 else "Байхгүй")
    with col6:
        waist = latest.get('Waist', 0)
        st.metric(label="📏 Хэвлийн Тойрог", value=f"{waist} см" if pd.notna(waist) and waist > 0 else "Байхгүй")
    with col7:
        fat = latest.get('BodyFat', 0)
        st.metric(label="📉 Өөхний Хувь", value=f"{fat}%" if pd.notna(fat) and fat > 0 else "Байхгүй")
        
    st.markdown("---")

    # --- ХЭСЭГ 2: ГРАФИКУУД ---
    df_chart = df.copy()
    if 'LogDate' in df_chart.columns:
        df_chart['LogDate_Str'] = df_chart['LogDate'].dt.strftime('%Y-%m-%d')

        # МӨР 1: Алхалт ба Цусны сахар
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            if 'Steps' in df_chart.columns:
                df_steps = df_chart.dropna(subset=['Steps'])
                if not df_steps.empty:
                    st.subheader("🏃 Алхалтын Түүхэн Хөдөлгөөн")
                    fig_steps = px.line(df_steps, x='LogDate_Str', y='Steps', markers=True, title="Өдрийн алхалтын хэмжээ")
                    fig_steps.update_traces(line_color='#2ca02c')
                    fig_steps.update_layout(xaxis_title="Огноо", yaxis_title="Алхалт", xaxis_type='category')
                    st.plotly_chart(fig_steps, use_container_width=True)
                
        with g_col2:
            if 'BloodSugar' in df_chart.columns:
                df_sugar = df_chart.dropna(subset=['BloodSugar'])
                df_sugar = df_sugar[df_sugar['BloodSugar'] > 0]
                if not df_sugar.empty:
                    st.subheader("🩸 Цусны Сахарын Өөрчлөлт")
                    fig_sugar = px.line(df_sugar, x='LogDate_Str', y='BloodSugar', markers=True, title="Сахарын хяналт")
                    fig_sugar.update_traces(line_color='#d62728')
                    fig_sugar.update_layout(xaxis_title="Огноо", yaxis_title="mmol/L", xaxis_type='category')
                    st.plotly_chart(fig_sugar, use_container_width=True)

        # МӨР 2: Даралт ба Пульс
        g_col3, g_col4 = st.columns(2)
        with g_col3:
            if 'SysBP' in df_chart.columns and 'DiaBP' in df_chart.columns:
                df_bp = df_chart.dropna(subset=['SysBP', 'DiaBP'])
                if not df_bp.empty:
                    st.subheader("❤️ Цусны Даралтын Түүх")
                    fig_bp = px.line(df_bp, x='LogDate_Str', y=['SysBP', 'DiaBP'], markers=True, title="Артерийн даралтын динамик")
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
        
        # МӨР 3: ШИНЭЭР НЭМЭГДСЭН (BMI, BodyFat, Waist) ГРАФИКУУД
        g_col5, g_col6, g_col7 = st.columns(3)
        
        with g_col5:
            if 'BMI' in df_chart.columns:
                df_bmi = df_chart.dropna(subset=['BMI'])
                df_bmi = df_bmi[df_bmi['BMI'] > 0]
                if not df_bmi.empty:
                    st.subheader("⚖️ БЖИ (BMI) Хяналт")
                    fig_bmi = px.line(df_bmi, x='LogDate_Str', y='BMI', markers=True, title="Биеийн жингийн индекс")
                    fig_bmi.update_traces(line_color='#9467bd') # Нил ягаан өнгө
                    fig_bmi.update_layout(xaxis_title="Огноо", yaxis_title="БЖИ", xaxis_type='category')
                    st.plotly_chart(fig_bmi, use_container_width=True)

        with g_col6:
            if 'BodyFat' in df_chart.columns:
                df_fat = df_chart.dropna(subset=['BodyFat'])
                df_fat = df_fat[df_fat['BodyFat'] > 0]
                if not df_fat.empty:
                    st.subheader("📉 Өөхний Хувийн Түүх")
                    fig_fat = px.line(df_fat, x='LogDate_Str', y='BodyFat', markers=True, title="Биеийн өөхний эзлэх хувь")
                    fig_fat.update_traces(line_color='#e377c2') # Ягаан өнгө
                    fig_fat.update_layout(xaxis_title="Огноо", yaxis_title="Өөх (%)", xaxis_type='category')
                    st.plotly_chart(fig_fat, use_container_width=True)

        with g_col7:
            if 'Waist' in df_chart.columns:
                df_waist = df_chart.dropna(subset=['Waist'])
                df_waist = df_waist[df_waist['Waist'] > 0]
                if not df_waist.empty:
                    st.subheader("📏 Хэвлийн Тойргийн Түүх")
                    fig_waist = px.line(df_waist, x='LogDate_Str', y='Waist', markers=True, title="Хэвлийн тойргийн хэмжээ")
                    fig_waist.update_traces(line_color='#17becf') # Цэнхэр өнгө
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
