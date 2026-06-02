#!/usr/bin/env python
"""Script para probar la detección automática de precisión de datos."""

from statistics_logic import calculate_frequency_table

# Prueba 1: Datos enteros
print("=== PRUEBA 1: Datos enteros ===")
result = calculate_frequency_table([12, 15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 40, 42, 45, 48], 'sturges')
print(f"c usado: {result['metadata']['c']}")
print(f"Pasos de detección:")
print(f"  {result['steps'][2]}\n")

# Prueba 2: Datos con 1 decimal
print("=== PRUEBA 2: Datos con 1 decimal ===")
result = calculate_frequency_table([12.3, 15.7, 18.4, 20.1, 22.5, 25.8, 28.2, 30.6, 32.9, 35.3, 38.7, 40.2, 42.5, 45.1, 48.9], 'sturges')
print(f"c usado: {result['metadata']['c']}")
print(f"Pasos de detección:")
print(f"  {result['steps'][2]}\n")

# Prueba 3: Datos con 2 decimales
print("=== PRUEBA 3: Datos con 2 decimales ===")
result = calculate_frequency_table([12.35, 15.72, 18.41, 20.51, 22.62, 25.83, 28.24, 30.65, 32.96, 35.37, 38.78, 40.29, 42.50, 45.13, 48.96], 'sturges')
print(f"c usado: {result['metadata']['c']}")
print(f"Pasos de detección:")
print(f"  {result['steps'][2]}\n")

# Prueba 4: Datos con 3 decimales
print("=== PRUEBA 4: Datos con 3 decimales ===")
result = calculate_frequency_table([12.357, 15.721, 18.416, 20.512, 22.625, 25.837, 28.241, 30.652, 32.963, 35.374, 38.785, 40.296, 42.503, 45.134, 48.965], 'sturges')
print(f"c usado: {result['metadata']['c']}")
print(f"Pasos de detección:")
print(f"  {result['steps'][2]}\n")

print("✅ ¡Todas las pruebas completadas exitosamente!")
