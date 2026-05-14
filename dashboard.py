import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Health Dashboard", layout="wide")

# Кэшийг бүрэн цэвэрлэх
st.cache_data.clear()

sheet_id = "1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc"
# CSV линк дээр санамсаргүй тоо нэмж кэшээс бүрэн зайлсхийх
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&update={int(time.time())}"

def load_data():
    return pd.read_csv(url)

try:
    df = load_data()
    df.columns = df.columns.str.strip()
    
    if 'LogDate' in df.columns:
        df['LogDate'] = pd.to_datetime(df['LogDate'], errors='coerce')
        df = df.dropna(subset=['LogDate'])
        df = df.sort_values('LogDate')

    st.title("🏥 Миний Эрүүл Мэндийн Хяналт")

    if not df.empty:
        latest = df.iloc[-1]
        
        # Үзүүлэлтүүд
        m1, m2, m3, m4 = st.columns(4)
        def clean(c): return pd.to_numeric(latest[c], errors='coerce') if c in latest else 0
        
        m1.metric("Алхалт", f"{int(clean('Steps'))}")
        m2.metric("BMI", f"{round(float(clean('BMI')), 2)}")
        m3.metric("Өөх", f"{clean('BodyFat')}%")
        m4.metric("Сахар", f"{clean('BloodSugar')}")

        st.divider()
        st.subheader("📈 Өөрчлөлтийн график")
        st.line_chart(df.set_index('LogDate')[['BMI', 'Steps']])
        
        # Шинэчлэгдсэн огноо
        st.success(f"Хамгийн сүүлийн өгөгдөл: {latest['LogDate'].strftime('%Y-%m-%d %H:%M')}")
        
        with st.expander("Бүх өгөгдөл харах"):
            st.write(df.sort_values('LogDate', ascending=False))

except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")
