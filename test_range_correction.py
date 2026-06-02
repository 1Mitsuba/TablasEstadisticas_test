"""
TEST DE CORRECCIÓN DE ALCANCE
Verifica que la corrección de alcance funciona correctamente para:
- Sobrante = 0 (sin corrección)
- Sobrante PAR (corrección simétrica)
- Sobrante IMPAR (corrección asimétrica)
"""

from statistics_logic import calculate_frequency_table, parse_numbers

def test_case(name: str, data_str: str, technique: str, k: int = None):
    """Ejecuta un caso de prueba y muestra los resultados."""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}")
    
    try:
        values = parse_numbers(data_str)
        result = calculate_frequency_table(values, technique, k)
        
        print(f"\n📊 TÉCNICA: {result['technique']}")
        print(f"📈 Datos (n={len(values)}): {sorted(values)}")
        print(f"\n📐 METADATOS:")
        print(f"   Dato mínimo original (d): {result['metadata']['d_original']}")
        print(f"   Dato máximo original (D): {result['metadata']['D_original']}")
        print(f"   Longitud alcance original (la): {result['metadata']['la_original']}")
        print(f"   Número de intervalos (K): {result['metadata']['K']}")
        print(f"   Tamaño de clase (t): {result['metadata']['t']}")
        
        print(f"\n🔧 CORRECCIÓN DE ALCANCE:")
        rc = result['range_correction']
        print(f"   Alcance original: {rc['original_range']}")
        print(f"   Longitud original: {rc['original_length']}")
        print(f"   Sobrante (t×K - la): {rc['leftover']}")
        print(f"   Corrección inferior: {rc['lower_adjustment']}")
        print(f"   Corrección superior: {rc['upper_adjustment']}")
        print(f"   Alcance corregido: {rc['corrected_range']}")
        print(f"   Longitud corregida: {rc['corrected_length']}")
        print(f"   ¿Se aplicó corrección?: {'SÍ' if rc['was_applied'] else 'NO'}")
        print(f"   Descripción: {rc['description']}")
        
        print(f"\n📋 TABLA DE FRECUENCIAS:")
        print(f"{'Intervalo':<20} {'fi':<6} {'hi':<8} {'pi':<8} {'Fi':<6} {'Hi':<8} {'Pi':<8}")
        print("-" * 80)
        for row in result['rows']:
            print(f"{row['intervalo']:<20} {row['fi']:<6} {row['hi']:<8} {row['pi']:<8} {row['Fi']:<6} {row['Hi']:<8} {row['Pi']:<8}")
        
        print(f"\n✅ VALIDACIONES:")
        for val in result['validations']:
            status = "✓" if val['ok'] else "✗"
            print(f"   {status} {val['name']}: {val['message']}")
        
        print(f"\n📝 PASOS DE CÁLCULO:")
        for i, step in enumerate(result['steps'], 1):
            if "VERIFICACION" in step or "ALCANCE CORREGIDO" in step:
                print(f"   [{i}] 🔴 {step}")
            else:
                print(f"   [{i}] {step}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")


# ============================================================================
# CASO 1: Sobrante = 0 (SIN CORRECCIÓN)
# ============================================================================
test_case(
    name="CASO 1: Sobrante = 0 (Sin corrección)",
    data_str="10 12 15 18 20 22 25 28 30 32 35 38 40 42 45 48 50 52 55 58 60 62 65",
    technique="arbitrary",
    k=5
)


# ============================================================================
# CASO 2: Sobrante PAR (CORRECCIÓN SIMÉTRICA)
# ============================================================================
test_case(
    name="CASO 2: Sobrante PAR (Corrección simétrica)",
    data_str="5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 105 110 115 120",
    technique="arbitrary",
    k=6
)


# ============================================================================
# CASO 3: Sobrante IMPAR (CORRECCIÓN ASIMÉTRICA)
# ============================================================================
test_case(
    name="CASO 3: Sobrante IMPAR (Corrección asimétrica)",
    data_str="1 5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 100 105 110",
    technique="arbitrary",
    k=5
)


# ============================================================================
# CASO 4: Sturges con corrección
# ============================================================================
test_case(
    name="CASO 4: Sturges con corrección automática",
    data_str="100 102 105 108 110 112 115 118 120 125 130 135 140 145 150 155 160 165 170 175 180",
    technique="sturges"
)


# ============================================================================
# CASO 5: Máximo Entero con corrección
# ============================================================================
test_case(
    name="CASO 5: Máximo Entero con corrección automática",
    data_str="2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 36 38 40 42 44 46 48 50 52 54 56 58 60 62 64 66 68 70",
    technique="max_integer"
)

print(f"\n{'='*80}")
print("✅ TODOS LOS TESTS COMPLETADOS")
print(f"{'='*80}\n")
