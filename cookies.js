/* Aviso de cookies — proximosconciertos.es
 *
 * Por qué existe: desde el 9/10/2026 la web mide visitas con Google Analytics 4, que
 * pone cookies de analítica. Esas cookies necesitan permiso PREVIO del visitante.
 *
 * Cómo funciona: el bloque del <head> de cada página declara Consent Mode v2 con todo
 * DENEGADO antes de cargar gtag.js, así que Analytics arranca sin cookies. Aquí solo se
 * pinta el aviso y, según lo que elija el visitante, se actualiza el consentimiento.
 * Copiado de davidmateos.com/cookie-consent.js (13/08/2026), sin la parte de anuncios.
 */
(function () {
  'use strict';

  var CLAVE = 'pc_consent_v1';
  var MESES = 6; // vuelve a preguntar pasado este tiempo

  function leer() {
    try {
      var b = JSON.parse(localStorage.getItem(CLAVE));
      if (!b || !b.ts) return null;
      var meses = (Date.now() - b.ts) / (1000 * 60 * 60 * 24 * 30);
      return meses > MESES ? null : b;
    } catch (e) { return null; }
  }

  function guardar(acepta) {
    try { localStorage.setItem(CLAVE, JSON.stringify({ acepta: acepta, ts: Date.now() })); } catch (e) {}
  }

  function aplicar(acepta) {
    if (typeof gtag === 'function') {
      gtag('consent', 'update', { analytics_storage: acepta ? 'granted' : 'denied' });
    }
  }

  // Ruta absoluta: la portada está en la raíz y las fichas, un nivel por debajo.
  var POLITICA = '/cookies.html';

  var ESTILO = [
    '.pc-cookies{position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#15131a;color:#f6f4ef;',
    'padding:1rem 1.25rem;box-shadow:0 -4px 20px rgba(0,0,0,.25);font-size:.9rem;line-height:1.5;',
    'max-height:55vh;overflow-y:auto}',
    '.pc-cookies-in{max-width:1000px;margin:0 auto;display:flex;gap:1.25rem;align-items:center;flex-wrap:wrap}',
    '.pc-cookies p{margin:0;flex:1 1 340px}',
    '.pc-cookies a{color:#ff8a80;text-decoration:underline}',
    '.pc-cookies-btns{display:flex;gap:.6rem;flex-wrap:wrap}',
    '.pc-cookies button{font-family:inherit;font-size:.85rem;padding:.6rem 1.3rem;border-radius:6px;',
    'cursor:pointer;border:1px solid #e4352b;white-space:nowrap}',
    '.pc-c-si{background:#e4352b;color:#fff;font-weight:700}',
    '.pc-c-no{background:transparent;color:#f6f4ef}',
    '.pc-c-no:hover{background:rgba(255,255,255,.1)}',
    '.pc-cookies-link{position:fixed;left:12px;bottom:12px;z-index:9998;background:#15131a;color:#f6f4ef;',
    'border:1px solid #e4352b;border-radius:6px;padding:.35rem .7rem;font-size:.72rem;cursor:pointer;opacity:.7}',
    '.pc-cookies-link:hover{opacity:1}',
    '@media(max-width:640px){.pc-cookies{font-size:.82rem;padding:.9rem 1rem;max-height:70vh}',
    '.pc-cookies-in{flex-direction:column;align-items:stretch;gap:.8rem}',
    '.pc-cookies p{flex:0 1 auto}',
    '.pc-cookies-btns button{flex:1}}'
  ].join('');

  function css() {
    if (document.getElementById('pc-cookies-css')) return;
    var s = document.createElement('style');
    s.id = 'pc-cookies-css'; s.textContent = ESTILO;
    document.head.appendChild(s);
  }

  function botonReabrir() {
    if (document.querySelector('.pc-cookies-link')) return;
    var b = document.createElement('button');
    b.className = 'pc-cookies-link';
    b.type = 'button';
    b.textContent = 'Cookies';
    b.setAttribute('aria-label', 'Cambiar mis preferencias de cookies');
    b.addEventListener('click', function () { b.remove(); aviso(); });
    document.body.appendChild(b);
  }

  function aviso() {
    css();
    var d = document.createElement('div');
    d.className = 'pc-cookies';
    d.setAttribute('role', 'dialog');
    d.setAttribute('aria-live', 'polite');
    d.setAttribute('aria-label', 'Aviso de cookies');
    d.innerHTML =
      '<div class="pc-cookies-in">' +
      '<p>Si lo autorizas, usamos cookies de Google Analytics para contar las visitas y saber qué ' +
      'conciertos interesan más. Si las rechazas, la web funciona igual. Más detalle en la ' +
      '<a href="' + POLITICA + '">política de cookies</a>.</p>' +
      '<div class="pc-cookies-btns">' +
      '<button type="button" class="pc-c-no">Rechazar</button>' +
      '<button type="button" class="pc-c-si">Aceptar</button>' +
      '</div></div>';
    document.body.appendChild(d);

    function decidir(acepta) {
      guardar(acepta); aplicar(acepta); d.remove(); botonReabrir();
    }
    d.querySelector('.pc-c-si').addEventListener('click', function () { decidir(true); });
    d.querySelector('.pc-c-no').addEventListener('click', function () { decidir(false); });
  }

  function arrancar() {
    var previo = leer();
    if (previo) { aplicar(previo.acepta); css(); botonReabrir(); return; }
    css(); aviso();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', arrancar);
  } else {
    arrancar();
  }
})();
