"""Interfaz gráfica de Streamlit para estimar la opción de IVA al 7 % en llamadas con prospectos."""

import json
from pathlib import Path
import streamlit as st
import calc_iva7


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


st.set_page_config(page_title="Calculadora IVA 7% RESICO", layout="centered")

config = cargar_configuracion()

if "region" not in st.session_state:
    limpiar_formulario()

# 1. Título y recuadro de estatus legal normativo
st.title("Calculadora interna: IVA al 7 % en RESICO 2027")

texto_estatus = config["estatus"].replace("[FECHA_REVISION]", config.get("fecha_revision", "06-nov-2026"))
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

st.write("")
btn_calcular = st.button("Calcular", type="primary", use_container_width=True)

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

# 5. Salvedades normativas obligatorias (siempre visibles)
st.divider()
st.subheader("Salvedades indispensables")
for idx, salv in enumerate(config["salvedades"], start=1):
    st.write(f"**{idx}.** {salv}")

# 6. Aspectos pendientes de confirmar
st.write("")
st.markdown("**Pendiente de confirmar (DOF / reglas misceláneas SAT):**")
for pendiente in config["por_validar"]:
    st.caption(f"• {pendiente}")

st.caption("Herramienta de uso interno para prospectiva en llamadas. Despacho Contable RESICO PF.")