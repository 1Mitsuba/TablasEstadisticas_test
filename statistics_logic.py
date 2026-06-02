from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any


EPSILON = 1e-9


@dataclass(frozen=True)
class FrequencyRow:
    interval: str
    fi: int
    hi: float
    pi: float
    Fi: int
    Hi: float
    Pi: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "intervalo": self.interval,
            "fi": self.fi,
            "hi": round(self.hi, 3),
            "pi": round(self.pi, 2),
            "Fi": self.Fi,
            "Hi": round(self.Hi, 3),
            "Pi": round(self.Pi, 2),
        }


@dataclass(frozen=True)
class ClassInterval:
    lower: float
    upper: float
    is_last: bool

    @property
    def label(self) -> str:
        closing = "]" if self.is_last else ")"
        return f"[{_format_number(self.lower)} ; {_format_number(self.upper)}{closing}"

    def contains(self, value: float) -> bool:
        if self.is_last:
            return self.lower <= value <= self.upper + EPSILON
        return self.lower <= value < self.upper


@dataclass(frozen=True)
class RangeCorrection:
    original_lower: float
    original_upper: float
    original_length: float
    leftover: float
    lower_correction: float
    upper_correction: float
    corrected_lower: float
    corrected_upper: float
    corrected_length: float
    was_applied: bool
    description: str


def parse_numbers(raw: str) -> list[float]:
    """Convierte texto separado por comas, espacios o saltos de linea en numeros."""
    normalized = raw.replace(";", " ").replace(",", " ")
    tokens = [token.strip() for token in normalized.split() if token.strip()]
    if not tokens:
        raise ValueError("Debe ingresar al menos un dato numerico.")

    values: list[float] = []
    invalid_tokens: list[str] = []
    for token in tokens:
        try:
            values.append(float(token))
        except ValueError:
            invalid_tokens.append(token)

    if invalid_tokens:
        raise ValueError(f"Datos no numericos encontrados: {', '.join(invalid_tokens)}")
    return values


def calculate_frequency_table(
    values: list[float],
    technique: str,
    arbitrary_k: int | None = None,
) -> dict[str, Any]:
    if not values:
        raise ValueError("Debe ingresar al menos un dato numerico.")

    sorted_values = sorted(values)
    n = len(sorted_values)
    distinct_count = len(set(sorted_values))

    if technique == "simple":
        if distinct_count >= 10:
            raise ValueError("La simple inspeccion se utiliza cuando existen menos de 10 valores distintos.")
        return _simple_inspection(sorted_values)
    if technique == "arbitrary":
        if n <= 19:
            raise ValueError("La distribucion arbitraria es aplicable cuando n > 19.")
        k = arbitrary_k if arbitrary_k is not None else _recommended_arbitrary_k(n)
        if not (5 <= k <= 7):
            raise ValueError("Para distribucion arbitraria, K debe estar entre 5 y 7.")
        return _grouped_distribution(sorted_values, k, "arbitrary")
    if technique == "sturges":
        if not (14 < n < 12000):
            raise ValueError("Sturges es aplicable cuando 14 < n < 12000.")
        k = max(1, round(1 + 3.3 * math.log10(n)))
        return _grouped_distribution(sorted_values, k, "sturges")
    if technique == "max_integer":
        if not (30 <= n <= 300):
            raise ValueError("Maximo entero es aplicable cuando 30 <= n <= 300.")
        k = max(1, int(10 * math.log10(n)))
        return _grouped_distribution(sorted_values, k, "max_integer")

    raise ValueError("Tecnica estadistica no reconocida.")


def _simple_inspection(values: list[float]) -> dict[str, Any]:
    """Agrupa por valor unico y calcula frecuencias absolutas, relativas y acumuladas."""
    n = len(values)
    counts = Counter(values)
    rows = _build_rows(
        labels=[_format_number(value) for value in sorted(counts)],
        frequencies=[counts[value] for value in sorted(counts)],
        n=n,
    )

    result = {
        "technique": "Simple inspeccion",
        "metadata": {
            "n": n,
            "d": min(values),
            "D": max(values),
            "valores_distintos": len(counts),
        },
        "steps": [
            "Se ordenaron los datos de menor a mayor.",
            f"Se identificaron {len(counts)} valores unicos.",
            "Se conto la aparicion de cada valor para obtener fi.",
            "Se calcularon hi, pi, Fi, Hi y Pi con las formulas indicadas.",
        ],
        "formulas": [
            "hi = fi / n",
            "pi = hi x 100",
            "Fi = suma acumulada de fi",
            "Hi = Fi / n",
            "Pi = Hi x 100",
        ],
        "rows": [row.to_dict() for row in rows],
    }
    result["validations"] = _validate_rows(rows, n)
    return result


