import requests
B="http://localhost:3001/api/v1";R=[]
def tk(u): return {"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"]}
A,G,G2,P1,P2,K=[tk(u) for u in ["admin","gv1","gv2","ph1","ph2","ketoan"]]
def c(n,r,e): R.append((n,r.status_code,"PASS" if r.status_code in e else "FAIL",(r.text[:120] if r.status_code not in e else "")))
L=lambda j:j if isinstance(j,list) else j.get("items",[])
gcls=requests.get(B+"/auth/me",headers=G).json()["classIds"]
kid=[k for k in L(requests.get(B+"/children",headers=P1).json()) if k.get("classId") in gcls][0]["id"]
# thuốc
r=requests.post(B+f"/children/{kid}/medicines",json={"date":"2026-10-09","name":"QA siro","dose":"5 ml","doses":[{"time":"11:30"}]},headers=P1);c("MED tạo",r,[201]);m=r.json()
c("MED ph2 tạo cho con ph1 403",requests.post(B+f"/children/{kid}/medicines",json={"date":"2026-10-12","name":"x","dose":"1","doses":[{"time":"11:30"}]},headers=P2),[403])
c("MED ngày quá khứ 400",requests.post(B+f"/children/{kid}/medicines",json={"date":"2026-10-08","name":"x","dose":"1","doses":[{"time":"11:30"}]},headers=P1),[400])
c("MED thiếu liều 400",requests.post(B+f"/children/{kid}/medicines",json={"date":"2026-10-12","name":"x"},headers=P1),[400])
c("MED cuối tuần 400",requests.post(B+f"/children/{kid}/medicines",json={"date":"2026-10-10","name":"x","dose":"1","doses":[{"time":"11:30"}]},headers=P1),[400])
did=m["doses"][0]["id"]
c("MED gv2 lớp khác cho uống 403",requests.post(B+f"/medicine-doses/{did}/given",json={},headers=G2),[403])
c("MED gv1 cho uống",requests.post(B+f"/medicine-doses/{did}/given",json={},headers=G),[200,201])
c("MED cho uống lần 2 409",requests.post(B+f"/medicine-doses/{did}/given",json={},headers=G),[409])
c("MED hủy sau khi đã uống 409",requests.delete(B+f"/medicines/{m['id']}",headers=P1),[409])
r=requests.post(B+f"/children/{kid}/medicines",json={"date":"2026-10-12","name":"QA hủy","dose":"1 viên","doses":[{"time":"08:30"},{"time":"15:30"}]},headers=P1);c("MED tạo 2 liều",r,[201])
c("MED PH hủy chưa uống",requests.delete(B+f"/medicines/{r.json()['id']}",headers=P1),[200])
# đón muộn
c("LP hôm nay giờ đã qua 400",requests.post(B+f"/children/{kid}/late-pickups",json={"date":"2026-10-09","time":"17:30"},headers=P1),[400])
c("LP ngoài giờ 400",requests.post(B+f"/children/{kid}/late-pickups",json={"date":"2026-10-12","time":"19:00"},headers=P1),[400])
r=requests.post(B+f"/children/{kid}/late-pickups",json={"date":"2026-10-12","time":"17:30","pickerName":"QA"},headers=P1);c("LP tạo",r,[201]);lp=r.json().get("id")
c("LP trùng 409",requests.post(B+f"/children/{kid}/late-pickups",json={"date":"2026-10-12","time":"17:45"},headers=P1),[409])
c("LP ph2 xem 403",requests.get(B+f"/children/{kid}/late-pickups",headers=P2),[403])
c("LP ph2 hủy 403",requests.delete(B+f"/late-pickups/{lp}",headers=P2),[403])
c("LP PH hủy",requests.delete(B+f"/late-pickups/{lp}",headers=P1),[200])
# cờ ảnh
r=requests.get(B+f"/children/{kid}/photo-consent",headers=P1);c("CON PH xem",r,[200]);print("consent",r.text[:200])
c("CON-02 ph2 xem 403",requests.get(B+f"/children/{kid}/photo-consent",headers=P2),[403])
c("CON gv2 xem 403",requests.get(B+f"/children/{kid}/photo-consent",headers=G2),[403])
# đóng cửa đột xuất
c("EMG thiếu lý do 400",requests.post(B+"/holidays/emergency",json={"date":"2026-10-09","dryRun":True},headers=A),[400])
for n,h in [("gv1",G),("ketoan",K),("ph1",P1)]: c(f"EMG {n} 403",requests.post(B+"/holidays/emergency",json={"date":"2026-10-09","reason":"QA","dryRun":True},headers=h),[403])
r=requests.post(B+"/holidays/emergency",json={"date":"2026-10-09","reason":"QA bão","dryRun":True},headers=A);c("EMG dryRun",r,[200,201]);print("dry",r.text[:300])
c("EMG dryRun không ghi",requests.get(B+"/settings/school",headers=P1),[200]);print("closure",requests.get(B+"/settings/school",headers=P1).json().get("todayClosure"))
d=requests.get(B+"/dashboard",headers=A);print("dash attention",d.status_code,str(d.json().get("attention",""))[:200])
for x in R: print(x)
print(sum(x[2]=="PASS" for x in R),"/",len(R))
