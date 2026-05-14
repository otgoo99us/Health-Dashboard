import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Health Dashboard", layout="wide")

# Google Sheets линк - Кэшээс зайлсхийхийн тулд цаг хугацааны тамга нэмэв
sheet_id = "1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&ts={int(time.time())}"

def load_data():
    # pandas-аар шууд унших (Streamlit-ийн кэш ашиглахгүй)
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    if 'LogDate' in df.columns:
        # Огноог хөрвүүлээд, алдаатайг нь хасах
        df['LogDate'] = pd.to_datetime(df['LogDate'], errors='coerce')
        df = df.dropna(subset=['LogDate'])
        # Огноогоор өсөх дарааллаар эрэмбэлэх
        df = df.sort_values('LogDate')
    
    st.title("🏥 Миний Эрүүл Мэндийн Хяналт")

    # Хэрэв дата байвал хамгийн сүүлийн мөрийг авах
    if not df.empty:
        latest = df.iloc[-1]

        def clean_num(col_name):
            if col_name in latest:
                val = pd.to_numeric(latest[col_name], errors='coerce')
                return val if pd.notnull(val) else 0
            return 0

        # Үндсэн үзүүлэлтүүд
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Алхалт", f"{int(clean_num('Steps'))}")
        m2.metric("BMI", f"{round(float(clean_num('BMI')), 2)}")
        m3.metric("Өөх", f"{clean_num('BodyFat')}%")
        m4.metric("Сахар", f"{clean_num('BloodSugar')}")

        st.divider()
        
        st.subheader("📈 Өөрчлөлтийн график")
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if 'ID' in numeric_cols: numeric_cols.remove('ID')
        
        selected_metrics = st.multiselect("Графикт харах үзүүлэлтүүд:", numeric_cols, default=['BMI', 'Steps'])
        if selected_metrics:
            st.line_chart(df.set_index('LogDate')[selected_metrics])
        
        # Хамгийн сүүлийн датаны огноог тод харуулах
        st.success(f"Сүүлчийн өгөгдөл шинэчлэгдсэн: {latest['LogDate'].strftime('%Y-%m-%d %H:%M')}")
        
        with st.expander("Бүх өгөгдлийг харах"):
            # Хамгийн шинэ датаг дээр нь харуулахын тулд буурах дарааллаар харуулна
            st.write(df.sort_values('LogDate', ascending=False))
    else:
        st.warning("Хүснэгтээс өгөгдөл олдсонгүй.")

except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")
