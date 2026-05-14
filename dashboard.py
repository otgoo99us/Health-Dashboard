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
        df['LogDate'] = pd.to_datetime(df['LogDate'], errors='coerce')
        df = df.dropna(subset=['LogDate'])
    
    df = df.sort_values('LogDate')

    st.title("🏥 Миний Эрүүл Мэндийн Хяналт")

    # Хамгийн сүүлчийн бодит датаг авах
    latest = df.iloc[-1]

    # Үзүүлэлтүүдийг тоо руу хөрвүүлэх функц
    def clean_num(col_name):
        if col_name in latest:
            val = pd.to_numeric(latest[col_name], errors='coerce')
            return val if pd.notnull(val) else 0
        return 0

    # Дээд талын үндсэн 4 үзүүлэлт
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Алхалт", f"{int(clean_num('Steps'))}")
    m2.metric("BMI", f"{round(float(clean_num('BMI')), 2)}")
    m3.metric("Өөх", f"{clean_num('BodyFat')}%")
    m4.metric("Сахар", f"{clean_num('BloodSugar')}")

    # Нэмэлтээр Даралт ба Пульс харуулах (Хэрэв дата байвал)
    if 'SysBP' in latest or 'Pulse' in latest:
        st.write("### 💓 Бусад үзүүлэлтүүд")
        c1, c2, c3 = st.columns(3)
        c1.metric("Даралт", f"{int(clean_num('SysBP'))}/{int(clean_num('DiaBP'))}")
        c2.metric("Пульс", f"{int(clean_num('Pulse'))}")
        c3.metric("Бүсэлхий", f"{clean_num('Waist')} см")

    st.divider()
    
    st.subheader("📈 Өөрчлөлтийн график")
    # Графикт бүх тоон үзүүлэлтүүдийг сонгох боломж олгох
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if 'ID' in numeric_cols: numeric_cols.remove('ID')
    
    selected_metrics = st.multiselect("Графикт харах үзүүлэлтүүд:", numeric_cols, default=['BMI', 'BodyFat'])
    if selected_metrics:
        st.line_chart(df.set_index('LogDate')[selected_metrics])
    
    st.info(f"Сүүлчийн өгөгдөл шинэчлэгдсэн: {latest['LogDate'].strftime('%Y-%m-%d %H:%M')}")
    
    with st.expander("Бүх өгөгдлийг харах"):
        st.write(df)

except Exception as e:
    st.error(f"Алдаа гарлаа: {e}")