def _grouped_distribution(values: list[float], k: int, technique: str) -> dict[str, Any]:
    """Construye intervalos semiabiertos y cuenta cada dato dentro de su clase."""
    n = len(values)
    d_original = min(values)
    D_original = max(values)
    max_decimals = _get_max_decimals(values)
    c = _calculate_c(max_decimals)
    la = D_original - d_original + c
    t_raw = la / k
    t = math.ceil(t_raw)  # Redondea al próximo número entero superior

    # CORRECCIÓN OBLIGATORIA DE ALCANCE
    range_correction = _calculate_range_correction(
        d=d_original,
        D=D_original,
        la=la,
        t=t,
        k=k,
        decimals=max_decimals
    )

    # Usar los límites corregidos
    d = range_correction.corrected_lower
    D = range_correction.corrected_upper

    # Recalcular la longitud corregida
    la_corrected = range_correction.corrected_length

    # Construir intervalos con límites corregidos
    intervals = []
    frequencies: list[int] = []
    lower = d
    for index in range(k):
        upper = lower + t
        is_last = index == k - 1
        fi = sum(1 for value in values if lower <= value < upper or (is_last and lower <= value <= upper))
        label = f"[{_format_number(lower)} ; {_format_number(upper)}{']' if is_last else ')'}"
        intervals.append(label)
        frequencies.append(fi)
        lower = upper

    rows = _build_rows(intervals, frequencies, n)
    formulas = _grouped_formulas(technique)
    steps = _grouped_steps(technique, n, d_original, D_original, c, la, k, t_raw, t, max_decimals, range_correction)

    result = {
        "technique": _technique_title(technique),
        "metadata": {
            "n": n,
            "d": d_original,
            "D": D_original,
            "d_original": d_original,
            "D_original": D_original,
            "d_corrected": d,
            "D_corrected": D,
            "c": c,
            "la": round(la, 4),
            "la_original": round(la, 4),
            "la_corrected": round(la_corrected, 4),
            "K": k,
            "t": int(t),
            "leftover": round(range_correction.leftover, 4),
            "correction_applied": range_correction.was_applied,
            "cobertura": f"{_format_number(d)} a {_format_number(D)}",
        },
        "range_correction": {
            "original_range": f"[{_format_number(range_correction.original_lower)} ; {_format_number(range_correction.original_upper)}]",
            "original_length": round(range_correction.original_length, 4),
            "leftover": round(range_correction.leftover, 4),
            "lower_adjustment": round(range_correction.lower_correction, 4),
            "upper_adjustment": round(range_correction.upper_correction, 4),
            "corrected_range": f"[{_format_number(range_correction.corrected_lower)} ; {_format_number(range_correction.corrected_upper)}]",
            "corrected_length": round(range_correction.corrected_length, 4),
            "was_applied": range_correction.was_applied,
            "description": range_correction.description,
        },
        "steps": steps,
        "formulas": formulas,
        "rows": [row.to_dict() for row in rows],
    }
    result["validations"] = _validate_rows(rows, n)
    result["validations"].extend(_validate_intervals(rows, values, d, D))
    return result


def _build_rows(labels: list[str], frequencies: list[int], n: int) -> list[FrequencyRow]:
    rows: list[FrequencyRow] = []
    cumulative = 0
    for label, fi in zip(labels, frequencies):
        cumulative += fi
        hi = fi / n
        Hi = cumulative / n
        rows.append(
            FrequencyRow(
                interval=label,
                fi=fi,
                hi=hi,
                pi=hi * 100,
                Fi=cumulative,
                Hi=Hi,
                Pi=Hi * 100,
            )
        )
    return rows


