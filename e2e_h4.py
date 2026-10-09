"""H4: đã đăng nhập mà mở '/' phải vào trang chính theo vai trò, không ra /login.
GV → /home, PH → /today, nhân viên (admin, kế toán) → /dashboard. Kiểm cả trang ngay sau đăng nhập và '/' khi chưa đăng nhập → /login.
Chạy: python e2e_h4.py [WEB] [u:p:đích ...]   (mặc định admin/gv1/ketoan/ph1, mật khẩu 123456)"""
import sys
from playwright.sync_api import sync_playwright
U=sys.argv[1] if len(sys.argv)>1 else "http://localhost:3000"
ACC=[x.split(":",2) for x in sys.argv[2:]] or [["admin","123456","/dashboard"],["gv1","123456","/home"],["ketoan","123456","/dashboard"],["ph1","123456","/today"]];R=[]
path=lambda url:"/"+url.split("://",1)[-1].split("/",1)[-1].split("?")[0].rstrip("/") if "/" in url.split("://",1)[-1] else "/"
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:200]));print(R[-1],flush=True)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    c=b.new_context(viewport={"width":390,"height":844}); g=c.new_page(); g.goto(U+"/",timeout=90000); g.wait_for_timeout(3000)
    rec("H4-0 chưa đăng nhập mở '/' → /login",path(g.url)=="/login",g.url); c.close()
    for u,p,want in ACC:
        c=b.new_context(viewport={"width":390,"height":844}); g=c.new_page()
        g.goto(U+"/login",timeout=90000); g.fill("input[autocomplete=username]",u); g.fill("input[type=password]",p); g.click("button"); g.wait_for_timeout(3500)
        rec(f"H4 {u} sau đăng nhập vào {want}",path(g.url)==want,g.url)
        g.goto(U+"/"); g.wait_for_timeout(3000)
        rec(f"H4 {u} mở '/' vào {want} (không ra /login)",path(g.url)==want,g.url)
        g.reload(); g.wait_for_timeout(2500); rec(f"H4 {u} tải lại vẫn ở {want}",path(g.url)==want,g.url); c.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
