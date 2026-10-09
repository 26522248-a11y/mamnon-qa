"""H7/G13/G12/G11 (nhánh design/h7-loading) – chạy local, mạng chậm giả lập bằng CDP để bắt trạng thái đang tải. Khổ 390px.
Chạy: python e2e_h7_g11.py [WEB=http://localhost:3006] [API=http://localhost:3001/api/v1]
[ghi] XOÁ chấm công HÔM NAY của gv1 (psql, DB local) trước/sau khi test G11; test API check-in rồi check-out ngay (cùng phút)."""
import sys,re,subprocess,datetime,requests
from playwright.sync_api import sync_playwright
from qa_login import login_ui
a=sys.argv+[None]*3; U=a[1] or "http://localhost:3006"; B=a[2] or "http://localhost:3001/api/v1"
DB="postgres://mamnon:mamnon@localhost:5432/mamnon"; S="/workspace/qa/shots/h7"; import os; os.makedirs(S,exist_ok=True); R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:240])); print(R[-1],flush=True)
tok=lambda u:requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"]
GV={"Authorization":"Bearer "+tok("gv1")}; GVID=requests.get(B+"/auth/me",headers=GV).json()["id"]
T=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=7)).date().isoformat()
reset=lambda:subprocess.run(["psql",DB,"-Atc",f"DELETE FROM staff_checkins WHERE user_id='{GVID}' AND date='{T}'"],capture_output=True,text=True).stdout
SNAP="()=>({t:document.body.innerText,load:!!document.querySelector('[data-testid=att-loading]'),allp:!!document.querySelector('[data-testid=att-all-present]'),rows:document.querySelectorAll('[data-testid=att-row]').length,sk:document.querySelectorAll('[data-testid=att-loading] .animate-pulse').length})"
def slow(page,lat=2500):
    c=page.context.new_cdp_session(page); c.send("Network.enable"); c.send("Network.emulateNetworkConditions",{"offline":False,"latency":lat,"downloadThroughput":-1,"uploadThroughput":-1}); return c
def snaps(page,path,until,secs=25):
    page.goto(U+path,wait_until="commit",timeout=90000); out=[]
    for _ in range(int(secs/0.25)):
        try: s=page.evaluate(SNAP); out.append(s)
        except Exception: pass
        if out and until(out[-1]): break
        page.wait_for_timeout(250)
    return out
