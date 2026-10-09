import requests
B="http://localhost:3001/api/v1"
def tk(u): return requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"]
A={"Authorization":"Bearer "+tk("admin")}; G={"Authorization":"Bearer "+tk("gv1")}
L=lambda j: j if isinstance(j,list) else j.get("items",j.get("data",[]))
r=requests.post(B+"/holidays/template",json={"year":2027,"dryRun":True},headers=A); print("dry",r.status_code)
n0=len(L(requests.get(B+"/holidays?year=2027",headers=A).json())); print("sau dry, số ngày 2027:",n0)
r=requests.post(B+"/holidays/template",json={"year":2027},headers=A); print("apply",r.status_code)
n1=len(L(requests.get(B+"/holidays?year=2027",headers=A).json()))
requests.post(B+"/holidays/template",json={"year":2027},headers=A)
n2=len(L(requests.get(B+"/holidays?year=2027",headers=A).json())); print("n1,n2 (không trùng):",n1,n2)
p=L(requests.get(B+"/holidays?year=2027&status=pending",headers=A).json())
print("pending:",[(x["date"],x.get("name")) for x in p])
print("gv confirm 403:",requests.post(B+f"/holidays/{p[0]['id']}/confirm",headers=G).status_code)
r=requests.post(B+f"/holidays/{p[0]['id']}/confirm",headers=A); j=r.json(); print("confirm",r.status_code,j.get("status"),j.get("confirmedBy"),j.get("confirmedAt"))
