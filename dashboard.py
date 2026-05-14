import streamlit as st
import pandas as pd
import time

# Хуудасны тохиргоо
st.set_page_config(page_title="Health Dashboard", layout="wide")

# Google Sheets CSV линк - Кэшээс бүрэн зайлсхийх "timestamp" нэмэв
sheet_id = "1euwmWQ45bwu-EOj1anYjaTXEI5yY7kyM3qWtlCi5fdc"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&cache_id={int(time.time())}"

@st.cache_data(ttl=60) # 1 минут тутамд датаг шинэчлэх
def load_data(url_link):
    df = pd.read_csv(url_link)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data(url)
    
    # Огноог хөрвүүлэх ба цэвэрлэх
    if 'LogDate' in df.columns:
        df['LogDate'] = pd.to_datetime(df['LogDate'], errors='coerce')
        df = df.dropna(subset=['LogDate'])
        # Огноогоор өсөх дарааллаар эрэмбэлэх (графикт зориулж)
        df = df.sort_values('LogDate')
    
    st.title("🏥 Миний Эрүүл Мэндийн Хяналт")

    if not df.empty:
        # Хамгийн сүүлчийн (хамгийн шинэ) мөрийг авах
        latest = df.iloc[-1]

        def get_val(col):
            if col in latest:
                v = pd.to_numeric(latest[col], errors='coerce')
                return v if pd.notnull(v) else 0
            return 0

        # Дээд талын үзүүлэлтүүд
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Алхалт", f"{int(get_val('Steps'))}")
        col2.metric("BMI", f"{round(float(get_val('BMI')), 2)}")
        col3.metric("Өөх", f"{get_val('BodyFat')}%")
        col4.metric("Сахар", f"{get_val('BloodSugar')}")

        st.divider()
        
        # Графикийн хэсэг
        st.subheader("📈 Өөрчлөлтийн график")
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if 'ID' in num_cols: num_cols.remove('ID')
        
        selected = st.multiselect("Харах үзүүлэлтүүд:", num_cols, default=['BMI', 'Steps'])
        if selected:
            st.line_chart(df.set_index('LogDate')[selected])
        
        # Шинэчлэгдсэн огноог харуулах
        st.success(f"Сүүлчийн өгөгдөл шинэчлэгдсэн: {latest['LogDate'].strftime('%Y-%m-%d %H:%M')}")
        
        with st.expander("Бүх өгөгдлийг харах"):
            # Хүснэгтийг хамгийн шинэ дата нь дээрээ байхаар харуулна
            st.write(df.sort_values('LogDate', ascending=False))
    else:
        st.error("Google Sheets-ээс өгөгдөл уншиж чадсангүй.")

except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")
