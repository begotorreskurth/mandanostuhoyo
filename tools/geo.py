"""Ubica esquinas y calles con la red de calles guardada. Uso: python3 -I tools/geo.py "calle A" "calle B"  |  python3 geo_tool.py "calle A" """
import json,math,sys,unicodedata,re
import os
_t=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','calles.js'),encoding='utf-8').read()
D=json.loads(_t[_t.index('{'):_t.rindex('}')+1]); OX,OY,U=D['o']
A='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
def d2(s,i): return A.index(s[i])*62+A.index(s[i+1])
W={'uno':'1','dos':'2','tres':'3','cuatro':'4','cinco':'5','seis':'6','siete':'7','ocho':'8','nueve':'9','diez':'10','once':'11','doce':'12','trece':'13'}
def norm(s):
    s=unicodedata.normalize('NFD',s.lower()); s=''.join(c for c in s if unicodedata.category(c)!='Mn')
    w=[W.get(x,x) for x in re.sub(r'[^a-z0-9 ]',' ',s).split()]
    while w and w[0] in('avenida','av','avda','calle','pasaje','psje','camino'): w=w[1:]
    return ' '.join(w)
R=6371000;rad=math.pi/180;cl=math.cos(-33.49*rad)
def m(lon,lat): return (lon*rad*R*cl,lat*rad*R)
def inv(p): return (round(p[1]/(rad*R),5),round(p[0]/(rad*R*cl),5))
S=[]
for name,c,enc in D['s']:
    for l in enc.split('.'):
        pts=[m(OX+d2(l,i)*U,OY+d2(l,i+2)*U) for i in range(0,len(l)-3,4)]
        S.append((name,norm(name),pts))
def cand(q):
    k=norm(q); r=[s for s in S if s[1]==k]
    return r or [s for s in S if (' '+k+' ') in (' '+s[1]+' ')]
def pseg(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]; l=dx*dx+dy*dy; t=((p[0]-a[0])*dx+(p[1]-a[1])*dy)/l if l else 0; t=max(0,min(1,t))
    q=(a[0]+t*dx,a[1]+t*dy); return math.hypot(p[0]-q[0],p[1]-q[1]),q
def dens(l):
    o=[]
    for a,b in zip(l,l[1:]):
        n=max(1,int(math.hypot(b[0]-a[0],b[1]-a[1])/8))
        o+=[(a[0]+(b[0]-a[0])*j/n,a[1]+(b[1]-a[1])*j/n) for j in range(n)]
    return o+[l[-1]]
def inter(a,b):
    ca,cb=cand(a),cand(b)
    if not ca or not cb: return None,(sorted({s[0] for s in ca}),sorted({s[0] for s in cb}))
    best=(1e12,None)
    for s in ca:
        for p in dens(s[2]):
            for t in cb:
                for x,y in zip(t[2],t[2][1:]):
                    d,q=pseg(p,x,y)
                    if d<best[0]: best=(d,((p[0]+q[0])/2,(p[1]+q[1])/2))
    return (round(best[0]),inv(best[1])),(sorted({s[0] for s in ca}),sorted({s[0] for s in cb}))
def centro(a):
    ca=cand(a)
    if not ca: return None
    pts=[p for s in ca for p in s[2]]; c=(sum(p[0] for p in pts)/len(pts),sum(p[1] for p in pts)/len(pts))
    best=min((pseg(c,x,y) for s in ca for x,y in zip(s[2],s[2][1:])),key=lambda r:r[0])
    return inv(best[1]),sorted({s[0] for s in ca})
if __name__=='__main__':
    a=sys.argv[1:]
    print(inter(a[0],a[1]) if len(a)==2 else centro(a[0]))
