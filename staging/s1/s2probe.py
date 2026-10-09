"""S2 (Nest 11 / Express 5): kiểm nhanh các điểm dễ vỡ của API trên staging. Chỉ đọc, trừ 1 upload ảnh người đón tạm rồi xoá."""
import os,io,requests
from PIL import Image
B="https://mamnon-api.onrender.com/api/v1"; R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:220]));print(R[-1],flush=True)
def tok(k):
    u,p=os.environ[k].split(":",1); return {"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":p}).json()["accessToken"]}
A,G,P=tok("SA"),tok("SG"),tok("SP")
r=requests.post(B+"/auth/login",json={"username":"hieutruong","password":"sai-mat-khau"}); rec("X-01 sai mật khẩu → 401 JSON có code",r.status_code==401 and r.headers.get("content-type","").startswith("application/json"),r.text[:100])
r=requests.post(B+"/auth/login",data="{bad json",headers={"Content-Type":"application/json"}); rec("X-02 body JSON hỏng → 400 (không 500)",r.status_code==400,(r.status_code,r.text[:100]))
r=requests.post(B+"/auth/login",json={"username":"x","password":"y","hack":1}); rec("X-03 trường lạ bị chặn (whitelist) → 400",r.status_code==400,(r.status_code,r.text[:120]))
r=requests.get(B+"/khong-ton-tai",headers=A); rec("X-04 route không có → 404",r.status_code==404,r.status_code)
r=requests.get(B+"/children",headers=A,params={"limit":"5"}); rec("X-05 query số (limit=5) vẫn chạy",r.ok,(r.status_code,r.text[:80]))
r=requests.get(B+"/children",headers=A,params={"a[b]":"1"}); rec("X-06 query lồng a[b]=1 không gây 500",r.status_code<500,(r.status_code,r.text[:100]))
r=requests.get(B+"/staff/attendance",headers=A,params={"from":"2026-10-12","to":"2026-10-12"}); rec("X-07 query ngày from/to",r.ok and r.json().get("from")=="2026-10-12",r.status_code)
r=requests.get(B+"/staff/attendance",headers=A,params={"from":"sai"}); rec("X-08 ngày sai → 400 (không 500)",r.status_code==400,(r.status_code,r.text[:100]))
r=requests.get(B+"/notifications",headers=P,params={"limit":"3"}); rec("X-09 thông báo PH limit=3",r.ok,r.status_code)
r=requests.options(B+"/children",headers={"Origin":"https://mamnon-web.vercel.app","Access-Control-Request-Method":"GET"}); rec("X-10 CORS preflight cho web",r.status_code in(200,204) and "mamnon-web.vercel.app" in r.headers.get("access-control-allow-origin",""),(r.status_code,r.headers.get("access-control-allow-origin")))
r=requests.get(B+"/finance/summary",headers=G); rec("X-11 GV vào thu chi → 403",r.status_code==403,r.status_code)
r=requests.get(B+"/children"); rec("X-12 không token → 401",r.status_code==401,r.status_code)
# multipart (multer trên Express 5)
kids=requests.get(B+"/children",headers=P).json(); kids=kids.get("items",kids); kid=kids[0]["id"]
img=io.BytesIO(); Image.new("RGB",(300,300),"green").save(img,"JPEG")
r=requests.post(B+f"/children/{kid}/authorized-pickers",headers=P,data={"fullName":"QA S2 tạm","relation":"Cô","phone1":"0911000888","idNumber":"079000000888"},files={"photo":("a.jpg",img.getvalue(),"image/jpeg")})
rec("X-13 upload multipart ảnh người đón → 201",r.status_code==201,(r.status_code,r.text[:120]))
if r.status_code==201:
    pid=r.json()["id"]; g=requests.get(B+f"/authorized-pickers/{pid}/photo",headers=P); rec("X-14 đọc lại ảnh → 200 image/jpeg",g.status_code==200 and g.headers.get("content-type")=="image/jpeg",(g.status_code,g.headers.get("content-type")))
    d=requests.delete(B+f"/authorized-pickers/{pid}",headers=P); rec("X-15 xoá người đón tạm",d.status_code in(200,204),(d.status_code,d.text[:100]))
r=requests.post(B+f"/children/{kid}/authorized-pickers",headers=P,data={"fullName":"QA S2 giả","relation":"Cô","phone1":"0911000889","idNumber":"079000000889"},files={"photo":("x.jpg",b"MZ not an image","image/jpeg")})
rec("X-16 file giả ảnh → 400",r.status_code==400,(r.status_code,r.text[:100]))
if r.status_code==201: requests.delete(B+f"/authorized-pickers/{r.json()['id']}",headers=P)
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