def _calculate_range_correction(
    d: float,
    D: float,
    la: float,
    t: float,
    k: int,
    decimals: int,
) -> RangeCorrection:
    """
    Calcula la corrección de alcance obligatoria.
    
    PASO 1: Calcular sobrante = (t × K) - la
    PASO 2: Si sobrante = 0, no hay corrección
    PASO 3: Si sobrante > 0:
        - CASO A (PAR): dividir en partes iguales
        - CASO B (IMPAR): dividir asimétricamente
    """
    # PASO 1: Calcular sobrante
    leftover = (t * k) - la
    
    # Redondear el sobrante para detectar si es entero
    leftover_rounded = round(leftover, decimals)
    
    # PASO 2: Verificar si no hay sobrante
    if math.isclose(leftover_rounded, 0, abs_tol=EPSILON):
        return RangeCorrection(
            original_lower=d,
            original_upper=D,
            original_length=la,
            leftover=0,
            lower_correction=0,
            upper_correction=0,
            corrected_lower=d,
            corrected_upper=D,
            corrected_length=la,
            was_applied=False,
            description="Sobrante = 0. No se requiere corrección de alcance.",
        )
    
    # PASO 3: Hay sobrante positivo, aplicar corrección
    if math.isclose(leftover_rounded % 2, 0, abs_tol=EPSILON):
        # CASO A: Sobrante PAR
        correction = leftover_rounded / 2
        lower_correction = correction
        upper_correction = correction
        description = f"Sobrante PAR ({int(leftover_rounded)}): Se divide en partes iguales ({int(correction)} a cada lado)."
    else:
        # CASO B: Sobrante IMPAR
        lower_correction = math.floor(leftover_rounded / 2)
        upper_correction = leftover_rounded - lower_correction
        description = f"Sobrante IMPAR ({int(leftover_rounded)}): Corrección asimétrica ({int(lower_correction)} abajo, {int(upper_correction)} arriba)."
    
    corrected_lower = d - lower_correction
    corrected_upper = D + upper_correction
    corrected_length = corrected_upper - corrected_lower + (10 ** (-decimals) if decimals > 0 else 1)
    
    return RangeCorrection(
        original_lower=d,
        original_upper=D,
        original_length=la,
        leftover=leftover_rounded,
        lower_correction=lower_correction,
        upper_correction=upper_correction,
        corrected_lower=corrected_lower,
        corrected_upper=corrected_upper,
        corrected_length=corrected_length,
        was_applied=True,
        description=description,
    )


def _validate_intervals(
    rows: list[FrequencyRow],
    values: list[float],
    d: float,
    D: float,
) -> list[dict[str, Any]]:
    """
    Validaciones obligatorias para asegurar que los intervalos sean correctos.
    
    Reglas:
    1. Todos los datos deben pertenecer a algún intervalo
    2. Ningún dato puede quedar fuera del primer o último intervalo
    3. El primer intervalo debe incluir el dato mínimo
    4. El último intervalo debe incluir el dato máximo
    5. Verificar que no haya intervalos vacíos en extremos
    """
    validations = []
    
    # Regla 1: Todos los datos deben estar en algún intervalo
    min_val = min(values)
    max_val = max(values)
    
    # El primer intervalo debe contener el mínimo
    first_row = rows[0]
    first_contains_min = f"[{_format_number(d)}" in first_row.interval and min_val >= d
    validations.append({
        "name": "Primer intervalo incluye dato mínimo",
        "ok": first_contains_min,
        "value": f"Min = {_format_number(min_val)}, primer intervalo comienza en {_format_number(d)}",
        "expected": "Min >= límite inferior",
        "message": "Correcto" if first_contains_min else "Error: el dato mínimo no está en el primer intervalo.",
    })
    
    # El último intervalo debe contener el máximo
    last_row = rows[-1]
    last_contains_max = max_val <= D and "]" in last_row.interval
    validations.append({
        "name": "Último intervalo incluye dato máximo",
        "ok": last_contains_max,
        "value": f"Max = {_format_number(max_val)}, último intervalo termina en {_format_number(D)}",
        "expected": "Max <= límite superior",
        "message": "Correcto" if last_contains_max else "Error: el dato máximo no está en el último intervalo.",
    })
    
    # No debe haber intervalos vacíos en los extremos
    has_empty_extremes = any(row.fi == 0 for row in [rows[0], rows[-1]])
    validations.append({
        "name": "Sin intervalos vacíos en extremos",
        "ok": not has_empty_extremes,
        "value": f"Primer fi = {rows[0].fi}, Último fi = {rows[-1].fi}",
        "expected": "Ambos > 0",
        "message": "Correcto" if not has_empty_extremes else "Error: hay intervalos vacíos en los extremos.",
    })
    
    # Verificar que no haya datos fuera de los intervalos
    total_in_intervals = sum(row.fi for row in rows)
    all_data_included = total_in_intervals == len(values)
    validations.append({
        "name": "Todos los datos están clasificados",
        "ok": all_data_included,
        "value": f"Datos clasificados = {total_in_intervals}, Total = {len(values)}",
        "expected": f"Ambos = {len(values)}",
        "message": "Correcto" if all_data_included else f"Error: {len(values) - total_in_intervals} datos sin clasificar.",
    })
    
    return validations


