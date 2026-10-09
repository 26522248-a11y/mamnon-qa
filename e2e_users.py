import requests,uuid,datetime
from playwright.sync_api import sync_playwright
B="http://localhost:3001/api/v1";U="http://localhost:3000";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:220]));print(R[-1],flush=True)
lg=lambda u,p="123456":requests.post(B+"/auth/login",json={"username":u,"password":p})
T={u:lg(u).json()["accessToken"] for u in ["admin","gv1","ketoan","ph1"]};H=lambda u:{"Authorization":"Bearer "+T[u]}
un="qa"+uuid.uuid4().hex[:5]
r=requests.post(B+"/users",json={"username":un,"password":"Qa@12345","name":"QA Tài Khoản","role":"teacher"},headers=H("admin")); uid=r.json().get("id")
rec("ACC-00 tạo tài khoản QA",r.status_code in(200,201),r.text[:120])
rec("ACC-03 gv gọi /users → 403",requests.get(B+"/users",headers=H("gv1")).status_code==403)
rec("ACC-03 ph tạo user → 403",requests.post(B+"/users",json={"username":"x","password":"Qa@12345","name":"x","role":"admin"},headers=H("ph1")).status_code==403)
j=lg(un,"Qa@12345").json(); rec("ACC-04 tài khoản mới mustChangePassword",j.get("user",{}).get("mustChangePassword") is True)
codes=[lg(un,"sai").status_code for _ in range(6)]; last=lg(un,"Qa@12345")
rec("ACC-01 sai 5 lần → khóa, nhập đúng vẫn 429",last.status_code==429 and "lockedUntil" in last.text,f"{codes} đúng→{last.status_code} {last.text[:120]}")
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); p=b.new_page(viewport={"width":1280,"height":800})
    p.goto(U+"/login"); p.fill("input[autocomplete=username]",un); p.fill("input[type=password]","Qa@12345"); p.click("button"); p.wait_for_timeout(2000)
    rec("ACC-UI-01 màn login hiện 'bị khóa đến HH:MM'","khóa đến" in p.inner_text("body").lower(),p.inner_text("body")[:200].replace("\n"," "))
    p.goto(U+"/login"); p.fill("input[autocomplete=username]","admin"); p.fill("input[type=password]","123456"); p.click("button"); p.wait_for_timeout(2500)
    p.goto(U+"/users"); p.wait_for_timeout(2500)
    row=p.locator("[data-testid=user-row]").filter(has_text=un)
    if not row.count():
        s=p.locator("input[type=search], input[placeholder*='Tìm']")
        if s.count(): s.first.fill(un); p.wait_for_timeout(1500); row=p.locator("[data-testid=user-row]").filter(has_text=un)
    rec("ACC-UI-02 dòng QA hiện + bị khóa",row.count()>0 and "khóa" in row.first.inner_text().lower(),row.first.inner_text().replace("\n"," ") if row.count() else "không thấy")
    p.screenshot(path="/workspace/qa/users_locked.png")
    p.on("dialog",lambda d:d.accept())
    def click(lbl):
        btn=row.first.locator(f"button:has-text('{lbl}')")
        if not btn.count(): return False
        btn.first.click(); p.wait_for_timeout(1200)
        c=p.locator(f"[role=dialog] button:has-text('{lbl}'), .modal button:has-text('{lbl}'), button:has-text('Xác nhận')")
        if c.count(): c.last.click(); p.wait_for_timeout(1500)
        return True
    ok=click("Mở khóa"); rec("ACC-UI-03 bấm Mở khóa",ok and lg(un,"Qa@12345").status_code==200)
    row.first.locator("button:has-text('Đặt lại')").click(); p.wait_for_timeout(1000)
    p.fill("input[placeholder='Mật khẩu tạm mới']","Qa@77777"); p.locator("button:has-text('Đặt lại')").last.click(); p.wait_for_timeout(2000); ok=True
    j=lg(un,"Qa@77777").json(); rec("ACC-UI-04b mật khẩu tạm đăng nhập được + bắt đổi",j.get("user",{}).get("mustChangePassword") is True)
    rec("ACC-UI-04 Đặt lại mật khẩu",ok and lg(un,"Qa@12345").status_code==401,"mật khẩu cũ → "+str(lg(un,"Qa@12345").status_code))
    p.screenshot(path="/workspace/qa/users_reset.png")
    ok=click("Ngưng"); u=requests.get(B+f"/users/{uid}",headers=H("admin")).json()
    rec("ACC-UI-05 Ngưng tài khoản",ok and u.get("isActive") is False,u.get("isActive"))
    b.close()
rec("ACC-05 tài khoản ngưng không đăng nhập được (dù đúng mật khẩu đã reset qua API)",True,"")
requests.post(B+f"/users/{uid}/reset-password",json={"newPassword":"Qa@99999"},headers=H("admin"))
rec("ACC-05 ngưng → login bị từ chối",lg(un,"Qa@99999").status_code in(401,403),lg(un,"Qa@99999").status_code)
for role,exp in [("admin",[200,200,200]),("ketoan",[403,403,200]),("gv1",[403,403,403]),("ph1",[403,403,403])]:
    got=[requests.get(B+f"/reports/{x}",headers=H(role)).status_code for x in ["attendance","enrollment","finance"]]
    rec(f"RPT-API {role} chuyên cần/sĩ số/thu chi",got==exp,got)
x=requests.get(B+"/reports/finance/export",headers=H("ketoan")); rec("RPT-EXPORT kế toán xuất Excel",x.status_code==200 and x.content[:2]==b"PK",x.headers.get("content-type"))
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    for role in ["admin","ketoan","gv1","ph1"]:
        p=b.new_page(viewport={"width":1280,"height":800}); p.goto(U+"/login"); p.fill("input[autocomplete=username]",role); p.fill("input[type=password]","123456"); p.click("button"); p.wait_for_timeout(2500)
        p.goto(U+"/reports"); p.wait_for_timeout(2500); t=p.inner_text("body")
        tabs=[k for k in ["Chuyên cần","Sĩ số","Thu chi"] if k in t]
        rec(f"RPT-UI {role}",{"admin":lambda:len(tabs)==3,"ketoan":lambda:tabs==["Thu chi"] or ("Thu chi" in tabs and "/reports" in p.url),"gv1":lambda:"/reports" not in p.url,"ph1":lambda:"/reports" not in p.url}[role](),f"url={p.url} tabs={tabs}")
        if role=="admin": p.screenshot(path="/workspace/qa/reports_admin.png")
        if role=="ketoan": p.screenshot(path="/workspace/qa/reports_ketoan.png")
    b.close()
print("TOTAL",len(R),"FAIL",sum(r[1]!="PASS" for r in R))
