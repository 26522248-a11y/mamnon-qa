import requests
from playwright.sync_api import sync_playwright
B="http://localhost:3001/api/v1";U="http://localhost:3000";Q="ac105557-e330-443b-bf67-f40bd1cb77e2";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:220]));print(R[-1],flush=True)
G=requests.post(B+"/auth/login",json={"username":"gv1","password":"123456"}).json()["accessToken"]
st=lambda:requests.get(B+f"/pickup-requests/{Q}",headers={"Authorization":"Bearer "+G}).json()
def login(b,u,pw="123456",mob=True):
    p=b.new_page(viewport={"width":390,"height":844} if mob else {"width":1280,"height":800}); p.goto(U+"/login"); p.fill("input[autocomplete=username]",u); p.fill("input[type=password]",pw); p.click("button"); p.wait_for_timeout(2500); return p
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    p=login(b,"0987000012","QaTest@2026"); p.goto(U+"/today"); p.wait_for_timeout(2000)
    p.click("button:has-text('Đúng, cho đón')"); p.wait_for_timeout(2000)
    c=p.locator("[role=dialog] button, .modal button").filter(has_text="Đúng")
    if c.count(): c.last.click(); p.wait_for_timeout(1500)
    p.screenshot(path="/workspace/qa/h_ph2.png",full_page=True); s=st()
    rec("UI-2 PH bấm 'Đúng, cho đón'",s["parent"]["status"]=="approved",s["parent"]["status"]); t=p.inner_text("body")
    rec("UI-2 PH thấy 'Chờ nhà trường duyệt'","nhà trường" in t.lower(),t[t.find("Đang chờ") if "Đang chờ" in t else 0:][:120].replace("\n"," "))
    g=login(b,"gv1"); aid=s.get("attendanceId"); g.goto(U+f"/pickups/handover/{aid}"); g.wait_for_timeout(2500)
    btn=g.locator("button:has-text('Giao bé')"); en=[i for i in range(btn.count()) if btn.nth(i).is_enabled() and "QA UI" in (btn.nth(i).text_content() or "")]
    rec("UI-3 chỉ PH xác nhận: nút giao vẫn khóa",not en)
    a=login(b,"admin",mob=False); a.goto(U+"/pickups"); a.wait_for_timeout(2500)
    card=a.locator(".card").filter(has_text="QA UI Hai Bước").first
    rec("UI-4 admin thấy yêu cầu",card.count()>0)
    if card.count():
        card.locator("button:has-text('Duyệt')").first.click(); a.wait_for_timeout(2000)
    a.screenshot(path="/workspace/qa/h_admin.png"); s=st(); rec("UI-4 admin duyệt 1 chạm, không cần ghi chú",s["school"]["status"]=="approved",s["school"]["status"])
    g.reload(); g.wait_for_timeout(2500); g.screenshot(path="/workspace/qa/h_2.png",full_page=True)
    btn=g.locator("button").filter(has_text="Giao bé"); t=g.inner_text("body")
    en=[i for i in range(btn.count()) if btn.nth(i).is_enabled()]
    rec("UI-5 đủ 2 bước: có nút giao mở",bool(en),t[:250].replace("\n"," | "))
    b.close()
print("TOTAL",len(R),"FAIL",sum(r[1]!="PASS" for r in R))
