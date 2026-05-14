import streamlit as st
import pandas as pd

st.set_page_config(page_title="Health Dashboard", layout="wide")

sheet_id = "1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

def load_data():
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip() # Баганын нэр цэвэрлэх
    return df

try:
    df = load_data()
    
    if 'LogDate' in df.columns:
        df['LogDate'] = pd.to_datetime(df['LogDate'], errors='coerce')
        # Зөвхөн огноотой бөгөөд дататай мөрүүдийг авна
        df = df.dropna(subset=['LogDate'])
        # Бүх утга нь 0 эсвэл хоосон мөрүүдийг хасна
        df = df[df.any(axis=1)] 
    
    df = df.sort_values('LogDate')

    st.title("🏥 Миний Эрүүл Мэндийн Хяналт")

    # Хамгийн сүүлчийн бодит датаг авах
    latest = df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)
    
    # Датаг аюулгүй унших функц
    def get_val(col_name, default=0):
        val = latest[col_name] if col_name in latest else default
        return val if pd.notnull(val) else default

    col1.metric("Алхалт", f"{int(get_val('Steps'))}")
    col2.metric("BMI", f"{round(get_val('BMI'), 2)}")
    col3.metric("Өөх", f"{get_val('BodyFat')}%")
    col4.metric("Сахар", f"{get_val('BloodSugar')}")

    st.divider()
    
    st.subheader("📈 Өөрчлөлтийн график")
    metrics = [m for m in ['BMI', 'BloodSugar', 'BodyFat'] if m in df.columns]
    if metrics:
        st.line_chart(df.set_index('LogDate')[metrics])
    
    st.info(f"Сүүлчийн өгөгдөл: {latest['LogDate'].strftime('%Y-%m-%d')}")
    
    # Дата шалгах хэсэг (Зөвхөн танд харагдана)
    with st.expander("Хүснэгтийн сүүлийн 5 мөрийг харах"):
        st.write(df.tail())

except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")    
