import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Health Dashboard", layout="wide")

# Google Sheets холболт
# ЭНД ӨӨРИЙН SHEETS-ИЙН ЛИНКИЙГ ХУУЛЖ ТАВИАРАЙ
url = "https://docs.google.com/spreadsheets/d/1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc/edit?usp=sharing"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=url)
    
    # Огноог зөв формат руу хөрвүүлэх
    df['LogDate'] = pd.to_datetime(df['LogDate'])
    
    st.title("🏥 Эрүүл Мэндийн Хяналт (Cloud)")

    # Хамгийн сүүлийн өгөгдлийг авах
    latest_data = df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Алхалт", f"{int(latest_data['Steps'])} алхам")
    col2.metric("BMI", latest_data['BMI'])
    col3.metric("Биеийн өөх", f"{latest_data['BodyFat']}%")
    col4.metric("Сахар", f"{latest_data['BloodSugar']} mmol/L")

    st.divider()
    st.subheader("📈 Өөрчлөлтийн график")
    # Огноогоор эрэмбэлж график зурах
    chart_data = df.sort_values('LogDate')
    st.line_chart(chart_data.set_index('LogDate')[['BMI', 'BloodSugar']])
    
    st.write("Сүүлчийн шинэчлэл:", latest_data['LogDate'])

except Exception as e:
    st.error(f"Өгөгдөл уншихад алдаа гарлаа: {e}")
    st.info("Google Sheets линкээ зөв эсэхийг, мөн 'Anyone with the link' эрхтэй эсэхийг шалгаарай.")
