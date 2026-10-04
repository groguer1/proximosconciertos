#!/usr/bin/env python3
"""Regenera datos.js con la agenda oficial de los recintos.

Fuentes (las webs oficiales de cada recinto, nada más):
  - Movistar Arena (Madrid): movistararena.es/programacion
  - Roig Arena (Valencia):   roigarena.com/es/eventos/?category=Música

Uso:  python3 actualizar.py
No copia imágenes ni textos: solo nombre, fecha, hora y los enlaces oficiales.
"""
import re, html, json, subprocess, datetime, pathlib, sys

UA = "Mozilla/5.0 (agenda-conciertos)"
HOY = datetime.date.today().isoformat()

def get(url):
    r = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA, url],
                       capture_output=True, text=True)
    return r.stdout

# Lo que no es un concierto en el Movistar Arena
NO_MUSICA = re.compile(r"real madrid|estudiantes|p[aá]del|disney on ice|alejo igoa|"
                       r"unipersonal|festival internacional de comedia|fich ", re.I)

MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto",
         "septiembre","octubre","noviembre","diciembre"]

def movistar():
    base = "https://www.movistararena.es"
    h = get(base + "/programacion")
    eventos, grupos = {}, set()
    for a in re.findall(r'<article class="event-card.*?</article>', h, re.S):
        u = re.search(r'event-card__media-link"\s*href="([^"]+)"', a)
        if not u:
            continue
        path = u.group(1)
        titulo = html.unescape(re.search(r'data-event-detail="([^"]+)"', a).group(1))
        if NO_MUSICA.search(titulo):
            continue
        dt = re.search(r'<time datetime="(\d{4}-\d\d-\d\dT[\d:]+)', a)
        buy = re.search(r'href="(https?://[^"]+)"\s*data-action="buy"', a)
        agotado = "agotad" in a.lower()
        partes = path.rstrip("/").split("/")
        if len(partes) == 4:            # ficha agrupada sin fecha: se abre aparte
            grupos.add((path, titulo))
            continue
        fecha = dt.group(1) if dt else None
        if not fecha:                    # fecha en la URL, hora sin confirmar (00:00)
            d, m, y = partes[4].split("-")
            fecha = f"{y}-{int(m):02d}-{int(d):02d}"
        eventos[fecha + titulo] = dict(titulo=titulo, fecha=fecha, ciudad="Madrid",
            recinto="Movistar Arena", info=base + path,
            entradas=html.unescape(buy.group(1)) if buy else None, agotado=agotado)
    for path, titulo in grupos:
        p = get(base + path)
        ag = "agotad" in p.lower()
        fechas = set(re.findall(r'<time datetime="(\d{4}-\d\d-\d\dT[\d:]+)', p))
        if not fechas:  # algunas fichas solo traen la fecha en texto: «19 de enero de 2027»
            for d, m, y in re.findall(r'(\d{1,2}) de (' + "|".join(MESES) + r') de (\d{4})', p):
                fechas.add(f"{y}-{MESES.index(m)+1:02d}-{int(d):02d}")
        for f in sorted(fechas):
            eventos.setdefault(f + titulo, dict(titulo=titulo, fecha=f, ciudad="Madrid",
                recinto="Movistar Arena", info=base + path, entradas=None, agotado=ag))
    return list(eventos.values())

def roig():
    base = "https://www.roigarena.com"
    out, vistos = [], set()
    for p in range(1, 40):
        u = base + "/es/eventos/?category=M%C3%BAsica" + (f"&page={p}" if p > 1 else "")
        cards = re.findall(r'<article class="m-event-card.*?</article>', get(u), re.S)
        nuevos = 0
        for c in cards:
            t = html.unescape(re.search(r'itemprop="name">([^<]+)', c).group(1)).strip()
            im = re.search(r'href="(/es/event/[^"]+/)"', c)
            clave = im.group(1) if im else t
            if clave in vistos:
                continue
            vistos.add(clave); nuevos += 1
            d = re.search(r'datetime="(\d\d)/(\d\d)/(\d{4})(?: (\d\d:\d\d))?"', c)
            if not d:
                continue
            fecha = f"{d.group(3)}-{d.group(2)}-{d.group(1)}" + (f"T{d.group(4)}:00" if d.group(4) else "")
            links = re.findall(r'<a href="([^"]+)"[^>]*>.*?<!--\[-->([^<]+)<!--\]-->', c, re.S)
            ent = [l for l, lab in links if "Entradas" in lab]
            ext = [l for l in ent if l.startswith("http")]
            out.append(dict(titulo=t, fecha=fecha, ciudad="Valencia", recinto="Roig Arena",
                info=(base + im.group(1)) if im else None,
                entradas=html.unescape(ext[0]) if ext else (base + html.unescape(ent[0]) if ent else None), agotado=False))
        if nuevos == 0:
            break
    return out

if __name__ == "__main__":
    ma, ra = movistar(), roig()
    # control: si una fuente viene vacía, no se pisa la agenda anterior
    if len(ma) < 20 or len(ra) < 20:
        sys.exit(f"Fuente sospechosa: Movistar {len(ma)}, Roig {len(ra)}. No se escribe nada.")
    todos = [e for e in ma + ra if e["fecha"][:10] >= HOY]
    todos.sort(key=lambda e: (e["fecha"], e["titulo"]))
    js = ("// Generado por actualizar.py el " + HOY + ". No editar a mano.\n"
          "window.AGENDA = " + json.dumps(dict(actualizado=HOY, eventos=todos),
                                         ensure_ascii=False, indent=1) + ";\n")
    pathlib.Path(__file__).with_name("datos.js").write_text(js, encoding="utf-8")
    print(f"Movistar Arena: {len(ma)} · Roig Arena: {len(ra)} · publicados: {len(todos)}")
