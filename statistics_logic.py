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
    d = min(values)
    D = max(values)
    max_decimals = _get_max_decimals(values)
    c = _calculate_c(max_decimals)
    la = D - d + c
    t_raw = la / k
    t = math.ceil(t_raw)  # Redondea al próximo número entero superior
    coverage = t * k

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
    steps = _grouped_steps(technique, n, d, D, c, la, k, t_raw, t, coverage, max_decimals)

    result = {
        "technique": _technique_title(technique),
        "metadata": {
            "n": n,
            "d": d,
            "D": D,
            "c": c,
            "la": round(la, 4),
            "K": k,
            "t": int(t),
            "cobertura": round(coverage, 4),
        },
        "steps": steps,
        "formulas": formulas,
        "rows": [row.to_dict() for row in rows],
    }
    result["validations"] = _validate_rows(rows, n)
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
        return ["a = [d ; D]", "la = D - d + c", "t = la / K", "t x K >= la"] + common
    if technique == "sturges":
        return ["a = [d ; D]", "la = D - d + 1", "K = 1 + 3.3 x log(n)", "t = la / K", "t x K >= la"] + common
    return ["a = [d ; D]", "la = D - d + 1", "K = parte_entera(10 x log(n))", "t = la / K", "t x K >= la"] + common


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
    coverage: float,
    max_decimals: int,
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
    
    return [
        intro,
        f"Se determino d = {_format_number(d)} y D = {_format_number(D)}.",
        c_description,
        f"Se calculo la amplitud la = D - d + c = {_format_number(D)} - {_format_number(d)} + {c} = {round(la, 4)}.",
        k_step,
        f"Se calculo t = la / K = {round(la, 4)} / {k} = {t_raw_display}. Se redondeo hacia arriba obteniendo: t = {int(t)}.",
        f"Se verifico t x K = {int(t)} x {k} = {round(coverage, 4)} >= la = {round(la, 4)}.",
        "Se generaron intervalos semiabiertos [Li ; Ls) y el ultimo intervalo incluye el extremo superior.",
        "Se calcularon fi, hi, pi, Fi, Hi y Pi.",
    ]


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
