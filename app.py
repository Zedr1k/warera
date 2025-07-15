
import streamlit as st
import importlib.util

# Cargar módulo wera_modular
spec = importlib.util.spec_from_file_location("wera", "wera_extendido_v2.py")
wera = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wera)

st.set_page_config(page_title="Calculadora de Builds", layout="wide")
st.title("Simulador de Build Óptima")

# --- Parámetros globales ---
st.sidebar.header("Parámetros globales")
MAX_LEVEL = st.sidebar.slider("Nivel del jugador", 1, 30, 12)
FOOD_HEALTH = st.sidebar.number_input("Vida por comida", value=20.0)
COSTO_COMIDA = st.sidebar.number_input("Costo por comida", value=2.2)
BATTLE_DURATION = st.sidebar.slider("Duración de la batalla (horas)", 1, 24, 7)
COSTO_BALAS_GRANDES = st.sidebar.number_input("Costo balas grandes", value=2.11)
COSTO_BALAS_CHICAS = st.sidebar.number_input("Costo balas chicas", value=0.56)

# --- Equipamiento ---
st.sidebar.header("Stats del Equipamiento")
equip = {
    "arma_daño": st.sidebar.number_input("Arma - Daño", value=100),
    "arma_critico": st.sidebar.number_input("Arma - Crítico", value=15),
    "casco_crit_damage": st.sidebar.number_input("Casco - Crit Damage", value=10),
    "chaleco_armor": st.sidebar.number_input("Chaleco - Armor", value=15),
    "pant_armor": st.sidebar.number_input("Pantalón - Armor", value=10),
    "botas_dodge": st.sidebar.number_input("Botas - Dodge", value=15),
    "guantes_acc": st.sidebar.number_input("Guantes - Precisión", value=20)
}

# Construir STATS según equipamiento
STATS = wera.build_stats_with_equipment(equip)
STAT_KEYS = list(STATS.keys())


st.subheader("Buscar Mejor Build Automáticamente")
if st.button("Buscar build óptima"):
    best = wera.find_best_distribution(MAX_LEVEL, STATS, FOOD_HEALTH, BATTLE_DURATION)
    if best:
        levels_distribution, stats, score = best
        score, comida_usada, ataques_totales = wera.evaluate_build(stats, FOOD_HEALTH, BATTLE_DURATION)
        costo_comida = comida_usada * COSTO_COMIDA
        costo_balas_grandes = ataques_totales * COSTO_BALAS_GRANDES
        costo_balas_chicas = ataques_totales * COSTO_BALAS_CHICAS

        st.success("Mejor build encontrada:")
        for stat, lvl in zip(STAT_KEYS, levels_distribution):
            st.write(f"**{stat}**: nivel {lvl}")
        st.write("Estadísticas finales:", stats)
        st.metric("Puntaje total", f"{score:.2f}")
        st.metric("Comida usada", f"{comida_usada:.2f}")
        st.metric("Ataques totales", f"{ataques_totales:.2f}")
        st.metric("Costo comida", f"{costo_comida:.2f}")
        st.metric("Costo balas grandes", f"{costo_balas_grandes:.2f}")
        st.metric("Costo balas chicas", f"{costo_balas_chicas:.2f}")
    else:
        st.warning("No se encontró una distribución válida.")

st.divider()

st.subheader("Evaluar Build Manual")

manual_input = []
for stat in STAT_KEYS:
    lvl = st.number_input(f"Nivel para {stat}", min_value=0, max_value=MAX_LEVEL, value=0, key=f"manual_{stat}")
    manual_input.append(lvl)

if st.button("Evaluar build manual"):
    try:
        stats, score, comida_usada, ataques_totales = wera.evaluate_custom_distribution(
            manual_input, STATS, FOOD_HEALTH, BATTLE_DURATION, MAX_LEVEL
        )
        costo_comida = comida_usada * COSTO_COMIDA
        costo_balas_grandes = ataques_totales * COSTO_BALAS_GRANDES
        costo_balas_chicas = ataques_totales * COSTO_BALAS_CHICAS

        st.success("Build evaluada correctamente:")
        st.write("Estadísticas resultantes:", stats)
        st.metric("Puntaje total", f"{score:.2f}")
        st.metric("Comida usada", f"{comida_usada:.2f}")
        st.metric("Ataques totales", f"{ataques_totales:.2f}")
        st.metric("Costo comida", f"{costo_comida:.2f}")
        st.metric("Costo balas grandes", f"{costo_balas_grandes:.2f}")
        st.metric("Costo balas chicas", f"{costo_balas_chicas:.2f}")
    except Exception as e:
        st.error(f"Error: {e}")

