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

# ---------- MOSTRAR TABLA MANUAL ----------
st.subheader("Primeros 10 registros")

# Estilo CSS para tabla
st.markdown("""
    <style>
    .registro {
        display: flex;
        border-bottom: 1px solid #ccc;
        padding: 6px 0;
        align-items: center;
        font-size: 14px;
    }
    .celda {
        width: 150px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .cabecera {
        font-weight: bold;
        border-bottom: 2px solid black;
    }
    </style>
""", unsafe_allow_html=True)

# Mostrar cabecera
st.markdown("<div class='registro cabecera'>" +
    "".join([f"<div class='celda'>{col}</div>" for col in df.columns]) +
    "<div class='celda'>Acción</div></div>", unsafe_allow_html=True)

# Mostrar registros
for idx, row in df.iterrows():
    cols = st.columns(len(df.columns) + 1)  # columnas + acción

    # Mostrar celdas
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
