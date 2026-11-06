"""Aplicación de Streamlit para estimar la conveniencia de la opción de IVA al 7 % en RESICO 2027."""

import json
from pathlib import Path
import streamlit as st
import calc_iva7


def cargar_configuracion() -> dict:
    """Lee el archivo JSON local de configuración legal y devuelve un diccionario con sus parámetros."""
    ruta_json = Path(__file__).parent / "config_ley.json"
    with open(ruta_json, "r", encoding="utf-8") as f:
        return json.load(f)


def formatear_moneda(cantidad: float) -> str:
    """Convierte un valor numérico a formato de moneda mexicana en pesos enteros sin decimales."""
    if cantidad < 0:
        return f"-${abs(cantidad):,.0f}"
    return f"${cantidad:,.0f}"


def aplicar_ejemplo(region: str, ing: int, gas: int, ret: int, compra: int, exentos: bool) -> None:
    """Actualiza las variables de estado en memoria para precargar un vector de prueba en la interfaz."""
    st.session_state["region"] = region
    st.session_state["ingresos"] = ing
    st.session_state["gastos"] = gas
    st.session_state["iva_retenido"] = ret
    st.session_state["compra_grande"] = compra
    st.session_state["hay_exentos_o_tasa0"] = exentos


def limpiar_formulario() -> None:
    """Restablece los campos de entrada a sus valores iniciales en blanco."""
    st.session_state["region"] = "general"
    st.session_state["ingresos"] = 0
    st.session_state["gastos"] = 0
    st.session_state["iva_retenido"] = 0
    st.session_state["compra_grande"] = 0
    st.session_state["hay_exentos_o_tasa0"] = False
    st.session_state["nombre_prospecto"] = ""
    st.session_state["notas_llamada"] = ""


# Configuración de página
st.set_page_config(page_title="Calculadora IVA 7% RESICO", layout="centered")

config = cargar_configuracion()

# Inicialización de estado en memoria
if "region" not in st.session_state:
    limpiar_formulario()

# 1. Título y Estatus Legal
st.title("Calculadora interna: IVA al 7 % en RESICO 2027")

texto_estatus = config["estatus"].replace("[FECHA_REVISION]", config.get("fecha_revision", "06-nov-2026"))
st.warning(f"**ESTATUS LEGAL:** {texto_estatus}")

# 2. Barra lateral con ejemplos
with st.sidebar:
    st.subheader("Casos de ejemplo rápidos")
    st.caption("Cifras de referencia para llamadas, no representan datos del cliente.")
    if st.button("Ejemplo V1: Servicios (gastos bajos)"):
        aplicar_ejemplo("general", 50000, 5000, 0, 0, False)
    if st.button("Ejemplo V2: Comercio (gastos altos)"):
        aplicar_ejemplo("general", 100000, 70000, 0, 0, False)
    if st.button("Ejemplo V6: Inversión en equipo"):
        aplicar_ejemplo("general", 40000, 4000, 0, 116000, False)
    st.divider()
    if st.button("Limpiar datos"):
        limpiar_formulario()

# 3. Entradas de datos
col_meta1, col_meta2 = st.columns(2)
with col_meta1:
    nombre_prospecto = st.text_input(
        "Nombre del prospecto (opcional)",
        value=st.session_state.get("nombre_prospecto", ""),
        help="Solo se muestra en pantalla durante la llamada; no se guarda en disco."
    )
with col_meta2:
    notas_llamada = st.text_input(
        "Notas breves de la llamada (opcional)",
        value=st.session_state.get("notas_llamada", ""),
        help="Apuntes rápidos de contexto para el contador."
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
    "Gastos y compras con IVA al mes (sin IVA)",
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
    help="Por ejemplo, retenciones del 10.6667 % de personas morales a servicios profesionales."
)

compra_grande = st.number_input(
    "Compra o inversión grande única en el año, sin IVA (opcional)",
    min_value=0,
    step=1000,
    format="%d",
    key="compra_grande",
    help="Maquinaria, equipo de transporte o mobiliario indispensable con factura e IVA."
)

