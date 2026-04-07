import pandas as pd
import numpy_financial as npf

FRECUENCIAS = {
    "mensual": 12,
    "trimestral": 4,
    "semestral": 2,
    "anual": 1
}


def calcular_tin_anual(euribor_anual, tipo_interes, bonificacion=0.0):
    """
    Devuelve el tipo nominal anual en formato decimal.
    euribor_anual: por ejemplo 0.025 para 2,5%
    tipo_interes: 'fijo' o 'variable'
    bonificacion: por ejemplo 0.001 para 0,10%
    """
    if tipo_interes == "fijo":
        tin = euribor_anual + 0.01
    elif tipo_interes == "variable":
        tin = euribor_anual + 0.005
    else:
        raise ValueError("El tipo de interés debe ser 'fijo' o 'variable'.")

    tin -= bonificacion

    if tin < 0:
        tin = 0

    return tin


def calcular_cuota_francesa(capital, tin_anual, pagos_por_anio, anios):
    """
    Calcula la cuota constante del sistema francés.
    """
    n = pagos_por_anio * anios
    i = tin_anual / pagos_por_anio

    if i == 0:
        return capital / n

    cuota = capital * (i / (1 - (1 + i) ** (-n)))
    return cuota


def generar_cuadro_amortizacion(capital, tin_anual, pagos_por_anio, anios):
    """
    Genera el cuadro de amortización sin comisiones ni gastos.
    """
    n = pagos_por_anio * anios
    i = tin_anual / pagos_por_anio
    cuota = calcular_cuota_francesa(capital, tin_anual, pagos_por_anio, anios)

    saldo = capital
    datos = []

    for periodo in range(1, n + 1):
        interes = round(saldo * i, 2)
        amortizacion = round(cuota - interes, 2)

        # Ajuste final para evitar errores por redondeo
        if periodo == n:
            amortizacion = saldo
            cuota_real = interes + amortizacion
            saldo_final = 0.0
        else:
            cuota_real = cuota
            saldo_final = saldo - amortizacion

        datos.append({
            "Periodo": periodo,
            "Saldo inicial": round(saldo, 2),
            "Cuota": round(cuota_real, 2),
            "Interés": round(interes, 2),
            "Amortización": round(amortizacion, 2),
            "Saldo final": round(saldo_final, 2)
        })

        saldo = saldo_final

    return pd.DataFrame(datos)


def calcular_tae(capital, cuota, num_cuotas, pagos_por_anio, gasto_estudio=150, gasto_admin_ratio=0.001):
    """
    Calcula el coste efectivo anual (TAE) usando los flujos de caja.
    Se considera:
    - Momento 0: capital recibido - gasto de estudio
    - Cada cuota: cuota + gasto de administración
    """
    flujo_inicial = capital - gasto_estudio
    gasto_admin = cuota * gasto_admin_ratio

    flujos = [flujo_inicial] + [-(cuota + gasto_admin)] * num_cuotas

    tir_periodica = npf.irr(flujos)
    tae = (1 + tir_periodica) ** pagos_por_anio - 1

    return tae


def simular_prestamo(capital, anios, frecuencia, euribor_anual, tipo_interes, bonificacion):
    """
    Función principal del backend.
    """
    frecuencia = frecuencia.lower()

    if frecuencia not in FRECUENCIAS:
        raise ValueError("Frecuencia no válida.")

    pagos_por_anio = FRECUENCIAS[frecuencia]

    tin_anual = calcular_tin_anual(
        euribor_anual=euribor_anual,
        tipo_interes=tipo_interes,
        bonificacion=bonificacion
    )

    cuota = calcular_cuota_francesa(
        capital=capital,
        tin_anual=tin_anual,
        pagos_por_anio=pagos_por_anio,
        anios=anios
    )

    cuadro = generar_cuadro_amortizacion(
        capital=capital,
        tin_anual=tin_anual,
        pagos_por_anio=pagos_por_anio,
        anios=anios
    )

    num_cuotas = pagos_por_anio * anios

    tae = calcular_tae(
        capital=capital,
        cuota=cuota,
        num_cuotas=num_cuotas,
        pagos_por_anio=pagos_por_anio
    )

    return {
        "tin_anual": tin_anual,
        "cuota": cuota,
        "tae": tae,
        "cuadro_amortizacion": cuadro
    }