def _validate_rows(rows: list[FrequencyRow], n: int) -> list[dict[str, Any]]:
    sum_fi = sum(row.fi for row in rows)
    sum_hi = sum(row.hi for row in rows)
    sum_pi = sum(row.pi for row in rows)
    last = rows[-1]
    checks = [
        (f"Suma fi = {n}", sum_fi == n, sum_fi, n),
        ("Suma hi = 1.000", math.isclose(sum_hi, 1, abs_tol=EPSILON), round(sum_hi, 3), 1.000),
        ("Suma pi = 100", math.isclose(sum_pi, 100, abs_tol=EPSILON), round(sum_pi, 2), 100),
        (f"Ultimo Fi = {n}", last.Fi == n, last.Fi, n),
        ("Ultimo Hi = 1.000", math.isclose(last.Hi, 1, abs_tol=EPSILON), round(last.Hi, 3), 1.000),
        ("Ultimo Pi = 100", math.isclose(last.Pi, 100, abs_tol=EPSILON), round(last.Pi, 2), 100),
    ]
    return [
        {
            "name": name,
            "ok": ok,
            "value": value,
            "expected": expected,
            "message": "Correcto" if ok else f"Error: se obtuvo {value}, se esperaba {expected}.",
        }
        for name, ok, value, expected in checks
    ]


def _recommended_arbitrary_k(n: int) -> int:
    if n < 40:
        return 5
    if n < 80:
        return 6
    return 7


def _grouped_formulas(technique: str) -> list[str]:
    common = [
        "hi = fi / n",
        "pi = hi x 100",
        "Fi = suma acumulada de fi",
        "Hi = Fi / n",
        "Pi = Hi x 100",
    ]
    if technique == "arbitrary":
        return ["a = [d ; D]", "la = D - d + c", "t = la / K"] + common
    if technique == "sturges":
        return ["a = [d ; D]", "la = D - d + 1", "K = 1 + 3.3 x log(n)", "t = la / K"] + common
    return ["a = [d ; D]", "la = D - d + 1", "K = parte_entera(10 x log(n))", "t = la / K"] + common