ovf=lambda p:p.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
# ── API G11: ra ca cùng phút vào ca
reset(); r1=requests.post(B+"/staff/me/check-in",headers=GV,json={}); r2=requests.post(B+"/staff/me/check-out",headers=GV,json={})
rec("G11-API ra ca ngay cùng phút vào ca bị backend chặn (dự kiến CHƯA – phần dev)",r2.status_code>=400,f"check-in {r1.status_code} {r1.text[:80]} | check-out {r2.status_code} {r2.text[:100]}")
reset()
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); V={"width":390,"height":844}
    # ── H7 dashboard (admin)
    c=b.new_context(viewport=V); p=c.new_page(); login_ui(p,U,"admin","123456",consent=None)
    rec("G12-01 menu BGH có 'Giao bé', không 'Đón bé'",("Giao bé" in p.inner_text("body") or p.locator("[data-testid=nav-tab-pickups]").count()) and "Đón bé" not in p.locator("nav").all_inner_texts().__str__(),p.locator("nav").all_inner_texts().__str__().replace("\\n"," ")[:200])
    slow(p); ss=snaps(p,"/dashboard",lambda s:"Số lớp" in s["t"] and "Đang tải" not in s["t"].split("Số lớp")[0][-60:]+s["t"].split("Số lớp")[1][:40] and re.search(r"Số lớp\s*\d",s["t"]))
    zero=[s["t"][:200] for s in ss if re.search(r"Số lớp\s*0(?!\d)|(?<!\d)0\s*Số lớp",s["t"]) ]; loading=[s for s in ss if re.search(r"Số lớp\s*Đang tải…|Đang tải…\s*Số lớp",s["t"])]
    fin=re.search(r"Số lớp\s*(\d+)",ss[-1]["t"]) if ss else None
    rec("H7-01 Tổng quan khi đang tải hiện 'Đang tải…' ở Số lớp",bool(loading),f"{len(loading)}/{len(ss)} mẫu 'Đang tải…'; cuối: Số lớp={fin.group(1) if fin else '?'}")
    rec("H7-02 không lúc nào hiện 'Số lớp 0'",not zero,zero[:1])
    dl=[s for s in ss if re.search(r"Điểm danh theo lớp hôm nay\s*Đang tải…",s["t"])]; dz=[s["t"][:160] for s in ss if re.search(r"(?<!\d)0/0 có mặt",s["t"])]
    rec("H3-01 ô 'Điểm danh theo lớp' hiện 'Đang tải…' khi đang tải",bool(dl),f"{len(dl)}/{len(ss)} mẫu")
    rec("H3-02 ô 'Điểm danh theo lớp' không hiện '0/0 có mặt' khi đang tải",not dz,dz[:1])
    p.screenshot(path=S+"/H7-dashboard-390.png",full_page=True)
    c.close(); c=b.new_context(viewport=V); p=c.new_page(); login_ui(p,U,"admin","123456",consent=None)
    p.goto(U+"/pickups"); p.wait_for_timeout(3500); t=p.inner_text("body"); h1=p.locator("h1").first.inner_text() if p.locator("h1").count() else ""
    rec("G12-02 BGH /pickups có thẻ 'Giao bé hôm nay'","Giao bé hôm nay" in t)
    rec("G12-03 BGH /pickups tiêu đề không còn 'Đón bé'",h1!="Đón bé",f"h1='{h1}'"); p.screenshot(path=S+"/G12-admin-pickups-390.png",full_page=True)
    for path in ["/dashboard","/pickups"]: p.goto(U+path); p.wait_for_timeout(2500); o=ovf(p); rec(f"OVF[390] admin {path}",o<=0,o)
    c.close()
    # ── G13 attendance (gv1) + G12 GV menu
    c=b.new_context(viewport=V); p=c.new_page(); login_ui(p,U,"gv1","123456",consent=None)
    nav=str(p.locator("nav").all_inner_texts()); rec("G12-04 menu GV có 'Giao bé', không 'Đón bé'","Giao bé" in nav and "Đón bé" not in nav,nav.replace("\\n"," ")[:200])
    slow(p); ss=snaps(p,"/attendance",lambda s:s["rows"]>0 or ("Lớp chưa có bé" in s["t"] and not s["load"]))
    pre=[s for s in ss if s["rows"]==0]; ld=[s for s in pre if s["load"]]
    rec("G13-01 đang tải hiện 'Đang tải danh sách lớp…' + khung chờ",any("Đang tải danh sách lớp…" in s["t"] and s["sk"]>=1 for s in ld),f"{len(ld)}/{len(ss)} mẫu đang tải; skeleton={max([s['sk'] for s in ld] or [0])}")
    bad=[s["t"][:150].replace("\n"," ") for s in pre if s["allp"] or "Cả lớp có mặt" in s["t"] or "đã điểm hết" in s["t"] or "Lớp chưa có bé" in s["t"] or re.search(r"(?<![\d/])0\s*/\s*0|(?<!\d)0 bé|0 trẻ",s["t"])]
    rec("G13-02 trước khi tải xong: không số 0, không danh sách trống, không nút 'Cả lớp có mặt'",not bad,bad[:1])
    rec("G13-03 tải xong có danh sách bé",ss and ss[-1]["rows"]>0,f"att-row={ss[-1]['rows'] if ss else 0}"); p.screenshot(path=S+"/G13-attendance-390.png",full_page=True)
    c.close()
    # ── G11 UI /home (gv1), page.clock
    c=b.new_context(viewport=V); p=c.new_page(); p.clock.install(); login_ui(p,U,"gv1","123456",consent=None)
    p.goto(U+"/home"); p.wait_for_timeout(3500); btn=p.locator("[data-testid=btn-checkin]")
    rec("G11-00 chưa vào ca: nút '✓ Vào ca'",btn.count() and btn.inner_text().strip()=="✓ Vào ca",btn.inner_text() if btn.count() else "")
    dialogs=[]; p.on("dialog",lambda d:(dialogs.append(d.message),d.dismiss() if len(dialogs)==1 else d.accept()))
    btn.click(); btn.click(timeout=2000,force=True); p.wait_for_timeout(2500)
    st=requests.get(B+"/staff/me/today",headers=GV).json()
    rec("G11-01 sau Vào ca: '✓ Đã vào ca' bị khoá",btn.inner_text().strip()=="✓ Đã vào ca" and btn.is_disabled(),f"'{btn.inner_text()}' disabled={btn.is_disabled()}")
    rec("G11-02 bấm 2 lần không ra ca",not (st.get("checkOutAt")) and not dialogs,{k:st.get(k) for k in ["checkInAt","checkOutAt"]})
    p.screenshot(path=S+"/G11-1-locked-390.png")
    p.clock.fast_forward("00:30"); p.wait_for_timeout(800); rec("G11-03 sau 30 giây vẫn khoá",btn.is_disabled(),btn.inner_text())
    p.clock.fast_forward("00:35"); p.wait_for_timeout(1200)
    cls=btn.get_attribute("class") or ""; bc=btn.evaluate("e=>getComputedStyle(e).borderColor")
    rec("G11-04 sau 1 phút: nút 'Ra ca' bấm được, viền peach",btn.inner_text().strip()=="Ra ca" and btn.is_enabled() and "border-peach-500" in cls,f"'{btn.inner_text()}' border={bc}"); p.screenshot(path=S+"/G11-2-raca-390.png")
    btn.click(); p.wait_for_timeout(2000); st=requests.get(B+"/staff/me/today",headers=GV).json()
    rec("G11-05 'Ra ca' hỏi xác nhận; Huỷ thì giữ nguyên",len(dialogs)==1 and not st.get("checkOutAt") and btn.count() and btn.inner_text().strip()=="Ra ca",f"hộp thoại={dialogs} checkOutAt={st.get('checkOutAt')}")
    btn.click(); p.wait_for_timeout(3000); st=requests.get(B+"/staff/me/today",headers=GV).json(); t=p.locator("[data-testid=home-punch]").inner_text()
    rec("G11-06 Đồng ý → ra ca, hiện '✓ Đã ra ca'",len(dialogs)==2 and "✓ Đã ra ca" in t and st.get("checkOutAt"),f"hộp thoại={dialogs} | {t.replace(chr(10),' ')} | API checkOutAt={st.get('checkOutAt')}")
    p.screenshot(path=S+"/G11-3-done-390.png")
    for path in ["/home","/attendance","/pickups"]: p.goto(U+path); p.wait_for_timeout(2500); o=ovf(p); rec(f"OVF[390] gv1 {path}",o<=0,o)
    c.close()
    # ── PH vẫn 'Đón bé'
    c=b.new_context(viewport=V); p=c.new_page(); login_ui(p,U,"ph1","123456",consent=True)
    nav=str(p.locator("[data-testid=parent-nav]").all_inner_texts()); rec("G12-05 menu PH vẫn 'Đón bé'","Đón bé" in nav and "Giao bé" not in nav,nav.replace("\\n"," ")[:200])
    for path in ["/today","/pickups"]: p.goto(U+path); p.wait_for_timeout(2500); o=ovf(p); rec(f"OVF[390] ph1 {path}",o<=0,o)
    c.close(); b.close()
print("reset chấm công gv1 hôm nay:",reset() or "ok")
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
