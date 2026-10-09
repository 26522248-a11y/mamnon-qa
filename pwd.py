import requests,time
B="http://localhost:3001/api/v1"
A={"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":"admin","password":"123456"}).json()["accessToken"]}
u="qapwd"+str(int(time.time()))[-5:]
r=requests.post(B+"/users",json={"username":u,"name":"QA Đổi MK","role":"teacher","password":"Tam12345"},headers=A);print("tạo",r.status_code,r.text[:200])
j=r.json();pw=j.get("tempPassword") or j.get("password") or "Tam12345"
l=requests.post(B+"/auth/login",json={"username":u,"password":pw});print("login",l.status_code,l.json().get("mustChangePassword") or l.json().get("user",{}).get("mustChangePassword"))
T={"Authorization":"Bearer "+l.json()["accessToken"]}
for p in ["/children","/classes","/notifications","/auth/me","/settings/school"]:
    x=requests.get(B+p,headers=T);print(p,x.status_code,(x.json().get("code") if x.status_code==403 else ""))
