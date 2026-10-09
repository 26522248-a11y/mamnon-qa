import requests
from playwright.sync_api import sync_playwright
B="http://localhost:3001/api/v1";U="http://localhost:3000";Q=open("/workspace/qa/pickup_q.txt").read().strip()
G=requests.post(B+"/auth/login",json={"username":"gv1","password":"123456"}).json()["accessToken"]
s=requests.get(B+f"/pickup-requests/{Q}",headers={"Authorization":"Bearer "+G}).json()
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); g=b.new_page(viewport={"width":390,"height":844})
    g.goto(U+"/login"); g.fill("input[autocomplete=username]","gv1"); g.fill("input[type=password]","123456"); g.click("button"); g.wait_for_timeout(2500)
    g.goto(U+f"/pickups/handover/{s['attendanceId']}"); g.wait_for_timeout(2500)
    g.click("text=QA UI Hai Bước"); g.wait_for_timeout(2000); g.screenshot(path="/workspace/qa/h_3.png",full_page=True)
    bt=g.locator("button").filter(has_text="Giao bé"); en=[bt.nth(i).text_content() for i in range(bt.count()) if bt.nth(i).is_enabled()]
    print("nút mở:",en)
    if en:
        bt.filter(has_text="Giao bé").last.click(); g.wait_for_timeout(1500)
        c=g.locator("[role=dialog] button, .modal button").filter(has_text="Giao")
        if c.count(): c.last.click(); g.wait_for_timeout(2000)
        g.screenshot(path="/workspace/qa/h_4.png",full_page=True)
    b.close()
s=requests.get(B+f"/pickup-requests/{Q}",headers={"Authorization":"Bearer "+G}).json(); print("status:",s.get("status"))
