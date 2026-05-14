import streamlit as st
import pandas as pd

# Хуудасны тохиргоо
st.set_page_config(page_title="Health Dashboard", layout="wide")

# Google Sheets CSV link
sheet_id = "1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

def load_data():
    df = pd.read_csv(url)
    # Баганын нэрнүүдийн илүүдэл зайг цэвэрлэх
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    # Огноог хөрвүүлэх
    if 'LogDate' in df.columns:
        df['LogDate'] = pd.to_datetime(df['LogDate'], errors='coerce')
        # Огноогүй эсвэл бүх мөр нь хоосон хэсгийг устгах
        df = df.dropna(subset=['LogDate'])
    
    # Датаг огноогоор эрэмбэлэх
    df = df.sort_values('LogDate')

    st.title("🏥 Миний Эрүүл Мэндийн Хяналт")

    # Хамгийн сүүлчийн (хамгийн шинэ огноотой) датаг авах
    latest = df.iloc[-1]

    # Үзүүлэлтүүдийг харуулах
    col1, col2, col3, col4 = st.columns(4)
    
    # Хүснэгтийн баганын нэр зөрөхөөс сэргийлж шалгах
    steps = latest['Steps'] if 'Steps' in latest else 0
    bmi = latest['BMI'] if 'BMI' in latest else 0
    bodyfat = latest['BodyFat'] if 'BodyFat' in latest else 0
    sugar = latest['BloodSugar'] if 'BloodSugar' in latest else 0

    col1.metric("Алхалт", f"{int(steps) if pd.notnull(steps) else 0}")
    col2.metric("BMI", f"{round(bmi, 2) if pd.notnull(bmi) else 0}")
    col3.metric("Өөх", f"{bodyfat if pd.notnull(bodyfat) else 0}%")
    col4.metric("Сахар", f"{sugar if pd.notnull(sugar) else 0}")

    st.divider()
    
    st.subheader("📈 Өөрчлөлтийн график")
    # Зөвхөн утгатай багануудыг график дээр харуулах
    available_metrics = [m for m in ['BMI', 'BloodSugar', 'BodyFat'] if m in df.columns]
    if available_metrics:
        st.line_chart(df.set_index('LogDate')[available_metrics])
    
    st.info(f"Сүүлчийн өгөгдөл: {latest['LogDate'].strftime('%Y-%m-%d')}")

except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")
