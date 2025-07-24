import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta

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

# ---------- ACTUALIZAR PROCESADO ----------
def actualizar_procesado(id_valor, estado):
    conn = get_connection()
    cursor = conn.cursor()
    query = "UPDATE inventario SET procesado = %s, proc_ts = NOW() WHERE id = %s"
    cursor.execute(query, (estado, id_valor))
    conn.commit()
    cursor.close()
    conn.close()

# ---------- CARGA DE DATOS ----------
@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM inventario LIMIT 10", conn)
    total = pd.read_sql("SELECT COUNT(*) as total FROM inventario", conn)
    conn.close()
    return df, int(total["total"].iloc[0])

df, total_registros = load_data()

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

# ---------- SEPARAR REGISTROS ----------
df_pendientes = df[df["procesado"] == 0]
df_procesados = df[df["procesado"] == 1]

tab1, tab2 = st.tabs([
    f"🔄 Pendientes ({len(df_pendientes)})",
    f"✅ Procesados ({len(df_procesados)})"
])

with tab1:
    st.subheader("Registros no marcados como 'Sí'")
    for _, row in df_pendientes.iterrows():
        with st.container():
            cols = st.columns([10, 1, 1, 0.5])
            with cols[0]:
                st.markdown(
                    "<div class='registro-scroll'>" +
                    "".join([f"<div><b>{col}:</b> {row[col]}</div>" for col in df.columns]) +
                    "</div>", unsafe_allow_html=True
                )
            key_flag = f"flag_{row['id']}"
            if key_flag not in st.session_state:
                st.session_state[key_flag] = False

            with cols[1]:
                if st.button("Sí", key=f"btn_si_{row['id']}"):
                    actualizar_procesado(row["id"], 1)
                    st.session_state[key_flag] = True
                    if "hora_inicio" not in st.session_state:
                        st.session_state["hora_inicio"] = datetime.now()
                    st.rerun()

            with cols[2]:
                if st.button("No", key=f"btn_no_{row['id']}"):
                    actualizar_procesado(row["id"], 0)
                    st.session_state[key_flag] = False
                    st.rerun()

            with cols[3]:
                if st.session_state[key_flag]:
                    st.markdown("<span style='font-size:1.5rem; color:green;'>✓</span>", unsafe_allow_html=True)

with tab2:
    st.subheader("Registros ya marcados como 'Sí'")
    for _, row in df_procesados.iterrows():
        with st.container():
            cols = st.columns([10, 1, 1, 0.5])
            with cols[0]:
                st.markdown(
                    "<div class='registro-scroll'>" +
                    "".join([f"<div><b>{col}:</b> {row[col]}</div>" for col in df.columns]) +
                    "</div>", unsafe_allow_html=True
                )
            key_flag = f"flag_{row['id']}"
            if key_flag not in st.session_state:
                st.session_state[key_flag] = True

            with cols[1]:
                st.button("Sí", key=f"btn_si_{row['id']}")

            with cols[2]:
                if st.button("No", key=f"btn_no_{row['id']}"):
                    actualizar_procesado(row["id"], 0)
                    st.session_state[key_flag] = False
                    st.rerun()

            with cols[3]:
                st.markdown("<span style='font-size:1.5rem; color:green;'>✓</span>", unsafe_allow_html=True)

# ---------- RESUMEN GENERAL ----------
st.markdown("---")
subtotal = len(df_procesados)
porcentaje = round((subtotal / total_registros) * 100, 1) if total_registros > 0 else 0.0

st.markdown("### 📊 Estado general del inventario")
col1, col2 = st.columns([1, 3])

with col1:
    st.metric(label="✅ Porcentaje marcado como 'Sí'", value=f"{porcentaje} %")

with col2:
    st.progress(int(porcentaje))

st.success(f"🔢 Subtotal de registros marcados como 'Sí': **{subtotal}** de {total_registros}")

# ---------- INFORMACIÓN DE TIEMPOS ----------
st.markdown("---")
st.markdown("### ⏱️ Estimación temporal")

if "hora_inicio" in st.session_state:
    hora_inicio = st.session_state["hora_inicio"]
    ahora = datetime.now()
    tiempo_transcurrido = ahora - hora_inicio
    minutos = tiempo_transcurrido.total_seconds() / 60

    if subtotal > 0:
        estimado_total_min = (minutos / subtotal) * total_registros
        hora_fin_estimada = hora_inicio + timedelta(minutes=estimado_total_min)

        st.info(f"🕒 Hora de inicio: **{hora_inicio.strftime('%H:%M:%S')}**")
        st.info(f"⏳ Tiempo transcurrido: **{str(tiempo_transcurrido).split('.')[0]}**")
        st.info(f"📅 Estimación de finalización: **{hora_fin_estimada.strftime('%H:%M:%S')}**")
    else:
        st.warning("Aún no se marcó ningún registro como 'Sí', no se puede calcular estimación.")
else:
    st.info("La hora de inicio se registrará al marcar el primer registro como 'Sí'.")

# ---------- BOTÓN DE REFRESCO MANUAL ----------
st.markdown("#### 🔄")
if st.button("Actualizar estimaciones"):
    st.rerun()
