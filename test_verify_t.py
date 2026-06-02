"""Verificar que la tabla se genera correctamente con t redondeado"""

from statistics_logic import calculate_frequency_table

result = calculate_frequency_table(
    [26.37, 27.45, 28.10, 28.75, 29.20, 29.84, 26.37, 27.45, 28.10, 28.75, 29.20, 29.84, 
     26.37, 27.45, 28.10, 28.75, 29.20, 29.84, 26.37, 27.45], 
    'sturges'
)

print("=== METADATA ===")
print(f"n: {result['metadata']['n']}")
print(f"d: {result['metadata']['d']}")
print(f"D: {result['metadata']['D']}")
print(f"c: {result['metadata']['c']}")
print(f"la: {result['metadata']['la']}")
print(f"K: {result['metadata']['K']}")
print(f"t: {result['metadata']['t']} (ahora es entero)")
print(f"cobertura: {result['metadata']['cobertura']}")

print("\n=== PASOS ===")
for i, step in enumerate(result['steps'], 1):
    print(f"{i}. {step}")

print("\n=== VALIDACIONES ===")
for v in result['validations']:
    status = "✓" if v['ok'] else "✗"
    print(f"{status} {v['name']}: {v['message']}")

print("\n=== TABLA DE FRECUENCIAS (primeras 3 filas) ===")
for i, row in enumerate(result['rows'][:3]):
    print(f"Intervalo: {row['intervalo']}, fi: {row['fi']}, hi: {row['hi']}, pi: {row['pi']}")
