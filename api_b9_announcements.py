import requests,datetime,io,time
from PIL import Image
B="http://localhost:3001/api/v1";R=[]
tok=lambda u:requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"]
H=lambda u:{"Authorization":"Bearer "+tok(u)}
A,P,K=H("admin"),H("ph1"),H("ketoan")
def chk(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:160]));print(R[-1])
def img(c,fmt="PNG"):
    b=io.BytesIO(); Image.new("RGB",(50,50),c).save(b,fmt); return b.getvalue()
ids=[]
for i,c in enumerate(["red","blue","green","yellow","black","white","gray"]):
    r=requests.post(B+"/announcements/attachments",headers=A,files={"file":(f"{i}.png",img(c),"image/png")}); ids.append(r.json().get("id"))
chk("B9-01 tải ảnh",all(ids),ids[:2])
r=requests.post(B+"/announcements/attachments",headers=A,files={"file":("x.png",b"not an image","image/png")}); chk("B9-02 file giả ảnh → 4xx",400<=r.status_code<500,r.status_code)
r=requests.post(B+"/announcements/attachments",headers=P,files={"file":("x.png",img("red"),"image/png")}); chk("B9-03 PH tải ảnh → 403",r.status_code==403,r.status_code)
base={"title":"QA hẹn giờ","body":"QA","scope":"school","audience":"all"}
r=requests.post(B+"/announcements",headers=A,json={**base,"attachmentIds":ids}); chk("B9-04 7 ảnh → 400",r.status_code==400,r.status_code)
r=requests.post(B+"/announcements",headers=A,json={**base,"scheduledAt":"2020-01-01T07:30:00+07:00"}); chk("B9-05 giờ đã qua → SCHEDULE_IN_PAST","SCHEDULE_IN_PAST" in r.text,r.text[:100])
when=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(seconds=70)).isoformat(timespec="seconds")
r=requests.post(B+"/announcements",headers=A,json={**base,"scheduledAt":when,"attachmentIds":ids[:4]}); a=r.json(); aid=a.get("id")
chk("B9-06 tạo tin hẹn giờ",r.status_code==201 and a.get("status")=="scheduled",str(a.get("status"))+" "+str(a.get("scheduledAt")))
chk("B9-07 scheduledAt +07:00",str(a.get("scheduledAt","")).endswith("+07:00"),a.get("scheduledAt"))
chk("B9-08 thứ tự ảnh giữ nguyên",[x["id"] for x in a.get("attachments",[])]==ids[:4])
pl=requests.get(B+"/announcements",headers=P).json(); items=pl.get("items",pl)
chk("B9-09 PH chưa thấy tin trước giờ gửi",all(x["id"]!=aid for x in items))
chk("B9-10 PH chưa xem được ảnh",requests.get(B+f"/announcements/attachments/{ids[0]}",headers=P).status_code in (403,404))
r=requests.patch(B+f"/announcements/{aid}",headers=A,json={"title":"QA hẹn giờ (sửa)"}); chk("B9-11 sửa tin chưa gửi",r.status_code==200,r.status_code)
chk("B9-12 cron sai khoá → 401",requests.post(B+"/internal/cron/announcements",headers={"X-Cron-Secret":"sai"}).status_code==401)
time.sleep(75)
r=requests.post(B+"/internal/cron/announcements",headers={"X-Cron-Secret":"dev-cron-secret"}); chk("B9-13 cron chạy",r.status_code==200,r.text[:100])
pl=requests.get(B+"/announcements",headers=P).json(); items=pl.get("items",pl); x=[i for i in items if i["id"]==aid]
chk("B9-14 PH thấy tin sau giờ gửi",bool(x))
if x: chk("B9-15 PH thấy ảnh đúng thứ tự",[i["id"] for i in x[0].get("attachments",[])]==ids[:4])
chk("B9-16 PH xem được ảnh",requests.get(B+f"/announcements/attachments/{ids[0]}",headers=P).status_code==200)
r=requests.patch(B+f"/announcements/{aid}",headers=A,json={"title":"x"}); chk("B9-17 sửa tin đã gửi → 409",r.status_code==409,r.status_code)
r=requests.post(B+f"/announcements/{aid}/cancel",headers=A); chk("B9-18 huỷ hẹn tin đã gửi → 409",r.status_code==409,r.status_code)
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
