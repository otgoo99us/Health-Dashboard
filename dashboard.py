import streamlit as st
import pandas as pd

# Хуудасны тохиргоо
st.set_page_config(page_title="Health Dashboard", layout="wide")

# Google Sheets линк (CSV хэлбэрээр унших)
sheet_id = "1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

def load_data():
    # Огноог автоматаар таних тохиргоотой унших
    df = pd.read_csv(url)
    return df

try:
    df = load_data()
    
    # Огноог хөрвүүлэх (format заахгүйгээр уян хатан хөрвүүлэх)
    if 'LogDate' in df.columns:
        df['LogDate'] = pd.to_datetime(df['LogDate'], errors='coerce')
        # Хоосон огноотой мөрийг хасах
        df = df.dropna(subset=['LogDate'])

    st.title("🏥 Миний Эрүүл Мэндийн Хяналт")

    # Хамгийн сүүлийн өгөгдлийг авах
    latest = df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Алхалт", f"{int(latest['Steps'])}")
    col2.metric("BMI", f"{latest['BMI']}")
    col3.metric("Өөх", f"{latest['BodyFat']}%")
    col4.metric("Сахар", f"{latest['BloodSugar']}")

    st.divider()
    
    st.subheader("📈 Өөрчлөлтийн график")
    # График зурах өгөгдлийг огноогоор эрэмбэлэх
    chart_data = df.sort_values('LogDate')
    st.line_chart(chart_data.set_index('LogDate')[['BMI', 'BloodSugar']])
    
    st.info(f"Сүүлчийн өгөгдөл: {latest['LogDate'].strftime('%Y-%m-%d')}")

except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")
