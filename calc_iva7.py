"""Motor de cálculo determinista para comparar IVA general vs. opción 7 % en RESICO 2027."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ResultadoCalculo:
    """Estructura inmutable que contiene todos los resultados, métricas y avisos del cálculo."""
    b_anual: float
    iva_trasladado_anual: float
    iva_acreditable_anual: float
    retencion_anual: float
    pago_normal_anual: float
    pago_opcion_anual: float
    ahorro_anual: float
    ahorro_pct: float
    r_acreditable: float
    r_equilibrio: float
    equilibrio_pesos: float
    veredicto: str
    es_caso_especial: bool
    avisos: List[str]


def obtener_tasa_region(region: str, config: dict) -> float:
    """Devuelve la tasa de IVA aplicable según la región geográfica indicada en la configuración."""
    if region == "frontera":
        return float(config["tasas"]["iva_frontera"])
    return float(config["tasas"]["iva_general"])


def calcular_comparativa(
    region: str,
    ingresos: float,
    hay_exentos_o_tasa0: bool,
    gastos: float,
    iva_retenido: float = 0.0,
    compra_grande: float = 0.0,
    config: Optional[dict] = None
) -> ResultadoCalculo:
    """Calcula la comparativa aritmética entre el régimen general de IVA y la opción del 7 % para RESICO."""
    if config is None:
        raise ValueError("Se requiere el diccionario de configuración de ley.")

    t = obtener_tasa_region(region, config)
    t_op = float(config["tasas"]["iva_opcion_resico"])
    zona_gris_pct = float(config["zona_gris_pct"])
    limite_resico = float(config["limite_resico_pf_anual"])

    avisos: List[str] = []

    # 1. Base gravada anual
    # b_anual = 12.0 * float(ingresos)

    # 2. Impuesto causado y acreditamiento
    # iva_tras = b_anual * t
    # acred = (12.0 * float(gastos) + float(compra_grande)) * t

    # 3. Retenciones anualizadas (acotadas al IVA trasladado en régimen normal)
    # ret_anual_solicitada = 12.0 * float(iva_retenido)
    # ret = min(ret_anual_solicitada, iva_tras)

    # 4. Impuesto a pagar o saldo a favor
    # normal = iva_tras - acred - ret
    # opcion = (b_anual * t_op) - ret
    # ahorro = normal - opcion

    # 5. Ratios de análisis y equilibrio
    # pct = (ahorro / b_anual) if b_anual > 0 else 0.0
    # r = (acred / b_anual) if b_anual > 0 else 0.0
    # r_eq = t - t_op
    #eq_pesos = b_anual * r_eq

# 1. Base gravada anual
    b_anual = round(12.0 * float(ingresos), 2)

    # 2. Impuesto causado y acreditamiento
    iva_tras = round(b_anual * t, 2)
    acred = round((12.0 * float(gastos) + float(compra_grande)) * t, 2)

    # 3. Retenciones anualizadas (acotadas al IVA trasladado en régimen normal)
    ret_anual_solicitada = round(12.0 * float(iva_retenido), 2)
    ret = min(ret_anual_solicitada, iva_tras)

    # 4. Impuesto a pagar o saldo a favor
    normal = round(iva_tras - acred - ret, 2)
    opcion = round((b_anual * t_op) - ret, 2)
    ahorro = round(normal - opcion, 2)

    # 5. Ratios de análisis y equilibrio
    pct = (ahorro / b_anual) if b_anual > 0 else 0.0
    r = (acred / b_anual) if b_anual > 0 else 0.0
    r_eq = round(t - t_op, 4)
    eq_pesos = round(b_anual * r_eq, 2)

    # 6. Detección de casos especiales
    es_caso_especial = False
    veredicto = "CASO_ESPECIAL"

    if hay_exentos_o_tasa0:
        es_caso_especial = True
        avisos.append("Tiene ingresos exentos o a tasa 0 %. Requiere estudio particular; no aplica cálculo estándar.")

    if b_anual > limite_resico:
        es_caso_especial = True
        avisos.append(
            f"Los ingresos proyectados (${b_anual:,.0f}) superan el límite de RESICO (${limite_resico:,.0f}). "
            "No tributaría en este régimen."
        )

    if ingresos <= 0:
        es_caso_especial = True
        avisos.append("Los ingresos cobrados mensuales deben ser mayores a cero para realizar la estimación.")

    # 7. Reglas de frontera y saldo a favor en opción
    if region == "frontera":
        avisos.append("Con 8 % de IVA el beneficio máximo es 1 punto sobre tus ingresos.")

    if opcion < 0:
        avisos.append("La opción resulta en saldo a favor por retenciones; su devolución o acreditamiento está PENDIENTE DE CONFIRMAR en reglas del SAT.")

    # 8. Determinación del veredicto si no es caso especial
    if not es_caso_especial:
        if pct > zona_gris_pct:
            veredicto = "CONVIENE"
        elif pct < -zona_gris_pct:
            veredicto = "NO_CONVIENE"
        else:
            veredicto = "ZONA_GRIS"

    return ResultadoCalculo(
        b_anual=b_anual,
        iva_trasladado_anual=iva_tras,
        iva_acreditable_anual=acred,
        retencion_anual=ret,
        pago_normal_anual=normal,
        pago_opcion_anual=opcion,
        ahorro_anual=ahorro,
        ahorro_pct=pct,
        r_acreditable=r,
        r_equilibrio=r_eq,
        equilibrio_pesos=eq_pesos,
        veredicto=veredicto,
        es_caso_especial=es_caso_especial,
        avisos=avisos,
    )