st.write("")
btn_calcular = st.button("Calcular comparativa", type="primary", use_container_width=True)

# 4. Procesamiento de resultados
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

    # Encabezado personalizado si se especificó nombre
    if nombre_prospecto.strip():
        st.subheader(f"Estimación orientativa para: {nombre_prospecto.strip()}")

    # Mensajes principales según veredicto
    ahorro_abs = formatear_moneda(abs(res.ahorro_anual))

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
        st.warning("⚠️ **CASO ESPECIAL:** No es posible emitir un veredicto automático con los datos capturados.")

    # Mostrar avisos normativos derivados del cálculo
    for av in res.avisos:
        st.caption(f"📌 {av}")

    # Métricas y comparativa anual/mensual
    if not res.es_caso_especial:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                label="Pagaría hoy (con acreditamiento)",
                value=formatear_moneda(res.pago_normal_anual),
                help=f"Equivalente mensual aproximado: {formatear_moneda(res.pago_normal_anual / 12)}"
            )
        with m2:
            st.metric(
                label="Pagaría con la opción 7 %",
                value=formatear_moneda(res.pago_opcion_anual),
                help=f"Equivalente mensual aproximado: {formatear_moneda(res.pago_opcion_anual / 12)}"
            )
        with m3:
            st.metric(
                label="Diferencia al año",
                value=formatear_moneda(res.ahorro_anual),
                delta=f"{res.ahorro_pct * 100:.1f} % de ingresos",
                help="Positivo significa que la opción del 7 % resulta más barata."
            )

        # Gráfica de barras comparativa
        datos_grafica = {
            "Régimen General": max(0.0, res.pago_normal_anual),
            "Opción 7 %": max(0.0, res.pago_opcion_anual)
        }
        st.bar_chart(datos_grafica)

        # Frase de punto de equilibrio
        pct_eq = res.r_equilibrio * 100
        st.write(
            f"💡 **Punto de equilibrio:** La opción deja de convenir si su IVA acreditable al año supera "
            f"**{formatear_moneda(res.equilibrio_pesos)}** (≈ {pct_eq:.1f} % de lo que cobra)."
        )

        # Guion sugerido para leer durante la llamada
        st.subheader("Guion para la llamada")
        ahorro_texto = f"{formatear_moneda(abs(res.ahorro_anual))} al año"
        if res.veredicto == "CONVIENE":
            resultado_verbal = f"la opción del 7 % podría costarte aproximadamente {ahorro_texto} menos"
        elif res.veredicto == "NO_CONVIENE":
            resultado_verbal = f"te convendría seguir igual, pues la opción te saldría cerca de {ahorro_texto} más cara al perder deducciones"
        else:
            resultado_verbal = f"la diferencia es mínima (cerca de {ahorro_texto}), por lo que cualquier gasto nuevo cambia el resultado"

        guion = (
            f"• Con tus ingresos proyectados de {formatear_moneda(res.b_anual)} al año y tus gastos habituales,\n"
            f"• calculamos que hoy pagarías de IVA neto cerca de {formatear_moneda(res.pago_normal_anual)}, contra {formatear_moneda(res.pago_opcion_anual)} con la opción al 7 %.\n"
            f"• En resumen: {resultado_verbal}.\n"
            f"• La opción deja de ser atractiva si tus compras y gastos con IVA superan {formatear_moneda(res.equilibrio_pesos)} anuales de puro impuesto.\n"
            f"• Esta cifra es solo una estimación; revisamos su caso con documentos antes de decidir."
        )
        st.code(guion, language="markdown")

# 5. Salvedades normativas (siempre visibles)
st.divider()
st.subheader("Salvedades indispensables")
for num, salv in enumerate(config["salvedades"], start=1):
    st.write(f"**{num}.** {salv}")

# 6. Aspectos pendientes de confirmar
st.write("")
st.caption("**Aspectos pendientes de confirmar por el SAT o texto final DOF:**")
for item in config["por_validar"]:
    st.caption(f"• {item}")

st.caption("Herramienta de uso interno para prospectiva en llamadas. Despacho Contable RESICO PF.")