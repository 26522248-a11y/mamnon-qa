from playwright.sync_api import sync_playwright
import requests
U="http://localhost:3000";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",i))
def login(p,u,pw="123456"):
    p.goto(U+"/login");p.fill("input[placeholder='Tên đăng nhập']",u);p.fill("input[type=password]",pw)
    p.click("button:has-text('Đăng nhập')");p.wait_for_timeout(2000)
with sync_playwright() as pw:
    b=pw.chromium.launch()
    p=b.new_page();login(p,"admin");p.goto(U+"/holidays");p.wait_for_timeout(2000)
    t=p.inner_text("body");rec("UI admin lịch nghỉ mở",p.url.endswith("/holidays") and "Lịch" in t)
    p.goto(U+"/holidays?year=2027");p.wait_for_timeout(1500);t=p.inner_text("body")
    rec("UI thanh vàng / chờ xác nhận",("chờ" in t.lower()),t[:0]);p.screenshot(path="/workspace/qa/2a_hol.png",full_page=True)
    m=b.new_page(viewport={"width":390,"height":844});login(m,"ph1");m.goto(U+"/messages");m.wait_for_timeout(2000)
    t=m.inner_text("body");rec("UI PH Nhắn cô mở",m.url.endswith("/messages"),m.url);m.screenshot(path="/workspace/qa/2a_msg.png",full_page=True)
    g=b.new_page();login(g,"gv1");g.goto(U+"/holidays");g.wait_for_timeout(1500)
    rec("UI GV không vào được lịch nghỉ",not ("Xác nhận cả năm" in g.inner_text("body")),g.url)
    q=b.new_page();login(q,"0987000001");q.wait_for_timeout(1000)
    rec("UI tài khoản buộc đổi MK → /change-password","change-password" in q.url,q.url)
    q.goto(U+"/today");q.wait_for_timeout(2000);rec("UI vào /today vẫn bị đưa về đổi MK","change-password" in q.url,q.url)
for r in R: print(r)
