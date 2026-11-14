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
