import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from scipy.optimize import minimize

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Farmacia Marina Cuántica", page_icon="🌊", layout="wide")
st.title("🌊 Farmacia Marina: Simulador Molecular Cuántico (VQE)")
st.write("Herramienta de biotecnología azul basada en **IBM Qiskit** para evaluar la estabilidad energética de compuestos bioactivos marinos mediante datos propios o simulaciones.")

with st.expander("ℹ️ Guía rápida para investigadores y empresas", expanded=False):
    st.markdown("""
    * **¿Qué hace esta herramienta?** Calcula el estado fundamental (mínima energía) de enlaces moleculares mediante el algoritmo híbrido **VQE** (*Variational Quantum Eigensolver*). Cuanto más negativa sea la energía (en Hartrees), más estable es el compuesto.
    * **3 Modos de uso (Menú izquierdo):** Puedes probar compuestos de referencia del Mediterráneo, introducir tus propios parámetros químicos manualmente o subir un archivo **CSV / Excel** para analizar múltiples moléculas en lote.
    """)

# --- FUNCIÓN DEL MOTOR CUÁNTICO VQE ---
def ejecutar_vqe_molecula(energia_base, interaccion_xx):
    hamiltoniano = SparsePauliOp.from_list([
        ("II", float(energia_base)),
        ("IZ", 0.39),
        ("ZI", -0.39),
        ("ZZ", -0.01),
        ("XX", float(interaccion_xx))
    ])
    theta_0, theta_1 = ParameterVector('theta', 2)
    qc = QuantumCircuit(2)
    qc.ry(theta_0, 0)
    qc.ry(theta_1, 1)
    qc.cx(0, 1)
    
    estimador = StatevectorEstimator()
    historial = []
    
    def calcular_energia(valores):
        trabajo = estimador.run([(qc, hamiltoniano, valores)])
        energia = float(next(iter(trabajo.result())).data.evs)
        historial.append(energia)
        return energia
        
    resultado = minimize(calcular_energia, [0.0, 0.0], method="COBYLA")
    return round(resultado.fun, 4), historial

# --- MENÚ LATERAL: MODO DE ENTRADA DE DATOS ---
st.sidebar.header("🧬 Fuente de Datos Moleculares")
modo_entrada = st.sidebar.radio(
    "Elige cómo introducir los datos:",
    (
        "1. Catálogo de Referencia (Mediterráneo)",
        "2. Control Numérico Manual",
        "3. Subir Archivo Propio (CSV / Excel)"
    )
)

# =========================================================
# MODO 1 Y MODO 2: ANÁLISIS INDIVIDUAL
# =========================================================
if modo_entrada != "3. Subir Archivo Propio (CSV / Excel)":
    if modo_entrada == "1. Catálogo de Referencia (Mediterráneo)":
        compuesto = st.sidebar.selectbox(
            "Selecciona un extracto marino:",
            (
                "Alcaloide de Microalga (Delta del Ebro)",
                "Péptido Antimicrobiano (Costa Daurada)",
                "Polifenol Antioxidante (Posidonia Mediterránea)"
            )
        )
        if "Alcaloide" in compuesto:
            energia_base, interaccion_xx = -1.05, 0.18
        elif "Péptido" in compuesto:
            energia_base, interaccion_xx = -1.15, 0.28
        else:
            energia_base, interaccion_xx = -0.95, 0.12
    else:
        st.sidebar.subheader("🎛️ Parámetros Químicos Manuales")
        compuesto = st.sidebar.text_input("Nombre de tu molécula:", "Compuesto_Lab_01")
        energia_base = st.sidebar.number_input("Energía Base del enlace (Hartrees):", min_value=-5.0, max_value=0.0, value=-1.10, step=0.05)
        interaccion_xx = st.sidebar.slider("Fuerza de Interacción Cuántica (XX):", min_value=0.01, max_value=1.00, value=0.22, step=0.01)

    st.subheader(f"🔬 Molécula seleccionada: {compuesto}")
    st.caption(f"Parámetros de entrada -> Energía Base: `{energia_base}` | Interacción Cuántica XX: `{interaccion_xx}`")

    if st.button("🚀 Ejecutar Simulación Molecular VQE"):
        with st.spinner("Optimizando ángulos cuánticos (theta) en IBM Qiskit..."):
            energia_min, historial = ejecutar_vqe_molecula(energia_base, interaccion_xx)
            
            col1, col2 = st.columns(2)
            col1.metric("Energía Mínima (Estabilidad)", f"{energia_min} Hartrees")
            col2.metric("Iteraciones del Optimizador", f"{len(historial)} pasos")
            
            if energia_min < -1.10:
                st.success("✅ **MOLÉCULA ALTAMENTE ESTABLE:** Candidata óptima para ensayos de laboratorio.")
            else:
                st.info("ℹ️ **ESTABILIDAD MODERADA:** Se recomienda ajustar la estructura química.")
                
            fig, ax = plt.subplots(figsize=(8, 3.5))
            ax.plot(historial, marker='o', color='#008080', linewidth=2)
            ax.set_title("Convergencia Cuántica VQE hacia el Estado Fundamental")
            ax.set_xlabel("Iteraciones")
            ax.set_ylabel("Energía (Hartrees)")
            ax.grid(True, linestyle='--', alpha=0.6)
            st.pyplot(fig)

