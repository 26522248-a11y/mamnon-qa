"""Tạo lại tài khoản PH dùng trong script QA sau khi seed lại DB (idempotent)."""
import requests
B="http://localhost:3001/api/v1"
def login(u,p): return requests.post(B+"/auth/login",json={"username":u,"password":p}).json().get("accessToken")
A={"Authorization":"Bearer "+login("admin","123456")}
for f in ["import/ok_openpyxl.xlsx","import/ok_v2.xlsx"]:
    # ok_v2 dòng 3 cố ý dùng lại SĐT 0987000001 (khác tên) -> xác nhận gắn
    r=requests.post(B+"/imports/children",headers=A,files={"file":open(f,"rb")},data={"confirmLinks":'[{"row":3,"guardian":2}]'}); print(f,r.status_code)
# (username, mật khẩu đích, có buộc đổi MK không)
NEED=[("0987000001","123456",True),("0987000011","QNN76eKmqR",False),("0987000012","QaTest@2026",False)]
for u,pw,must in NEED:
    us=requests.get(B+"/users",params={"search":u},headers=A).json(); us=us.get("items",us)
    x=[i for i in us if i.get("username")==u]
    if not x: print(u,"KHÔNG TÌM THẤY"); continue
    tmp="Tmp@"+u[-4:]+"x" if not must else pw
    requests.post(B+f"/users/{x[0]['id']}/reset-password",json={"newPassword":tmp},headers=A)
    if not must:
        t=login(u,tmp); r=requests.post(B+"/auth/change-password",json={"currentPassword":tmp,"newPassword":pw},headers={"Authorization":"Bearer "+t}); print(u,r.status_code)
    print(u,"OK", "buộc đổi MK" if must else "")
