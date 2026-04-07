import streamlit as st
import pandas as pd
import plotly.express as px
from backend import simular_prestamo

# Configuramos primero la página
st.set_page_config(page_title="Simulador Financiero", page_icon="🏦", layout="wide")

# Marcamos el estilo
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilo para las tarjetas de métricas */
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #2e77d0;
        text-align: center;
        margin-bottom: 20px;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px); /* Efecto de elevación al pasar el ratón */
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #1f2937;
        margin-top: 5px;
    }
    .metric-label {
        font-size: 14px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# Formateamos los números
def formato_euro(numero):
    return f"{numero:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")

# Configuramos el sidebar que es la entrada de datos
with st.sidebar:
    st.header("⚙️ Configuración del Préstamo")
    capital = st.number_input("Capital (€)", min_value=100000, max_value=200000, value=150000, step=5000)
    anios = st.slider("Plazo (años)", min_value=1, max_value=30, value=25)
    frecuencia = st.selectbox("Frecuencia de pago", ["mensual", "trimestral", "semestral", "anual"])
    
    st.divider()
    
    st.header("📈 Condiciones de Mercado")
    euribor_porcentaje = st.number_input("Euribor actual (%)", value=3.5, step=0.1)
    tipo_interes = st.radio("Tipo de interés", ["fijo", "variable"])
    # Bonificación interactiva y restrictiva
    aplicar_bono = st.checkbox("¿Aplicar bonificación por productos?")
    
    if aplicar_bono:
        # Si marca la casilla, puede elegir entre 0,10 y 0,25
        bonificacion_porcentaje = st.number_input(
            "Porcentaje de bonificación (%)", 
            min_value=0.10, 
            max_value=0.25, 
            value=0.10, 
            step=0.01,
            help="Según las condiciones, debe estar entre el 0,10% y el 0,25%"
        )
    else:
        # Si no contrata productos, el descuento es nulo
        bonificacion_porcentaje = 0.0

# Llamamos a backend para que nos haga los calculos
euribor_decimal = euribor_porcentaje / 100
bonificacion_decimal = bonificacion_porcentaje / 100

# Hacemos que se actualice cada vez que se cambie cualquier valor
resultados = simular_prestamo(
    capital=capital,
    anios=anios,
    frecuencia=frecuencia,
    euribor_anual=euribor_decimal,
    tipo_interes=tipo_interes,
    bonificacion=bonificacion_decimal
)

# Mostramos los datos
cuota = resultados["cuota"]
tin = resultados["tin_anual"] * 100
tae = resultados["tae"] * 100
df = resultados["cuadro_amortizacion"]

# Situamos los resultados en la interfaz
st.title("🏦 Simulador Financiero - Sistema Francés")
st.markdown("Análisis y valoración de la rentabilidad y coste efectivo de la operación.")
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Cuota {frecuencia.capitalize()}</div>
        <div class="metric-value">{formato_euro(cuota)} €</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Tipo Nominal (TIN)</div>
        <div class="metric-value">{formato_euro(tin)} %</div>
    </div>""", unsafe_allow_html=True)

with col3:
    # En verde la TAE
    st.markdown(f"""<div class="metric-card" style="border-left-color: #10b981;">
        <div class="metric-label">TAE (Coste Efectivo)</div>
        <div class="metric-value">{formato_euro(tae)} %</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# Creamos la sección de gráfico y tabla
tab1, tab2 = st.tabs(["📉 Gráfico de Evolución", "📋 Cuadro de Amortización"])

with tab1:
    st.subheader("Evolución de Intereses vs Amortización de Capital")
    
    # Creamos el gráfico profesional con Plotly
    fig = px.line(df, x="Periodo", y=["Interés", "Amortización"], 
                  title="Cruce de líneas del Sistema Francés",
                  labels={"value": "Euros (€)", "variable": "Concepto"},
                  color_discrete_map={"Interés": "#ef4444", "Amortización": "#3b82f6"}) # Rojo y Azul
    
    # Ocultamos el título dentro del gráfico para que quede más limpio
    fig.update_layout(title_text='', margin=dict(t=10, b=10))
    
    # Streamlit muestra el gráfico
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Cuadro de Amortización Detallado")
    st.dataframe(df, height=400, use_container_width=True)