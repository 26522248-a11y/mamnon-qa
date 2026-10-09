import requests
B="http://localhost:3001/api/v1";R=[]
tok=lambda u:requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"]
H=lambda u:{"Authorization":"Bearer "+tok(u)}
A,G1,G2,K,P=H("admin"),H("gv1"),H("gv2"),H("ketoan"),H("ph1")
def chk(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:200]));print(R[-1])
sc=lambda m,u,h,**k: requests.request(m,B+u,headers=h,**k).status_code
for n,h in [("ph1",P)]: chk(f"STF-01 {n} xem ca → 403",sc("GET","/staff/shifts",h)==403)
chk("STF-02 gv tạo ca → 403",sc("POST","/staff/shifts",G1,json={"name":"x","startTime":"07:00","endTime":"16:00"})==403)
chk("STF-03 gv xem nhu cầu trông thay → 403",sc("GET","/staff/substitutions/needs",G1)==403)
me=requests.get(B+"/auth/me",headers=G1).json(); uid=me.get("id") or me.get("user",{}).get("id")
chk("STF-04 gv sửa công → 403",sc("PUT",f"/staff/attendance/{uid}/2026-10-08",G1,json={"note":"x"})==403)
chk("STF-05 sửa công ngày tương lai → 400",sc("PUT",f"/staff/attendance/{uid}/2030-01-01",A,json={"checkInAt":"2030-01-01T00:00:00Z","note":"QA"})==400)
chk("STF-06 sửa công thiếu lý do → 400",sc("PUT",f"/staff/attendance/{uid}/2026-10-08",A,json={"checkInAt":"2026-10-08T00:10:00Z"})==400)
a=requests.get(B+"/staff/attendance",headers=G1,params={"from":"2026-10-05","to":"2026-10-09"}).json()
chk("STF-07 gv chỉ thấy công của mình",len(a.get("items",[]))==1,len(a.get("items",[])))
a=requests.get(B+"/staff/attendance",headers=A,params={"from":"2026-10-05","to":"2026-10-09"}).json()
chk("STF-08 admin thấy toàn bộ GV",len(a.get("items",[]))>=3,len(a.get("items",[])))
r=requests.post(B+"/staff/leaves",headers=G1,json={"fromDate":"2026-10-20","toDate":"2026-10-21","reason":"QA nghỉ"}); lid=r.json().get("id")
chk("STF-09 gv xin nghỉ → chờ duyệt",r.status_code==201 and r.json().get("status")=="pending",r.text[:120])
chk("STF-10 gv tự duyệt → 403",sc("POST",f"/staff/leaves/{lid}/approve",G1,json={})==403)
chk("STF-11 gv2 không thấy đơn của gv1",all(i["id"]!=lid for i in requests.get(B+"/staff/leaves",headers=G2).json()["items"]))
chk("STF-12 gv2 không huỷ được đơn gv1",sc("POST",f"/staff/leaves/{lid}/cancel",G2,json={}) in (403,404))
chk("STF-13 gv1 huỷ đơn của mình",sc("POST",f"/staff/leaves/{lid}/cancel",G1,json={})==200)
n=requests.get(B+"/staff/substitutions/needs",headers=A).json(); chk("STF-14 admin xem nhu cầu trông thay",isinstance(n,(dict,list)),str(n)[:200])
print("TOTAL",len(R),"FAIL",sum(1 for x in R if x[1]=="FAIL"))
