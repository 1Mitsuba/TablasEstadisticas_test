"""Pruebas para verificar que t se muestra correctamente"""

from statistics_logic import calculate_frequency_table

# Prueba 1: Datos con 1 decimal
print("=== PRUEBA 1: Datos con 1 decimal ===")
result = calculate_frequency_table([12.3, 15.7, 18.4, 20.1, 22.5, 25.8, 28.2, 30.6, 32.9, 35.3, 38.7, 40.2, 42.5, 45.1, 48.9], 'sturges')
print(f"Paso 6 - Cálculo de t:")
print(f"  {result['steps'][5]}")
print()

# Prueba 2: Datos con 3 decimales
print("=== PRUEBA 2: Datos con 3 decimales ===")
result = calculate_frequency_table([12.357, 15.721, 18.416, 20.512, 22.625, 25.837, 28.241, 30.652, 32.963, 35.374, 38.785, 40.296, 42.503, 45.134, 48.965], 'sturges')
print(f"Paso 6 - Cálculo de t:")
print(f"  {result['steps'][5]}")
print()

# Prueba 3: Datos enteros
print("=== PRUEBA 3: Datos enteros ===")
result = calculate_frequency_table([12, 15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48], 'sturges')
print(f"Paso 6 - Cálculo de t:")
print(f"  {result['steps'][5]}")
print()

# Prueba 4: 2 decimales (original del usuario)
print("=== PRUEBA 4: Datos con 2 decimales (caso del usuario) ===")
result = calculate_frequency_table([26.37, 27.45, 28.10, 28.75, 29.20, 29.84, 26.37, 27.45, 28.10, 28.75, 29.20, 29.84, 26.37, 27.45, 28.10, 28.75, 29.20, 29.84, 26.37, 27.45], 'sturges')
print(f"Paso 6 - Cálculo de t:")
print(f"  {result['steps'][5]}")
print(f"\nMetadata:")
print(f"  c: {result['metadata']['c']}")
print(f"  la: {result['metadata']['la']}")
print(f"  K: {result['metadata']['K']}")
print(f"  t: {result['metadata']['t']}")
