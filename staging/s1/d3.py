import os,sys
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
from playwright.sync_api import sync_playwright
W="https://mamnon-web.vercel.app"; R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:260]));print(R[-1],flush=True)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); p=b.new_page(viewport={"width":390,"height":844}); errs=[]; p.on("pageerror",lambda e: errs.append(str(e)[:150]))
    login_ui(p,W,*os.environ["SP"].split(":",1),consent=True); p.goto(W+"/today"); p.wait_for_timeout(6000)
    t=p.locator("[data-testid=tile-picked-up]")
    rec("D3-01 có dòng tile-picked-up, có ›",t.count()==1 and "›" in t.inner_text() and "Đã được" in t.inner_text(),t.inner_text() if t.count() else "")
    rec("D3-02 tên truy cập (aria) có tên + giờ đón",t.count()==1 and "đón lúc" in (t.get_attribute("aria-label") or t.inner_text()),t.get_attribute("aria-label") if t.count() else "")
    if t.count(): t.click(); p.wait_for_timeout(5000)
    p.screenshot(path="/workspace/stg/s1/D3-log-390.png",full_page=True)
    rec("D3-03 bấm → /today/log/<id>?tab=attendance","/today/log/" in p.url and "tab=attendance" in p.url,p.url)
    rec("D3-04 trang lịch sử điểm danh hiện nội dung",len(p.inner_text("main"))>40,p.inner_text("main")[:120])
    rec("D3-JS không lỗi JS",not errs,errs); b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
