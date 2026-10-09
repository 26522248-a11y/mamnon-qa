"""Smoke test bản chạy thử (staging). Chỉ đọc là chính; các bước có ghi dữ liệu được đánh dấu [ghi] và dùng tiêu đề 'SMOKE ...' để dễ dọn.
Chạy:  API=https://<backend>/api/v1 WEB=https://<web> ADMIN=admin:<mk> GV=<user>:<mk> KT=<user>:<mk> PH=<user>:<mk> CRON=<secret> python smoke_staging.py
Thiếu tài khoản nào thì bỏ qua nhóm bước của vai trò đó."""
import os,requests,datetime,time
API=os.environ["API"].rstrip("/");WEB=os.environ.get("WEB","").rstrip("/");R=[]
def chk(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:160]));print(R[-1],flush=True)
def login(k):
    v=os.environ.get(k)
    if not v: print("BỎ QUA",k); return None
    u,p=v.split(":",1); r=requests.post(API+"/auth/login",json={"username":u,"password":p})
    chk(f"LOGIN {k}",r.status_code==200,r.status_code); return {"Authorization":"Bearer "+r.json()["accessToken"]} if r.ok else None
g=lambda h,u,**k: requests.get(API+u,headers=h,timeout=30,**k)
# 0. Hạ tầng
chk("HC-01 /settings/school (tên trường thật)","Như Ý" in requests.get(API+"/settings/school",timeout=60).text)
if WEB: r=requests.get(WEB+"/login",timeout=60); chk("HC-02 web /login",r.status_code==200,r.status_code)
chk("HC-03 mật khẩu mẫu 123456 bị từ chối",requests.post(API+"/auth/login",json={"username":"admin","password":"123456"}).status_code!=200)
A,G,K,P=login("ADMIN"),login("GV"),login("KT"),login("PH")
today=datetime.date.today().isoformat()
if A:
    chk("ADM-01 danh sách lớp",g(A,"/classes").ok); chk("ADM-02 danh sách trẻ",g(A,"/children").ok)
    chk("ADM-03 công nợ",g(A,"/debts").ok); chk("ADM-04 lịch sử thay đổi",g(A,"/audit/sensitive").ok)
    chk("ADM-05 chấm công",g(A,"/staff/attendance").ok); chk("ADM-06 thu chi tổng",g(A,"/finance/summary").ok)
    chk("ADM-07 xem trông thay",g(A,"/staff/substitutions/needs").ok)
if G:
    c=g(G,"/classes").json(); c=(c.get("items",c) if isinstance(c,dict) else c)
    chk("GV-01 có lớp phụ trách",bool(c))
    if c: chk("GV-02 mở điểm danh hôm nay",g(G,f"/classes/{c[0]['id']}/attendance",params={"date":today}).ok)
    chk("GV-03 chấm công của mình",g(G,"/staff/me/today").ok)
    chk("GV-04 bị chặn thu chi",g(G,"/finance/summary").status_code==403)
    chk("GV-05 bị chặn lịch sử thay đổi",g(G,"/audit/sensitive").status_code==403)
if K:
    chk("KT-01 thu chi",g(K,"/finance/summary").ok); chk("KT-02 công nợ",g(K,"/debts").ok)
if P:
    chk("PH-01 thấy con",bool(g(P,"/children").json().get("items")))
    chk("PH-02 thông báo",g(P,"/announcements").ok)
    chk("PH-03 bị chặn thu chi",g(P,"/finance/summary").status_code==403)
# [ghi] Thông báo hẹn giờ + cron (chỉ khi có ADMIN, PH và CRON)
if A and P and os.environ.get("CRON"):
    when=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=75)).isoformat(timespec="seconds")
    r=requests.post(API+"/announcements",headers=A,json={"title":"SMOKE hẹn giờ","body":"Tin kiểm thử, vui lòng bỏ qua","scope":"school","audience":"staff","scheduledAt":when})
    aid=r.json().get("id"); chk("ANN-01 tạo tin hẹn giờ (chỉ gửi nhân viên)",r.status_code==201,r.text[:100])
    time.sleep(80); r=requests.post(API+"/internal/cron/announcements",headers={"X-Cron-Secret":os.environ["CRON"]})
    chk("ANN-02 cron gửi tin",r.ok and aid in r.text,r.text[:100])
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
