import requests,json,re
B="http://localhost:3001/api/v1"
def tok(u,p="123456"):
    r=requests.post(B+"/auth/login",json={"username":u,"password":p});return r
T={u:tok(u).json()["accessToken"] for u in ["admin","gv1","gv2","ketoan","ph1","ph2"]}
H=lambda u:{"Authorization":"Bearer "+T[u]}
res=[]
def chk(name,r,exp): res.append((name,r.status_code,exp,"PASS" if r.status_code in exp else "FAIL"))
chk("AUTH-02 sai mk",tok("gv1","x"),[401])
chk("AUTH-04 no token",requests.get(B+"/classes"),[401])
chk("AUTH-04 token sửa",requests.get(B+"/classes",headers={"Authorization":"Bearer "+T["gv1"][:-3]+"abc"}),[401])
me=requests.get(B+"/auth/me",headers=H("gv1")).json()
res.append(("AUTH-07 me không lộ hash",0,0,"FAIL" if bool(re.search(r'"(password|passwordhash|password_hash|hash|salt)"\s*:',json.dumps(me).lower())) else "PASS"))
cls=requests.get(B+"/classes",headers=H("admin")).json()
cls=cls.get("items",cls) if isinstance(cls,dict) else cls
mine=requests.get(B+"/classes",headers=H("gv1")).json(); mine=mine.get("items",mine) if isinstance(mine,dict) else mine
mids={c["id"] for c in mine}; other=[c for c in cls if c["id"] not in mids][0]["id"]; m=list(mids)[0]
chk("PERM-01 gv lớp mình",requests.get(B+f"/classes/{m}",headers=H("gv1")),[200])
chk("PERM-02 gv lớp khác",requests.get(B+f"/classes/{other}",headers=H("gv1")),[403])
chk("PERM-02 gv điểm danh lớp khác",requests.get(B+f"/classes/{other}/attendance?date=2026-10-09",headers=H("gv1")),[403])
ch=requests.get(B+f"/children?classId={other}",headers=H("gv1")).json()
items=ch.get("items",[]) if isinstance(ch,dict) else ch
res.append(("PERM-03 gv lọc lớp khác",len(items),0,"PASS" if not items else "FAIL"))
oc=requests.get(B+f"/children?classId={other}&limit=1",headers=H("admin")).json()["items"][0]["id"]
chk("PERM-04 gv xem trẻ lớp khác",requests.get(B+f"/children/{oc}",headers=H("gv1")),[403])
chk("PERM-04 gv sửa trẻ lớp khác",requests.patch(B+f"/children/{oc}",json={"fullName":"x"},headers=H("gv1")),[403,404])
chk("PERM-05 gv tạo lớp",requests.post(B+"/classes",json={"name":"X"},headers=H("gv1")),[403])
chk("PERM-05 gv xóa lớp",requests.delete(B+f"/classes/{m}",headers=H("gv1")),[403])
pc=requests.get(B+"/children",headers=H("ph1")).json(); pitems=pc.get("items",pc) if isinstance(pc,dict) else pc
res.append(("PERM-08 ph1 list chỉ con mình",len(pitems),"<=vài","PASS" if len(pitems)<5 else "FAIL"))
p2=requests.get(B+"/children",headers=H("ph2")).json(); p2i=p2.get("items",p2) if isinstance(p2,dict) else p2
if p2i: chk("PERM-07 ph1 xem con ph2",requests.get(B+f"/children/{p2i[0]['id']}",headers=H("ph1")),[403])
chk("PERM-09 ph PUT điểm danh",requests.put(B+f"/classes/{m}/attendance",json={"date":"2026-10-09","items":[]},headers=H("ph1")),[403])
chk("PERM-10 kt điểm danh",requests.get(B+f"/classes/{m}/attendance?date=2026-10-09",headers=H("ketoan")),[403])
chk("CHD-05 limit=10000",requests.get(B+"/children?limit=10000",headers=H("admin")),[400,200])
chk("CHD-05 limit=-1",requests.get(B+"/children?limit=-1",headers=H("admin")),[400])
chk("ATT-05 ngày tương lai",requests.put(B+f"/classes/{m}/attendance",json={"date":"2027-01-01","items":[]},headers=H("gv1")),[400])
chk("ATT-04 trẻ lớp khác",requests.put(B+f"/classes/{m}/attendance",json={"date":"2026-10-09","items":[{"childId":oc,"status":"present"}]},headers=H("gv1")),[400])
chk("ATT-06 sửa lùi 5 ngày (gv)",requests.put(B+f"/classes/{m}/attendance",json={"date":"2026-10-04","items":[]},headers=H("gv1")),[403,400])
r=requests.get(B+"/classes/not-a-uuid",headers=H("admin")); chk("CLS-06 id sai",r,[400,404])
res.append(("Lỗi định dạng {code,message}",0,0,"PASS" if {"code","message"}<=set(r.json()) else "FAIL "+r.text[:120]))
fails=0
for x in res:
    print(x); fails+=x[3]!="PASS"
print("TOTAL",len(res),"FAIL",fails)
