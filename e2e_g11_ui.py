"""G11 UI /home: Vào ca → '✓ Đã vào ca' khoá 1 phút → 'Ra ca' có hỏi xác nhận. [ghi] 1 lượt vào+ra ca. Chạy: WEB=… G11_USER=u:p python e2e_g11_ui.py"""
import os,sys
from playwright.sync_api import sync_playwright
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
W=os.environ.get("WEB","http://localhost:3002");R=[];S="/workspace/stg3/shots"
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:200]));print(R[-1],flush=True)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); p=b.new_page(viewport={"width":390,"height":844})
    login_ui(p,W,*os.environ["G11_USER"].split(":",1),consent=None); p.goto(W+"/home"); p.wait_for_timeout(4000); bt=p.locator("[data-testid=btn-checkin]")
    rec("G11-UI-0 chưa vào ca → nút '✓ Vào ca'",bt.inner_text().strip()=="✓ Vào ca",bt.inner_text())
    bt.click(); p.wait_for_timeout(2500); rec("G11-UI-1 sau Vào ca → '✓ Đã vào ca', bị khoá",bt.inner_text().strip()=="✓ Đã vào ca" and bt.is_disabled(),(bt.inner_text(),bt.is_disabled())); p.screenshot(path=f"{S}/G11-locked.png")
    p.wait_for_timeout(30000); rec("G11-UI-2 sau 30s vẫn khoá",bt.is_disabled())
    p.wait_for_timeout(32000); cls=bt.get_attribute("class") or ""
    rec("G11-UI-3 sau 1 phút → 'Ra ca' bấm được, màu khác (viền peach)",bt.inner_text().strip()=="Ra ca" and bt.is_enabled() and "peach" in cls,(bt.inner_text(),cls[:80])); p.screenshot(path=f"{S}/G11-raca.png")
    msgs=[]; p.once("dialog",lambda d:(msgs.append(d.message),d.dismiss())); bt.click(); p.wait_for_timeout(2000)
    rec("G11-UI-4 bấm Ra ca → hỏi xác nhận; Huỷ thì chưa ra ca",msgs==["Ra ca bây giờ?"] and bt.inner_text().strip()=="Ra ca",(msgs,bt.inner_text()))
    p.once("dialog",lambda d:d.accept()); bt.click(); p.wait_for_timeout(3000); t=p.inner_text("main")
    rec("G11-UI-5 đồng ý → '✓ Đã ra ca'","Đã ra ca" in t,t[:120]); p.screenshot(path=f"{S}/G11-done.png")
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
