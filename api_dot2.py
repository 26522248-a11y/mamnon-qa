import requests,datetime,io
B="http://localhost:3001/api/v1";S="http://localhost:3001"
T={u:requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"] for u in ["admin","gv1","gv2","ketoan","ph1","ph2"]}
H=lambda u:{"Authorization":"Bearer "+T[u]};R=[]
def chk(n,r,exp,extra=""):
    ok=r.status_code in exp; R.append((n,r.status_code,exp,"PASS" if ok else "FAIL",extra or ("" if ok else r.text[:150]))); print(R[-1],flush=True)
def items(j): return j.get("items",j.get("data",j)) if isinstance(j,dict) else j
today=datetime.date.today().isoformat()
mine=items(requests.get(B+"/classes",headers=H("gv1")).json())[0]["id"]
kid=items(requests.get(B+"/children",headers=H("ph1")).json())[0]
kidp2=items(requests.get(B+"/children",headers=H("ph2")).json())[0]
r=requests.put(B+f"/classes/{mine}/attendance",json={"date":today,"items":[{"childId":kid["id"],"status":"present"}]},headers=H("gv1"))
att=requests.get(B+f"/classes/{mine}/attendance?date={today}",headers=H("gv1")).json()["items"]
a=[x for x in att if x.get("childId")==kid["id"]][0]; aid=a.get("attendanceId") or a.get("id")
def preq(name):
    r=requests.post(B+f"/attendance/{aid}/pickup-requests",json={"pickerName":name,"pickerPhone":"0901234567","relation":"Cô","note":"test"},headers=H("gv1")); return r
r=preq("Cô Tư"); chk("PU-01 gv tạo yêu cầu đón",r,[200,201]); q1=r.json().get("id")
chk("PU-02 giao bé khi đang chờ → 403",requests.post(B+f"/attendance/{aid}/pickup",json={"pickupRequestId":q1},headers=H("gv1")),[403])
chk("PU-03 gv tự xác nhận → 403",requests.post(B+f"/pickup-requests/{q1}/confirm",json={"note":"x"},headers=H("gv1")),[403])
chk("PU-04 ph2 xác nhận yêu cầu con ph1 → 403/404",requests.post(B+f"/pickup-requests/{q1}/confirm",json={},headers=H("ph2")),[403,404])
chk("PU-05 ph1 thấy yêu cầu",requests.get(B+"/pickup-requests",headers=H("ph1")),[200])
lst=items(requests.get(B+"/pickup-requests",headers=H("ph2")).json())
R.append(("PU-06 ph2 không thấy yêu cầu con ph1",len([x for x in lst if x.get("id")==q1]),0,"PASS" if not [x for x in lst if x.get("id")==q1] else "FAIL",""));print(R[-1])
r2=preq("Chú Năm"); q2=r2.json().get("id")
chk("PU-07 ph1 từ chối",requests.post(B+f"/pickup-requests/{q2}/reject",json={"note":"không quen"},headers=H("ph1")),[200,201])
chk("PU-08 giao bé khi bị từ chối → 403",requests.post(B+f"/attendance/{aid}/pickup",json={"pickupRequestId":q2},headers=H("gv1")),[403])
chk("PU-09 xác nhận lại yêu cầu đã từ chối → 4xx",requests.post(B+f"/pickup-requests/{q2}/confirm",json={},headers=H("ph1")),[400,409,403])
chk("PU-10 ph1 xác nhận",requests.post(B+f"/pickup-requests/{q1}/confirm",json={},headers=H("ph1")),[200,201])
chk("PU-10b chỉ PH xác nhận, chưa trường duyệt → 403",requests.post(B+f"/attendance/{aid}/pickup",json={"pickupRequestId":q1},headers=H("gv1")),[403])
chk("PU-10c admin duyệt (bước nhà trường)",requests.post(B+f"/pickup-requests/{q1}/confirm",json={},headers=H("admin")),[200,201])
chk("PU-11 giao bé sau đủ 2 bước",requests.post(B+f"/attendance/{aid}/pickup",json={"pickupRequestId":q1},headers=H("gv1")),[200,201])
gs=items(requests.get(B+f"/children/{kid['id']}/guardians",headers=H("admin")).json())
banned=[g for g in gs if g.get("canPickup") is False]
if not banned:
    banned=[requests.post(B+f"/children/{kid['id']}/guardians",json={"fullName":"Cấm đón","relation":"Chú","phone":"0909000000","canPickup":False},headers=H("admin")).json()]
chk("PU-12 người giám hộ bị cấm đón → 403",requests.post(B+f"/attendance/{aid}/pickup",json={"guardianId":banned[0]["id"]},headers=H("gv1")),[403,409])
chk("ATT-H lịch sử sửa điểm danh (gv)",requests.get(B+f"/attendance/{aid}/history",headers=H("gv1")),[200])
chk("ATT-H ph2 xem lịch sử con ph1",requests.get(B+f"/attendance/{aid}/history",headers=H("ph2")),[403,404])
# Ảnh
png=bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")
tk=[c for c in items(requests.get(B+f"/children?classId={mine}&limit=50",headers=H("admin")).json()) if c["id"]!=kid["id"]][-1]["id"]
r=requests.post(B+f"/children/{tk}/photo",files={"file":("a.png",png,"image/png")},headers=H("admin")); chk("PH-01 upload ảnh",r,[200,201])
chk("PH-02 upload .exe đổi đuôi → 400",requests.post(B+f"/children/{tk}/photo",files={"file":("x.jpg",b"MZ\x90\x00"*50,"image/jpeg")},headers=H("admin")),[400,415,422])
d={}; url=B+f"/children/{kid['id']}/photo"
if url:
    full=url if url.startswith("http") else S+url
    chk("PH-03 ảnh không đăng nhập → 401",requests.get(full),[401,403],full)
    chk("PH-04 ph2 xem ảnh con ph1 → 403",requests.get(full,headers=H("ph2")),[403,404])
    chk("PH-05 ph1 xem ảnh con mình",requests.get(full,headers=H("ph1")),[200])
else: R.append(("PH-03 không tìm thấy photoUrl",0,0,"FAIL",str(d)[:150]))
# Học phí / sức khỏe
chk("FEE-01 gv xem công nợ → 403",requests.get(B+"/debts",headers=H("gv1")),[403])
chk("FEE-02 ph2 xem số dư con ph1 → 403",requests.get(B+f"/children/{kid['id']}/balance",headers=H("ph2")),[403])
chk("FEE-03 ph1 xem số dư con mình",requests.get(B+f"/children/{kid['id']}/balance",headers=H("ph1")),[200])
chk("FEE-04 ph tạo khoản thu → 403",requests.post(B+"/fee-items",json={"name":"x","amount":1},headers=H("ph1")),[403])
chk("FEE-05 khoản thu số âm → 400",requests.post(B+"/fee-items",json={"name":"âm","amount":-100000,"type":"monthly","scope":"school"},headers=H("ketoan")),[400])
inv=items(requests.get(B+"/invoices",headers=H("ketoan")).json())
if inv:
    i0=inv[0]["id"]
    chk("FEE-06 thanh toán 0đ → 400",requests.post(B+f"/invoices/{i0}/payments",json={"amount":0,"method":"cash"},headers=H("ketoan")),[400])
    chk("FEE-07 gv ghi thanh toán → 403",requests.post(B+f"/invoices/{i0}/payments",json={"amount":1000,"method":"cash"},headers=H("gv1")),[403])
chk("HL-01 kt xem tăng trưởng → 403",requests.get(B+f"/children/{kid['id']}/growth",headers=H("ketoan")),[403])
chk("HL-02 ph1 thêm tăng trưởng → 403",requests.post(B+f"/children/{kid['id']}/growth",json={"date":today,"heightCm":90,"weightKg":13},headers=H("ph1")),[403])
chk("HL-03 cân nặng âm → 400",requests.post(B+f"/children/{kid['id']}/growth",json={"date":today,"heightCm":90,"weightKg":-5},headers=H("gv1")),[400])
chk("HL-04 ph2 xem nhật ký con ph1 → 403",requests.get(B+f"/children/{kid['id']}/daily-notes",headers=H("ph2")),[403])
chk("HL-05 gv sửa thực đơn → 403",requests.put(B+"/menus",json={"weekStart":today,"items":[]},headers=H("gv1")),[403])
print("TOTAL",len(R),"FAIL",sum(r[3]!="PASS" for r in R))
