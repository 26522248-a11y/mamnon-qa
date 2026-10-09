"""Góp ý phụ huynh lần 2 – P1..P6 (nhánh design/ph-copy). Khổ 390px + máy tính 1280px.
Chạy: python e2e_phcopy.py [WEB] [API] [PH_USER] [PH_PASS] [SHOTS]   (mặc định local :3002, ph1/123456)"""
import sys,re,json,requests
from playwright.sync_api import sync_playwright
a=sys.argv+[None]*6
U=a[1] or "http://localhost:3002";B=a[2] or "http://localhost:3001/api/v1";PU=a[3] or "ph1";PP=a[4] or "123456";S=a[5] or "/workspace/phcopy-shots";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:300]));print(R[-1],flush=True)
H={"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":PU,"password":PP}).json()["accessToken"]}
kid=requests.get(B+"/children",headers=H).json()["items"][0];KID=kid["id"]
bal=requests.get(B+f"/children/{KID}/balance",headers=H).json()
inv=requests.get(B+f"/invoices?childId={KID}&limit=100",headers=H).json()["items"]
att=requests.get(B+f"/children/{KID}/attendance",headers=H).json()
INIT="""Object.defineProperty(Notification,'permission',{get:()=> 'denied'});"""
VAPID=json.dumps({"publicKey":"BElx_fake_key_for_qa","enabled":True,"channels":[]})
def page(b,w,h,denied=False):
    ctx=b.new_context(viewport={"width":w,"height":h})
    if denied:
        ctx.add_init_script(INIT); ctx.route("**/push/vapid-public-key",lambda r:r.fulfill(status=200,content_type="application/json",body=VAPID))
    p=ctx.new_page(); p.goto(U+"/login"); p.fill("input[autocomplete=username]",PU); p.fill("input[type=password]",PP); p.click("button"); p.wait_for_timeout(3500); return p
