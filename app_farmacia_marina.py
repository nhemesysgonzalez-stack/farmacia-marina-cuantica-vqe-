import streamlit as st
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from scipy.optimize import minimize

# --- CARA A: DISEÑO DE LA PANTALLA WEB ---
st.set_page_config(page_title="Farmacia Marina Cuántica", page_icon="🌊")
st.title("🌊 Farmacia Marina: Simulador Molecular VQE")
st.write("Prototipo de biotecnología azul basado en IBM Qiskit para analizar la estabilidad energética de compuestos bioactivos del Mediterráneo y el Delta del Ebro.")

with st.expander("ℹ️ ¿Cómo funciona este simulador cuántico?", expanded=True):
    st.markdown("""
    * **Objetivo:** Evaluar si una molécula natural extraída de microalgas o bacterias marinas es energéticamente estable para desarrollarla como antibiótico o activo regenerador.
    * **Algoritmo VQE:** Combina un circuito cuántico parametrizado (**Ansatz**) con un optimizador clásico para encontrar el estado fundamental (mínima energía) de la molécula.
    """)

# Selector de compuesto marino en la barra lateral
st.sidebar.header("🧬 Selección de Bioactivo Marino")
compuesto = st.sidebar.selectbox(
    "Elige el extracto a analizar:",
    (
        "Alcaloide de Microalga (Delta del Ebro)",
        "Péptido Antimicrobiano (Costa Daurada)",
        "Polifenol Antioxidante (Posidonia Mediterránea)"
    )
)

# Ajustamos ligeramente el enlace cuántico según el compuesto elegido
if "Alcaloide" in compuesto:
    interaccion_xx = 0.18
    energia_base = -1.05
elif "Péptido" in compuesto:
    interaccion_xx = 0.28
    energia_base = -1.15
else:
    interaccion_xx = 0.12
    energia_base = -0.95

if st.button("🚀 Ejecutar Simulación Molecular VQE"):
    with st.spinner("Optimizando ángulos cuánticos (theta) en el circuito..."):
        
        # --- CARA B: MOTOR CUÁNTICO VQE (QISKIT) ---
        hamiltoniano = SparsePauliOp.from_list([
            ("II", energia_base),
            ("IZ", 0.39),
            ("ZI", -0.39),
            ("ZZ", -0.01),
            ("XX", interaccion_xx)
        ])
        
        theta_0, theta_1 = ParameterVector('theta', 2)
        qc = QuantumCircuit(2)
        qc.ry(theta_0, 0)
        qc.ry(theta_1, 1)
        qc.cx(0, 1)
        
        estimador = StatevectorEstimator()
        historial_energia = []
        
        def calcular_energia(valores):
            trabajo = estimador.run([(qc, hamiltoniano, valores)])
            energia = float(next(iter(trabajo.result())).data.evs)
            historial_energia.append(energia)
            return energia
            
        resultado = minimize(calcular_energia, [0.0, 0.0], method="COBYLA")
        energia_minima = round(resultado.fun, 4)
        
        # --- RESULTADOS Y GRÁFICA EN PANTALLA ---
        st.subheader(f"🔬 Análisis de Estabilidad: {compuesto}")
        
        col1, col2 = st.columns(2)
        col1.metric("Energía Mínima (Estado Fundamental)", f"{energia_minima} Hartrees")
        col2.metric("Iteraciones del Optimizador", f"{len(historial_energia)} pasos")
        
        if energia_minima < -1.10:
            st.success("✅ **MOLÉCULA ALTAMENTE ESTABLE:** Candidata óptima para ensayos de laboratorio biotecnológico.")
        else:
            st.info("ℹ️ **ESTABILIDAD MODERADA:** Se recomienda optimizar la estructura química antes de sintetizar.")
            
        # Dibujo de la gráfica de convergencia VQE
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(historial_energia, marker='o', color='#008080', linewidth=2)
        ax.set_title("Convergencia Cuántica VQE hacia la Estabilidad Molecular")
        ax.set_xlabel("Iteraciones del Optimizador")
        ax.set_ylabel("Energía (Hartrees)")
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)