def _grouped_steps(
    technique: str,
    n: int,
    d: float,
    D: float,
    c: float,
    la: float,
    k: int,
    t_raw: float,
    t: float,
    max_decimals: int,
    range_correction: RangeCorrection | None = None,
) -> list[str]:
    if technique == "arbitrary":
        intro = f"Como n = {n} > 19, se aplica la distribucion arbitraria."
        k_step = f"K = {k}, elegido dentro del rango recomendado."
    elif technique == "sturges":
        intro = f"Como 14 < n = {n} < 12000, se aplica Sturges."
        k_step = f"K = redondeo(1 + 3.3 x log10({n})) = {k}."
    else:
        intro = f"Como 30 <= n = {n} <= 300, se aplica Maximo Entero."
        k_step = f"K = 10 x log10({n}) = {k}."

    # Determinar la descripción de c basada en decimales
    if max_decimals == 0:
        c_description = "Se detectaron datos enteros, por lo que c = 1."
    elif max_decimals == 1:
        c_description = "Se detectaron datos con 1 decimal, por lo que c = 0.1."
    elif max_decimals == 2:
        c_description = "Se detectaron datos con 2 decimales, por lo que c = 0.01."
    elif max_decimals == 3:
        c_description = "Se detectaron datos con 3 decimales, por lo que c = 0.001."
    else:
        c_description = f"Se detectaron datos con {max_decimals} decimales, por lo que c = {c}."

    # Formato para mostrar t_raw con decimales y t como entero
    t_raw_display = f"{t_raw:.4f}".rstrip('0').rstrip('.')
    
    steps = [
        intro,
        f"Se determino d = {_format_number(d)} y D = {_format_number(D)}.",
        c_description,
        f"Se calculo la amplitud la = D - d + c = {_format_number(D)} - {_format_number(d)} + {c} = {round(la, 4)}.",
        k_step,
        f"Se calculo t = la / K = {round(la, 4)} / {k} = {t_raw_display}. Se redondeo hacia arriba obteniendo: t = {int(t)}.",
    ]
    
    # Agregar pasos de corrección de alcance
    if range_correction:
        steps.append(f"VERIFICACION DE CORRECCIÓN DE ALCANCE (OBLIGATORIA)")
        steps.append(f"Sobrante = (t × K) - la = ({int(t)} × {k}) - {round(la, 4)} = {round(range_correction.leftover, 4)}")
        
        if range_correction.was_applied:
            if range_correction.leftover == int(range_correction.leftover) and int(range_correction.leftover) % 2 == 0:
                steps.append(f"Sobrante es PAR ({int(range_correction.leftover)}): Se divide en partes iguales.")
                steps.append(f"Corrección = {int(range_correction.leftover)} / 2 = {int(range_correction.lower_correction)}")
                steps.append(f"Nuevo d = {_format_number(d)} - {int(range_correction.lower_correction)} = {_format_number(range_correction.corrected_lower)}")
                steps.append(f"Nuevo D = {_format_number(D)} + {int(range_correction.upper_correction)} = {_format_number(range_correction.corrected_upper)}")
            else:
                steps.append(f"Sobrante es IMPAR ({int(range_correction.leftover)}): Corrección asimétrica.")
                steps.append(f"Corrección inferior = truncar({int(range_correction.leftover)} / 2) = {int(range_correction.lower_correction)}")
                steps.append(f"Corrección superior = {int(range_correction.leftover)} - {int(range_correction.lower_correction)} = {int(range_correction.upper_correction)}")
                steps.append(f"Nuevo d = {_format_number(d)} - {int(range_correction.lower_correction)} = {_format_number(range_correction.corrected_lower)}")
                steps.append(f"Nuevo D = {_format_number(D)} + {int(range_correction.upper_correction)} = {_format_number(range_correction.corrected_upper)}")
            steps.append(f"ALCANCE CORREGIDO: [{_format_number(range_correction.corrected_lower)} ; {_format_number(range_correction.corrected_upper)}]")
        else:
            steps.append(f"Sobrante = 0: NO se requiere corrección. Se mantiene el alcance original.")
    
    steps.append("Se generaron intervalos semiabiertos [Li ; Ls) y el ultimo intervalo incluye el extremo superior.")
    steps.append("Se calcularon fi, hi, pi, Fi, Hi y Pi.")
    
    return steps


def _ceil_to_precision(value: float, decimals: int) -> float:
    """Redondea un valor hacia el entero superior (ceiling) manteniendo la precisión decimal.
    
    Funciona correctamente tanto con valores positivos como negativos.
    """
    factor = 10 ** decimals
    # Escala el valor, aplica ceiling, y luego devuelve a la escala original
    scaled = value * factor
    # Restamos EPSILON para evitar problemas de precisión flotante
    return math.ceil(scaled - EPSILON) / factor


def _count_decimals(value: float) -> int:
    """Cuenta la cantidad de decimales significativos en un número."""
    if math.isclose(value, round(value), abs_tol=EPSILON):
        return 0
    # Convierte a string y cuenta decimales
    str_value = f"{value:.10f}".rstrip("0").rstrip(".")
    if "." in str_value:
        return len(str_value.split(".")[1])
    return 0


def _get_max_decimals(values: list[float]) -> int:
    """Obtiene la cantidad máxima de decimales en la lista de valores."""
    if not values:
        return 0
    return max(_count_decimals(value) for value in values)


def _calculate_c(max_decimals: int) -> float:
    """Calcula el valor de c basado en la cantidad máxima de decimales."""
    if max_decimals == 0:
        return 1.0
    elif max_decimals == 1:
        return 0.1
    elif max_decimals == 2:
        return 0.01
    elif max_decimals == 3:
        return 0.001
    else:
        # Para más de 3 decimales, usar la potencia correspondiente
        return 10 ** (-max_decimals)


def _has_decimals(values: list[float]) -> bool:
    return any(not math.isclose(value, round(value), abs_tol=EPSILON) for value in values)


def _format_number(value: float) -> str:
    if math.isclose(value, round(value), abs_tol=EPSILON):
        return str(int(round(value)))
    return f"{value:.4f}".rstrip("0").rstrip(".")


def _technique_title(technique: str) -> str:
    titles = {
        "arbitrary": "Distribucion arbitraria",
        "sturges": "Sturges",
        "max_integer": "Maximo entero",
    }
    return titles[technique]
