import streamlit as st
import pandas as pd
import mysql.connector

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="Revisión de inventario", layout="wide")
st.title("✅ Revisión de inventario")

# ---------- CONEXIÓN A MySQL ----------
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["app_marco_new"]["host"],
        user=st.secrets["app_marco_new"]["user"],
        password=st.secrets["app_marco_new"]["password"],
        database=st.secrets["app_marco_new"]["database"],
        port=3306,
    )

# ---------- CARGA DE DATOS ----------
@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM inventario LIMIT 10", conn)
    conn.close()
    return df

df = load_data()

st.subheader("Primeros 10 registros")

# ---------- MOSTRAR REGISTROS COMO FILAS HORIZONTALES ----------
# Mostrar cabecera
columnas = list(df.columns) + ["Acción"]
st.markdown(
    "<style>th, td { padding: 6px 12px; }</style>",
    unsafe_allow_html=True
)
st.markdown(
    "<div style='font-weight:bold; display:flex; gap:20px; margin-bottom:10px;'>"
    + "".join([f"<div style='width:150px'>{col}</div>" for col in columnas])
    + "</div>",
    unsafe_allow_html=True,
)

# Mostrar filas
for idx, row in df.iterrows():
    cols = st.columns([1] * len(columnas))  # una columna por campo

    # Mostrar datos
    for i, col in enumerate(df.columns):
        cols[i].write(str(row[col]))

    # Acción: botón o tilde
    key_flag = f"flag_{idx}"
    key_btn = f"btn_{idx}"

    with cols[-1]:
        if st.session_state.get(key_flag, False):
            st.markdown("✔️", unsafe_allow_html=True)
        else:
            if st.button("Sí", key=key_btn):
                st.session_state[key_flag] = True
                st.experimental_rerun()
