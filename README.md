# Aplicacion web de tablas de frecuencia

Aplicacion ligera para generar tablas de distribucion de frecuencias con cuatro tecnicas:

- Simple inspeccion
- Distribucion arbitraria
- Sturges
- Maximo entero

La logica estadistica esta implementada en Python. La interfaz usa HTML, CSS y JavaScript sin frameworks.

## Ejecutar

```bash
python -B app.py
```

Luego abrir:

```text
http://localhost:8000
```

## Estructura

```text
app.py                  Servidor HTTP y API JSON
statistics_logic.py     Calculos y validaciones estadisticas
static/
  index.html            Interfaz
  styles.css            Diseno
  app.js                Interaccion con la API
```
