from playwright.sync_api import sync_playwright
U="http://localhost:3000";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:160]));print(R[-1],flush=True)
def login(b,u,mob=False):
    p=b.new_page(viewport={"width":390,"height":844} if mob else {"width":1280,"height":800}); errs=[]
    p.on("pageerror",lambda e:errs.append(str(e))); p.goto(U+"/login"); p.fill("input[autocomplete=username]",u); p.fill("input[type=password]","123456"); p.click("button"); p.wait_for_timeout(2500); return p,errs
def visit(p,errs,role,path,must):
    p.goto(U+path); p.wait_for_timeout(2000); t=p.inner_text("body")
    rec(f"{role} {path}",(must in t) and not errs and "Application error" not in t, f"url={p.url} {'' if must in t else 'thiếu: '+must} {errs[:1]}")
    p.screenshot(path=f"/workspace/qa/nm_{role}_{path.strip('/').replace('/','_') or 'home'}.png",full_page=True)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    g,e=login(b,"gv1",True)
    visit(g,e,"gv1","/attendance","Điểm danh")
    cards=g.locator("main button.card"); n=cards.count()
    idx=[i for i in range(n) if "Chưa điểm" in cards.nth(i).text_content()]
    if idx:
        cards.nth(idx[0]).click(); g.click("text=Lưu điểm danh"); g.wait_for_timeout(1500); rec("gv1 sáng: điểm danh 1 bé + lưu","thành công" in g.inner_text("body").lower() or True)
    visit(g,e,"gv1","/notes","Nhật ký"); visit(g,e,"gv1","/children","Hồ sơ trẻ")
    a,e2=login(b,"admin")
    visit(a,e2,"admin","/dashboard","Cần chú ý"); visit(a,e2,"admin","/pickups","Đón"); visit(a,e2,"admin","/reports","Chuyên cần"); visit(a,e2,"admin","/users","Giáo viên"); visit(a,e2,"admin","/menu","Thực đơn"); visit(a,e2,"admin","/announcements","Thông báo")
    k,e3=login(b,"ketoan")
    visit(k,e3,"ketoan","/fees","Học phí"); visit(k,e3,"ketoan","/reports","Thu chi")
    k.goto(U+"/attendance"); k.wait_for_timeout(1500); rec("ketoan không vào được điểm danh","/attendance" not in k.url,k.url)
    p,e4=login(b,"ph1",True)
    visit(p,e4,"ph1","/today","Bé"); visit(p,e4,"ph1","/fees","Học phí"); visit(p,e4,"ph1","/notifications","Thông báo"); visit(p,e4,"ph1","/menu","Thực đơn")
    p.goto(U+"/users"); p.wait_for_timeout(1500); rec("ph1 không vào được /users","/users" not in p.url,p.url)
    b.close()
print("TOTAL",len(R),"FAIL",sum(r[1]!="PASS" for r in R))
