"""Pruebas unitarias de cálculo determinista para validar vectores normativos V1 a V8."""

import json
from pathlib import Path
import unittest
import calc_iva7


class TestCalculadoraIVA7(unittest.TestCase):
    """Pruebas de regresión aritmética para validar exactitud al peso."""

    @classmethod
    def setUpClass(cls):
        """Carga el archivo de configuración oficial antes de ejecutar las pruebas."""
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
        self.assertEqual(res.pago_opcion_anual, 42000)
        self.assertEqual(res.ahorro_anual, 44400)
        self.assertEqual(res.veredicto, "CONVIENE")

    def test_v2_comercio_gastos_altos(self):
        """V2: Comercio con altos gastos de operación; debe resultar NO_CONVIENE."""
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
        self.assertEqual(res.pago_opcion_anual, 84000)
        self.assertEqual(res.ahorro_anual, -26400)
        self.assertEqual(res.veredicto, "NO_CONVIENE")

    def test_v3_empate_zona_gris(self):
        """V3: Gastos en punto exacto de equilibrio; debe resultar ZONA_GRIS."""
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
        self.assertEqual(res.pago_opcion_anual, 84000)
        self.assertEqual(res.ahorro_anual, 0)
        self.assertEqual(res.veredicto, "ZONA_GRIS")

    def test_v4_con_retenciones_saldo_favor(self):
        """V4: Retenciones mensuales que generan saldo a favor bajo la opción 7 %."""
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
        self.assertEqual(res.pago_opcion_anual, -26400)
        self.assertEqual(res.ahorro_anual, 45600)
        self.assertEqual(res.veredicto, "CONVIENE")
        self.assertTrue(any("saldo a favor" in aviso.lower() for aviso in res.avisos))

    def test_v5_frontera_zona_gris(self):
        """V5: Operación en región fronteriza al 8 %; diferencia menor a zona gris."""
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
        self.assertEqual(res.pago_opcion_anual, 84000)
        self.assertEqual(res.ahorro_anual, 2400)
        self.assertEqual(res.veredicto, "ZONA_GRIS")

    def test_v6_inversion_compra_grande(self):
        """V6: Inversión en activo fijo durante el año; debe resultar CONVIENE."""
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
        self.assertEqual(res.pago_opcion_anual, 33600)
        self.assertEqual(res.ahorro_anual, 16960)
        self.assertEqual(res.veredicto, "CONVIENE")

    def test_v7_ingresos_exentos(self):
        """V7: Presencia de ingresos exentos o tasa 0 %; debe detener veredicto automático."""
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

    def test_v8_supera_limite_resico(self):
        """V8: Ingresos que rebasan el tope legal de RESICO PF; marca caso especial."""
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


if __name__ == "__main__":
    unittest.main()