import requests
B="http://localhost:3001/api/v1"; R=[]
def tk(u):
    r=requests.post(B+"/auth/login",json={"username":u,"password":"123456"}); return r.json().get("accessToken")
T={u:tk(u) for u in ["admin","gv1","ph1","ph2","ketoan"]}
H=lambda u:{"Authorization":"Bearer "+T[u]}
def c(n,r,e): R.append((n,r.status_code,"PASS" if r.status_code in e else "FAIL"))
s=requests.get(B+"/settings/school",headers=H("ph1")); c("ABS-17 settings",s,[200]); print(s.json() if s.ok else s.text)
c("HOL list admin",requests.get(B+"/holidays",headers=H("admin")),[200])
for u in ["gv1","ph1","ketoan"]:
    c(f"HOL-04 {u} tạo ngày nghỉ 403",requests.post(B+"/holidays",json={"date":"2026-12-24","name":"x"},headers=H(u)),[403])
    c(f"HOL-04 {u} confirm năm 403",requests.post(B+"/holidays/confirm",json={"year":2027},headers=H(u)),[403])
h=requests.get(B+"/holidays",headers=H("admin")).json()
items=h if isinstance(h,list) else h.get("items",h.get("data",[]))
print("pending:",[(i.get("date"),i.get("name")) for i in items if i.get("status")=="pending"][:6])
kids=requests.get(B+"/children",headers=H("ph2")).json()
kids=kids if isinstance(kids,list) else kids.get("items",kids.get("data",[]))
mine={k["id"] for k in kids}
k1=requests.get(B+"/children",headers=H("ph1")).json(); k1=k1 if isinstance(k1,list) else k1.get("items",k1.get("data",[]))
other=[k["id"] for k in k1 if k["id"] not in mine][0]
c("MSG-H4 ph2 xem lịch sử bé ph1 403",requests.get(B+f"/children/{other}/absences?from=2026-09-10&to=2026-10-09",headers=H("ph2")),[403])
r=requests.get(B+f"/children/{other}/absences?from=2026-09-10&to=2026-10-09",headers=H("ph1")); c("MSG-H5 ph1 lịch sử",r,[200]); print(r.text[:400])
c("CON-02 ph2 photo-consent bé ph1 403",requests.get(B+f"/children/{other}/photo-consent",headers=H("ph2")),[403])
for x in R: print(x)
print(sum(x[2]=="PASS" for x in R),"/",len(R))
