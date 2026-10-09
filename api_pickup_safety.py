import requests,datetime,uuid
B="http://localhost:3001/api/v1";R=[]
def tok(u,p="123456"): return requests.post(B+"/auth/login",json={"username":u,"password":p}).json().get("accessToken")
H=lambda t:{"Authorization":"Bearer "+t}
A,G,K,P2=tok("admin"),tok("gv1"),tok("ketoan"),tok("ph2"); P=tok("0987000011","QNN76eKmqR")
def chk(n,r,exp): ok=r.status_code in exp; R.append((n,r.status_code,"PASS" if ok else "FAIL",r.text[:140] if not ok else "")); print(R[-1],flush=True); return r
d=datetime.date.today().isoformat()
c=requests.get(B+"/classes",headers=H(G)).json(); c=(c.get("items",c) if isinstance(c,dict) else c)[0]["id"]
kid=[k for k in requests.get(B+"/children",headers=H(P)).json()["items"]][0]["id"]
requests.put(B+f"/classes/{c}/attendance",json={"date":d,"items":[{"childId":kid,"status":"present"}]},headers=H(G))
aid=[i for i in requests.get(B+f"/classes/{c}/attendance?date={d}",headers=H(G)).json()["items"] if i["childId"]==kid][0]
aid=aid.get("attendanceId") or aid.get("id")
def newreq(n): return requests.post(B+f"/attendance/{aid}/pickup-requests",json={"pickerName":n,"pickerPhone":"0909555666","note":"QA","relation":"Cô"},headers=H(G))
q=chk("D00 gv tạo yêu cầu",newreq("QA Hai Bước"),[201]).json()["id"]
chk("D06 gv duyệt bước trường → 403",requests.post(B+f"/pickup-requests/{q}/confirm",json={},headers=H(G)),[403])
chk("D06 kế toán duyệt → 403",requests.post(B+f"/pickup-requests/{q}/confirm",json={},headers=H(K)),[403])
chk("B03 ph2 xác nhận con người khác → 403",requests.post(B+f"/pickup-requests/{q}/confirm",json={},headers=H(P2)),[403,404])
chk("D02 chỉ trường duyệt",requests.post(B+f"/pickup-requests/{q}/confirm",json={},headers=H(A)),[200,201])
chk("D02 giao khi PH chưa xác nhận → 403",requests.post(B+f"/attendance/{aid}/pickup",json={"pickupRequestId":q},headers=H(G)),[403])
chk("B07 push action token giả → 403",requests.post(B+"/push/actions",json={"token":"gia.mao.token","action":"confirm","requestId":q}),[403])
chk("D01 PH xác nhận",requests.post(B+f"/pickup-requests/{q}/confirm",json={},headers=H(P)),[200,201])
chk("D03 đủ 2 bước → giao được",requests.post(B+f"/attendance/{aid}/pickup",json={"pickupRequestId":q},headers=H(G)),[201,200])
chk("D07 giao lần 2 → 409",requests.post(B+f"/attendance/{aid}/pickup",json={"pickupRequestId":q},headers=H(G)),[409])
chk("D-x tạo yêu cầu khi bé đã giao → 409",newreq("QA Muộn"),[409])
chk("E02 trường từ chối thiếu ghi chú → 400 (tạo yêu cầu bé khác)",requests.post(B+f"/pickup-requests/{q}/reject",json={},headers=H(A)),[400,409])
# trực đón
gv2=[u for u in requests.get(B+"/users?limit=50",headers=H(A)).json().get("items",[]) if u["username"]=="gv2"][0]["id"]
chk("G04 gv tự chỉ định trực đón → 403",requests.post(B+"/pickup-duties",json={"userId":gv2,"dates":[d]},headers=H(G)),[403])
chk("G01 admin chỉ định gv2 trực hôm nay",requests.post(B+"/pickup-duties",json={"userId":gv2,"dates":[d]},headers=H(A)),[200,201])
me=requests.get(B+"/pickup-duties/me",headers=H(tok("gv2"))).json(); R.append(("G01 gv2 canApproveToday",0,"PASS" if me.get("canApproveToday") else "FAIL",str(me)[:120]));print(R[-1])
# người đón hộ
png=bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")
f=lambda: {"fullName":"QA Dì Ba","relation":"Dì","idNumber":"079123456789","phone1":"0909111222"}
chk("A02 thiếu ảnh → 400",requests.post(B+f"/children/{kid}/authorized-pickers",data=f(),headers=H(P)),[400])
chk("A03 CCCD 11 số → 400",requests.post(B+f"/children/{kid}/authorized-pickers",data={**f(),"idNumber":"07912345678"},files={"photo":("a.png",png,"image/png")},headers=H(P)),[400])
chk("A04 ph2 thêm cho bé khác → 403",requests.post(B+f"/children/{kid}/authorized-pickers",data=f(),files={"photo":("a.png",png,"image/png")},headers=H(P2)),[403])
chk("I08 ảnh .exe đổi đuôi .heic → 400",requests.post(B+f"/children/{kid}/authorized-pickers",data=f(),files={"photo":("x.heic",open("heic/gia_exe.heic","rb"),"image/heic")},headers=H(P)),[400])
r=chk("I07 ảnh HEIC thật → 201",requests.post(B+f"/children/{kid}/authorized-pickers",data=f(),files={"photo":("t.heic",open("heic/that.heic","rb"),"image/heic")},headers=H(P)),[201])
pk=r.json().get("id")
if pk:
    ph=requests.get(B+f"/authorized-pickers/{pk}/photo",headers=H(P)); R.append(("I07 lưu thành JPEG",ph.status_code,"PASS" if ph.content[:3]==b"\xff\xd8\xff" else "FAIL",ph.headers.get("content-type")));print(R[-1])
    chk("A05 ảnh người đón: không login → 401",requests.get(B+f"/authorized-pickers/{pk}/photo"),[401])
    chk("A05 ảnh người đón: ph2 → 403",requests.get(B+f"/authorized-pickers/{pk}/photo",headers=H(P2)),[403])
    v=requests.get(B+f"/children/{kid}/authorized-pickers",headers=H(P)).json(); s=str(v)
    R.append(("A08 danh sách không lộ CCCD đầy đủ",0,"PASS" if "079123456789" not in s else "FAIL",""));print(R[-1])
    chk("D08b người đón hộ chưa duyệt → giao bị chặn",requests.post(B+f"/attendance/{aid}/pickup",json={"authorizedPickerId":pk},headers=H(G)),[403,409])
    chk("A-x reject thiếu ghi chú → 400",requests.post(B+f"/authorized-pickers/{pk}/reject",json={},headers=H(A)),[400])
# số liên hệ
chk("I02 số 1 = số 2 → 400",requests.patch(B+f"/children/{kid}/contact-phones",json={"phone1":"0909000111","phone2":"0909000111"},headers=H(P)),[400])
chk("I03 ph2 sửa số bé khác → 403",requests.patch(B+f"/children/{kid}/contact-phones",json={"phone1":"0909000111"},headers=H(P2)),[403])
chk("I03 gv sửa số → 403",requests.patch(B+f"/children/{kid}/contact-phones",json={"phone1":"0909000111"},headers=H(G)),[403])
chk("I01 PH sửa số hợp lệ",requests.patch(B+f"/children/{kid}/contact-phones",json={"phone1":"0909000111","phone2":"0909000222"},headers=H(P)),[200])
h=requests.get(B+f"/children/{kid}/contact-phones/history",headers=H(A)).json(); R.append(("I01 có lịch sử",0,"PASS" if h.get("items") else "FAIL",""));print(R[-1])
print("TOTAL",len(R),"FAIL",sum(r[2]!="PASS" for r in R))
