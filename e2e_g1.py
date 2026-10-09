"""G1: lưu điểm danh → khung mint '✓ Đã lưu điểm danh (n bé)' vẫn còn sau ~3s, n đúng số bé đã đổi; lỗi lưu → khung rose. Khổ 390px.
Chạy: python e2e_g1.py [WEB] [GV u:p] [SHOTS]  (mặc định :3002, gv1:123456). [ghi] đổi 2 bé Có mặt→Đi muộn (G14: chạm→Vắng, att-why, att-late) rồi trả lại Có mặt (1 chạm)."""
import sys,re,os
from playwright.sync_api import sync_playwright
a=sys.argv+[None]*4
U=a[1] or "http://localhost:3002";GU,GP=(a[2] or "gv1:123456").split(":",1);S=a[3] or "/workspace/g1-shots";os.makedirs(S,exist_ok=True);R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:250]));print(R[-1],flush=True)
def box(p):
    m=p.locator("[data-testid=att-msg]")
    if not m.count() or not m.first.is_visible(): return None
    return m.first.evaluate("e=>({t:e.innerText,bg:getComputedStyle(e).backgroundColor,c:getComputedStyle(e).color,cls:e.className,role:e.getAttribute('role')})")
mint=lambda x: x and "bg-mint" in x["cls"]; rose=lambda x: x and "bg-rose" in x["cls"]
def save_and_check(p,tag,n):
    btn=p.locator("[data-testid=att-save]"); bt=btn.inner_text()
    k=int(re.search(r"\((\d+)\)",bt).group(1)) if re.search(r"\((\d+)\)",bt) else -1
    btn.click(); p.wait_for_timeout(1000); b1=box(p); p.wait_for_timeout(2200); b3=box(p); p.screenshot(path=f"{S}/G1-{tag}-390.png",full_page=True)
    got=int(re.search(r"\((\d+) bé\)",b3["t"]).group(1)) if b3 and re.search(r"\((\d+) bé\)",b3["t"]) else None
    rec(f"G1-{tag}a sau lưu có khung '✓ Đã lưu điểm danh (n bé)' màu mint",bool(b1) and b1["t"].startswith("✓ Đã lưu điểm danh") and mint(b1),b1)
    rec(f"G1-{tag}b khung vẫn hiện sau ~3s",bool(b3) and b3["t"].startswith("✓ Đã lưu điểm danh") and mint(b3),b3 and (b3["t"],b3["bg"]))
    rec(f"G1-{tag}c n khớp số bé đã đổi (nút '{bt}', kỳ vọng {n})",got==n==k,f"n trong khung={got}")
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); p=b.new_page(viewport={"width":390,"height":844})
    p.goto(U+"/login",timeout=90000); p.fill("input[autocomplete=username]",GU); p.fill("input[type=password]",GP); p.click("button"); p.wait_for_timeout(4000)
    p.goto(U+"/attendance"); p.wait_for_selector("[data-testid=att-row]",timeout=20000); p.wait_for_timeout(1500)
    rows=p.locator("[data-testid=att-row]"); st=[rows.nth(i).get_attribute("data-status") for i in range(rows.count())]
    pres=[i for i,s in enumerate(st) if s=="present"][:2]
    rec("G1-00 lớp có ≥2 bé 'Có mặt' để thử",len(pres)==2,st)
    for i in pres:  # G14: 1 chạm Có mặt→Vắng, rồi 'Ghi lý do · sửa ›' (att-why) → 'Đi muộn' (att-late)
        rows.nth(i).locator("button").first.click(); p.wait_for_timeout(150); rows.nth(i).locator("[data-testid=att-why]").click(); p.wait_for_timeout(150); rows.nth(i).locator("[data-testid=att-late]").click(); p.wait_for_timeout(150)
    save_and_check(p,"01",len(pres))
    rec("G1-01d sau lưu, các bé hiện 'Đi muộn' (dữ liệu đã tải lại)",all(rows.nth(i).get_attribute("data-status")=="late" for i in pres))
    o=p.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth"); rec("OVF[390] /attendance không tràn ngang (có khung Đã lưu)",o<=0,f"scrollWidth-clientWidth={o}")
    # trả lại Có mặt (G14 e72bfb6: Đi muộn chạm 1 lần → Có mặt)
    for i in pres: rows.nth(i).locator("button").first.click(); p.wait_for_timeout(150)
    save_and_check(p,"02",len(pres))
    # lỗi: chặn request lưu
    p.route(re.compile(r".*/classes/[^/]+/attendance$"),lambda r: r.abort() if r.request.method=="PUT" else r.continue_())
    i=pres[0]; rows.nth(i).locator("button").first.click(); p.wait_for_timeout(150)  # G14: 1 chạm Có mặt→Vắng
    p.locator("[data-testid=att-save]").click(); p.wait_for_timeout(1500); e1=box(p); p.wait_for_timeout(1800); e3=box(p); p.screenshot(path=f"{S}/G1-error-390.png",full_page=True)
    rec("G1-03a lưu lỗi (request bị chặn) → khung màu rose, không có '✓'",bool(e1) and rose(e1) and not e1["t"].startswith("✓"),e1)
    rec("G1-03b khung lỗi vẫn hiện sau ~3s",bool(e3) and rose(e3),e3 and e3["t"])
    sv=p.locator("[data-testid=att-save]"); rec("G1-03c sau lỗi nút Lưu bấm lại được (thay đổi chưa mất)",sv.is_enabled() and "(1)" in sv.inner_text(),sv.inner_text())
    o=p.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth"); rec("OVF[390] /attendance không tràn ngang (khung lỗi)",o<=0,f"{o}")
    p.unroute(re.compile(r".*/classes/[^/]+/attendance$")); p.reload(); p.wait_for_timeout(3000)
    rows=p.locator("[data-testid=att-row]"); rec("G1-04 dữ liệu sau test đã về như ban đầu ('Có mặt')",all(rows.nth(i).get_attribute("data-status")=="present" for i in pres))
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
