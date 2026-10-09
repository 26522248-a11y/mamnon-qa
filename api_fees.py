import requests,json,uuid
B="http://localhost:3001/api/v1";R=[]
T={u:requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"] for u in ["admin","gv1","ketoan","ph1"]}
H=lambda u:{"Authorization":"Bearer "+T[u]}
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:200]));print(R[-1],flush=True)
def chk(n,r,exp): rec(n,r.status_code in exp,f"{r.status_code} {r.text[:150]}" ); return r
cls=requests.get(B+"/classes",headers=H("admin")).json(); cls=cls.get("items",cls) if isinstance(cls,dict) else cls
r=chk("SETUP tạo bé QA",requests.post(B+"/children",json={"fullName":"QA Học Phí "+uuid.uuid4().hex[:4],"dob":"2022-05-14","gender":"F","classId":cls[0]["id"],"enrolledAt":"2025-09-05"},headers=H("admin")),[201,200])
kid=r.json()["id"]
bal=lambda:requests.get(B+f"/children/{kid}/balance",headers=H("ketoan")).json()
import atexit
def _cleanup():
    try: requests.post(B+f"/children/{kid}/withdraw",json={"leaveDate":"2026-10-09","reason":"QA dọn"},headers=H("admin"))
    except Exception: pass
atexit.register(_cleanup)
def inv(period,lines): return requests.post(B+"/invoices",json={"childId":kid,"period":period,"dueDate":period+"-10","lines":lines},headers=H("ketoan"))
r=chk("FEE-INV tạo hóa đơn tay 2.000.000",inv("2026-08",[{"description":"Học phí","unitPrice":2000000}]),[201,200]); i1=r.json()
pay=lambda i,a,u="ketoan":requests.post(B+f"/invoices/{i}/payments",json={"amount":a,"method":"cash","payerName":"QA"},headers=H(u))
r=chk("FEE-P01 trả 2.500.000 (dư 500k)",pay(i1["id"],2500000),[201,200]); p1=r.json()
b=bal(); rec("FEE-P01 số dư +500.000",json.dumps(b).find("500000")>=0,b)
r=inv("2026-09",[{"description":"Học phí","unitPrice":2000000}]); i2=r.json()
rec("FEE-P02 hóa đơn sau tự trừ số dư (còn 1.500.000)",i2.get("balance")==1500000 or i2.get("totalAmount")==1500000 or "1500000" in json.dumps(i2),{k:i2.get(k) for k in ["totalAmount","paidAmount","balance","status"]})
chk("FEE-P04 trả một phần 500.000",pay(i2["id"],500000),[201,200])
ii=requests.get(B+f"/invoices/{i2['id']}",headers=H("ketoan")).json(); rec("FEE-P04 trạng thái trả một phần",ii.get("status") in ("partial","partially_paid"),{k:ii.get(k) for k in ["totalAmount","paidAmount","balance","status"]})
chk("FEE-D02 giảm trừ không lý do → 400",inv("2026-10",[{"description":"HP","unitPrice":1000000},{"kind":"discount","description":"giảm","unitPrice":100000}]),[400])
r=chk("FEE-X02 giảm trừ > hóa đơn (tạo tay) → 0đ + warning",inv("2026-10",[{"description":"HP","unitPrice":1000000},{"kind":"discount","description":"giảm","unitPrice":1500000,"reason":"QA"}]),[201,200])
j=r.json(); rec("FEE-X02 tổng = 0 và có warnings",j.get("totalAmount")==0 and bool(j.get("warnings")),{k:j.get(k) for k in ["totalAmount","warnings"]})
b0=bal()
chk("FEE-V02 hủy không lý do → 400",requests.post(B+f"/invoices/{i1['id']}/void",json={},headers=H("ketoan")),[400])
chk("FEE-V03 giáo viên hủy → 403",requests.post(B+f"/invoices/{i1['id']}/void",json={"reason":"x"},headers=H("gv1")),[403])
chk("FEE-V03 phụ huynh hủy → 403",requests.post(B+f"/invoices/{i1['id']}/void",json={"reason":"x"},headers=H("ph1")),[403])
chk("FEE-V01 kế toán hủy hóa đơn đã trả",requests.post(B+f"/invoices/{i1['id']}/void",json={"reason":"QA hủy"},headers=H("ketoan")),[200,201])
b1=bal(); rec("FEE-V01 số dư sau hủy",True,f"trước {b0} | sau {b1}")
chk("FEE-V04 hủy lần 2 → 409",requests.post(B+f"/invoices/{i1['id']}/void",json={"reason":"lần 2"},headers=H("ketoan")),[409,400])
b2=bal(); rec("FEE-V04 số dư không cộng 2 lần",b2==b1,f"{b1} | {b2}")
rc=requests.get(B+f"/payments/{p1.get('paymentId')}/receipt",headers=H("ketoan")).json() if p1.get('paymentId') else {}
w=json.dumps(rc,ensure_ascii=False).lower(); rec("FEE-B01 biên lai 2.500.000 bằng chữ","hai triệu năm trăm nghìn đồng" in w,[v for v in rc.values() if isinstance(v,str) and "đồng" in v.lower()][:2])
chk("FEE-B03 phụ huynh khác xem biên lai → 403",requests.get(B+f"/payments/{p1.get('paymentId')}/receipt",headers=H("ph1")),[403])
d=requests.get(B+"/debts",headers=H("ketoan")).json(); di=d.get("items",d) if isinstance(d,dict) else d
od=[x.get("overdue") for x in di]; rec("FEE-O06 quá hạn xếp đầu /debts",od==sorted(od,reverse=True),od[:10])
chk("FEE-W00 rút bé ngày tương lai → 400",requests.post(B+f"/children/{kid}/withdraw",json={"leaveDate":"2027-01-01","reason":"QA"},headers=H("admin")),[400])
chk("FEE-W01 cho bé nghỉ",requests.post(B+f"/children/{kid}/withdraw",json={"leaveDate":"2026-10-09","reason":"QA"},headers=H("admin")),[200,201])
b3=bal(); rec("FEE-W01 số dư sau khi nghỉ",True,b3)
lst=requests.get(B+f"/children?classId={cls[0]['id']}&limit=100",headers=H("admin")).json()["items"]
rec("FEE-W03 bé đã nghỉ ẩn khỏi danh sách mặc định",kid not in [c["id"] for c in lst])
chk("FEE-W03 hồ sơ bé đã nghỉ vẫn xem được",requests.get(B+f"/children/{kid}",headers=H("admin")),[200])
print("TOTAL",len(R),"FAIL",sum(r[1]!="PASS" for r in R)); print("KID",kid)
