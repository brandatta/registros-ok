import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Obtener credenciales de los secretos de Streamlit
def get_data():
    try:
        # Accede a las credenciales guardadas en los secretos
        mysql_secrets = st.secrets["mysql"]
        connection = mysql.connector.connect(
            host=mysql_secrets["host"],
            user=mysql_secrets["user"],
            password=mysql_secrets["password"],
            database=mysql_secrets["database"]
        )
        if connection.is_connected():
            query = "SELECT * FROM TU_TABLA LIMIT 10"  # Aquí reemplaza 'TU_TABLA' por el nombre de tu tabla
            df = pd.read_sql(query, connection)
            return df
    except Error as e:
        st.error(f"Error en la conexión a la base de datos: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()

# Función para mostrar la tabla estilizada
def display_table(df):
    if df is not None:
        # Mostrar los registros con un estilo personalizado
        for index, row in df.iterrows():
            st.write(f"### Registro {index + 1}")
            st.markdown(f"**Columna1**: {row['columna1']} - **Columna2**: {row['columna2']} - **Columna3**: {row['columna3']}")
            
            # Botón de confirmación "Sí"
            confirm_button = st.button(f"✔ Sí para {index + 1}", key=f"btn_{index}")

            if confirm_button:
                st.success(f"✔ Confirmado: Registro {index + 1}")
    else:
        st.write("No se pudo obtener la información.")

# Interfaz de Streamlit
st.title("Aplicación de Confirmación de Registros")
df = get_data()
display_table(df)
