#!/usr/bin/env python3
"""Genera una página estática por artista a partir de datos/artistas/<slug>.json.

Cada JSON se rellena a mano contra la WEB OFICIAL del artista (o de su promotora)
y lleva la fecha de la última revisión. Las fechas ya pasadas se quitan solas al
regenerar. Uso:  python3 generar_artistas.py
"""
import json, html, datetime, pathlib

RAIZ = pathlib.Path(__file__).parent
HOY = datetime.date.today()
MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto",
         "septiembre","octubre","noviembre","diciembre"]
DIAS = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
e = html.escape


def fecha_larga(d):
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month-1]} de {d.year}"


def fecha_corta(d):
    return f"{d.day} de {MESES[d.month-1]}"


def pagina(a):
    fechas = [f for f in a["fechas"] if datetime.date.fromisoformat(f["fecha"]) >= HOY]
    fechas.sort(key=lambda f: f["fecha"])
    rev = datetime.date.fromisoformat(a["revisado"])
    anios = sorted({f["fecha"][:4] for f in fechas}) or [str(HOY.year)]
    anio_txt = " y ".join(anios)
    ciudades = []
    for f in fechas:
        if f["ciudad"] not in ciudades:
            ciudades.append(f["ciudad"])
    n = len(fechas)

    titulo = f"Conciertos de {a['artista']} {anio_txt}: fechas y entradas"
    desc = (f"Todas las fechas de {a['artista']} en España: {n} conciertos del {a['gira']} en "
            f"{', '.join(ciudades[:-1])} y {ciudades[-1]}, con hora, recinto y enlace a la venta oficial."
            if n else f"Próximos conciertos de {a['artista']} en España.")

    filas, por_ciudad = [], {}
    for f in fechas:
        d = datetime.date.fromisoformat(f["fecha"])
        por_ciudad.setdefault(f["ciudad"], []).append(d)
        hora = f.get("hora", "")
        estado = f.get("estado", "")
        destino = f.get("entradas") or f.get("ficha") or a["fuente"]
        etiqueta = {"agotado": f"Agotado (a {rev.day}/{rev.month})", "ultimas": "Últimas entradas"}.get(estado, "")
        boton = "Ver en la web oficial ↗" if estado == "agotado" or not f.get("entradas") else "Entradas oficiales ↗"
        gira_f = f" · {e(f['gira'])}" if f.get("gira") else ""
        filas.append(f"""<li class="row{' soldout' if estado == 'agotado' else ''}">
  <div class="cal"><b>{d.day}</b><small>{MESES[d.month-1][:3]}</small></div>
  <div class="info">
    <strong>{e(f['ciudad'])}{f' <em class="tag-{estado}">{etiqueta}</em>' if etiqueta else ''}</strong>
    <span>{e(f['recinto'])} · {fecha_larga(d).capitalize()} · {e(hora) + ' h' if hora else 'hora por confirmar'}{gira_f}</span>
  </div>
  <a class="btn" href="{e(destino)}" target="_blank" rel="noopener nofollow">{boton}</a>
</li>""")

    resumen = "".join(
        f"<li><b>{e(c)}</b>: {', '.join(fecha_corta(x) for x in ds)}</li>" for c, ds in por_ciudad.items())

    eventos_ld = [{
        "@type": "MusicEvent",
        "name": f"{a['artista']} · {a['gira']} en {f['ciudad']}",
        "startDate": f"{f['fecha']}T{f['hora']}:00" if f.get("hora") else f["fecha"],
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {"@type": "Place", "name": f["recinto"],
                     "address": {"@type": "PostalAddress", "addressLocality": f["ciudad"], "addressCountry": "ES"}},
        "performer": {"@type": a.get("tipo", "Person"), "name": a["artista"]},
        "offers": {"@type": "Offer", "url": f.get("entradas") or f.get("ficha") or a["fuente"],
                   "availability": "https://schema.org/SoldOut" if f.get("estado") == "agotado" else "https://schema.org/InStock"},
    } for f in fechas]
    faq = [
        (f"¿Cuándo actúa {a['artista']} en España?",
         f"El {a['gira']} tiene {n} conciertos: " + "; ".join(
             f"{c}, {', '.join(fecha_corta(x) for x in ds)}" for c, ds in por_ciudad.items()) + "."),
        (f"¿Dónde se compran las entradas de {a['artista']}?",
         f"En los enlaces de venta que publica la {a['fuente_nombre']}. Cada fecha de esta página "
         f"enlaza directamente a esa venta. Desconfía de reventas con precios por encima del oficial."),
        (f"¿Hay conciertos de {a['artista']} en 2027?", a.get("nota_2027", "")),
    ]
    faq = [(q, r) for q, r in faq if r]
    ld = {"@context": "https://schema.org", "@graph": eventos_ld + [{
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faq]}]}

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="https://proximosconciertos.es/artistas/{a['slug']}.html">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="https://proximosconciertos.es/artistas/{a['slug']}.html">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&family=Archivo+Narrow:wght@700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>
:root{{--bg:#f6f4ef;--surface:#fff;--ink:#15131a;--muted:#6b6672;--line:#e3dfd6;--accent:#e4352b;--chip:#ece8df}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#111014;--surface:#1b1a20;--ink:#f2f0f5;--muted:#a19ca8;--line:#2c2a33;--accent:#ff4d42;--chip:#26242c}}}}
:root[data-theme="dark"]{{--bg:#111014;--surface:#1b1a20;--ink:#f2f0f5;--muted:#a19ca8;--line:#2c2a33;--accent:#ff4d42;--chip:#26242c}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Archivo,system-ui,sans-serif}}
a{{color:inherit}}
.wrap{{max-width:860px;margin:0 auto;padding:0 16px}}
header.top{{border-bottom:1px solid var(--line)}}
header.top .wrap{{display:flex;align-items:center;height:60px;gap:12px}}
.logo{{font:800 22px/1 Archivo,sans-serif;letter-spacing:-.02em;text-decoration:none;display:flex;align-items:center;gap:8px}}
.logo i{{width:12px;height:12px;border-radius:50%;background:var(--accent)}}
.crumbs{{font-size:14px;color:var(--muted);margin:20px 0 0}}
.hero{{margin:16px 0 8px;border-radius:18px;padding:28px 24px;color:#fff;background:{arte(a['artista'])};position:relative;overflow:hidden}}
.hero::after{{content:"";position:absolute;inset:0;background:repeating-linear-gradient(115deg,rgba(255,255,255,.06) 0 2px,transparent 2px 14px)}}
.hero *{{position:relative;z-index:1}}
.hero .tag{{font:600 13px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.06em;opacity:.85}}
h1{{font:800 clamp(30px,5.5vw,52px)/1.02 Archivo,sans-serif;letter-spacing:-.03em;margin:6px 0 10px}}
.hero p{{margin:0;max-width:56ch;opacity:.95}}
.facts{{display:flex;gap:28px;flex-wrap:wrap;margin:18px 0 0}}
.facts b{{display:block;font:800 30px/1 Archivo,sans-serif}}
.facts span{{font-size:13px;opacity:.85}}
.rev{{font-size:14px;color:var(--muted);margin:14px 0 28px}}
h2{{font:800 24px/1.2 Archivo,sans-serif;letter-spacing:-.02em;margin:36px 0 14px}}
ul.dates{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}}
.row{{display:flex;align-items:center;gap:14px;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px}}
.cal{{flex:none;width:56px;text-align:center;background:var(--chip);border-radius:10px;padding:8px 0;line-height:1}}
.cal b{{display:block;font:800 22px Archivo,sans-serif}}
.cal small{{font:600 12px Archivo,sans-serif;text-transform:uppercase}}
.info{{flex:1;min-width:0;display:flex;flex-direction:column}}
.info strong{{font-size:17px}}
.info span{{font-size:14px;color:var(--muted)}}
.row em{{font-style:normal;font:600 11px Archivo,sans-serif;text-transform:uppercase;letter-spacing:.04em;padding:3px 7px;border-radius:6px;margin-left:6px;vertical-align:2px;background:var(--ink);color:var(--bg)}}
.row em.tag-ultimas{{background:var(--accent);color:#fff}}
.row.soldout .btn{{background:var(--muted)}}
.btn{{flex:none;display:inline-flex;align-items:center;border-radius:999px;padding:10px 16px;font:600 14px Archivo,sans-serif;text-decoration:none;background:var(--accent);color:#fff;white-space:nowrap}}
ul.resumen{{padding-left:20px}}
details{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:0 0 10px}}
summary{{font-weight:600;cursor:pointer}}
details p{{margin:10px 0 0;color:var(--muted)}}
.aviso{{background:var(--chip);border-radius:12px;padding:14px 16px;font-size:14px;margin:28px 0 0}}
footer{{margin-top:56px;border-top:1px solid var(--line);padding:24px 0 40px;color:var(--muted);font-size:14px}}
@media (max-width:560px){{.row{{flex-wrap:wrap}}.btn{{width:100%;justify-content:center}}}}
</style>
</head>
<body>
<header class="top"><div class="wrap"><a class="logo" href="../index.html"><i aria-hidden="true"></i>Próximos Conciertos</a></div></header>
<main class="wrap">
  <p class="crumbs"><a href="../index.html">Agenda</a> › Artistas › {e(a['artista'])}</p>
  <section class="hero">
    <div class="tag">{e(a['gira'])}</div>
    <h1>Conciertos de {e(a['artista'])} {anio_txt}</h1>
    <p>Todas las fechas de la gira en España, con el recinto, la hora y el enlace a la venta oficial de cada concierto.</p>
    <div class="facts">
      <div><b>{n}</b><span>conciertos</span></div>
      <div><b>{len(ciudades)}</b><span>ciudades</span></div>
      <div><b>{fecha_corta(datetime.date.fromisoformat(fechas[-1]['fecha'])) if fechas else '—'}</b><span>último concierto</span></div>
    </div>
  </section>
  <p class="rev">Revisado el {rev.day} de {MESES[rev.month-1]} de {rev.year} contra la <a href="{e(a['fuente'])}" rel="noopener">{e(a['fuente_nombre'])}</a>.</p>

  <h2>Fechas y entradas</h2>
  <ul class="dates">
{chr(10).join(filas) if filas else '<li>No hay conciertos anunciados ahora mismo.</li>'}
  </ul>

  <h2>Resumen por ciudad</h2>
  <ul class="resumen">{resumen}</ul>

  <h2>Preguntas frecuentes</h2>
  {''.join(f'<details><summary>{e(q)}</summary><p>{e(r)}</p></details>' for q, r in faq)}

  <p class="aviso">Próximos Conciertos no vende entradas. Los botones llevan a la venta que enlaza la propia {e(a['fuente_nombre'])}. Las fechas y los horarios pueden cambiar: confírmalos allí antes de comprar.</p>
</main>
<footer><div class="wrap">Próximos Conciertos · Agenda de conciertos en España. Datos de fuentes oficiales, revisados a mano. · <a href="../contacto.html">Contacto</a></div></footer>
</body>
</html>
"""


def arte(nombre):
    """El mismo degradado que las tarjetas de la agenda (hash de index.html)."""
    h = 0
    for c in nombre.lower():
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    if h >= 2**31:
        h -= 2**32
    h = abs(h)
    a1 = h % 360
    a2 = (a1 + 40 + (h >> 8) % 80) % 360
    return f"linear-gradient({(h >> 4) % 180}deg,hsl({a1} 70% 42%),hsl({a2} 75% 30%))"


if __name__ == "__main__":
    indice = {}
    for p in sorted((RAIZ / "datos" / "artistas").glob("*.json")):
        a = json.loads(p.read_text(encoding="utf-8"))
        dias = (HOY - datetime.date.fromisoformat(a["revisado"])).days
        if dias > 7:
            print(f"⚠ {a['artista']}: revisado hace {dias} días; toca repasarlo contra {a['fuente']}")
        (RAIZ / "artistas" / f"{a['slug']}.html").write_text(pagina(a), encoding="utf-8")
        indice[a["artista"].lower()] = f"artistas/{a['slug']}.html"
        print(f"{a['artista']}: {sum(1 for f in a['fechas'] if f['fecha'] >= HOY.isoformat())} fechas")
    # enlaces estáticos en la portada (Google no sigue los que pinta el JavaScript)
    import re as _re
    nombres = {}
    for p in sorted((RAIZ / "datos" / "artistas").glob("*.json")):
        a = json.loads(p.read_text(encoding="utf-8"))
        nombres[a["artista"]] = a["slug"]
    bloque = ('<!--ARTISTAS--><section class="giras"><h2>Giras completas por España</h2><ul>'
              + "".join(f'<li><a href="artistas/{s}.html">Conciertos de {e(n)}</a></li>' for n, s in nombres.items())
              + "</ul></section><!--/ARTISTAS-->")
    idx = RAIZ / "index.html"
    idx.write_text(_re.sub(r"<!--ARTISTAS-->.*?<!--/ARTISTAS-->", lambda m: bloque, idx.read_text(encoding="utf-8"), flags=_re.S), encoding="utf-8")
    (RAIZ / "artistas" / "indice.js").write_text(
        "window.ARTISTAS = " + json.dumps(indice, ensure_ascii=False) + ";\n", encoding="utf-8")
