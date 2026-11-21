"""Prueba obligatoria de persistencia SQL (Semana 2): guardar -> cerrar -> recuperar -> verificar."""

import os
import tempfile
import server

with tempfile.TemporaryDirectory() as tmp:
    db_file = os.path.join(tmp, "test_simtele.db")
    server.init_db(db_file)

    sample = {
        "caso": "deterioro",
        "escenario": "MAL_CONDICIONADO",
        "parametros": {"D0": 0.1, "alpha": 1e-5, "beta": 1e-6, "umbral": 0.1001},
        "fuente_parametros": "Parámetros educativos sintéticos",
        "resumen": {"tiempo_umbral": 7.2665, "condicion_matriz_aprox": 1e6},
        "notas": ["Prueba automatizada de persistencia SQL."],
        "conclusion_numerica": "LU y Gradiente Conjugado mantienen precisión.",
        "conclusion_problema": "Indicador sintético.",
        "metodos": [
            {
                "metodo": "Gradiente conjugado",
                "valor": [1.0, 2.0, 3.0, 4.0],
                "referencia": [1.0, 2.0, 3.0, 4.0],
                "error_abs": 2.909e-13,
                "error_rel": 5.3e-14,
                "error_porcentual": 5.3e-12,
                "residual": 2.893e-13,
                "detalles": {"convergio": True},
                "iteraciones": [{"numero": 1, "aproximacion": [1.1, 2.1, 3.1, 3.9], "residual": 0.5}],
            }
        ],
    }

    saved = server.save_simulation(sample, db_file)
    assert saved["id"] == 1

    lista = server.list_simulations("deterioro", db_file)
    assert len(lista) == 1 and lista[0]["escenario"] == "MAL_CONDICIONADO"

    recovered = server.get_simulation(saved["id"], db_file)
    assert recovered is not None
    assert recovered["parametros"] == sample["parametros"]
    assert recovered["metodos"][0]["valor"] == [1.0, 2.0, 3.0, 4.0]
    assert len(recovered["metodos"][0]["iteraciones"]) == 1
    print("OK: Persistencia SQLite (guardar -> cerrar -> recuperar) verificada.")
