"""Interfaz gráfica de Streamlit para estimar la opción de IVA al 7 % en llamadas con prospectos."""

import json
from pathlib import Path
import streamlit as st
import calc_iva7


def aplicar_estilos() -> None:
    """Inyecta CSS personalizado inspirado en el sistema de diseño Wise."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');

        :root {
            /* Paleta Wise Style Reference */
            --color-forest-ink: #163300;
            --color-lime-voltage: #9fe870;
            --color-lime-hover: #8cd85c;
            --color-spruce: #054d28;
            --color-linen-mist: #e2f6d5;
            --color-signal-blue: #0b4c72;
            --color-alarm-red: #cb272f;
            --color-charcoal: #454745;
            --color-obsidian: #0e0f0c;
            --color-pebble: #868685;
            --color-slate: #6a6c6a;
            --color-fog: #e8ebe6;
            --color-paper: #ffffff;

            /* Tipografía */
            --font-principal: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

            /* Radios y elevación */
            --radius-pill: 9999px;
            --radius-card: 16px;
            --radius-input: 10px;
            --shadow-card: 0 6px 20px rgba(14, 15, 12, 0.06);
        }

        /* 1. Forzar lienzo principal (Paper #ffffff) y fuente base */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background-color: var(--color-paper) !important;
            color: var(--color-charcoal) !important;
            font-family: var(--font-principal) !important;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 860px !important;
            padding-top: 2.5rem !important;
            padding-bottom: 4rem !important;
        }

        /* 2. Ocultar barra superior, menú hamburguesa y footer sin romper botones de sidebar */
        #MainMenu, footer {
            display: none !important;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* 3. Tipografía jerárquica estilo Wise (Black 900 con tracking cerrado) */
        h1 {
            font-family: var(--font-principal) !important;
            font-weight: 900 !important;
            color: var(--color-obsidian) !important;
            letter-spacing: -0.035em !important;
            line-height: 1.05 !important;
            font-size: 2.6rem !important;
            margin-bottom: 1rem !important;
        }

        h2, h3 {
            font-family: var(--font-principal) !important;
            font-weight: 700 !important;
            color: var(--color-forest-ink) !important;
            letter-spacing: -0.02em !important;
        }

        p, span, label, div, li {
            font-family: var(--font-principal) !important;
            color: var(--color-charcoal);
        }

        /* 4. Sidebar (Superficie Fog #e8ebe6) */
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
            background-color: var(--color-fog) !important;
            border-right: 1px solid rgba(22, 51, 0, 0.12) !important;
        }

        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: var(--color-forest-ink) !important;
            font-weight: 800 !important;
        }

        /* 5. Botones secundarios (Outlined Pill Button - Blanco + borde Forest Ink) */
        .stButton > button {
            border-radius: var(--radius-pill) !important;
            background-color: var(--color-paper) !important;
            color: var(--color-forest-ink) !important;
            border: 1.5px solid var(--color-forest-ink) !important;
            font-family: var(--font-principal) !important;
            font-weight: 600 !important;
            font-size: 15px !important;
            padding: 0.55rem 1.4rem !important;
            transition: all 0.18s ease !important;
            box-shadow: none !important;
        }

        .stButton > button:hover {
            background-color: var(--color-linen-mist) !important;
            color: var(--color-forest-ink) !important;
            border-color: var(--color-forest-ink) !important;
        }

        .stButton > button p {
            color: var(--color-forest-ink) !important;
            font-weight: 600 !important;
        }

        /* 6. Botón Primario (Primary CTA Pill - Lime Voltage #9fe870 + texto Forest Ink) */
        .stButton > button[kind="primary"],
        .stButton > button[data-testid="baseButton-primary"] {
            background-color: var(--color-lime-voltage) !important;
            color: var(--color-forest-ink) !important;
            border: none !important;
            border-radius: var(--radius-pill) !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            padding: 0.75rem 2rem !important;
            box-shadow: 0 4px 12px rgba(22, 51, 0, 0.12) !important;
        }

        .stButton > button[kind="primary"]:hover,
        .stButton > button[data-testid="baseButton-primary"]:hover {
            background-color: var(--color-lime-hover) !important;
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(22, 51, 0, 0.18) !important;
        }

        .stButton > button[kind="primary"] p,
        .stButton > button[data-testid="baseButton-primary"] p {
            color: var(--color-forest-ink) !important;
            font-weight: 700 !important;
        }

        /* 7. Inputs y Number Inputs (Alto contraste: fondo blanco puro y texto oscuro) */
        [data-testid="stTextInput"] div[data-baseweb="input"],
        [data-testid="stNumberInput"] div[data-baseweb="input"],
        div[data-baseweb="input"],
        div[data-baseweb="base-input"],
        div[data-baseweb="base-input"] > div {
            background-color: var(--color-paper) !important;
            color: var(--color-obsidian) !important;
            border-radius: var(--radius-input) !important;
        }

        div[data-baseweb="input"] {
            border: 1.5px solid var(--color-pebble) !important;
            transition: border-color 0.15s ease !important;
        }

        div[data-baseweb="input"]:focus-within {
            border: 2px solid var(--color-forest-ink) !important;
            box-shadow: none !important;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input {
            background-color: var(--color-paper) !important;
            color: var(--color-obsidian) !important;
            -webkit-text-fill-color: var(--color-obsidian) !important;
            caret-color: var(--color-forest-ink) !important;
            font-weight: 500 !important;
            font-size: 16px !important;
        }

        input::placeholder {
            color: var(--color-slate) !important;
            -webkit-text-fill-color: var(--color-slate) !important;
            opacity: 1 !important;
        }

        /* Botones + / - de number_input */
        [data-testid="stNumberInput"] button,
        button[data-testid="stNumberInputStepDown"],
        button[data-testid="stNumberInputStepUp"] {
            background-color: var(--color-fog) !important;
            color: var(--color-forest-ink) !important;
            border: none !important;
            border-radius: 6px !important;
        }

        [data-testid="stNumberInput"] button:hover {
            background-color: var(--color-linen-mist) !important;
        }

        [data-testid="stNumberInput"] button svg {
            fill: var(--color-forest-ink) !important;
            color: var(--color-forest-ink) !important;
        }

        label[data-testid="stWidgetLabel"] p {
            color: var(--color-obsidian) !important;
            font-weight: 600 !important;
            font-size: 14.5px !important;
            margin-bottom: 4px !important;
        }

        /* 8. Radio Buttons como Segmented Control estilo Wise */
        div[role="radiogroup"] {
            gap: 10px !important;
        }

        div[role="radiogroup"] label {
            background-color: var(--color-fog) !important;
            border: 1px solid transparent !important;
            border-radius: var(--radius-pill) !important;
            padding: 8px 18px !important;
            transition: all 0.15s ease !important;
        }

        div[role="radiogroup"] label:hover {
            background-color: var(--color-linen-mist) !important;
        }

        div[role="radiogroup"] label[data-checked="true"],
        div[role="radiogroup"] label:has(input:checked) {
            background-color: var(--color-lime-voltage) !important;
            border-color: var(--color-forest-ink) !important;
        }

        div[role="radiogroup"] label:has(input:checked) p {
            color: var(--color-forest-ink) !important;
            font-weight: 700 !important;
        }

        /* 9. Métricas (Tarjetas con superficie Fog #e8ebe6 y acento Forest Ink) */
        div[data-testid="stMetric"] {
            background-color: var(--color-fog) !important;
            border-radius: var(--radius-card) !important;
            padding: 1.25rem 1.35rem !important;
            border: 1px solid rgba(22, 51, 0, 0.10) !important;
            box-shadow: var(--shadow-card) !important;
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--color-slate) !important;
            font-size: 13.5px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.03em !important;
        }

        div[data-testid="stMetricValue"] div {
            color: var(--color-forest-ink) !important;
            font-weight: 900 !important;
            font-size: 1.9rem !important;
            letter-spacing: -0.03em !important;
        }

        /* 10. Alertas (ESTATUS LEGAL, CONVIENE, NO CONVIENE, ZONA GRIS - Alto contraste garantizado) */
        div[data-testid="stAlert"],
        div[data-testid="stAlertContainer"] {
            border-radius: var(--radius-card) !important;
            padding: 1rem 1.25rem !important;
            border: 1.5px solid var(--color-forest-ink) !important;
            border-left: 6px solid var(--color-forest-ink) !important;
            background-color: var(--color-fog) !important;
        }

        /* Forzar texto negro/verde oscuro en TODOS los elementos internos de cualquier alerta */
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span,
        div[data-testid="stAlert"] strong,
        div[data-testid="stAlert"] b,
        div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] {
            color: var(--color-obsidian) !important;
            opacity: 1 !important;
            font-size: 15.5px !important;
            line-height: 1.5 !important;
        }

        div[data-testid="stAlert"] strong,
        div[data-testid="stAlert"] b {
            color: var(--color-forest-ink) !important;
            font-weight: 800 !important;
        }

        /* Diferenciación visual sutil por tipo de notificación manteniendo legibilidad total */
        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentSuccess"]) {
            background-color: var(--color-linen-mist) !important;
            border-color: var(--color-forest-ink) !important;
        }

        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentWarning"]) {
            background-color: #fef6d8 !important;
            border-color: #8a6100 !important;
            border-left-color: #b88100 !important;
        }

        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentError"]) {
            background-color: #fdeaea !important;
            border-color: var(--color-alarm-red) !important;
            border-left-color: var(--color-alarm-red) !important;
        }

        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentInfo"]) {
            background-color: var(--color-fog) !important;
            border-color: var(--color-signal-blue) !important;
            border-left-color: var(--color-signal-blue) !important;
        }

        /* 11. Bloque de código (Guion para la llamada - Dark Card Forest Ink) */
        [data-testid="stCodeBlock"], pre {
            background-color: var(--color-forest-ink) !important;
            border-radius: 18px !important;
            padding: 1.25rem !important;
            border: none !important;
        }

        [data-testid="stCodeBlock"] code, pre code, pre span {
            color: var(--color-linen-mist) !important;
            font-family: 'Inter', monospace !important;
            font-size: 14.5px !important;
            line-height: 1.6 !important;
            background: transparent !important;
        }

        /* 12. Divisores */
        hr {
            border: none !important;
            border-top: 1px solid var(--color-fog) !important;
            margin: 2rem 0 !important;
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
    st.session_state["importaciones_anuales"] = 0
    st.session_state["hay_exentos_o_tasa0"] = exentos


def limpiar_formulario() -> None:
    """Restablece los campos de captura a ceros y textos vacíos en la memoria de la sesión."""
    st.session_state["region"] = "general"
    st.session_state["ingresos"] = 0
    st.session_state["gastos"] = 0
    st.session_state["iva_retenido"] = 0
    st.session_state["compra_grande"] = 0
    st.session_state["importaciones_anuales"] = 0
    st.session_state["hay_exentos_o_tasa0"] = False
    st.session_state["nombre_prospecto"] = ""
    st.session_state["notas_llamada"] = ""


st.set_page_config(page_title="Calculadora IVA 7% RESICO", layout="centered")
aplicar_estilos()

config = cargar_configuracion()

if "region" not in st.session_state:
    limpiar_formulario()

# 1. Título y recuadro de estatus legal normativo
st.title("Calculadora interna: IVA al 7 % en RESICO 2027")

texto_estatus = config["estatus"].replace(
    "[FECHA_REVISION]",
    config.get("fecha_revision", "13-nov-2026 (DOF LIF 2027)")
)
st.warning(f"**ESTATUS LEGAL:** {texto_estatus}")

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

importaciones_anuales = st.number_input(
    "Importaciones de bienes tangibles al año, sin IVA (opcional)",
    min_value=0,
    step=1000,
    format="%d",
    key="importaciones_anuales",
    help="Si importa mercancía o equipo: paga IVA general en aduana (no acreditable con esta opción) y si rebasa $5,000,000 MXN al año queda excluido."
)

st.write("")
btn_calcular = st.button("Calcular", type="primary", use_container_width=True)

# 4. Procesamiento y presentación de resultados
if btn_calcular or ingresos > 0 or hay_exentos_o_tasa0 or importaciones_anuales > 0:
    res = calc_iva7.calcular_comparativa(
        region=region,
        ingresos=float(ingresos),
        hay_exentos_o_tasa0=hay_exentos_o_tasa0,
        gastos=float(gastos),
        iva_retenido=float(iva_retenido),
        compra_grande=float(compra_grande),
        importaciones_anuales=float(importaciones_anuales),
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
            f"{ahorro_abs} menos al año. **Reglas críticas:** el aviso al SAT debe presentarse dentro de los "
            f"**30 días siguientes al primer cobro del año**, aplica por meses completos y es irrevocable en todo el ejercicio."
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
            etiqueta_opcion = "Remanente por retenciones (devolución no garantizada)"
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

        # Guion para la llamada (6 líneas listas para copiar)
        st.subheader("Guion para la llamada")
        if res.pago_normal_anual < 0:
            resumen_actual = f"hoy tendrías un saldo a favor estimado de {formatear_moneda(res.pago_normal_anual)}"
        else:
            resumen_actual = f"hoy pagarías aproximadamente {formatear_moneda(res.pago_normal_anual)} de IVA al año"

        if res.opcion_matematica < 0:
            resumen_op = (
                f"con el 7 % pagarías $0 y quedaría un remanente de {formatear_moneda(res.saldo_favor_opcion)} "
                f"por retenciones (sujeto a reglas del SAT para acreditarlo)"
            )
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
            "• Seguirás facturando con IVA normal (16 % / 8 %), pero solo enteras 7 % al SAT; la diferencia que conservas no paga ISR.",
            f"• El punto de equilibrio es {formatear_moneda(res.equilibrio_pesos)} de IVA acreditable anual (si gastas más con factura, la opción pierde ventaja).",
            "• Importante: Tenemos 30 días tras tu primer cobro del año para presentar el aviso y aplica todo el año. Revisamos tus documentos antes de decidir."
        ]
        st.code("\n".join(lineas_guion), language="markdown")

# 5. Salvedades normativas obligatorias (siempre visibles)
st.divider()
st.subheader("Salvedades indispensables")
for idx, salv in enumerate(config["salvedades"], start=1):
    st.write(f"**{idx}.** {salv}")

# 6. Aspectos pendientes de confirmar
st.write("")
st.markdown("**Pendiente de confirmar (Reglas Misceláneas SAT):**")
for pendiente in config["por_validar"]:
    st.caption(f"• {pendiente}")

st.caption("Herramienta de uso interno para prospectiva en llamadas. Despacho Contable RESICO PF.")