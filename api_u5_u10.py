"""U5 (người đón hộ chỉ cần tên + SĐT) và U10 (giao bé → báo phụ huynh, không gửi trùng).
Chạy: python api_u5_u10.py [API] [ADMIN user:mk] [PH user:mk]   (mặc định local admin, ph2). [ghi] tạo 1 người đón 'QA U5 ...' + 1 lượt giao bé hôm nay."""
import sys,io,uuid,datetime,requests
from PIL import Image
a=sys.argv+[None]*4;B=a[1] or "http://localhost:3001/api/v1";AD=(a[2] or "admin:123456").split(":",1);PH=(a[3] or "ph2:123456").split(":",1);R=[]
def chk(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:180]));print(R[-1],flush=True)
tok=lambda u,p:requests.post(B+"/auth/login",json={"username":u,"password":p}).json()["accessToken"]
A={"Authorization":"Bearer "+tok(*AD)};P={"Authorization":"Bearer "+tok(*PH)}
def jpg(c="red"): b=io.BytesIO(); Image.new("RGB",(80,80),c).save(b,"JPEG"); return b.getvalue()
kid=requests.get(B+"/children",headers=P).json()["items"][0]; cid=kid["id"]; d=datetime.date.today().isoformat()
name="QA U5 "+uuid.uuid4().hex[:4]
# U5
r=requests.post(B+f"/children/{cid}/authorized-pickers",headers=P,data={"fullName":name}); chk("U5-01 thiếu SĐT → 400",r.status_code==400,r.text[:120])
r=requests.post(B+f"/children/{cid}/authorized-pickers",headers=P,data={"fullName":name,"phone1":"abc"}); chk("U5-02 SĐT sai → 400, lời báo dễ hiểu",r.status_code==400,r.text[:150])
r=requests.post(B+f"/children/{cid}/authorized-pickers",headers=P,data={"fullName":name,"phone1":"0909"+uuid.uuid4().int.__str__()[:6]})
pk=r.json(); pid=pk.get("id"); chk("U5-03 chỉ tên + SĐT → tạo được",r.status_code==201,r.text[:150])
chk("U5-04 không có ảnh → photoUrl null",pk.get("photoUrl") is None,pk.get("photoUrl"))
chk("U5-05 ảnh chưa có → 404",requests.get(B+f"/authorized-pickers/{pid}/photo",headers=A).status_code==404)
r=requests.post(B+f"/authorized-pickers/{pid}/approve",headers=A,json={}); chk("U5-06 BGH duyệt",r.status_code==200,r.text[:100])
# U10
cls=kid.get("classId") or requests.get(B+f"/children/{cid}",headers=A).json()["classId"]
requests.put(B+f"/classes/{cls}/attendance",headers=A,json={"date":d,"items":[{"childId":cid,"status":"present"}]})
att=[i for i in requests.get(B+f"/classes/{cls}/attendance",headers=A,params={"date":d}).json()["items"] if i["childId"]==cid][0]; aid=att["attendanceId"]
chk("U10-00 bé có mặt hôm nay",bool(aid) and not att.get("pickup"),att.get("pickup"))
cnt=lambda:sum(1 for n in requests.get(B+"/notifications",headers=P).json().get("items",[]) if "đã được đón" in (n.get("title","")+n.get("body","")) and kid["fullName"].split()[-1] in (n.get("title","")+n.get("body","")))
n0=cnt()
r=requests.post(B+f"/attendance/{aid}/pickup",headers=A,data={"authorizedPickerId":pid},files={"photo":("p.jpg",jpg(),"image/jpeg")}); chk("U10-01 giao bé kèm ảnh",r.status_code in(200,201),r.text[:150])
r2=requests.post(B+f"/attendance/{aid}/pickup",headers=A,data={"authorizedPickerId":pid}); chk("U10-02 bấm giao lần 2 → từ chối",r2.status_code in(400,409),r2.status_code)
n1=cnt(); chk("U10-03 phụ huynh nhận đúng 1 thông báo 'đã được đón'",n1-n0==1,f"{n0}->{n1}")
nn=[n for n in requests.get(B+"/notifications",headers=P).json()["items"] if "đã được đón" in (n.get("title","")+n.get("body",""))][:1]
txt=str(nn[0]) if nn else ""; chk("U10-04 thông báo có tên người đón và giờ",name in txt and ":" in txt,txt[:180])
chk("U10-05 PH xem được ảnh lúc giao",requests.get(B+f"/attendance/{aid}/pickup-photo",headers=P).status_code==200)
O=tok("ph1","123456") if "localhost" in B else None
if O: chk("U10-06 PH khác không xem được ảnh giao",requests.get(B+f"/attendance/{aid}/pickup-photo",headers={"Authorization":"Bearer "+O}).status_code in(403,404))
chk("U5-07 ảnh lần giao đầu thành ảnh người đón",requests.get(B+f"/authorized-pickers/{pid}/photo",headers=A).status_code==200)
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
