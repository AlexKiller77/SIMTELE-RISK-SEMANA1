# SIMTELE-RISK — Versión GitHub Pages (100% JavaScript)

Aplicación educativa de Métodos Numéricos, con cuatro casos y tres escenarios por caso. No representa datos reales ni certifica la seguridad de Mi Teleférico.

## Publicar

Subir **index.html** y **numerics.js** a la raíz del repositorio GitHub (ambos al mismo nivel). En Settings → Pages seleccionar Deploy from a branch, main, /(root). La dirección será `https://USUARIO.github.io/REPOSITORIO/`.

## Uso

Abrir la web, seleccionar caso y escenario, cambiar parámetros, pulsar «Ejecutar y guardar». Ver gráficas, métodos, errores e iteraciones. En Historial local, abrir una simulación para recuperar parámetros y repetir el cálculo.

El historial utiliza `localStorage`, por lo que **no** se comparte entre navegadores/dispositivos ni es una base de datos SQL. Si se borran los datos del navegador, se pierde el historial. Para cumplir la exigencia de persistencia SQL de la consigna original, se necesita conservar la versión Python + base de datos como entrega complementaria.

## Métodos

- Detención: RK2/RK4, trapecio, Simpson 1/3, Romberg, bisección, Newton-Raphson, secante.
- Deterioro: raíces; Jacobi, Gauss-Seidel, eliminación LU con pivoteo, gradiente conjugado y solución directa de referencia, con matrices SPD de 4×4.
- Oscilaciones: RK2/RK4, trapecio, Simpson 1/3, Romberg; referencia RK4 refinada.
- Sensores: Lagrange baricéntrico, Newton por diferencias divididas, spline cúbico natural; errores sobre puntos ocultos.

**Precaución matemática:** la referencia RK4 refinada es aproximada, no una solución exacta. El caso de deterioro usa una matriz auxiliar sintética; el mal condicionamiento de otros módulos debe justificarse cuantitativamente en el informe. Esta versión no reemplaza la validación matemática ni el informe del curso.

## Gráficos

Plotly se carga desde CDN; se requiere conexión a Internet para mostrar los gráficos. Los cálculos y el historial no requieren servidor.

## Pruebas

Ejecutar `node tests.js` si Node.js está instalado. También puede abrirse `index.html` directamente en el navegador.

# SIMTELE-RISK — Semana 2 (Integración matemática y persistencia SQL)

Aplicación educativa de Métodos Numéricos con cuatro módulos, tres escenarios por módulo (`NORMAL`, `ESTRÉS`, `MAL CONDICIONADO`) y persistencia en base de datos SQLite (con respaldo automático en `localStorage` si se abre de forma estática en GitHub Pages).

## Ejecución con Base de Datos SQL (Recomendado para Semana 2)

1. Abrir una terminal en la carpeta del proyecto.
2. Iniciar el servidor Python (no requiere instalar paquetes externos):
   ```bash
   python server.py
   ```
3. Abrir en el navegador: `http://localhost:8000`
4. Verificar que el indicador superior muestre **BD SQL: SQLite conectada**.

La base de datos `simtele_risk.db` se crea automáticamente a partir de `schema.sql` con las 6 entidades obligatorias (`caso_estudio`, `escenario`, `simulacion`, `ejecucion_metodo`, `iteracion_resultado`, `resultado_resumen`).

## Pruebas automatizadas

- **Algoritmos numéricos (12 combinaciones módulo × escenario):**
  ```bash
  node tests.js
  ```
- **Persistencia SQL (guardar, cerrar, recuperar y verificar):**
  ```bash
  python test_db.py
  ```

## Publicación estática (GitHub Pages)

Si se publica `index.html` y `numerics.js` en GitHub Pages, la aplicación detecta la ausencia de backend y opera automáticamente en modo estático con `localStorage`.
