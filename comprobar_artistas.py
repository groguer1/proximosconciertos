#!/usr/bin/env python3
"""Revisión semanal: ¿ha cambiado la gira de algún artista en su fuente oficial?

No usa ninguna API de pago ni ningún modelo: descarga la página oficial de cada
artista y saca la lista de identificadores de concierto con la expresión de su
JSON (campo "vigilar"). La compara con la huella guardada la última vez.

  python3 comprobar_artistas.py              revisa todos
  python3 comprobar_artistas.py --sellar X   guarda la huella actual de X (slug)
                                             DESPUÉS de verificar y actualizar sus fechas

El script solo AVISA. Las fechas nuevas se verifican a mano en la fuente oficial
antes de tocar el JSON: es la regla de toda la web.
"""
import json, re, subprocess, sys, pathlib, datetime

RAIZ = pathlib.Path(__file__).parent / "datos" / "artistas"


def huella_actual(v):
    html = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", "Mozilla/5.0", v["url"]],
                          capture_output=True, text=True).stdout
    return sorted(set(re.findall(v["patron"], html))), len(html)


def main():
    sellar = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--sellar" else None
    cambios = 0
    for p in sorted(RAIZ.glob("*.json")):
        a = json.loads(p.read_text(encoding="utf-8"))
        v = a.get("vigilar")
        if sellar and a["slug"] != sellar:
            continue
        if not v or v.get("manual"):
            # webs que bloquean a curl (403): se revisan con el navegador del panel
            print(f"· {a['artista']}: revisar A MANO en el navegador: {a['fuente']} "
                  f"(última revisión {a['revisado']})")
            continue
        ids, tam = huella_actual(v)
        if not ids:
            # control: cero coincidencias casi nunca es «gira terminada», suele ser una web que ha cambiado
            print(f"⚠ {a['artista']}: 0 conciertos en la fuente ({tam} bytes). ¿Ha cambiado la web? Mirar a mano: {v['url']}")
            cambios += 1
            continue
        if sellar:
            v["huella"] = ids
            a["revisado"] = datetime.date.today().isoformat()
            p.write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"✔ {a['artista']}: huella sellada ({len(ids)} conciertos) y revisado hoy")
            continue
        antes = set(v.get("huella", []))
        nuevos, fuera = sorted(set(ids) - antes), sorted(antes - set(ids))
        if nuevos or fuera:
            cambios += 1
            print(f"⚠ {a['artista']}: CAMBIOS en {v['url']}")
            for x in nuevos:
                print(f"     + nuevo: {x}")
            for x in fuera:
                print(f"     − ya no está: {x}")
        else:
            print(f"✔ {a['artista']}: sin cambios ({len(ids)} conciertos)")
    if not sellar:
        print("\nTodo igual." if not cambios else
              f"\n{cambios} artista(s) con cambios: verificar en la fuente, actualizar su JSON, "
              "`python3 generar_artistas.py` y `--sellar <slug>`.")


if __name__ == "__main__":
    main()
