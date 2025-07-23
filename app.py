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

# ---------- ESTILO SCROLL HORIZONTAL ----------
st.markdown("""
<style>
.registro-scroll {
    display: flex;
    overflow-x: auto;
    padding: 8px 0;
    border-bottom: 1px solid #ddd;
    font-family: monospace;
    font-size: 14px;
}
.registro-scroll div {
    flex: 0 0 auto;
    padding-right: 16px;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

# ---------- MOSTRAR CADA REGISTRO EN UNA LÍNEA SCROLLEABLE ----------
for idx, row in df.iterrows():
    with st.container():
        cols = st.columns([10, 1])  # datos | acción

        # Sección de datos scrolleable
        with cols[0]:
            st.markdown(
                "<div class='registro-scroll'>" +
                "".join([f"<div><b>{col}:</b> {row[col]}</div>" for col in df.columns]) +
                "</div>",
                unsafe_allow_html=True
            )

        # Acción: botón o tick
        with cols[1]:
            key_flag = f"flag_{idx}"
            key_btn = f"btn_{idx}"

            if st.session_state.get(key_flag, False):
                st.markdown("<span style='font-size:2rem; color:green;'>✔️</span>", unsafe_allow_html=True)
            else:
                if st.button("Sí", key=key_btn):
                    st.session_state[key_flag] = True
                    st.experimental_rerun()