def go(p,path,wait=2500): p.goto(U+path); p.wait_for_timeout(wait); return p.inner_text("body")
def ovf(p): return p.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")
BAD=re.compile(r"căn cước|BMI|Cabin cước",re.I)
PAGES=["/today","/pickups","/pickups/delegates","/fees","/notifications","/account","/messages",f"/health/{KID}","/menu","/photos"]+[f"/fees/invoice/{i['id']}" for i in inv if i["status"]=="paid"][:1]
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    for W,Hh,tag in [(390,844,"390"),(1280,800,"1280")]:
        p=page(b,W,Hh)
        # P1
        t=go(p,"/fees",3000); p.screenshot(path=f"{S}/P1-fees-{tag}.png",full_page=True)
        rows=p.locator("[data-testid=invoice-row]").count(); voidv="Đã hủy" in t; zero=re.findall(r"(?<![\d.])0\s?đ",t)
        rec(f"P1[{tag}] bé đóng đủ (balance={bal['balance']}) chỉ hiện 'Đã đóng đủ', 0 dòng hoá đơn, không '0đ'",
            "Đã đóng đủ" in t and rows==0 and not zero and not voidv, f"invoice-row={rows}; 0đ={zero}; 'Đã hủy'={voidv}; HĐ: {[ (i['period'],i['status']) for i in inv]}")
        # P2 + overflow
        for path in PAGES:
            t=go(p,path)
            if path=="/pickups/delegates":
                tg=p.locator("[data-testid=delegate-optional-toggle]")
                if tg.count(): tg.first.click(); p.wait_for_timeout(500)
                else:
                    add=p.get_by_text(re.compile("Thêm người")).first
                    if add.count(): add.click(); p.wait_for_timeout(800); tg=p.locator("[data-testid=delegate-optional-toggle]");
                    if tg.count(): tg.first.click(); p.wait_for_timeout(500)
                t=p.inner_text("body")
            texts=[t]
            if path=="/messages":
                for tb in ["absence","medicine","late"]:
                    l=p.locator(f"[data-testid=msg-tab-{tb}]")
                    if l.count(): l.click(); p.wait_for_timeout(1200); texts.append(p.inner_text("body")); p.screenshot(path=f"{S}/P5-messages-{tb}-{tag}.png",full_page=True)
            hits=sorted({m for x in texts for m in BAD.findall(x)}); slug=path.strip("/").replace("/","_")[:30] or "root"
            if path.startswith("/health") or path.startswith("/pickups/delegates"): p.screenshot(path=f"{S}/P2-{slug}-{tag}.png",full_page=True)
            rec(f"P2[{tag}] {path} không có 'căn cước'/'BMI'",not hits,hits)
            if path=="/pickups": rec(f"P2c[{tag}] /pickups ghi 'Thêm người đón hộ (tên và số điện thoại)'","(tên và số điện thoại)" in t,re.findall(r"Thêm người đón hộ[^\n]*",t))
            if path=="/pickups/delegates": bad=re.findall(r"Giấy tờ số …[^\n]*",t); rec(f"P2d[{tag}] không còn 'Giấy tờ số …' (dấu … thừa)",not bad,bad[:2] or re.findall(r"Giấy tờ số[^\n]*",t)[:2])
            if tag=="390": o=ovf(p); rec(f"OVF[390] {path} không tràn ngang",o<=0,f"scrollWidth-clientWidth={o}")
            if path=="/messages":
                allt="\n".join(texts); up=[x for x in texts if re.search(r"ĐÃ QUA",x)]
                hdr=p.locator("[data-testid=past-medicine] h2, [data-testid=past-late] h2, [data-testid=absence-history] h2")
                caps=[h.inner_text() for h in hdr.all()]
                p.locator("[data-testid=msg-tab-absence]").click(); p.wait_for_timeout(1200); at=p.inner_text("body")
                rec(f"P5[{tag}] tab Nghỉ: có 'Báo trước 8 giờ sáng thì trường trả lại tiền ăn', không 'ĐÃ QUA'","Báo trước 8 giờ sáng thì trường trả lại tiền ăn" in at and "ĐÃ QUA" not in at,
                    re.findall(r"Báo trước[^\n]*",at))
                rec(f"P5b[{tag}] không còn 'ĐÃ QUA' ở mọi tab /messages; tab Thuốc/Đón muộn ghi 'Trong 30 ngày qua'",not up and all(c.strip()=="Trong 30 ngày qua" for c in caps if c.strip()!="" and not c.startswith("Báo trước")),f"tiêu đề lịch sử đang hiện: {caps}")
        # P4
        t=go(p,"/today",3000); btn=p.locator("button:has-text('Con nghỉ hôm nay')")
        here=any(x["date"]==__import__('datetime').datetime.now(__import__('datetime').timezone(__import__('datetime').timedelta(hours=7))).strftime("%Y-%m-%d") and x["status"]=="present" for x in att)
        if btn.count():
            btn.first.click(); p.wait_for_timeout(1200); p.screenshot(path=f"{S}/P4-absence-dialog-{tag}.png")
            h=p.locator("[data-testid=absence-here-hint]"); ht=h.inner_text() if h.count() else ""
            rec(f"P4[{tag}] bé đã có mặt hôm nay (API present={here}) → hộp báo nghỉ ghi 'Hôm nay bé đã đi học rồi'","Hôm nay bé đã đi học rồi" in ht,ht)
            p.keyboard.press("Escape"); p.mouse.click(5,5)
        else: rec(f"P4[{tag}] có nút 'Con nghỉ hôm nay'",False,t[:200])
        # P6
        if tag=="1280":
            p.goto(U+"/today"); p.wait_for_timeout(2500); p.screenshot(path=f"{S}/P6-sidebar-1280.png")
            side=[x.strip() for x in p.locator("aside a").all_inner_texts()]
            rec("P6[1280] menu trái PH đúng 5 mục = menu điện thoại",len(side)==5 and [s.split(" ",1)[-1] for s in side]==["Hôm nay","Đón bé","Học phí","Thông báo","Tài khoản"],side)
            nav=p.locator("[data-testid=parent-nav]"); rec("P6[1280] thanh dưới ẩn trên máy tính",not nav.is_visible())
            p.goto(U+"/messages"); p.wait_for_timeout(2000); act=p.locator("aside a.bg-mint-100").all_inner_texts(); rec("P6[1280] /messages vẫn sáng mục 'Tài khoản'",act==["👤 Tài khoản"] or any("Tài khoản" in x for x in act),act)
        else:
            p.goto(U+"/today"); p.wait_for_timeout(2000); p.screenshot(path=f"{S}/P6-bottomnav-390.png")
            tabs=[x.strip().replace("\n"," ") for x in p.locator("[data-testid=parent-nav] a").all_inner_texts()]; rec("P6[390] thanh dưới 5 mục",len(tabs)==5,tabs)
        p.context.close()
    # P3
    for W,Hh,tag in [(390,844,"390"),(1280,800,"1280")]:
        p=page(b,W,Hh,denied=True); go(p,"/today",3000); d=p.locator("[data-testid=push-denied]")
        p.screenshot(path=f"{S}/P3-denied-before-{tag}.png")
        txt=d.inner_text() if d.count() else ""
        rec(f"P3[{tag}] bảng chặn thông báo có chữ mới + nút 'Ẩn'",("Điện thoại đang tắt thông báo" in txt) and p.locator("[data-testid=push-denied-hide]").count()==1,txt)
        if d.count():
            p.click("[data-testid=push-denied-hide]"); p.wait_for_timeout(600); h1=p.locator("[data-testid=push-denied]").count()
            p.reload(); p.wait_for_timeout(3000); h2=p.locator("[data-testid=push-denied]").count(); p.screenshot(path=f"{S}/P3-denied-after-reload-{tag}.png")
            rec(f"P3[{tag}] bấm Ẩn thì mất, tải lại vẫn ẩn",h1==0 and h2==0,f"sau Ẩn={h1}, sau reload={h2}")
        p.context.close()
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
