import streamlit as st
import pandas as pd

# Хуудасны тохиргоо
st.set_page_config(page_title="Health Dashboard", layout="wide")

# Google Sheets линк (CSV хэлбэрээр унших)
sheet_id = "1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

def load_data():
    return pd.read_csv(url)

try:
    df = load_data()
    
    # Огноо хөрвүүлэх
    if 'LogDate' in df.columns:
        df['LogDate'] = pd.to_datetime(df['LogDate'])

    st.title("🏥 Миний Эрүүл Мэндийн Хяналт")

    # Сүүлийн мөрийн дата
    latest = df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Алхалт", f"{latest['Steps']}")
    col2.metric("BMI", f"{latest['BMI']}")
    col3.metric("Өөх", f"{latest['BodyFat']}%")
    col4.metric("Сахар", f"{latest['BloodSugar']}")

    st.divider()
    st.subheader("📈 Өөрчлөлтийн график")
    st.line_chart(df.set_index('LogDate')[['BMI', 'BloodSugar']])

except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")
