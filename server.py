#!/usr/bin/env python3
"""Servidor local SIMTELE-RISK (Semana 2) con persistencia SQLite en 6 tablas."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timezone
import json
import os
import sqlite3
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "simtele_risk.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def init_db(db_path: str = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()


def save_simulation(payload: dict, db_path: str = DB_PATH) -> dict:
    caso = payload["caso"]
    escenario_tipo = payload["escenario"]
    parametros = payload.get("parametros", {})
    fuente = payload.get("fuente_parametros", "Parámetros educativos sintéticos")
    metodos = payload.get("metodos", [])
    fecha = payload.get("fecha") or datetime.now(timezone.utc).isoformat()
    concl_num = payload.get("conclusion_numerica", "")
    concl_prob = payload.get("conclusion_problema", "")
    notas = payload.get("notas", [])
    resumen = payload.get("resumen", {})

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO escenario (caso_id, tipo, parametros_json, fuente_datos) VALUES (?, ?, ?, ?)",
            (caso, escenario_tipo, json.dumps(parametros), fuente),
        )
        escenario_id = cur.lastrowid

        cur.execute(
            "INSERT INTO simulacion (escenario_id, fecha, usuario_equipo, estado) VALUES (?, ?, ?, ?)",
            (escenario_id, fecha, payload.get("usuario_equipo", "web-local"), "COMPLETADA"),
        )
        sim_id = cur.lastrowid

        paso = parametros.get("pasos") or parametros.get("nodos")
        for m in metodos:
            det = m.get("detalles") or {}
            convergio = 1 if det.get("convergio", True) else 0
            cur.execute(
                """INSERT INTO ejecucion_metodo
                   (simulacion_id, metodo, tolerancia, paso, max_iter, convergio, tiempo_ms)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (sim_id, m["metodo"], 1e-10, paso, 500, convergio, 0.0),
            )
            ej_id = cur.lastrowid

            for idx, it in enumerate(m.get("iteraciones", []), start=1):
                cur.execute(
                    """INSERT INTO iteracion_resultado
                       (ejecucion_id, numero, aproximacion_json, residual, error_abs, error_rel)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        ej_id,
                        it.get("numero") or it.get("nivel") or idx,
                        json.dumps(it.get("aproximacion")),
                        it.get("residual"),
                        it.get("error_abs"),
                        it.get("error_rel"),
                    ),
                )

            metrica = {
                "error_abs": m.get("error_abs"),
                "error_rel": m.get("error_rel"),
                "error_porcentual": m.get("error_porcentual"),
                "residual": m.get("residual"),
                "detalles": det,
                "resumen_global": resumen,
                "notas": notas,
                "conclusion_numerica": concl_num,
                "conclusion_problema": concl_prob,
            }
            cur.execute(
                """INSERT INTO resultado_resumen
                   (ejecucion_id, referencia, valor_json, metrica_error_json, interpretacion)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    ej_id,
                    json.dumps(m.get("referencia")),
                    json.dumps(m.get("valor")),
                    json.dumps(metrica),
                    concl_prob,
                ),
            )

        conn.commit()
    return {"id": sim_id, "fecha": fecha}


def list_simulations(query: str = "", db_path: str = DB_PATH) -> list[dict]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        sql = """
            SELECT s.id, s.fecha, s.estado, e.tipo AS escenario, e.caso_id AS caso,
                   c.nombre AS caso_nombre
            FROM simulacion s
            JOIN escenario e ON s.escenario_id = e.id
            JOIN caso_estudio c ON e.caso_id = c.id
        """
        params = ()
        if query:
            sql += " WHERE LOWER(e.caso_id) LIKE ? OR LOWER(e.tipo) LIKE ? OR CAST(s.id AS TEXT) LIKE ?"
            like = f"%{query.lower()}%"
            params = (like, like, like)
        sql += " ORDER BY s.id DESC LIMIT 50"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def get_simulation(sim_id: int, db_path: str = DB_PATH) -> dict | None:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        sim = conn.execute(
            """SELECT s.id, s.fecha, s.estado, e.caso_id AS caso, e.tipo AS escenario,
                      e.parametros_json, e.fuente_datos
               FROM simulacion s
               JOIN escenario e ON s.escenario_id = e.id
               WHERE s.id = ?""",
            (sim_id,),
        ).fetchone()
        if not sim:
            return None

        ej_rows = conn.execute(
            "SELECT * FROM ejecucion_metodo WHERE simulacion_id = ? ORDER BY id ASC",
            (sim_id,),
        ).fetchall()

        metodos = []
        meta_global = {}
        for ej in ej_rows:
            res_row = conn.execute(
                "SELECT * FROM resultado_resumen WHERE ejecucion_id = ?",
                (ej["id"],),
            ).fetchone()
            it_rows = conn.execute(
                "SELECT * FROM iteracion_resultado WHERE ejecucion_id = ? ORDER BY numero ASC",
                (ej["id"],),
            ).fetchall()

            metrica = json.loads(res_row["metrica_error_json"]) if res_row else {}
            if not meta_global and metrica:
                meta_global = metrica

            metodos.append(
                {
                    "metodo": ej["metodo"],
                    "valor": json.loads(res_row["valor_json"]) if res_row else None,
                    "referencia": json.loads(res_row["referencia"]) if res_row else None,
                    "error_abs": metrica.get("error_abs"),
                    "error_rel": metrica.get("error_rel"),
                    "error_porcentual": metrica.get("error_porcentual"),
                    "residual": metrica.get("residual"),
                    "detalles": metrica.get("detalles", {}),
                    "iteraciones": [
                        {
                            "numero": it["numero"],
                            "aproximacion": json.loads(it["aproximacion_json"]),
                            "residual": it["residual"],
                        }
                        for it in it_rows
                    ],
                }
            )

        return {
            "id": sim["id"],
            "fecha": sim["fecha"],
            "caso": sim["caso"],
            "escenario": sim["escenario"],
            "parametros": json.loads(sim["parametros_json"]),
            "fuente_parametros": sim["fuente_datos"],
            "metodos": metodos,
            "resumen": meta_global.get("resumen_global", {}),
            "notas": meta_global.get("notas", []),
            "conclusion_numerica": meta_global.get("conclusion_numerica", ""),
            "conclusion_problema": meta_global.get("conclusion_problema", ""),
        }


class SimteleHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _send_json(self, code: int, obj: object) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/health":
            return self._send_json(200, {"ok": True, "db": "sqlite"})
        if parsed.path == "/api/simulaciones":
            qs = urllib.parse.parse_qs(parsed.query)
            q = qs.get("q", [""])[0]
            return self._send_json(200, list_simulations(q))
        if parsed.path.startswith("/api/simulaciones/"):
            try:
                sim_id = int(parsed.path.rsplit("/", 1)[-1])
            except ValueError:
                return self._send_json(400, {"error": "ID inválido"})
            data = get_simulation(sim_id)
            if not data:
                return self._send_json(404, {"error": "Simulación no encontrada"})
            return self._send_json(200, data)
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/simulaciones":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                payload = json.loads(body.decode("utf-8"))
                saved = save_simulation(payload)
                return self._send_json(201, saved)
            except Exception as exc:
                return self._send_json(400, {"error": str(exc)})
        return self._send_json(404, {"error": "Endpoint no encontrado"})


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8000"))
    print(f"SIMTELE-RISK Semana 2 corriendo en http://localhost:{port} (SQLite: {DB_PATH})")
    ThreadingHTTPServer(("0.0.0.0", port), SimteleHandler).serve_forever()
