import urllib.request
ID="02f73bfa-6a3d-4a1e-b78e-77af447bac2f"
urls=[f"https://playtomic.com/de/activities/tournaments/{ID}",
f"https://api.playtomic.io/v1/tournaments/{ID}",
f"https://api.playtomic.io/v2/tournaments/{ID}",
f"https://api.playtomic.io/v1/tournaments/{ID}/participants",
f"https://playtomic.io/api/v1/tournaments/{ID}",
f"https://playtomic.com/api/v1/tournaments/{ID}"]
H=[{"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36","Accept":"text/html,application/json,*/*","Accept-Language":"de-DE,de;q=0.9"},
   {"User-Agent":"Playtomic/5.0 (Android)","Accept":"application/json","X-Requested-With":"com.playtomic.app"}]
out=[]
for u in urls:
  for i,h in enumerate(H):
    try:
      r=urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=20); b=r.read().decode('utf-8','replace')
      out.append(f"{r.status} h{i} {u} :: {b[:400]!r}")
    except Exception as e:
      body=getattr(e,'read',lambda:b'')()[:200]
      out.append(f"ERR h{i} {u} :: {e} {body!r}")
open("probe/result.txt","w").write("\n".join(out)+"\n")
