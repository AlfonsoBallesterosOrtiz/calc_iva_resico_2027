"""Pruebas de regresión unitaria para validar los 10 vectores normativos de prueba."""

import json
from pathlib import Path
import unittest
import calc_iva7


class TestCalculadoraIVA7(unittest.TestCase):
    """Valida que cada vector de prueba coincida al peso y cumpla los veredictos normativos."""

    @classmethod
    def setUpClass(cls):
        """Carga el archivo de configuración legal para los ensayos."""
        ruta_cfg = Path(__file__).parent / "config_ley.json"
        with open(ruta_cfg, "r", encoding="utf-8") as f:
            cls.config = json.load(f)

    def test_v1_servicios_gastos_bajos(self):
        """V1: Servicios con gastos reducidos; debe resultar CONVIENE."""
        res = calc_iva7.calcular_comparativa(
            region="general",
            ingresos=50000,
            hay_exentos_o_tasa0=False,
            gastos=5000,
            iva_retenido=0,
            compra_grande=0,
            config=self.config
        )
        self.assertEqual(res.b_anual, 600000)
        self.assertEqual(res.iva_acreditable_anual, 9600)
        self.assertEqual(res.pago_normal_anual, 86400)
        self.assertEqual(res.opcion_matematica, 42000)
        self.assertEqual(res.ahorro_anual, 44400)
        self.assertEqual(res.veredicto, "CONVIENE")

    def test_v2_comercio_gastos_altos(self):
        """V2: Comercio con gastos elevados; debe resultar NO_CONVIENE."""
        res = calc_iva7.calcular_comparativa(
            region="general",
            ingresos=100000,
            hay_exentos_o_tasa0=False,
            gastos=70000,
            iva_retenido=0,
            compra_grande=0,
            config=self.config
        )
        self.assertEqual(res.b_anual, 1200000)
        self.assertEqual(res.iva_acreditable_anual, 134400)
        self.assertEqual(res.pago_normal_anual, 57600)
        self.assertEqual(res.opcion_matematica, 84000)
        self.assertEqual(res.ahorro_anual, -26400)
        self.assertEqual(res.veredicto, "NO_CONVIENE")

    def test_v3_empate_zona_gris(self):
        """V3: Punto exacto de empate; debe resultar ZONA_GRIS."""
        res = calc_iva7.calcular_comparativa(
            region="general",
            ingresos=100000,
            hay_exentos_o_tasa0=False,
            gastos=56250,
            iva_retenido=0,
            compra_grande=0,
            config=self.config
        )
        self.assertEqual(res.b_anual, 1200000)
        self.assertEqual(res.iva_acreditable_anual, 108000)
        self.assertEqual(res.pago_normal_anual, 84000)
        self.assertEqual(res.opcion_matematica, 84000)
        self.assertEqual(res.ahorro_anual, 0)
        self.assertEqual(res.veredicto, "ZONA_GRIS")

    def test_v4_retenciones_saldo_favor_opcion(self):
        """V4: Opción genera saldo a favor; pago 0 y ahorro conservador de 19,200."""
        res = calc_iva7.calcular_comparativa(
            region="general",
            ingresos=60000,
            hay_exentos_o_tasa0=False,
            gastos=10000,
            iva_retenido=6400,
            compra_grande=0,
            config=self.config
        )
        self.assertEqual(res.b_anual, 720000)
        self.assertEqual(res.iva_acreditable_anual, 19200)
        self.assertEqual(res.pago_normal_anual, 19200)
        self.assertEqual(res.opcion_matematica, -26400)
        self.assertEqual(res.opcion_pago_anual, 0)
        self.assertEqual(res.saldo_favor_opcion, 26400)
        self.assertEqual(res.ahorro_anual, 19200)
        self.assertEqual(res.ahorro_si_se_recupera, 45600)
        self.assertEqual(res.veredicto, "CONVIENE")

    def test_v5_frontera_zona_gris(self):
        """V5: Frontera 8 % con margen pequeño; cae en ZONA_GRIS."""
        res = calc_iva7.calcular_comparativa(
            region="frontera",
            ingresos=100000,
            hay_exentos_o_tasa0=False,
            gastos=10000,
            iva_retenido=0,
            compra_grande=0,
            config=self.config
        )
        self.assertEqual(res.b_anual, 1200000)
        self.assertEqual(res.iva_acreditable_anual, 9600)
        self.assertEqual(res.pago_normal_anual, 86400)
        self.assertEqual(res.opcion_matematica, 84000)
        self.assertEqual(res.ahorro_anual, 2400)
        self.assertEqual(res.veredicto, "ZONA_GRIS")

    def test_v6_inversion_compra_grande(self):
        """V6: Inversión única en maquinaria o equipo; resulta CONVIENE."""
        res = calc_iva7.calcular_comparativa(
            region="general",
            ingresos=40000,
            hay_exentos_o_tasa0=False,
            gastos=4000,
            iva_retenido=0,
            compra_grande=116000,
            config=self.config
        )
        self.assertEqual(res.b_anual, 480000)
        self.assertEqual(res.iva_acreditable_anual, 26240)
        self.assertEqual(res.pago_normal_anual, 50560)
        self.assertEqual(res.opcion_matematica, 33600)
        self.assertEqual(res.ahorro_anual, 16960)
        self.assertEqual(res.veredicto, "CONVIENE")

    def test_v7_ingresos_exentos(self):
        """V7: Ingresos exentos o tasa 0 %; clasifica como CASO_ESPECIAL sin veredicto."""
        res = calc_iva7.calcular_comparativa(
            region="general",
            ingresos=50000,
            hay_exentos_o_tasa0=True,
            gastos=5000,
            iva_retenido=0,
            compra_grande=0,
            config=self.config
        )
        self.assertTrue(res.es_caso_especial)
        self.assertEqual(res.veredicto, "CASO_ESPECIAL")

    def test_v8_rebasa_limite_resico(self):
        """V8: Ingresos anuales mayores a 5,000,000; marca CASO_ESPECIAL."""
        res = calc_iva7.calcular_comparativa(
            region="general",
            ingresos=450000,
            hay_exentos_o_tasa0=False,
            gastos=20000,
            iva_retenido=0,
            compra_grande=0,
            config=self.config
        )
        self.assertEqual(res.b_anual, 5400000)
        self.assertTrue(res.es_caso_especial)
        self.assertEqual(res.veredicto, "CASO_ESPECIAL")

    def test_v9_criterio_conservador_saldo_favor(self):
        """V9: Normal da 0 y opción da saldo a favor; criterio conservador da ahorro 0 (ZONA_GRIS)."""
        res = calc_iva7.calcular_comparativa(
            region="general",
            ingresos=60000,
            hay_exentos_o_tasa0=False,
            gastos=20000,
            iva_retenido=6400,
            compra_grande=0,
            config=self.config
        )
        self.assertEqual(res.b_anual, 720000)
        self.assertEqual(res.iva_acreditable_anual, 38400)
        self.assertEqual(res.pago_normal_anual, 0)
        self.assertEqual(res.opcion_matematica, -26400)
        self.assertEqual(res.opcion_pago_anual, 0)
        self.assertEqual(res.saldo_favor_opcion, 26400)
        self.assertEqual(res.ahorro_anual, 0)
        self.assertEqual(res.ahorro_si_se_recupera, 26400)
        self.assertEqual(res.veredicto, "ZONA_GRIS")

    def test_v10_saldo_favor_actual_vs_pago_opcion(self):
        """V10: Inversión alta genera saldo a favor hoy; la opción cobraría 33,600 (NO_CONVIENE)."""
        res = calc_iva7.calcular_comparativa(
            region="general",
            ingresos=40000,
            hay_exentos_o_tasa0=False,
            gastos=4000,
            iva_retenido=0,
            compra_grande=600000,
            config=self.config
        )
        self.assertEqual(res.b_anual, 480000)
        self.assertEqual(res.iva_acreditable_anual, 103680)
        self.assertEqual(res.pago_normal_anual, -26880)
        self.assertEqual(res.opcion_matematica, 33600)
        self.assertEqual(res.opcion_pago_anual, 33600)
        self.assertEqual(res.ahorro_anual, -60480)
        self.assertEqual(res.veredicto, "NO_CONVIENE")


if __name__ == "__main__":
    unittest.main()