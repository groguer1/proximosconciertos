#!/usr/bin/env python3
"""Genera recintos/<slug>.html (guía práctica) desde datos/recintos/<slug>.json.

Los textos se escriben a mano a partir de las páginas oficiales del recinto
(campo "fuentes"). La lista de próximos conciertos sale sola de datos.js.
Uso:  python3 generar_recintos.py   (después de actualizar.py)
"""
import json, html, datetime, pathlib
from generar_artistas import MESES, DIAS, arte

RAIZ = pathlib.Path(__file__).parent
HOY = datetime.date.today().isoformat()
e = html.escape


def proximos(nombre, n=12):
    t = (RAIZ / "datos.js").read_text(encoding="utf-8")
    ev = json.loads(t[t.index("{"):t.rindex("}") + 1])["eventos"]
    return [x for x in ev if x["recinto"] == nombre and x["fecha"][:10] >= HOY][:n]


def pagina(r, artistas):
    rev = datetime.date.fromisoformat(r["revisado"])
    titulo = f"{r['nombre']}: cómo llegar, parking, puertas y normas"
    desc = (f"Guía práctica del {r['nombre']}: metro y autobús, aparcamiento, puertas de acceso, qué no "
            f"se puede llevar, consigna y próximos conciertos. Datos de la web oficial del recinto.")
    filas = []
    for x in proximos(r["nombre"]):
        d = datetime.date.fromisoformat(x["fecha"][:10])
        hora = x["fecha"][11:16]
        dest = x.get("entradas") or x.get("info")
        nombre = x["titulo"]
        extra = ""
        for a, url in artistas.items():
            if a in nombre.lower():
                extra = f' · <a href="../{url}">todas sus fechas</a>'
        filas.append(f'<li><span class="f">{d.day} {MESES[d.month-1][:3]}{" · " + hora if hora else ""}</span>'
                     f'<span class="t">{e(nombre)}{"" if not x.get("agotado") else " <em>agotado</em>"}{extra}</span>'
                     f'{f"<a class=btn href={chr(34)}{e(dest)}{chr(34)} target=_blank rel={chr(34)}noopener nofollow{chr(34)}>Entradas ↗</a>" if dest else ""}</li>')
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "MusicVenue", "name": r["nombre"],
         "address": {"@type": "PostalAddress", "streetAddress": r["datos"][0][1], "addressLocality": r["ciudad"], "addressCountry": "ES"}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in r["faq"]]}]}
    fuentes = " · ".join(f'<a href="{e(u)}" rel="noopener">{e(n)}</a>' for n, u in r["fuentes"])
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="https://proximosconciertos.es/recintos/{r['slug']}.html">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="https://proximosconciertos.es/recintos/{r['slug']}.html">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
:root{{--bg:#f6f4ef;--surface:#fff;--ink:#15131a;--muted:#6b6672;--line:#e3dfd6;--accent:#e4352b;--chip:#ece8df}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#111014;--surface:#1b1a20;--ink:#f2f0f5;--muted:#a19ca8;--line:#2c2a33;--accent:#ff4d42;--chip:#26242c}}}}
:root[data-theme="dark"]{{--bg:#111014;--surface:#1b1a20;--ink:#f2f0f5;--muted:#a19ca8;--line:#2c2a33;--accent:#ff4d42;--chip:#26242c}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 Archivo,system-ui,sans-serif}}
a{{color:inherit}}
.wrap{{max-width:860px;margin:0 auto;padding:0 16px}}
header.top{{border-bottom:1px solid var(--line)}}
header.top .wrap{{display:flex;align-items:center;height:60px}}
.logo{{font:800 22px/1 Archivo,sans-serif;letter-spacing:-.02em;text-decoration:none;display:flex;align-items:center;gap:8px}}
.logo i{{width:12px;height:12px;border-radius:50%;background:var(--accent)}}
.crumbs{{font-size:14px;color:var(--muted);margin:20px 0 0}}
.hero{{margin:16px 0 8px;border-radius:18px;padding:28px 24px;color:#fff;background:{arte(r['nombre'])}}}
h1{{font:800 clamp(28px,5vw,46px)/1.05 Archivo,sans-serif;letter-spacing:-.03em;margin:0 0 10px}}
.hero p{{margin:0;max-width:60ch}}
.datos{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;margin:18px 0 6px}}
.dato{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px 12px}}
.dato small{{display:block;font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}}
.rev{{font-size:14px;color:var(--muted);margin:10px 0 0}}
h2{{font:800 23px/1.2 Archivo,sans-serif;letter-spacing:-.02em;margin:34px 0 10px}}
section ul{{padding-left:20px}} section li{{margin:4px 0}}
ul.prox{{list-style:none;padding:0;display:flex;flex-direction:column;gap:8px}}
ul.prox li{{display:flex;align-items:center;gap:12px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px 12px;margin:0}}
.f{{flex:none;width:92px;font-weight:600;font-size:14px}}
.t{{flex:1;min-width:0}}
.t em{{font-style:normal;font-size:11px;text-transform:uppercase;background:var(--ink);color:var(--bg);padding:2px 6px;border-radius:5px;margin-left:4px}}
.btn{{flex:none;border-radius:999px;padding:8px 14px;font:600 14px Archivo,sans-serif;text-decoration:none;background:var(--accent);color:#fff}}
details{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:0 0 10px}}
summary{{font-weight:600;cursor:pointer}}
details p{{margin:10px 0 0;color:var(--muted)}}
.aviso{{background:var(--chip);border-radius:12px;padding:14px 16px;font-size:14px;margin:28px 0 0}}
footer{{margin-top:56px;border-top:1px solid var(--line);padding:24px 0 40px;color:var(--muted);font-size:14px}}
@media (max-width:560px){{ul.prox li{{flex-wrap:wrap}}.f{{width:auto}}}}
</style>
</head>
<body>
<header class="top"><div class="wrap"><a class="logo" href="../index.html"><i aria-hidden="true"></i>Directo</a></div></header>
<main class="wrap">
  <p class="crumbs"><a href="../index.html">Agenda</a> › Recintos › {e(r['nombre'])}</p>
  <section class="hero">
    <h1>Guía del {e(r['nombre'])}</h1>
    <p>{e(r['intro'])}</p>
  </section>
  <div class="datos">{''.join(f'<div class="dato"><small>{e(k)}</small>{e(v)}</div>' for k, v in r['datos'])}</div>
  <p class="rev">Revisado el {rev.day} de {MESES[rev.month-1]} de {rev.year} con las páginas oficiales del recinto: {fuentes}.</p>
  {''.join(f'<section><h2>{e(t)}</h2>{h}</section>' for t, h in r['secciones'])}
  <h2>Próximos conciertos en el {e(r['nombre'])}</h2>
  <ul class="prox">{''.join(filas) or '<li>No hay conciertos anunciados.</li>'}</ul>
  <p><a href="../index.html">Ver toda la agenda</a></p>
  <h2>Preguntas frecuentes</h2>
  {''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in r['faq'])}
  <p class="aviso">Horarios, normas y servicios pueden cambiar en cada evento. Antes de ir, mira la ficha del concierto y la web oficial del recinto. Directo no vende entradas.</p>
</main>
<footer><div class="wrap">Directo · Agenda de conciertos en España. Datos de fuentes oficiales, revisados a mano.</div></footer>
</body>
</html>
"""


if __name__ == "__main__":
    artistas = {}
    for p in (RAIZ / "datos" / "artistas").glob("*.json"):
        a = json.loads(p.read_text(encoding="utf-8"))
        artistas[a["artista"].lower()] = f"artistas/{a['slug']}.html"
    guias = []
    for p in sorted((RAIZ / "datos" / "recintos").glob("*.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        (RAIZ / "recintos" / f"{r['slug']}.html").write_text(pagina(r, artistas), encoding="utf-8")
        guias.append(r)
        print(f"{r['nombre']}: guía generada ({len(proximos(r['nombre']))} próximos conciertos)")
    import re
    bloque = ('<!--RECINTOS--><section class="giras"><h2>Guías de recinto</h2><ul>'
              + "".join(f'<li><a href="recintos/{r["slug"]}.html">{e(r["nombre"])}: cómo llegar y normas</a></li>' for r in guias)
              + "</ul></section><!--/RECINTOS-->")
    idx = RAIZ / "index.html"
    idx.write_text(re.sub(r"<!--RECINTOS-->.*?<!--/RECINTOS-->", lambda m: bloque, idx.read_text(encoding="utf-8"), flags=re.S), encoding="utf-8")
