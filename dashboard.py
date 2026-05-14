import streamlit as st
import pandas as pd

st.set_page_config(page_title="Health Dashboard", layout="wide")

sheet_id = "1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

def load_data():
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    if 'LogDate' in df.columns:
        # Огноог хөрвүүлэх
        df['LogDate'] = pd.to_datetime(df['LogDate'], errors='coerce')
        # Зөвхөн огноо нь зөв уншигдсан мөрүүдийг үлдээх
        df = df[df['LogDate'].notnull()]
    
    # Датаг огноогоор эрэмбэлэх
    df = df.sort_values('LogDate')

    st.title("🏥 Миний Эрүүл Мэндийн Хяналт")

    # Хамгийн сүүлчийн бодит датаг авах
    latest = df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    
    # Датаг аюулгүй унших функц (NaN утгыг 0 болгоно)
    def get_val(col_name):
        if col_name in latest:
            val = latest[col_name]
            return val if pd.notnull(val) else 0
        return 0

    col1.metric("Алхалт", f"{int(get_val('Steps'))}")
    col2.metric("BMI", f"{round(float(get_val('BMI')), 2)}")
    col3.metric("Өөх", f"{get_val('BodyFat')}%")
    col4.metric("Сахар", f"{get_val('BloodSugar')}")

    st.divider()
    
    st.subheader("📈 Өөрчлөлтийн график")
    # Графикт орох үзүүлэлтүүд
    metrics = [m for m in ['BMI', 'BloodSugar', 'BodyFat'] if m in df.columns]
    if metrics:
        st.line_chart(df.set_index('LogDate')[metrics])
    
    st.info(f"Сүүлчийн өгөгдөл: {latest['LogDate'].strftime('%Y-%m-%d')}")
    
    # Хүснэгтийг бүтнээр нь харах (Датагаа шалгахад тусална)
    with st.expander("Бүх өгөгдлийг харах"):
        st.write(df)

except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")
