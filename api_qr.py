import requests,json
B="http://localhost:3001/api/v1";R=[];INV=[]
def tk(u): return {"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"]}
A,G,K,P1,P2=[tk(u) for u in ["admin","gv1","ketoan","ph1","ph2"]]
def c(n,r,e): R.append((n,r.status_code,"PASS" if r.status_code in e else "FAIL",("" if r.status_code in e else r.text[:150]))); return r
def ok(n,b,i=""): R.append((n,"-","PASS" if b else "FAIL",str(i)[:150]))
L=lambda j:j if isinstance(j,list) else j.get("items",[])
kid=L(requests.get(B+"/children",headers=P1).json())[0]["id"]
def inv(p,amt): r=requests.post(B+"/invoices",json={"childId":kid,"period":p,"dueDate":p+"-10","lines":[{"description":"QA QR","unitPrice":amt}]},headers=K); j=r.json(); INV.append(j["id"]); return j
try:
    i=inv("2027-03",1000000); I=i["id"]
    r=c("QR-01 PH xem QR",requests.get(B+f"/invoices/{I}/qr",headers=P1),[200]); q=r.json()
    ok("QR-01 số tiền = còn nợ, nội dung = mã HĐ",q.get("amount")==i.get("totalAmount",1000000)-i.get("paidAmount",0) and q.get("transferContent")==q.get("invoiceNo"),{k:q.get(k) for k in["amount","transferContent","invoiceNo"]})
    ok("QR-04 sample:true",q.get("sample") is True)
    c("QR-02 ph2 xem QR 403",requests.get(B+f"/invoices/{I}/qr",headers=P2),[403])
    c("QR-02 gv xem QR 403",requests.get(B+f"/invoices/{I}/qr",headers=G),[403])
    c("QR-02 ph2 báo chuyển 403",requests.post(B+f"/invoices/{I}/transfer-claims",json={},headers=P2),[403])
    c("QR future 400",requests.post(B+f"/invoices/{I}/transfer-claims",json={"transferredAt":"2027-01-01T00:00:00Z"},headers=P1),[400])
    r1=c("QR-05 PH báo chuyển 201",requests.post(B+f"/invoices/{I}/transfer-claims",json={"amount":600000},headers=P1),[201]); cl=r1.json()["claim"]
    r2=c("QR-06 báo lần 2 → 200",requests.post(B+f"/invoices/{I}/transfer-claims",json={},headers=P1),[200]); ok("QR-06 cùng claim",r2.json()["claim"]["id"]==cl["id"])
    d=requests.get(B+f"/invoices/{I}",headers=K).json(); ok("QR-05/10 HĐ chưa trả, paymentStatus chờ",d.get("status")=="unpaid" and d.get("paidAmount",0)==0 and d.get("paymentStatus")=="pending_confirmation",{k:d.get(k) for k in["status","paidAmount","paymentStatus"]})
    c("QR-08 gv confirm 403",requests.post(B+f"/transfer-claims/{cl['id']}/confirm",json={},headers=G),[403])
    c("QR-08 ph1 confirm 403",requests.post(B+f"/transfer-claims/{cl['id']}/confirm",json={},headers=P1),[403])
    c("QR-08 ph1 list claims 403",requests.get(B+"/transfer-claims",headers=P1),[403])
    c("QR-07 reject thiếu lý do 400",requests.post(B+f"/transfer-claims/{cl['id']}/reject",json={"reason":"  "},headers=K),[400])
    c("QR-07 reject có lý do",requests.post(B+f"/transfer-claims/{cl['id']}/reject",json={"reason":"QA chưa thấy tiền"},headers=K),[200,201])
    c("QR-07 confirm sau reject 409",requests.post(B+f"/transfer-claims/{cl['id']}/confirm",json={},headers=K),[409])
    cl2=c("QR-07 PH báo lại sau từ chối 201",requests.post(B+f"/invoices/{I}/transfer-claims",json={"amount":600000},headers=P1),[201]).json()["claim"]
    r=c("QR-09 confirm thiếu (600k/1tr)",requests.post(B+f"/transfer-claims/{cl2['id']}/confirm",json={},headers=K),[200,201]); ok("QR-07 có phiếu thu",bool(r.json().get("receipt")))
    d=requests.get(B+f"/invoices/{I}",headers=K).json(); ok("QR-09 partial, còn 400k",d.get("status") in("partial","partially_paid") and d.get("paidAmount")==600000,{k:d.get(k) for k in["status","paidAmount","paymentStatus"]})
    q=requests.get(B+f"/invoices/{I}/qr",headers=P1).json(); ok("QR-01 QR sau trả 1 phần = 400k",q.get("amount")==400000,q.get("amount"))
    cl3=requests.post(B+f"/invoices/{I}/transfer-claims",json={"amount":700000},headers=P1).json()["claim"]
    c("QR-09 confirm dư (700k/400k)",requests.post(B+f"/transfer-claims/{cl3['id']}/confirm",json={},headers=K),[200,201])
    d=requests.get(B+f"/invoices/{I}",headers=K).json(); ok("QR-09 HĐ paid",d.get("status")=="paid",d.get("status"))
    c("QR-03 QR HĐ đã trả 409",requests.get(B+f"/invoices/{I}/qr",headers=P1),[409])
    c("QR-03 báo chuyển HĐ đã trả 409",requests.post(B+f"/invoices/{I}/transfer-claims",json={},headers=P1),[409])
    j=inv("2027-04",500000); cl4=requests.post(B+f"/invoices/{j['id']}/transfer-claims",json={},headers=P1).json()["claim"]
    c("void HĐ có claim chờ",requests.post(B+f"/invoices/{j['id']}/void",json={"reason":"QA"},headers=K),[200,201])
    x=[y for y in L(requests.get(B+"/transfer-claims?status=rejected",headers=K).json()) if y["id"]==cl4["id"]]; ok("void → claim tự từ chối",bool(x) and x[0].get("rejectReason"),x and x[0].get("rejectReason"))
    c("QR-03 QR HĐ đã hủy 409",requests.get(B+f"/invoices/{j['id']}/qr",headers=P1),[409])
finally:
    for x in R: print(x)
    print(sum(x[2]=="PASS" for x in R),"/",len(R)); print("INV",INV)
