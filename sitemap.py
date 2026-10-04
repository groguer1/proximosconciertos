#!/usr/bin/env python3
"""Escribe sitemap.xml con la portada, las páginas de artista y las guías de recinto."""
import pathlib, datetime
RAIZ = pathlib.Path(__file__).parent
D = "https://proximosconciertos.es"
hoy = datetime.date.today().isoformat()
urls = [D + "/", D + "/contacto.html"] + [f"{D}/{p.parent.name}/{p.name}" for c in ("artistas", "recintos")
                     for p in sorted((RAIZ / c).glob("*.html"))]
xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
xml += [f"  <url><loc>{u}</loc><lastmod>{hoy}</lastmod></url>" for u in urls]
xml.append("</urlset>")
(RAIZ / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")
print(f"sitemap.xml: {len(urls)} URLs")
