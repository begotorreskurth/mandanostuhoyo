"""Arma data/hoyos.js y data/config.js (datos PÚBLICOS) desde un volcado de la base interna.

Uso: python3 -I tools/publicar.py /tmp/hoyos_db.json
El volcado es una lista JSON de objetos {"id": ..., "data": {...}} tal como los entrega db_list.
Solo se copian las claves públicas; nombres, teléfonos y comentarios nunca salen de aquí.
Las fotos subidas desde la página interna (ids sin punto) se omiten: no son accesibles fuera de Claude.
"""
import json, sys, os, datetime
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
docs = json.load(open(sys.argv[1], encoding='utf-8'))
if not docs:
    sys.exit('Volcado vacío: no se publica nada.')
CLAVES = ['n', 'dir', 'grav', 'estado', 'lat', 'lon', 'ubic', 'repFecha']
pub = []
for d in docs:
    x = d['data']
    o = {'id': d['id']}
    for k in CLAVES:
        o[k] = x.get(k)
    o['fotos'] = [f for f in (x.get('fotos') or []) if '.' in f and os.path.exists(os.path.join(RAIZ, 'fotos', f))]
    pub.append(o)
pub.sort(key=lambda o: o.get('n') or 0)
s = 'window.HOYOS=' + json.dumps(pub, ensure_ascii=False) + ';\n'
for mala in ('"nombre"', '"tel"', '"coment"', '"dirOriginal"', '"repPor"', '"enviado"'):
    assert mala not in s, mala
open(os.path.join(RAIZ, 'data', 'hoyos.js'), 'w', encoding='utf-8').write(s)
ahora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(timespec='seconds')
open(os.path.join(RAIZ, 'data', 'config.js'), 'w', encoding='utf-8').write('window.CFG=' + json.dumps({'modo': 'publico', 'actualizado': ahora}) + ';\n')
print(len(pub), 'hoyos publicados;', sum(1 for o in pub if o['estado'] == 'reparado'), 'reparados;', ahora)
