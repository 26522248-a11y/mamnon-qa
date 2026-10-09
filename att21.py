import requests
B="http://localhost:3001/api/v1"
t=requests.post(B+"/auth/login",json={"username":"gv1","password":"123456"}).json()["accessToken"];H={"Authorization":"Bearer "+t}
me=requests.get(B+"/auth/me",headers=H).json();print({k:me[k] for k in me if 'class' in k.lower()})
C=me['classIds'][0];D="2026-10-08"
s=requests.get(B+f"/classes/{C}/attendance?date={D}",headers=H).json()
it=[i for i in s["items"] if not i.get("excusedBy")=="parent"][-1];cid=it["childId"];orig={k:it.get(k) for k in["status","absenceReason"]};print("bé",it.get("childName",cid),orig)
def put(x):
    r=requests.put(B+f"/classes/{C}/attendance",json={"date":D,"items":[dict(childId=cid,**x)]},headers=H);return r
def get(): return [i for i in requests.get(B+f"/classes/{C}/attendance?date={D}",headers=H).json()["items"] if i["childId"]==cid][0]
r=put({"status":"absent","absenceReason":"sick"});g=get();print("1 có phép",r.status_code,g["status"],g["absenceReason"],g["excused"],g["excusedBy"],g["refundEligible"])
put({"status":"absent"});g=get();print("2 thiếu trường giữ nguyên",g["absenceReason"],g["excused"])
put({"status":"absent","absenceReason":None});g=get();print("3 null xóa",g["absenceReason"],g["excused"],g["excusedBy"])
put({"status":"absent","absenceReason":"family"});put({"status":"present"});put({"status":"absent"});g=get();print("4 qua có mặt rồi vắng",g["absenceReason"],g["excused"])
r=put({k:v for k,v in orig.items() if v is not None});print("khôi phục",r.status_code,get()["status"])
