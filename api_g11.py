"""G11 API: vào/ra ca idempotent, ra ca <1 phút → 409 CHECKOUT_TOO_SOON. Tài khoản qua env G11_USER=u:p, API qua env API.
G11_MODE=full (tài khoản chưa vào ca hôm nay, [ghi] tạo 1 lượt vào+ra ca) | repeat (tài khoản đã vào+ra ca: chỉ bấm lại, không đổi dữ liệu)."""
import os,time,requests,threading
B=os.environ["API"];u,p=os.environ["G11_USER"].split(":",1);MODE=os.environ.get("G11_MODE","repeat");R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:220]));print(R[-1],flush=True)
H={"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":p}).json()["accessToken"]}
t0=requests.get(B+"/staff/me/today",headers=H).json(); print("trước:",t0.get("date"),t0.get("checkInAt"),t0.get("checkOutAt"))
if MODE=="full":
    assert not t0.get("checkInAt"),"tài khoản đã vào ca hôm nay – dùng G11_MODE=repeat"
    rs=[];th=[threading.Thread(target=lambda: rs.append(requests.post(B+"/staff/me/check-in",headers=H,json={}))) for _ in range(3)]
    [x.start() for x in th];[x.join() for x in th]
    rec("G11-01 3 lần bấm Vào ca cùng lúc → tất cả 200, chỉ 1 giờ vào",all(r.status_code==200 for r in rs) and len({r.json().get("checkInAt") for r in rs})==1,[(r.status_code,r.json().get("alreadyCheckedIn"),r.json().get("checkInAt")) for r in rs])
    r=requests.post(B+"/staff/me/check-out",headers=H,json={}); rec("G11-02 Ra ca ngay (<1 phút) → 409 CHECKOUT_TOO_SOON, câu tiếng Việt",r.status_code==409 and "CHECKOUT_TOO_SOON" in r.text,r.text[:200])
    t=requests.get(B+"/staff/me/today",headers=H).json(); rec("G11-03 sau 409 chưa có giờ ra",not t.get("checkOutAt"),t.get("checkOutAt"))
    time.sleep(62)
    rs=[];th=[threading.Thread(target=lambda: rs.append(requests.post(B+"/staff/me/check-out",headers=H,json={}))) for _ in range(3)]
    [x.start() for x in th];[x.join() for x in th]
    rec("G11-04 sau 1 phút 3 lần Ra ca cùng lúc → 200, chỉ 1 giờ ra",all(r.status_code==200 for r in rs) and len({r.json().get("checkOutAt") for r in rs})==1,[(r.status_code,r.json().get("alreadyCheckedOut"),r.json().get("checkOutAt")) for r in rs])
t1=requests.get(B+"/staff/me/today",headers=H).json()
r=requests.post(B+"/staff/me/check-in",headers=H,json={}); j=r.json()
rec("G11-05 Vào ca lại → 200 alreadyCheckedIn, giờ vào không đổi",r.status_code==200 and j.get("alreadyCheckedIn") is True and j.get("checkInAt")==t1.get("checkInAt"),(r.status_code,j.get("alreadyCheckedIn"),j.get("checkInAt")))
r=requests.post(B+"/staff/me/check-out",headers=H,json={}); j=r.json()
rec("G11-06 Ra ca lại → 200 alreadyCheckedOut, giờ ra không đổi",r.status_code==200 and j.get("alreadyCheckedOut") is True and j.get("checkOutAt")==t1.get("checkOutAt"),(r.status_code,j.get("alreadyCheckedOut"),j.get("checkOutAt")))
t2=requests.get(B+"/staff/me/today",headers=H).json(); rec("G11-07 dữ liệu hôm nay không đổi sau khi bấm lại",(t2.get("checkInAt"),t2.get("checkOutAt"))==(t1.get("checkInAt"),t1.get("checkOutAt")),(t2.get("checkInAt"),t2.get("checkOutAt")))
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
