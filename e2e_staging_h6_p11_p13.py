"""Staging UI: G12, H6, P13, A3, P11, H7/H3/G13 loading. Tài khoản qua env SA/SG/SP (u:p), WEB, API."""
import os,re,sys,json,requests
from playwright.sync_api import sync_playwright
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
W=os.environ["WEB"];B=os.environ["API"];S=os.environ.get("SHOTS","/workspace/stg3/shots");os.makedirs(S,exist_ok=True);R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:300]));print(R[-1],flush=True)
cr=lambda k: os.environ[k].split(":",1)
def ctx(b,acc,w=390,h=844,tz=None,init=None,route=None,consent=None):
    c=b.new_context(viewport={"width":w,"height":h},timezone_id=tz) if tz else b.new_context(viewport={"width":w,"height":h})
    if init: c.add_init_script(init)
    if route: c.route(*route)
    p=c.new_page(); login_ui(p,W,*cr(acc),consent=consent); return c,p
def slow(c,p,on=True):
    s=c.new_cdp_session(p); s.send("Network.enable"); s.send("Network.emulateNetworkConditions",{"offline":False,"latency":2500 if on else 0,"downloadThroughput":60000 if on else -1,"uploadThroughput":60000 if on else -1}); return s
def watch(p,secs=9):
    seen=[];last=None
    for i in range(int(secs*4)):
        try: t=re.sub(r"\s+"," ",p.inner_text("main",timeout=400))
        except Exception: t=""
        if t!=last: seen.append((round(i/4,1),t[:200])); last=t
        p.wait_for_timeout(250)
    return seen
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    # G12
    for acc,want in [("SA","Giao bé"),("SG","Giao bé"),("SP","Đón bé")]:
        c,p=ctx(b,acc,consent=True); p.goto(W+"/pickups"); p.wait_for_timeout(4000); h=p.locator("main h1").first.inner_text() if p.locator("main h1").count() else ""
        rec(f"G12 {acc} /pickups tiêu đề '{want}'",want in h and not (want=="Giao bé" and "Đón bé" in h),h); c.close()
    # H6 (chỉ đọc)
    c,p=ctx(b,"SA",1280,900); p.goto(W+"/staff"); p.wait_for_timeout(5000)
    nx=p.locator("button[aria-label='Tuần sau']")
    if nx.count(): nx.first.click(); p.wait_for_timeout(4000)
    t=p.inner_text("main"); p.screenshot(path=f"{S}/H6-staff-week-12-10.png",full_page=True)
    rs=p.locator("[data-testid=row-sub]").all_inner_texts()
    rec("H6-01 dòng Cô Mai có '↔ Trông thay Mầm 1 (T2)'",any("Trông thay Mầm 1 (T2)" in x for x in rs) or "↔ Trông thay Mầm 1" in t,rs or re.findall(r"[^\n]*(?:Mai|Trông thay)[^\n]*",t)[:6])
    ol=p.locator("[data-testid=on-leave]").inner_text() if p.locator("[data-testid=on-leave]").count() else ""
    rec("H6-02 ô Nghỉ phép tuần 12/10 = 0,5 ngày (Cô Lan nghỉ sáng T2)",ol.startswith("0,5"),f"on-leave='{ol}' | {re.findall(r'[^\n]*Lan[^\n]*(?:\n[^\n]*){0,2}',t)[:2]}")
    c.close()
    # A3
    c,p=ctx(b,"SA",1280,900); p.goto(W+"/sensitive-changes"); p.wait_for_timeout(6000); t=p.inner_text("main"); p.screenshot(path=f"{S}/A3-sensitive-1280.png")
    users=re.findall(r"\b(demo_ph_phuc|hieutruong|gv_mam1|ketoan|ph_an)\b",t); names=re.findall(r"Phụ huynh demo|Cô Hiệu trưởng|Cô Lan|Chị Hoa|Nguyễn Văn Bình",t)
    rec("A3 'Người sửa' hiện tên hiển thị, không hiện tên đăng nhập",not users and bool(names),f"tên={sorted(set(names))} username={sorted(set(users))}")
    c.close()
    # P13 – ngày VN với múi giờ máy khác + Đang tải…
    H={"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":cr("SP")[0],"password":cr("SP")[1]}).json()["accessToken"]}
    import datetime; vn=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=7)).date().isoformat()
    kid=requests.get(B+"/children",headers=H).json()["items"][0]; a=requests.get(B+f"/children/{kid['id']}/attendance?from={vn}&to={vn}",headers=H).json()
    exp={"present":"Có mặt","absent":"Vắng","late":"Đi muộn"}.get(a[0]["status"] if a else "", "Cô chưa điểm danh")
    for tz in ["America/Los_Angeles","UTC","Asia/Ho_Chi_Minh"]:
        c,p=ctx(b,"SP",tz=tz,consent=True); s=slow(c,p); p.goto(W+"/today",wait_until="commit"); seen=watch(p,8); p.screenshot(path=f"{S}/P13-today-{tz.replace('/','_')}.png")
        s.send("Network.emulateNetworkConditions",{"offline":False,"latency":0,"downloadThroughput":-1,"uploadThroughput":-1}); p.wait_for_timeout(3500); t=p.inner_text("main")
        loading=any("Đang tải" in x[1] for x in seen); wrong=[x for x in seen if "Cô chưa điểm danh" in x[1]] if exp!="Cô chưa điểm danh" else []
        rec(f"P13 [{tz}] ô điểm danh 'Đang tải…' rồi '{exp}' (ngày VN {vn}), không lóe 'Cô chưa điểm danh'",loading and exp in t and not wrong,f"loading={loading} lóe_sai={wrong[:1]} cuối={re.findall(r'(?:Có mặt|Vắng|Đi muộn|Cô chưa điểm danh)',t)[:2]}")
        c.close()
    # P11 – trạng thái thông báo ở Tài khoản
    V=json.dumps({"publicKey":"BElxQA","enabled":True,"channels":[]})
    def perm(state,sub):
        return f"""Object.defineProperty(Notification,'permission',{{get:()=>'{state}'}});
        if(navigator.serviceWorker){{const g=navigator.serviceWorker.getRegistration.bind(navigator.serviceWorker);
        navigator.serviceWorker.getRegistration=async()=>({{pushManager:{{getSubscription:async()=>{'({endpoint:"x"})' if sub else 'null'}}}}});}}"""
    for nm,state,sub,want in [("denied","denied",False,"Đang tắt"),("granted+subscribed","granted",True,"✓ Đang bật"),("default","default",False,"Bật")]:
        c,p=ctx(b,"SP",init=perm(state,sub),route=("**/push/vapid-public-key",lambda r:r.fulfill(status=200,content_type="application/json",body=V)),consent=True)
        p.goto(W+"/account"); p.wait_for_timeout(5000); row=p.locator("[data-testid=account-push]"); txt=row.inner_text() if row.count() else ""
        stt=p.locator("[data-testid=account-push-state]"); en=p.locator("[data-testid=account-push-enable]")
        tag=stt.first.evaluate("e=>e.tagName") if stt.count() else ""
        p.screenshot(path=f"{S}/P11-{nm}.png")
        if nm=="default": ok=en.count()==1 and stt.count()==0
        else: ok=stt.count()==1 and want in stt.inner_text() and tag=="SPAN" and en.count()==0 and (nm!="denied" or "Muốn bật lại" in txt)
        rec(f"P11 [{nm}] → {'nút Bật' if nm=='default' else 'nhãn '+want+(' + hướng dẫn' if nm=='denied' else '')}",ok,f"{txt!r} tag={tag} btnBật={en.count()}")
        c.close()
    # H7/H3/G13 loading
    for acc,path in [("SA","/dashboard"),("SA","/attendance"),("SG","/attendance"),("SG","/home")]:
        c,p=ctx(b,acc); s=slow(c,p); p.goto(W+path,wait_until="commit"); seen=watch(p,9); p.screenshot(path=f"{S}/LOAD{acc}{path.replace('/','_')}.png")
        bad=[x for x in seen if re.search(r"Số lớp 0\b|Chưa có dữ liệu|đã điểm hết|Có mặt: 0 .*Chưa điểm: 0|0/0",x[1])]
        rec(f"H7/H3/G13 {acc} {path}: lúc tải 'Đang tải…', không số 0/'đã điểm hết'/'Chưa có dữ liệu'",any("Đang tải" in x[1] for x in seen) and not bad,f"bad={bad[:1]} đầu={seen[0][1][:120] if seen else ''}")
        c.close()
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
