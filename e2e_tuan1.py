from playwright.sync_api import sync_playwright
U="http://localhost:3000"; R=[]
def rec(n,ok,info=""): R.append((n,"PASS" if ok else "FAIL",info)); print(R[-1],flush=True)
def login(p,u,pw="123456"):
    p.goto(U+"/login"); p.fill("input[placeholder='Tên đăng nhập']",u); p.fill("input[type=password]",pw)
    p.click("button:has-text('Đăng nhập')"); p.wait_for_timeout(1500)
with sync_playwright() as pw:
    b=pw.chromium.launch(channel="chrome",headless=True)
    for role in ["admin","gv1","ketoan","ph1"]:
        c=b.new_context(); p=c.new_page(); errs=[]
        p.on("pageerror",lambda e:errs.append(str(e)))
        login(p,role); ok="/login" not in p.url
        rec(f"UI-LOGIN {role}",ok,p.url)
        nav=p.locator("nav, aside").first.inner_text() if p.locator("nav, aside").count() else ""
        rec(f"UI-MENU {role}",True,nav.replace("\n"," | ")[:150])
        for path in ["/dashboard","/children","/attendance"]:
            p.goto(U+path); p.wait_for_timeout(1200)
            txt=p.inner_text("body")[:200].replace("\n"," ")
            rec(f"UI-PAGE {role} {path}",not errs,f"url={p.url} :: {txt}")
        p.screenshot(path=f"/workspace/qa/shot_{role}.png",full_page=True); c.close()
    c=b.new_context(); p=c.new_page(); login(p,"gv1","sai")
    rec("UI-AUTH sai mật khẩu ở lại login + báo lỗi","/login" in p.url, p.inner_text("body")[:150].replace("\n"," "))
    c.close()
    c=b.new_context(); p=c.new_page(); p.goto(U+"/children"); p.wait_for_timeout(1500)
    rec("UI-AUTH chưa login vào /children bị chuyển về login","/login" in p.url,p.url); c.close()
    c=b.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True); p=c.new_page()
    login(p,"gv1"); p.goto(U+"/attendance"); p.wait_for_timeout(1500)
    p.screenshot(path="/workspace/qa/shot_attendance_mobile.png",full_page=True)
    small=p.evaluate("""()=>[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&b.getBoundingClientRect().height<48).map(b=>b.innerText.trim().slice(0,20)+':'+Math.round(b.getBoundingClientRect().height))""")
    rec("UI-ATT ô chạm >=48px (mobile)",not small,str(small[:8]))
    hs=p.evaluate("document.documentElement.scrollWidth>window.innerWidth")
    rec("UI-ATT không tràn ngang mobile",not hs)
    p.reload(); p.wait_for_timeout(1500); rec("UI-AUTH reload giữ đăng nhập","/login" not in p.url,p.url)
    c.close(); b.close()
print("TOTAL",len(R),"FAIL",sum(r[1]!="PASS" for r in R))
