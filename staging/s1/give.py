import os,sys,re,requests
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
from playwright.sync_api import sync_playwright
W="https://mamnon-web.vercel.app"; B="https://mamnon-api.onrender.com/api/v1"; R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:300]));print(R[-1],flush=True)
u,pw_=os.environ["SG"].split(":",1); G={"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":pw_}).json()["accessToken"]}
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); c=b.new_context(viewport={"width":390,"height":844}); p=c.new_page(); errs=[]; p.on("pageerror",lambda e: errs.append(str(e)[:150]))
    login_ui(p,W,u,pw_,consent=None); p.goto(W+"/pickups"); p.wait_for_timeout(4000)
    l=p.locator("[data-testid=handover-link]",has_text="Long"); l.first.click(); p.wait_for_timeout(4000); aid=p.url.rstrip("/").split("/")[-1]
    card=p.locator("[data-testid=handover-guardian]").first
    card.locator("[data-testid=handover-photo-input]").set_input_files("/tmp/qa_s1.jpg"); p.wait_for_timeout(1500)
    ups=[]; p.on("response",lambda r: ups.append((r.request.method,r.url.split('/api/v1')[-1],r.status)) if r.request.method=="POST" else None)
    card.locator("[data-testid=handover-give]").click(); p.wait_for_timeout(7000)
    p.screenshot(path="/workspace/stg/s1/PK-give-390.png",full_page=True)
    rec("PK-11 giao bé kèm ảnh: POST thành công",any(s<300 for _,_,s in ups) and not [x for x in ups if x[2]>=400],ups)
    rec("PK-12 màn xác nhận 'Đã giao bé'",p.locator("[data-testid=handover-done]").count()>0,p.inner_text("main")[:150])
    r=requests.get(B+f"/attendance/{aid}/pickup-photo",headers=G); rec("PK-13 API ảnh giao bé trả 200 image (cùng bản deploy)",r.status_code==200 and r.headers.get("content-type","").startswith("image"),(r.status_code,r.headers.get("content-type")))
    rec("PK-14 không lỗi JS",not errs,errs[:3]); b.close()
print("AID",aid); print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
