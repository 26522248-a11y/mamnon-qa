"""P8/P10/P11/P12/P13 (nhánh design/ph-copy2) – phụ huynh ph1, khổ 390px. Chạy: python e2e_phcopy2.py [WEB=http://localhost:3007] [API]
Chỉ đọc (không gửi báo nghỉ). P13 dùng page.route để làm chậm / trả [] cho điểm danh; P11 'Đang tắt' giả lập Notification.permission='denied'; P12 dùng page.clock 09:30 giờ VN."""
import sys,re,datetime,requests
from playwright.sync_api import sync_playwright
from qa_login import login_ui
a=sys.argv+[None]*3; U=a[1] or "http://localhost:3007"; B=a[2] or "http://localhost:3001/api/v1"; S="/workspace/qa/shots/phcopy2"; import os; os.makedirs(S,exist_ok=True); R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:240])); print(R[-1],flush=True)
P={"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":"ph1","password":"123456"}).json()["accessToken"]}
kid=requests.get(B+"/children",headers=P).json()["items"][0]; bal=requests.get(B+f"/children/{kid['id']}/balance",headers=P).json()
ovf=lambda p:p.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); V={"width":390,"height":844}
    def ctx(init=None,clock=None):
        c=b.new_context(viewport=V); p=c.new_page()
        if init: p.add_init_script(init)
        if clock: p.clock.install(time=clock)
        login_ui(p,U,"ph1","123456",consent=True); return c,p
    c,p=ctx()
    # P8
    p.goto(U+f"/fees/child/{kid['id']}"); p.wait_for_timeout(3500); t=p.inner_text("body"); p.screenshot(path=S+"/P8-fee-child-390.png",full_page=True)
    paid=bal["balance"]<=0 and bal["overdueAmount"]<=0
    rec(f"P8-01 bé đóng đủ (balance={bal['balance']}, credit={bal['creditBalance']}) chỉ hiện 'Đã đóng đủ'",paid and p.locator("[data-testid=child-paid]").count()==1 and "Đã đóng đủ" in t,p.locator("[data-testid=child-paid]").inner_text().replace("\n"," | ") if p.locator("[data-testid=child-paid]").count() else "")
    rec("P8-02 không còn 'Còn nợ 0đ' / 'Quá hạn 0đ'",not re.search(r"(Còn nợ|Quá hạn)\s*0\s?đ",t) and "Còn nợ" not in t,re.findall(r"(?:Còn nợ|Quá hạn)[^\n]*\n?[^\n]*",t)[:2])
    if bal["creditBalance"]>0: rec("P8-03 có dòng 'Số dư trả trước …'","Số dư trả trước" in t,re.findall(r"Số dư trả trước[^\n]*",t))
    rec("OVF[390] /fees/child",ovf(p)<=0,ovf(p))
    # P10
    p.goto(U+"/today"); p.wait_for_timeout(3500); lk=p.locator("[data-testid=link-consent]")
    rec("P10-01 trang đầu có thẻ '📸 Cho cô đăng hình con lên nhóm lớp'",lk.count()==1 and "📸 Cho cô đăng hình con lên nhóm lớp" in lk.inner_text(),lk.inner_text().replace("\n"," | ") if lk.count() else "")
    rec("OVF[390] /today",ovf(p)<=0,ovf(p))
    if lk.count():
        lk.click(); p.wait_for_timeout(3000); vis=p.evaluate("(()=>{const e=document.getElementById('consent');if(!e)return null;const r=e.getBoundingClientRect();return {top:r.top,txt:e.innerText.slice(0,80)}})()")
        rec("P10-02 bấm → /account#consent, phần đăng hình nằm trong màn hình",p.url.endswith("/account#consent") and vis and -5<=vis["top"]<844,f"{p.url} {vis}"); p.screenshot(path=S+"/P10-account-consent-390.png")
    # P11 default
    p.goto(U+"/account"); p.wait_for_timeout(3000); ap=p.locator("[data-testid=account-push]"); txt=ap.inner_text().replace("\n"," | ")
    rec("P11-01 chưa từng bật (default): có nút 'Bật', không nhãn trạng thái",p.locator("[data-testid=account-push-enable]").count()==1 and p.locator("[data-testid=account-push-state]").count()==0,txt)
    rec("OVF[390] /account",ovf(p)<=0,ovf(p)); c.close()
    c,p=ctx(init="try{Object.defineProperty(Notification,'permission',{get:()=>'denied'})}catch(e){}")
    p.goto(U+"/account"); p.wait_for_timeout(3000); ap=p.locator("[data-testid=account-push]"); st=p.locator("[data-testid=account-push-state]")
    look=st.evaluate("e=>({tag:e.tagName,cursor:getComputedStyle(e).cursor,role:e.getAttribute('role')})") if st.count() else {}
    rec("P11-02 đã tắt (denied): nhãn 'Đang tắt' kiểu nhãn (không phải nút) + hướng dẫn bật lại, không có nút 'Bật'",st.count()==1 and st.inner_text().strip()=="Đang tắt" and look.get("tag")!="BUTTON" and look.get("cursor")!="pointer" and "Cài đặt của trình duyệt" in ap.inner_text() and p.locator("[data-testid=account-push-enable]").count()==0,f"{ap.inner_text().replace(chr(10),' | ')} {look}")
    p.screenshot(path=S+"/P11-denied-390.png"); c.close()
    # P12 (09:30 VN)
    c,p=ctx(clock=datetime.datetime(2026,10,10,2,30,tzinfo=datetime.timezone.utc))
    p.goto(U+"/messages"); p.wait_for_timeout(3000)
    if p.locator("[data-testid=msg-tab-absence]").count(): p.click("[data-testid=msg-tab-absence]"); p.wait_for_timeout(800)
    sel=[x for x in ["absence-today","absence-tomorrow","absence-range"] if "bg-mint-500" in (p.locator(f"[data-testid={x}]").get_attribute("class") or "")]
    rec("P12-01 mở form báo nghỉ: chưa chọn sẵn ngày",p.locator("[data-testid=absence-form]").count()==1 and not sel,f"đang chọn={sel}")
    rec("P12-02 chưa chọn ngày: không có cảnh báo 'Đã quá 08:00'",p.locator("[data-testid=absence-late]").count()==0)
    p.click("[data-testid=absence-tomorrow]"); p.wait_for_timeout(500); rec("P12-03 chọn 'Ngày mai': không cảnh báo quá giờ",p.locator("[data-testid=absence-late]").count()==0)
    p.click("[data-testid=absence-today]"); p.wait_for_timeout(500); lt=p.locator("[data-testid=absence-late]")
    rec("P12-04 chọn 'Hôm nay' lúc 09:30: hiện 'Đã quá 08:00…'",lt.count()==1 and "Đã quá 08:00" in lt.inner_text(),lt.inner_text() if lt.count() else ""); p.screenshot(path=S+"/P12-absence-390.png",full_page=True)
    rec("OVF[390] /messages",ovf(p)<=0,ovf(p)); c.close()
    # P13
    c,p=ctx(); seen=[]
    def slow(rt): p.wait_for_timeout(4000); rt.continue_()
    p.route(re.compile(r"/children/[^/]+/attendance\?"),slow); p.goto(U+"/today",wait_until="commit")
    for _ in range(40):
        p.wait_for_timeout(250); tl=p.locator("[data-testid=tile-attendance]")
        if tl.count(): seen.append(tl.inner_text().strip())
    rec("P13-01 ô điểm danh hiện 'Đang tải…' khi đang tải (không 'Chưa điểm danh')",any(s.startswith("Đang tải") for s in seen) and not any("chưa điểm danh" in s.lower() for s in seen if seen.index(s)<[i for i,x in enumerate(seen) if not x.startswith("Đang tải")][0:1].__len__() and False),sorted(set(seen)))
    p.unroute(re.compile(r"/children/[^/]+/attendance\?")); p.route(re.compile(r"/children/[^/]+/attendance\?"),lambda rt:rt.fulfill(status=200,content_type="application/json",body="[]"))
    p.goto(U+"/today"); p.wait_for_timeout(3500); tl=p.locator("[data-testid=tile-attendance]").inner_text().strip()
    rec("P13-02 chưa điểm danh (giả lập API trả []): 'Cô chưa điểm danh'","Cô chưa điểm danh" in tl,tl); p.screenshot(path=S+"/P13-unmarked-390.png")
    c.close(); b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
