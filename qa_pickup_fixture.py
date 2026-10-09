"""Chuẩn bị dữ liệu cho e2e_2buoc*: điểm danh bé của PH 0987000012 hôm nay + tạo yêu cầu đón 'QA UI Hai Bước'. Ghi id ra /workspace/qa/pickup_q.txt."""
import requests,datetime
B="http://localhost:3001/api/v1"
tok=lambda u,p="123456":requests.post(B+"/auth/login",json={"username":u,"password":p}).json()["accessToken"]
H=lambda t:{"Authorization":"Bearer "+t}
G=tok("gv1");P=tok("0987000012","QaTest@2026");d=datetime.date.today().isoformat()
kid=requests.get(B+"/children",headers=H(P)).json()["items"][0]["id"]
c=requests.get(B+"/classes",headers=H(G)).json(); c=(c.get("items",c) if isinstance(c,dict) else c)[0]["id"]
requests.put(B+f"/classes/{c}/attendance",json={"date":d,"items":[{"childId":kid,"status":"present"}]},headers=H(G))
a=[i for i in requests.get(B+f"/classes/{c}/attendance?date={d}",headers=H(G)).json()["items"] if i["childId"]==kid][0]
aid=a["attendanceId"]
r=requests.post(B+f"/attendance/{aid}/pickup-requests",json={"pickerName":"QA UI Hai Bước","pickerPhone":"0909777888","note":"QA UI","relation":"Cô"},headers=H(G))
q=r.json()["id"]; open("/workspace/qa/pickup_q.txt","w").write(q); print("attendance",aid,"request",q,r.status_code)
