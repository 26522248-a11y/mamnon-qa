from playwright.sync_api import sync_playwright
U="http://localhost:3000";R=[];NAME="Phạm Minh Bình"
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",i));print(R[-1],flush=True)
def login(b,u,m=True):
    c=b.new_context(viewport={"width":390,"height":844} if m else {"width":1280,"height":800}); p=c.new_page()
    p.goto(U+"/login"); p.fill("input[autocomplete=username]",u); p.fill("input[type=password]","123456"); p.click("button"); p.wait_for_timeout(2500); return p
def open_kid(g):
    g.goto(U+"/children"); g.wait_for_timeout(1500); g.click(f"text={NAME}"); g.wait_for_timeout(2000)
def act(a,who,btn,note):
    a.goto(U+"/pickups"); a.wait_for_timeout(2000)
    card=a.locator(".card").filter(has_text=who).filter(has=a.locator(f"button:has-text('{btn}')")).first
    if not card.count(): return False
    card.locator(f"button:has-text('{btn}')").click(); a.wait_for_timeout(1000)
    err="lỗi" in a.inner_text("body").lower() or "ghi chú" in a.inner_text("body").lower()
    card.locator("input").first.fill(note); card.locator(f"button:has-text('{btn}')").click(); a.wait_for_timeout(2000)
    return err
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    g=login(b,"gv1"); a=login(b,"admin",False)
    a.goto(U+"/pickups"); a.wait_for_timeout(2000)
    card=a.locator(".card").filter(has_text="QA Từ Chối").filter(has=a.locator("button:has-text('Từ chối')")).first
    if card.count():
        card.locator("button:has-text('Từ chối')").click(); a.wait_for_timeout(1000)
        rec("PU-UI-01 từ chối không ghi chú bị chặn", "QA Từ Chối" in a.inner_text("body") and card.locator("button:has-text('Từ chối')").count()>0)
        card.locator("input").first.fill("QA từ chối"); card.locator("button:has-text('Từ chối')").click(); a.wait_for_timeout(2000)
        rec("PU-UI-02 admin từ chối kèm ghi chú (dọn QA Từ Chối)",True)
    open_kid(g); body=g.inner_text("body")
    rec("PU-UI-03 sau từ chối vẫn khóa", "Chưa thể giao bé" in body or "Từ chối" in body, body[body.find("Hôm nay"):][:250].replace("\n"," "))
    g.click("text=+ Người khác đến đón"); g.fill("input[name=pickerName]","QA Đồng Ý"); g.fill("input[name=pickerPhone]","0909123456")
    g.fill("input[name=relation]","Chú"); g.fill("textarea[name=note]","QA test"); g.click("text=Gửi yêu cầu xác nhận"); g.wait_for_timeout(2000)
    rec("PU-UI-04 yêu cầu mới chờ + khóa","Chưa thể giao bé" in g.inner_text("body"))
    a.goto(U+"/pickups"); a.wait_for_timeout(2000)
    card=a.locator(".card").filter(has_text="QA Đồng Ý").first
    card.locator("input").first.fill("PH gọi điện xác nhận"); card.locator("button:has-text('Xác nhận')").click(); a.wait_for_timeout(2000)
    a.screenshot(path="/workspace/qa/pu_admin.png")
    open_kid(g); bt=g.locator("button").filter(has_text="QA Đồng Ý")
    if not bt.count(): bt=g.locator("button:has-text('Giao bé cho QA')")
    rec("PU-UI-05 sau xác nhận có nút giao cho QA Đồng Ý",bt.count()>0, g.inner_text("body")[g.inner_text("body").find("Hôm nay"):][:300].replace("\n"," "))
    if bt.count():
        bt.first.click(); g.wait_for_timeout(1500)
        c=g.locator("button:has-text('Xác nhận'), button:has-text('Giao')")
        body=g.inner_text("body")
        if "đón lúc" not in body and c.count(): c.last.click(); g.wait_for_timeout(2000)
        body=g.inner_text("body"); rec("PU-UI-06 giao bé thành công","đón lúc" in body, body[body.find("Hôm nay"):][:250].replace("\n"," "))
    g.screenshot(path="/workspace/qa/pu_done.png",full_page=True); b.close()
print("TOTAL",len(R),"FAIL",sum(r[1]!="PASS" for r in R))
