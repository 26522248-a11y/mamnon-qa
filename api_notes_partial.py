import requests,datetime,sys
B="http://localhost:3001/api/v1"
L=lambda u:requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"]
G={"Authorization":"Bearer "+L("gv1")};A={"Authorization":"Bearer "+L("admin")}
c=requests.get(B+"/classes",headers=G).json(); c=(c.get("items",c) if isinstance(c,dict) else c)[0]["id"]
d=datetime.date.today().isoformat()
items=requests.get(B+f"/classes/{c}/daily-notes?date={d}",headers=G).json()["items"]
k=[i for i in items if not i["recorded"]][-1]["childId"]   # bé chưa có nhật ký hôm nay
r1=requests.put(B+f"/classes/{c}/daily-notes",json={"date":d,"items":[{"childId":k,"eating":"all"}]},headers=G)          # cô 1 ghi ăn
r2=requests.put(B+f"/classes/{c}/daily-notes",json={"date":d,"items":[{"childId":k,"sleepMinutes":90}]},headers=A)      # người 2 ghi ngủ
x=[i for i in requests.get(B+f"/classes/{c}/daily-notes?date={d}",headers=G).json()["items"] if i["childId"]==k][0]
ok=x["eating"] is not None and x["sleepMinutes"]==90
print(r1.status_code,r2.status_code,{"eating":x["eating"],"sleepMinutes":x["sleepMinutes"]},"PASS" if ok else "FAIL – mất trường eating")
