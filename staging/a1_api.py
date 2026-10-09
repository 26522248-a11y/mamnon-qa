import os,io,json,requests
from PIL import Image
B=os.environ["API"];CL="da948ed1-e420-450a-a65a-ccce44c09c09"
def tok(k): u,p=os.environ[k].split(":",1); return {"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":p}).json()["accessToken"]}
G=tok("SG")
def jpg():
    b=io.BytesIO(); Image.new("RGB",(64,64),"gray").save(b,"JPEG"); return b.getvalue()
s=requests.get(B+f"/classes/{CL}/photo-consent-summary",headers=G).json()
print("notAllowed",len(s["notAllowed"]),"/",len(s["items"]),[x["fullName"] for x in s["notAllowed"]][:5])
before=requests.get(B+f"/classes/{CL}/photo-posts",headers=G).json()["items"]; print("posts before",len(before))
bad=s["notAllowed"][0]["childId"]
r=requests.post(B+f"/classes/{CL}/photo-posts",headers=G,files=[("files",("qa.jpg",jpg(),"image/jpeg"))],data={"caption":"QA test chặn","tags":json.dumps([[bad]])})
print("A1-API tag bé chưa đồng ý ->",r.status_code,r.text[:300])
if r.status_code<300 and r.json().get("id"): print("XOÁ ngay",requests.delete(B+f"/photo-posts/{r.json()['id']}",headers=G).status_code)
r=requests.post(B+f"/classes/{CL}/photo-posts",headers=G,files=[("files",("qa.jpg",jpg(),"image/jpeg")),("files",("qa2.jpg",jpg(),"image/jpeg"))],data={"caption":"QA","tags":json.dumps([[bad],[bad]])})
print("A1-API 2 ảnh đều gắn bé chưa đồng ý ->",r.status_code,r.text[:200])
if r.status_code<300 and r.json().get("id"): print("XOÁ ngay",requests.delete(B+f"/photo-posts/{r.json()['id']}",headers=G).status_code)
after=requests.get(B+f"/classes/{CL}/photo-posts",headers=G).json()["items"]; print("posts after",len(after))
