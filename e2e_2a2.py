from playwright.sync_api import sync_playwright
import requests
B="http://localhost:3001/api/v1";U="http://localhost:3000";D="2026-10-09"
H={"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":"gv1","password":"123456"}).json()["accessToken"]}
C=requests.get(B+"/auth/me",headers=H).json()["classIds"][0]
s=requests.get(B+f"/classes/{C}/attendance?date={D}",headers=H).json()["items"]
it=None
it=it[0] if it else None; print("bé test", it and (it.get("childName") or it["childId"]))
pass
def login(p,u,pw):
    p.goto(U+"/login");p.fill("input[placeholder='Tên đăng nhập']",u);p.fill("input[type=password]",pw);p.click("button:has-text('Đăng nhập')");p.wait_for_timeout(2500)
with sync_playwright() as pw:
    b=pw.chromium.launch()
    q=b.new_page();login(q,"qapwd51318","Tam12345");print("sau login:",q.url)
    q.goto(U+"/children");q.wait_for_timeout(2500);print("vào /children:",q.url)
    g=b.new_page(viewport={"width":390,"height":844});login(g,"gv1","123456");g.goto(U+"/attendance");g.wait_for_timeout(3000)
    t=g.inner_text("body");print("có 'Cô ghi':","Cô ghi" in t,"| có 🚫:","🚫" in t);g.screenshot(path="/workspace/qa/2a2_att.png",full_page=True)
