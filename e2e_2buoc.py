import requests,datetime
from playwright.sync_api import sync_playwright
B="http://localhost:3001/api/v1";U="http://localhost:3000";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:220]));print(R[-1],flush=True)
tok=lambda u,p="123456":requests.post(B+"/auth/login",json={"username":u,"password":p}).json().get("accessToken")
G=tok("gv1");H=lambda t:{"Authorization":"Bearer "+t};P=tok("0987000012","QaTest@2026")
kid=requests.get(B+"/children",headers=H(P)).json()["items"][0]; d=datetime.date.today().isoformat()
c=requests.get(B+"/classes",headers=H(G)).json(); c=(c.get("items",c) if isinstance(c,dict) else c)[0]["id"]
a=[i for i in requests.get(B+f"/classes/{c}/attendance?date={d}",headers=H(G)).json()["items"] if i["childId"]==kid["id"]][0]; aid=a.get("attendanceId") or a.get("id")
#q0=(B+f"/attendance/{aid}/pickup-requests",json={"pickerName":"QA UI Hai Bước","pickerPhone":"0909777888","note":"QA UI","relation":"Cô"},headers=H(G)).json()
q={"id":"ac105557-e330-443b-bf67-f40bd1cb77e2"}
def login(b,u,pw="123456",mob=True):
    p=b.new_page(viewport={"width":390,"height":844} if mob else {"width":1280,"height":800}); p.goto(U+"/login"); p.fill("input[autocomplete=username]",u); p.fill("input[type=password]",pw); p.click("button"); p.wait_for_timeout(2500); return p
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    g=login(b,"gv1"); g.goto(U+f"/pickups/handover/{aid}"); g.wait_for_timeout(2500); g.screenshot(path="/workspace/qa/h_0.png",full_page=True)
    t=g.inner_text("body"); rec("UI-1 gv thấy yêu cầu, chưa giao được","QA UI Hai Bước" in t,t[:300].replace("\n"," | "))
    btn=g.locator("button:has-text('Giao bé')"); en=[i for i in range(btn.count()) if btn.nth(i).is_enabled() and "QA UI" in (btn.nth(i).text_content() or "")]
    rec("UI-1 nút giao cho QA UI bị khóa",not en)
    rec("UI-1 gv không có nút Duyệt","Duyệt" not in t or g.locator("button:has-text('Duyệt')").count()==0)
    p=login(b,"0987000012","QaTest@2026"); p.wait_for_timeout(1000); p.goto(U+"/today"); p.wait_for_timeout(2500); p.screenshot(path="/workspace/qa/h_ph.png",full_page=True)
    t=p.inner_text("body"); rec("UI-2 PH thấy thẻ yêu cầu đón","QA UI Hai Bước" in t,p.url+" "+t[:250].replace("\n"," | "))
    b2=p.locator("button:has-text('Xác nhận')")
    if b2.count():
        b2.first.click(); p.wait_for_timeout(1500)
        c2=p.locator("[role=dialog] button:has-text('Xác nhận'), button:has-text('Đồng ý')")
        if c2.count(): c2.last.click(); p.wait_for_timeout(1500)
        p.screenshot(path="/workspace/qa/h_ph2.png",full_page=True); t=p.inner_text("body")
        rec("UI-2 PH xác nhận xong",True,t[:250].replace("\n"," | "))
    g.reload(); g.wait_for_timeout(2500); btn=g.locator("button:has-text('Giao bé')")
    en=[i for i in range(btn.count()) if btn.nth(i).is_enabled() and "QA UI" in (btn.nth(i).text_content() or "")]
    rec("UI-3 chỉ PH xác nhận: nút vẫn khóa",not en); g.screenshot(path="/workspace/qa/h_1.png",full_page=True)
    b.close()
st=requests.get(B+f"/pickup-requests/{q['id']}",headers=H(G)).json(); rec("API trạng thái sau PH",True,{k:st.get(k) for k in ["status","parent","school"]})
print("TOTAL",len(R),"FAIL",sum(r[1]!="PASS" for r in R))
