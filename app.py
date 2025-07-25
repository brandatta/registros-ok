import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import pytz

# ---------- CONFIGURACIÓN ----------
st.set_page_config(page_title="Revisión de inventario", layout="wide")
st.title("✅ Revisión de inventario")

# ---------- ZONA HORARIA ----------
BA = pytz.timezone("America/Argentina/Buenos_Aires")

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

# ---------- ESTADO ----------
if "hora_inicio" not in st.session_state:
    st.session_state.hora_inicio = None
if "ultimo_tick" not in st.session_state:
    st.session_state.ultimo_tick = None
if "mensaje_exito" not in st.session_state:
    st.session_state.mensaje_exito = None
if "cambios" not in st.session_state:
    st.session_state.cambios = False
if "refrescar_manual" not in st.session_state:
    st.session_state.refrescar_manual = False

# ---------- CARGA DE DATOS ----------
@st.cache_data(ttl=1)
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM inventario ORDER BY id", conn)
    conn.close()
    return df

# ---------- BOTÓN DE ACTUALIZACIÓN MANUAL ----------
if st.button("🔄 Actualizar registros manualmente"):
    st.session_state.refrescar_manual = True

if st.session_state.cambios or st.session_state.refrescar_manual:
    st.cache_data.clear()
    st.session_state.cambios = False
    st.session_state.refrescar_manual = False

df = load_data()
df_pendientes = df[df["procesado"] == 0].head(10)
df_procesados = df[df["procesado"] == 1].head(10)
total_registros = len(df_pendientes) + len(df_procesados)

# ---------- INTERFAZ ----------
tabs = st.tabs([
    f"🔄 Pendientes ({len(df_pendientes)})",
    f"✅ Procesados ({len(df_procesados)})"
])

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

if st.session_state.mensaje_exito:
    st.success(st.session_state.mensaje_exito)
    st.session_state.mensaje_exito = None

# ---------- TAB 1: Pendientes ----------
with tabs[0]:
    st.subheader("Registros no marcados como 'Sí'")
    for _, row in df_pendientes.iterrows():
        with st.container():
            cols = st.columns([10, 1, 0.5])
            with cols[0]:
                st.markdown(
                    "<div class='registro-scroll'>" +
                    "".join([f"<div><b>{col}:</b> {row[col]}</div>" for col in df.columns]) +
                    "</div>", unsafe_allow_html=True
                )
            with cols[1]:
                if st.button("Sí", key=f"btn_si_{row['id']}"):
                    actualizar_procesado(row["id"], 1)
                    st.session_state.ultimo_tick = row["id"]
                    st.session_state.mensaje_exito = f"✅ Registro {row['id']} marcado como 'Sí'."
                    if not st.session_state.hora_inicio:
                        st.session_state.hora_inicio = datetime.now(BA)
                    st.session_state.cambios = True
            with cols[2]:
                if st.session_state.ultimo_tick == row["id"]:
                    st.markdown("<span style='font-size:1.5rem; color:green;'>✓</span>", unsafe_allow_html=True)

# ---------- TAB 2: Procesados ----------
with tabs[1]:
    st.subheader("Registros ya marcados como 'Sí'")
    for _, row in df_procesados.iterrows():
        with st.container():
            cols = st.columns([10, 1])
            with cols[0]:
                st.markdown(
                    "<div class='registro-scroll'>" +
                    "".join([f"<div><b>{col}:</b> {row[col]}</div>" for col in df.columns]) +
                    "</div>", unsafe_allow_html=True
                )
            with cols[1]:
                if st.button("No", key=f"btn_no_{row['id']}"):
                    actualizar_procesado(row["id"], 0)
                    st.session_state.mensaje_exito = f"↩️ Registro {row['id']} revertido a pendiente."
                    st.session_state.cambios = True

# ---------- MÉTRICAS ----------
st.markdown("---")
subtotal = len(df_procesados)
porcentaje = round((subtotal / total_registros) * 100, 1) if total_registros else 0.0

col1, col2 = st.columns([1, 3])
with col1:
    st.metric("✅ Porcentaje marcado como 'Sí'", f"{porcentaje} %")
with col2:
    st.progress(int(porcentaje))

st.success(f"🔢 Subtotal de registros visibles marcados como 'Sí': **{subtotal}** de {total_registros}**")

# ---------- ESTIMACIÓN TEMPORAL ----------
st.markdown("---")
if st.button("🔁 Actualizar estimación temporal"):
    st.session_state.refresh_estimacion = True

st.markdown("### ⏱️ Estimación temporal")
if st.session_state.hora_inicio:
    ahora = datetime.now(BA)
    transcurrido = ahora - st.session_state.hora_inicio
    minutos = transcurrido.total_seconds() / 60
    if subtotal > 0:
        estimado_total = (minutos / subtotal) * total_registros
        fin_est = st.session_state.hora_inicio + timedelta(minutes=estimado_total)
        st.info(f"🕒 Hora de inicio: **{st.session_state.hora_inicio.strftime('%H:%M:%S')}**")
        st.info(f"⏳ Tiempo transcurrido: **{str(transcurrido).split('.')[0]}**")
        st.info(f"📅 Estimación de finalización: **{fin_est.strftime('%H:%M:%S')}**")
    else:
        st.warning("Aún no se marcó ningún registro como 'Sí'.")
else:
    st.info("La hora de inicio se registrará al marcar el primer registro como 'Sí'.")
