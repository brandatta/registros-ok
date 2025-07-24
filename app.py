import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime

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

# ---------- ACTUALIZAR REGISTRO ----------
def marcar_como_procesado(id_valor):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE inventario SET procesado = 1, proc_ts = NOW() WHERE id = %s"
    cursor.execute(query, (id_valor,))
    conn.commit()
    cursor.close()
    conn.close()

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

# ---------- MOSTRAR CADA REGISTRO ----------
for idx, row in df.iterrows():
    with st.container():
        cols = st.columns([10, 2])  # datos | acción

        with cols[0]:
            st.markdown(
                "<div class='registro-scroll'>" +
                "".join([f"<div><b>{col}:</b> {row[col]}</div>" for col in df.columns]) +
                "</div>",
                unsafe_allow_html=True
            )

        with cols[1]:
            key_flag = f"flag_{row['id']}"  # usamos el ID real como clave

            col_btn, col_tick = st.columns([1, 0.3])

            with col_btn:
                if key_flag not in st.session_state:
                    st.session_state[key_flag] = row['procesado'] == 1

                if st.button("Sí", key=f"btn_{row['id']}"):
                    marcar_como_procesado(row["id"])
                    st.session_state[key_flag] = True
                    st.rerun()

            with col_tick:
                if st.session_state[key_flag]:
                    st.markdown("<span style='font-size:1.5rem; color:green;'>✓</span>", unsafe_allow_html=True)