# =========================================================
# MODO 3: SUBIDA DE ARCHIVO CSV O EXCEL EN LOTE
# =========================================================
else:
    st.subheader("📂 Análisis en Lote mediante Archivo (CSV o Excel)")
    st.write("Sube tu tabla de laboratorio con las columnas: `Compuesto`, `Energia_Base` y `Interaccion_XX`.")
    
    # Botón para descargar plantilla de ejemplo
    plantilla = pd.DataFrame({
        "Compuesto": ["Extracto_Alga_01", "Bioactivo_Esponja_02", "Enzima_Marina_03"],
        "Energia_Base": [-1.05, -1.25, -0.90],
        "Interaccion_XX": [0.18, 0.30, 0.15]
    })
    st.download_button(
        label="📥 Descargar plantilla CSV de ejemplo",
        data=plantilla.to_csv(index=False).encode('utf-8'),
        file_name="plantilla_moleculas_marinas.csv",
        mime="text/csv"
    )
    
    archivo_subido = st.file_uploader("Arrastra aquí tu archivo CSV o Excel (.xlsx)", type=["csv", "xlsx"])
    
    if archivo_subido is not None:
        if archivo_subido.name.endswith('.csv'):
            df = pd.read_csv(archivo_subido)
        else:
            df = pd.read_excel(archivo_subido)
            
        st.write("Vista previa de tus datos cargados:", df)
        
        if st.button("🚀 Analizar Todas las Moléculas con VQE"):
            resultados_lote = []
            barra = st.progress(0)
            total_filas = len(df)
            
            for idx, fila in df.iterrows():
                e_min, pasos = ejecutar_vqe_molecula(fila["Energia_Base"], fila["Interaccion_XX"])
                estado = "Alta Estabilidad" if e_min < -1.10 else "Estabilidad Moderada"
                resultados_lote.append({
                    "Compuesto": fila["Compuesto"],
                    "Energia_Minima_Hartrees": e_min,
                    "Pasos_Optimizacion": len(pasos),
                    "Diagnostico": estado
                })
                barra.progress((idx + 1) / total_filas)
                
            df_final = pd.DataFrame(resultados_lote).sort_values(by="Energia_Minima_Hartrees")
            st.success("✅ Análisis cuántico completado. Ranking ordenado de mayor a menor estabilidad:")
            st.dataframe(df_final, use_container_width=True)

# --- SECCIÓN DE FEEDBACK Y CONTACTO ---
st.divider()
st.subheader("💬 Valoración y Contacto Profesional")
col_f1, col_f2 = st.columns(2)
with col_f1:
    if st.button("👍 ¡Esta herramienta me ha resultado útil!"):
        st.toast("¡Muchas gracias por tu valoración! Seguimos innovando en Economía Azul.")
with col_f2:
       st.markdown("¿Quieres comentar el desarrollo o proponer una colaboración?")
       st.markdown("📩 **Correo directo:** [nhemesysgonzalez@gmail.com](mailto:nhemesysgonzalez@gmail.com) | 💬 **[Foro en GitHub](https://github.com/nhemesysgonzalez-stack/farmacia-marina-cuantica-vqe-/issues)**")
