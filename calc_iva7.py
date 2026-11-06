"""Motor de cálculo determinista para evaluar la opción de IVA al 7 % en RESICO 2027."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ResultadoCalculo:
    """Estructura de datos que almacena las cifras, razones de equilibrio, veredicto y avisos."""
    b_anual: float
    iva_trasladado_anual: float
    iva_acreditable_anual: float
    retencion_anual: float
    pago_normal_anual: float
    opcion_matematica: float
    opcion_pago_anual: float
    saldo_favor_opcion: float
    ahorro_anual: float
    ahorro_si_se_recupera: float
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
    """Ejecuta la aritmética para comparar el IVA general con la opción del 7 % bajo criterio conservador."""
    if config is None:
        raise ValueError("Se requiere el diccionario de configuración legal.")

    t = obtener_tasa_region(region, config)
    t_op = float(config["tasas"]["iva_opcion_resico"])
    zona_gris_pct = float(config["zona_gris_pct"])
    limite_resico = float(config["limite_resico_pf_anual"])

    avisos: List[str] = []

    # 1. Base gravada y montos con redondeo a 2 decimales para precisión contable
    b_anual = round(12.0 * float(ingresos), 2)
    iva_tras = round(b_anual * t, 2)
    acred = round((12.0 * float(gastos) + float(compra_grande)) * t, 2)
    ret_anual_solicitada = round(12.0 * float(iva_retenido), 2)
    ret = min(ret_anual_solicitada, iva_tras)

    # 2. Esquema normal y opción (criterio conservador)
    normal = round(iva_tras - acred - ret, 2)
    opcion = round((b_anual * t_op) - ret, 2)
    opcion_pago = max(opcion, 0.0)
    saldo_op = max(-opcion, 0.0)

    ahorro = round(normal - opcion_pago, 2)
    ahorro_si_se_recupera = round(normal - opcion, 2)

    # 3. Ratios de análisis y equilibrio
    pct = (ahorro / b_anual) if b_anual > 0 else 0.0
    r = (acred / b_anual) if b_anual > 0 else 0.0
    r_eq = round(t - t_op, 4)
    eq_pesos = round(b_anual * r_eq, 2)

    # 4. Verificación de casos especiales sin veredicto
    es_caso_especial = False
    veredicto = "CASO_ESPECIAL"

    if hay_exentos_o_tasa0:
        es_caso_especial = True
        avisos.append("Tiene ingresos exentos o a tasa 0 %. Requiere estudio particular; no aplica cálculo estándar.")

    if b_anual > limite_resico:
        es_caso_especial = True
        avisos.append(
            f"Los ingresos anuales estimados (${b_anual:,.0f}) superan el límite de RESICO (${limite_resico:,.0f}). "
            "No tributaría en este régimen."
        )

    if ingresos <= 0:
        es_caso_especial = True
        avisos.append("Los ingresos cobrados mensuales deben ser mayores a cero para realizar la estimación.")

    # 5. Notas legales obligatorias y saldos a favor
    if region == "frontera":
        avisos.append("Con 8 % de IVA el beneficio máximo es 1 punto sobre tus ingresos.")

    if opcion < 0:
        avisos.append(
            f"Muestra posible saldo a favor de ${saldo_op:,.0f} por confirmar en reglas del SAT. "
            "El veredicto conservador no cuenta este saldo como dinero recuperado."
        )

    if normal < 0 or opcion < 0:
        avisos.append("Un saldo a favor no es dinero en el bolsillo hasta que se acredita o se devuelve; hay que revisar el caso.")

    # 6. Veredicto cuando no es caso especial
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
        opcion_matematica=opcion,
        opcion_pago_anual=opcion_pago,
        saldo_favor_opcion=saldo_op,
        ahorro_anual=ahorro,
        ahorro_si_se_recupera=ahorro_si_se_recupera,
        ahorro_pct=pct,
        r_acreditable=r,
        r_equilibrio=r_eq,
        equilibrio_pesos=eq_pesos,
        veredicto=veredicto,
        es_caso_especial=es_caso_especial,
        avisos=avisos,
    )