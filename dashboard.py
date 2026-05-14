import streamlit as st
from st_gsheets_connection import GSheetsConnection  # Энэ мөрийг яг ингэж бичнэ
import pandas as pd

# Вэб хуудасны тохиргоо
st.set_page_config(page_title="Health Dashboard", layout="wide")

# Google Sheets холболт
url = "https://docs.google.com/spreadsheets/d/1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url)
    
    # Огноог зөв формат руу хөрвүүлэх
    df['LogDate'] = pd.to_datetime(df['LogDate'])
    
    st.title("🏥 Миний Эрүүл Мэндийн Хяналт")

    # Хамгийн сүүлийн өгөгдлийг авах
    latest_data = df.iloc[-1]

    # Үзүүлэлтүүдийг харуулах (Метрик)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Алхалт", f"{int(latest_data['Steps'])} алхам")
    col2.metric("BMI", latest_data['BMI'])
    col3.metric("Биеийн өөх", f"{latest_data['BodyFat']}%")
    col4.metric("Сахар", f"{latest_data['BloodSugar']} mmol/L")

    st.divider()
    
    # График хэсэг
    st.subheader("📈 Хугацааны өөрчлөлт")
    chart_data = df.sort_values('LogDate')
    
    tab1, tab2 = st.tabs(["BMI & Сахар", "Алхалт"])
    
    with tab1:
        st.line_chart(chart_data.set_index('LogDate')[['BMI', 'BloodSugar']])
    
    with tab2:
        st.bar_chart(chart_data.set_index('LogDate')['Steps'])
    
    st.info(f"Сүүлчийн өгөгдөл шинэчлэгдсэн: {latest_data['LogDate'].strftime('%Y-%m-%d %H:%M')}")

except Exception as e:
    st.error(f"Өгөгдөл уншихад алдаа гарлаа: {e}")
