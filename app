"""Interfaz gráfica de Streamlit para estimar la opción de IVA al 7 % en llamadas con prospectos."""

import json
from pathlib import Path
import streamlit as st
import calc_iva7


def aplicar_estilos() -> None:
    """Aplica una identidad visual fintech clara y profesional."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {
            --navy: #17324D;
            --navy-2: #244965;
            --teal: #168B83;
            --teal-soft: #E8F5F3;
            --ink: #203040;
            --muted: #687887;
            --line: #E2E8EF;
            --canvas: #F4F7FA;
            --surface: #FFFFFF;
            --amber-bg: #FFF7E6;
            --amber-line: #E8B64D;
            --green-bg: #EAF6EF;
            --green-line: #60A77A;
            --red-bg: #FCEEEE;
            --red-line: #D87979;
            --radius: 16px;
            --shadow: 0 8px 24px rgba(23, 50, 77, .06);
        }

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            color: var(--ink);
        }
        .stApp {
            background:
                radial-gradient(circle at 85% 0%, rgba(22,139,131,.07), transparent 26rem),
                var(--canvas);
        }
        [data-testid="stMainBlockContainer"] {
            max-width: 1180px;
            padding-top: 2.2rem;
            padding-bottom: 4rem;
        }
        [data-testid="stHeader"] { background: transparent; }
        #MainMenu, footer { visibility: hidden; }

        h1, h2, h3 {
            font-family: 'Manrope', sans-serif !important;
            color: var(--navy) !important;
            letter-spacing: -.035em;
            font-weight: 800 !important;
        }
        h1 { font-size: clamp(2rem, 4vw, 2.8rem) !important; line-height: 1.12 !important; }
        h2 { font-size: 1.45rem !important; }
        h3 { font-size: 1.12rem !important; }
        p, label, span, div { font-family: 'DM Sans', sans-serif; }

        [data-testid="stSidebar"] {
            background: #EDF3F6 !important;
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: var(--navy) !important;
        }

        [data-testid="stWidgetLabel"] p {
            color: #405466 !important;
            font-size: .91rem !important;
            font-weight: 600 !important;
        }
        [data-baseweb="input"], [data-baseweb="select"] > div,
        [data-testid="stNumberInput"] [data-baseweb="input"] {
            background: var(--surface) !important;
            border: 1px solid #D7E0E8 !important;
            border-radius: 10px !important;
        }
        [data-baseweb="input"]:focus-within {
            border-color: var(--teal) !important;
            box-shadow: 0 0 0 3px rgba(22,139,131,.12) !important;
        }
        input, textarea {
            color: var(--ink) !important;
            font-family: 'DM Sans', sans-serif !important;
        }

        .stButton > button {
            border-radius: 10px !important;
            border: 1px solid #D4DFE7 !important;
            background: #FFFFFF !important;
            color: var(--navy) !important;
            font-weight: 700 !important;
            min-height: 2.7rem;
            transition: all .18s ease;
        }
        .stButton > button:hover {
            border-color: var(--teal) !important;
            color: var(--teal) !important;
            transform: translateY(-1px);
            box-shadow: 0 5px 14px rgba(23,50,77,.08);
        }
        .stButton > button[kind="primary"] {
            background: var(--navy) !important;
            border-color: var(--navy) !important;
            color: white !important;
            box-shadow: 0 7px 16px rgba(23,50,77,.16);
            min-height: 3.15rem;
            font-size: 1rem !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: var(--teal) !important;
            border-color: var(--teal) !important;
            color: white !important;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid var(--line);
            border-radius: var(--radius);
            padding: 1.15rem 1.2rem;
            box-shadow: var(--shadow);
        }
        div[data-testid="stMetricLabel"] p {
            color: var(--muted) !important;
            font-weight: 600 !important;
            font-size: .82rem !important;
        }
        div[data-testid="stMetricValue"] {
            color: var(--navy) !important;
            font-family: 'Manrope', sans-serif !important;
            font-weight: 800 !important;
        }
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            border-width: 1px !important;
            box-shadow: none !important;
        }
        div[data-testid="stAlert"][kind="warning"] {
            background: var(--amber-bg) !important;
            border-color: var(--amber-line) !important;
        }
        div[data-testid="stAlert"][kind="success"] {
            background: var(--green-bg) !important;
            border-color: var(--green-line) !important;
        }
        div[data-testid="stAlert"][kind="error"] {
            background: var(--red-bg) !important;
            border-color: var(--red-line) !important;
        }
        div[data-testid="stAlert"][kind="info"] {
            background: var(--teal-soft) !important;
            border-color: #9BCFC8 !important;
        }

        div[role="radiogroup"] { gap: .55rem; }
        div[role="radiogroup"] label {
            background: white;
            border: 1px solid var(--line);
            border-radius: 10px;
            padding: .45rem .8rem;
        }
        div[role="radiogroup"] label:hover {
            border-color: var(--teal);
            background: var(--teal-soft);
        }
        [data-testid="stCheckbox"] label { gap: .55rem; }

        [data-testid="stExpander"] {
            background: white;
            border: 1px solid var(--line);
            border-radius: 12px;
            overflow: hidden;
        }
        [data-testid="stCodeBlock"] {
            border: 1px solid var(--line);
            border-radius: 12px;
        }
        hr {
            border-color: var(--line) !important;
            margin: 1.5rem 0 !important;
        }
        .hero-kicker {
            color: var(--teal);
            font-size: .76rem;
            font-weight: 800;
            letter-spacing: .13em;
            text-transform: uppercase;
            margin-bottom: .45rem;
        }
        .hero-subtitle {
            color: var(--muted);
            font-size: 1.02rem;
            margin-top: -.45rem;
            margin-bottom: 1.15rem;
        }
        .section-kicker {
            color: var(--teal);
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .12em;
            text-transform: uppercase;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def cargar_configuracion() -> dict:
    """Carga los parámetros normativos y textos fijos desde el archivo JSON sin persistir datos."""
    ruta_cfg = Path(__file__).parent / "config_ley.json"
    with open(ruta_cfg, "r", encoding="utf-8") as f:
        return json.load(f)


def formatear_moneda(cantidad: float) -> str:
    """Formatea una cantidad numérica en formato entero de pesos mexicanos sin signo negativo explícito."""
    return f"${abs(cantidad):,.0f}"


def aplicar_ejemplo(region: str, ing: int, gas: int, ret: int, compra: int, exentos: bool) -> None:
    """Precarga en session_state los parámetros de un vector de ejemplo para agilizar la llamada."""
    st.session_state["region"] = region
    st.session_state["ingresos"] = ing
    st.session_state["gastos"] = gas
    st.session_state["iva_retenido"] = ret
    st.session_state["compra_grande"] = compra
    st.session_state["hay_exentos_o_tasa0"] = exentos


def limpiar_formulario() -> None:
    """Restablece los campos de captura a ceros y textos vacíos en la memoria de la sesión."""
    st.session_state["region"] = "general"
    st.session_state["ingresos"] = 0
    st.session_state["gastos"] = 0
    st.session_state["iva_retenido"] = 0
    st.session_state["compra_grande"] = 0
    st.session_state["hay_exentos_o_tasa0"] = False
    st.session_state["nombre_prospecto"] = ""
    st.session_state["notas_llamada"] = ""


st.set_page_config(page_title="RESICO | Simulador de IVA 2027", page_icon="📊", layout="wide")
aplicar_estilos()

config = cargar_configuracion()

if "region" not in st.session_state:
    limpiar_formulario()

# 1. Encabezado del producto y estatus legal
st.markdown('<div class="hero-kicker">DESPACHO CONTABLE · HERRAMIENTAS DE ANÁLISIS</div>', unsafe_allow_html=True)
st.title("Simulador de IVA · RESICO 2027")
st.markdown(
    '<div class="hero-subtitle">Compara escenarios fiscales y prepara una conversación informada con tu prospecto.</div>',
    unsafe_allow_html=True,
)
texto_estatus = config["estatus"].replace("[FECHA_REVISION]", config.get("fecha_revision", "06-nov-2026"))
with st.container(border=True):
    st.markdown("**ESTATUS NORMATIVO**")
    st.warning(texto_estatus)

# 2. Barra lateral con ejemplos y limpieza
with st.sidebar:
    st.subheader("Ejemplos rápidos para llamada")
    st.caption("Ejemplo, no son cifras del cliente:")
    if st.button("Ejemplo V1: Servicios (gastos bajos)"):
        aplicar_ejemplo("general", 50000, 5000, 0, 0, False)
    if st.button("Ejemplo V2: Comercio (gastos altos)"):
        aplicar_ejemplo("general", 100000, 70000, 0, 0, False)
    if st.button("Ejemplo V6: Compra de equipo"):
        aplicar_ejemplo("general", 40000, 4000, 0, 116000, False)
    st.divider()
    if st.button("Limpiar datos"):
        limpiar_formulario()

# 3. Entradas de datos
st.markdown('<div class="section-kicker">01 · PERFIL DEL PROSPECTO</div>', unsafe_allow_html=True)
col_apoyo1, col_apoyo2 = st.columns(2)
with col_apoyo1:
    nombre_prospecto = st.text_input(
        "Nombre del prospecto (opcional)",
        value=st.session_state.get("nombre_prospecto", ""),
        help="Solo visible en tu pantalla durante la llamada. No se guarda."
    )
with col_apoyo2:
    notas_llamada = st.text_input(
        "Notas de la llamada (opcional)",
        value=st.session_state.get("notas_llamada", ""),
        help="Apuntes internos temporales para la conversación."
    )

st.markdown('<div class="section-kicker">02 · PARÁMETROS DE OPERACIÓN</div>', unsafe_allow_html=True)
region = st.radio(
    "Región de operación",
    options=["general", "frontera"],
    format_func=lambda r: "Interior del país (IVA 16 %)" if r == "general" else "Región Fronteriza Norte (IVA 8 %)",
    horizontal=True,
    key="region"
)

ingresos = st.number_input(
    "Ingresos cobrados al mes (sin IVA)",
    min_value=0,
    step=1000,
    format="%d",
    key="ingresos",
    help="Promedio mensual efectivamente cobrado de actividades gravadas."
)

hay_exentos_o_tasa0 = st.checkbox(
    "Parte de sus ingresos no lleva IVA (exentos o tasa 0 %: consultas médicas, exportación de servicios, alimentos)",
    key="hay_exentos_o_tasa0"
)

gastos = st.number_input(
    "Gastos y compras con IVA al mes, sin IVA",
    min_value=0,
    step=1000,
    format="%d",
    key="gastos",
    help="Solo los que tienen factura a su nombre y son del negocio. Sueldos e impuestos no llevan IVA acreditable."
)

iva_retenido = st.number_input(
    "IVA que le retienen sus clientes al mes (opcional)",
    min_value=0,
    step=1000,
    format="%d",
    key="iva_retenido",
    help="Retenciones que te efectúan personas morales (ej. servicios profesionales)."
)

compra_grande = st.number_input(
    "Compra o inversión grande del año, sin IVA (opcional)",
    min_value=0,
    step=1000,
    format="%d",
    key="compra_grande",
    help="Compra única anual de equipo o mobiliario indispensable con IVA."
)

st.write("")
st.markdown('<div class="section-kicker">03 · SIMULACIÓN</div>', unsafe_allow_html=True)
btn_calcular = st.button("Calcular escenario", type="primary", use_container_width=True)

# 4. Procesamiento y presentación de resultados
if btn_calcular or ingresos > 0 or hay_exentos_o_tasa0:
    res = calc_iva7.calcular_comparativa(
        region=region,
        ingresos=float(ingresos),
        hay_exentos_o_tasa0=hay_exentos_o_tasa0,
        gastos=float(gastos),
        iva_retenido=float(iva_retenido),
        compra_grande=float(compra_grande),
        config=config
    )

    st.divider()

    if nombre_prospecto.strip():
        st.subheader(f"Estimación para: {nombre_prospecto.strip()}")

    ahorro_abs = formatear_moneda(res.ahorro_anual)

    # Mensajes por veredicto estricto
    if res.veredicto == "CONVIENE":
        st.success(
            f"✅ **CONVIENE:** Con estos datos, la opción del 7 % podría costar aproximadamente "
            f"{ahorro_abs} menos al año. Antes de decidir hay que confirmar el caso: el aviso al SAT "
            f"es obligatorio y la decisión vale todo el año."
        )
    elif res.veredicto == "NO_CONVIENE":
        st.error(
            f"❌ **NO CONVIENE:** Con estos datos, seguir como está podría costar aproximadamente "
            f"{ahorro_abs} menos al año, porque perdería el IVA que hoy acredita."
        )
    elif res.veredicto == "ZONA_GRIS":
        st.info(
            f"⚖️ **ZONA GRIS:** Con estos datos la diferencia es pequeña ({ahorro_abs} al año). "
            f"Un cambio en sus gastos puede inclinar la balanza."
        )
    else:
        st.warning("⚠️ **CASO ESPECIAL:** No se emite veredicto automático. Requiere análisis manual.")

    # Avisos normativos y notas de saldos
    for av in res.avisos:
        st.caption(f"📌 {av}")

    if not res.es_caso_especial:
        # Etiquetas dinámicas para evitar números negativos
        if res.pago_normal_anual < 0:
            etiqueta_normal = "Saldo a favor hoy"
            valor_normal_str = formatear_moneda(res.pago_normal_anual)
            sub_normal = f"Promedio mensual a favor: {formatear_moneda(res.pago_normal_anual / 12)}"
        else:
            etiqueta_normal = "Pagaría hoy (con acreditamiento)"
            valor_normal_str = formatear_moneda(res.pago_normal_anual)
            sub_normal = f"Promedio mensual: {formatear_moneda(res.pago_normal_anual / 12)}"

        if res.opcion_matematica < 0:
            etiqueta_opcion = "Posible saldo a favor con la opción (por confirmar)"
            valor_opcion_str = formatear_moneda(res.saldo_favor_opcion)
            sub_opcion = f"Pago inmediato estimado: $0 (remanente: {formatear_moneda(res.saldo_favor_opcion)})"
        else:
            etiqueta_opcion = "Pagaría con la opción 7 %"
            valor_opcion_str = formatear_moneda(res.opcion_pago_anual)
            sub_opcion = f"Promedio mensual: {formatear_moneda(res.opcion_pago_anual / 12)}"

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label=etiqueta_normal, value=valor_normal_str, help=sub_normal)
        with c2:
            st.metric(label=etiqueta_opcion, value=valor_opcion_str, help=sub_opcion)
        with c3:
            st.metric(
                label="Diferencia al año (base conservadora)",
                value=formatear_moneda(res.ahorro_anual),
                delta=f"{res.ahorro_pct * 100:.1f} % s/ingresos",
                help="Positivo indica que la opción cuesta menos. Negativo indica que seguir como está es mejor."
            )

        # Gráfica de barras comparativa (valores absolutos con piso en 0 para pagos)
        datos_grafica = {
            "Régimen General (pago neto)": max(0.0, res.pago_normal_anual),
            "Opción 7 % (pago efectivo)": res.opcion_pago_anual
        }
        st.bar_chart(datos_grafica)

        # Frase de equilibrio
        pct_eq = res.r_equilibrio * 100
        st.write(
            f"💡 **Punto de equilibrio:** La opción deja de convenir si su IVA acreditable al año supera "
            f"**{formatear_moneda(res.equilibrio_pesos)}** (≈ {pct_eq:.1f} % de lo que cobra)."
        )

        # Guion para la llamada (4 a 6 líneas listas para copiar)
        st.subheader("Guion para la llamada")
        if res.pago_normal_anual < 0:
            resumen_actual = f"hoy tendrías un saldo a favor estimado de {formatear_moneda(res.pago_normal_anual)}"
        else:
            resumen_actual = f"hoy pagarías aproximadamente {formatear_moneda(res.pago_normal_anual)} de IVA al año"

        if res.opcion_matematica < 0:
            resumen_op = f"con el 7 % pagarías $0 y generarías un posible saldo a favor de {formatear_moneda(res.saldo_favor_opcion)}"
        else:
            resumen_op = f"con la opción al 7 % pagarías cerca de {formatear_moneda(res.opcion_pago_anual)}"

        if res.veredicto == "CONVIENE":
            resumen_ahorro = f"la opción del 7 % podría costarte aproximadamente {formatear_moneda(res.ahorro_anual)} menos al año"
        elif res.veredicto == "NO_CONVIENE":
            resumen_ahorro = f"seguir como estás te convendría más, ahorrándote cerca de {formatear_moneda(res.ahorro_anual)} al conservar acreditamientos"
        else:
            resumen_ahorro = f"la diferencia es mínima ({formatear_moneda(res.ahorro_anual)} al año) y cualquier gasto la mueve"

        lineas_guion = [
            f"• Con tus ingresos anuales proyectados de {formatear_moneda(res.b_anual)} y tus gastos declarados,",
            f"• {resumen_actual}, mientras que {resumen_op}.",
            f"• En conclusión: {resumen_ahorro}.",
            f"• El punto de equilibrio es {formatear_moneda(res.equilibrio_pesos)} de IVA acreditable anual (si gastas más con factura, la opción pierde ventaja).",
            "• Recuerda que esta es una estimación; revisamos su caso con documentos antes de decidir."
        ]
        st.code("\n".join(lineas_guion), language="markdown")

# 5. Salvedades normativas obligatorias
st.divider()
with st.expander("Consideraciones fiscales, salvedades y puntos pendientes", expanded=False):
    st.subheader("Salvedades indispensables")
    for idx, salv in enumerate(config["salvedades"], start=1):
        st.write(f"**{idx}.** {salv}")

    st.markdown("**Pendiente de confirmar (DOF / reglas misceláneas SAT):**")
    for pendiente in config["por_validar"]:
        st.caption(f"• {pendiente}")

st.caption("Herramienta de uso interno para prospectiva en llamadas · Despacho Contable RESICO PF.")