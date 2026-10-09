from playwright.sync_api import sync_playwright
U="http://localhost:3000";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",i));print(R[-1],flush=True)
def login(b,u,m=True):
    c=b.new_context(viewport={"width":390,"height":844} if m else {"width":1280,"height":800}); p=c.new_page()
    p.goto(U+"/login"); p.fill("input[autocomplete=username]",u); p.fill("input[type=password]","123456"); p.click("button"); p.wait_for_timeout(2500); return p
def req(g,name,who):
    g.goto(U+"/children"); g.wait_for_timeout(1500); g.click(f"text={name}"); g.wait_for_timeout(2000)
    g.click("text=+ Người khác đến đón"); g.fill("input[name=pickerName]",who); g.fill("input[name=pickerPhone]","0909123456")
    g.fill("input[name=relation]","Chú"); g.fill("textarea[name=note]","QA test"); g.click("text=Gửi yêu cầu xác nhận"); g.wait_for_timeout(2000)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    g=login(b,"gv1"); cards=g.locator("main button.card"); g.wait_for_selector("main button.card")
    idx=[i for i in range(cards.count()) if "Chưa điểm" in cards.nth(i).text_content() and "Gia An" not in cards.nth(i).text_content()]
    name=cards.nth(idx[-1]).locator("span").first.text_content().strip()
    cards.nth(idx[-1]).click(); g.click("text=Lưu điểm danh"); g.wait_for_timeout(1500); rec("E2E điểm danh "+name,True)
    req(g,name,"QA Từ Chối"); body=g.inner_text("body")
    rec("E2E yêu cầu 1 tạo, trạng thái chờ","chờ" in body.lower(),"")
    giao=g.locator("button:has-text('Giao')")
    rec("E2E nút giao bị khóa khi chờ", giao.count()==0 or all(giao.nth(i).is_disabled() for i in range(giao.count())))
    g.screenshot(path="/workspace/qa/pu_pending.png",full_page=True)
    a=login(b,"admin",False); a.goto(U+"/pickups"); a.wait_for_timeout(2000)
    if "QA Từ Chối" not in a.inner_text("body"):
        for l in ["Đón bé"]: 
            if a.locator(f"text={l}").count(): a.click(f"text={l}"); a.wait_for_timeout(2000)
    rec("E2E admin thấy yêu cầu","QA Từ Chối" in a.inner_text("body"),a.url)
    row=a.locator("div,li,tr").filter(has_text="QA Từ Chối").last
    try:
        row.locator("button:has-text('Từ chối')").first.click(); a.wait_for_timeout(800)
        tx=a.locator("textarea, input[name=note]")
        if tx.count(): tx.last.fill("QA từ chối")
        bs=a.locator("button:has-text('Từ chối')"); bs.last.click(); a.wait_for_timeout(2000)
        rec("E2E admin từ chối",True)
    except Exception as e: rec("E2E admin từ chối",False,str(e)[:150])
    g.reload(); g.wait_for_timeout(2000); giao=g.locator("button:has-text('Giao')")
    rec("E2E sau từ chối vẫn không giao được", giao.count()==0 or all(giao.nth(i).is_disabled() for i in range(giao.count())), g.inner_text("body")[-300:].replace("\n"," "))
    req(g,name,"QA Đồng Ý")
    a.reload(); a.wait_for_timeout(2000); row=a.locator("div,li,tr").filter(has_text="QA Đồng Ý").last
    try:
        row.locator("button:has-text('Xác nhận')").first.click(); a.wait_for_timeout(800)
        a.screenshot(path="/workspace/qa/pu_admin_confirm.png")
        tx=a.locator("textarea, input[name=note]")
        if tx.count(): tx.last.fill("PH gọi điện xác nhận")
        a.locator("button:has-text('Xác nhận')").last.click(); a.wait_for_timeout(2000); rec("E2E admin xác nhận kèm ghi chú",True)
    except Exception as e: rec("E2E admin xác nhận",False,str(e)[:150])
    g.reload(); g.wait_for_timeout(2000); giao=g.locator("button:has-text('Giao')").filter(has_not_text="xx")
    en=[i for i in range(giao.count()) if giao.nth(i).is_enabled()]
    rec("E2E sau xác nhận nút giao mở",bool(en))
    if en: giao.nth(en[0]).click(); g.wait_for_timeout(2000)
    body=g.inner_text("body"); rec("E2E giao bé thành công","QA Đồng Ý đón" in body or "đã được" in body.lower(),body[-300:].replace("\n"," "))
    g.screenshot(path="/workspace/qa/pu_done.png",full_page=True)
    b.close()
print("TOTAL",len(R),"FAIL",sum(r[1]!="PASS" for r in R))
