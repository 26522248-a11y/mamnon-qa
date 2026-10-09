"""Staging H5 (giữ phiên khi đóng/mở tab, mở lại trình duyệt) + P13 (dòng ngày /today theo giờ VN kể cả khi máy ở múi giờ khác). Tài khoản qua env SA/SG/SP."""
import os,re,sys
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
from playwright.sync_api import sync_playwright
W="https://mamnon-web.vercel.app"; R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:250]));print(R[-1],flush=True)
cr=lambda k: os.environ[k].split(":",1)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    for acc,home in [("SP","/today"),("SG","/home"),("SA","/dashboard")]:
        c=b.new_context(viewport={"width":390,"height":844}); p=c.new_page(); login_ui(p,W,*cr(acc),consent=True)
        p.goto(W+home); p.wait_for_timeout(2500); p.close()
        q=c.new_page(); q.goto(W+home,timeout=90000); q.wait_for_timeout(5000)
        rec(f"H5-01 {acc} đóng tab, mở tab mới {home} không bị đòi đăng nhập","/login" not in q.url,q.url)
        st=c.storage_state(path=f"/workspace/stg/st_{acc}.json"); c.close()
        c2=b.new_context(viewport={"width":390,"height":844},storage_state=f"/workspace/stg/st_{acc}.json"); q=c2.new_page(); q.goto(W+"/",timeout=90000); q.wait_for_timeout(5000)
        rec(f"H5-02 {acc} mở lại trình duyệt (giữ cookie/localStorage) vào {home}",home in q.url,q.url); c2.close()
    # P13: trình duyệt ở giờ Mỹ (đang là 09/10 bên đó), trang đầu PH phải ghi ngày VN 10/10
    for tz in ["America/Los_Angeles","Asia/Ho_Chi_Minh"]:
        c=b.new_context(viewport={"width":390,"height":844},timezone_id=tz,storage_state="/workspace/stg/st_SP.json"); p=c.new_page(); p.goto(W+"/today",timeout=90000); p.wait_for_timeout(6000)
        t=p.inner_text("main"); p.screenshot(path=f"/workspace/stg/P13-today-{tz.split('/')[1]}.png",full_page=True)
        d=re.findall(r"[^\n]*(?:Thứ|Chủ nhật|\d{1,2}/\d{1,2})[^\n]*",t)[:4]
        rec(f"P13-01 /today ({tz}) dòng ngày là Thứ Bảy 10/10",any(("10/10" in x or "10 tháng 10" in x) for x in d) and not any("9/10" in x or "09/10" in x or "Thứ Sáu" in x for x in d),d)
        c.close()
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
