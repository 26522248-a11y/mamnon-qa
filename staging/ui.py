import os,re,io,json,time,requests,sys
from PIL import Image
from playwright.sync_api import sync_playwright
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
W=os.environ["WEB"];B=os.environ["API"];S="/workspace/stg2/shots";os.makedirs(S,exist_ok=True);R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:260]));print(R[-1],flush=True)
cr=lambda k: os.environ[k].split(":",1)
BAD=re.compile(r"(?<!\d)0 trẻ|Lớp chưa có bé|Chưa có bé|Không có trẻ|0 bé")
def throttled(b,acc,paths,tag):
    ctx=b.new_context(viewport={"width":390,"height":844}); p=ctx.new_page(); login_ui(p,W,*cr(acc),consent=None)
    cdp=ctx.new_cdp_session(p); cdp.send("Network.enable")
    for path in paths:
        cdp.send("Network.emulateNetworkConditions",{"offline":False,"latency":2500,"downloadThroughput":60000,"uploadThroughput":60000})
        try: p.goto(W+path,wait_until="commit",timeout=60000)
        except Exception as e: pass
        seen=[];loading=False;shot=False
        for i in range(60):
            try: t=p.inner_text("main",timeout=500)
            except Exception: t=""
            if "Đang tải" in t or p.locator(".animate-pulse,[data-testid$=skeleton],[data-testid$=loading]").count(): loading=True
            if loading and not shot: p.screenshot(path=f"{S}/{tag}{path.replace('/','_')}-loading.png"); shot=True
            m=BAD.findall(t)
            if m: seen.append((round(i*0.25,1),m[0]))
            p.wait_for_timeout(250)
        cdp.send("Network.emulateNetworkConditions",{"offline":False,"latency":0,"downloadThroughput":-1,"uploadThroughput":-1})
        p.wait_for_timeout(3000); final=p.inner_text("main"); p.screenshot(path=f"{S}/{tag}{path.replace('/','_')}-done.png",full_page=True)
        rec(f"H3/G2 {acc} {path}: lúc tải hiện 'Đang tải…'/khung chờ, không '0 trẻ'/'Lớp chưa có bé'",loading and not seen,f"loading={loading} bad_during_load={seen[:3]} final_bad={BAD.findall(final)[:2]}")
        if path=="/notes":
            imgs=p.locator("main img").count(); rec("G2 nhật ký: mỗi bé có họ tên đầy đủ + ảnh",imgs>0 and bool(re.search(r"\w+ \w+ \w+",final)),f"img={imgs} | {final[:200]!r}")
    ctx.close()
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    throttled(b,"SG",["/notes","/attendance"],"gv")
    throttled(b,"SA",["/children","/users","/notes","/dashboard","/attendance"],"bgh")
    # H2
    ctx=b.new_context(viewport={"width":1280,"height":900}); p=ctx.new_page(); login_ui(p,W,*cr("SA"),consent=None); p.goto(W+"/audit"); p.wait_for_timeout(6000)
    t=p.inner_text("main"); p.screenshot(path=f"{S}/H2-audit-1280.png",full_page=True)
    tech=re.findall(r"\b[a-z_]+\.[a-z_]+(?:\.[a-z_]+)?\b|\bamount\b|\bout\b|\bin\b(?= *→)",t)
    money=re.findall(r"\d{1,3}(?:\.\d{3})+ ?đ",t); rawnum=re.findall(r"(?<![\d.,])\d{6,}(?![\d.,])",t)
    rec("H2-01 nhật ký thao tác không còn chữ kỹ thuật (finance.expense.create/amount/out)",not tech,tech[:8])
    rec("H2-02 số tiền dạng 12.000.000đ (không có số thô ≥6 chữ số)",bool(money) and not rawnum,f"tiền={money[:5]} thô={rawnum[:5]}")
    ctx.close()
    # A1 UI (không bấm Đăng)
    ctx=b.new_context(viewport={"width":390,"height":844}); p=ctx.new_page(); login_ui(p,W,*cr("SG"),consent=None); p.goto(W+"/photos"); p.wait_for_timeout(5000)
    bimg=io.BytesIO(); Image.new("RGB",(200,200),"orange").save(bimg,"JPEG"); open("/tmp/qa_a1.jpg","wb").write(bimg.getvalue())
    soon=p.locator("[data-testid=photos-soon]").count(); rec("A1-00 trang ảnh đã bật thật (không 'Sắp có')",soon==0)
    fi=p.locator("[data-testid=file-input]")
    if fi.count(): fi.first.set_input_files("/tmp/qa_a1.jpg"); p.wait_for_timeout(2500)
    nk=p.locator("[data-testid=no-consent-kid]"); bc=nk.first.evaluate("e=>getComputedStyle(e.querySelector('span')||e).borderColor") if nk.count() else ""
    rec("A1-01 danh sách bé chưa đồng ý kèm ảnh/khung đỏ",nk.count()>0 and "rgb(2" in bc,f"no-consent-kid={nk.count()} border={bc} banner={p.locator('[data-testid=no-consent-banner]').inner_text()[:120] if p.locator('[data-testid=no-consent-banner]').count() else ''}")
    tap=p.locator("[data-testid=compose-photo-tap]");
    if tap.count(): tap.first.click(); p.wait_for_timeout(800)
    chips=p.locator("[data-testid=tag-chips] button, [data-testid=photo-tagger] button")
    bad=[i for i in range(chips.count()) if "rose" in (chips.nth(i).get_attribute("class") or "")]
    if bad: chips.nth(bad[0]).click(); p.wait_for_timeout(800)
    post=p.locator("[data-testid=btn-post]"); pt=post.inner_text() if post.count() else ""; p.screenshot(path=f"{S}/A1-flagged-390.png",full_page=True)
    rec("A1-02 gắn bé chưa đồng ý → ảnh viền đỏ + bảng xử lý, nút Đăng khoá 'còn n ảnh cần xử lý'",p.locator("[data-testid=flag-panel]").count()>0 and "cần xử lý" in pt and post.is_disabled(),f"chips={chips.count()} bad={len(bad)} nút='{pt}' disabled={post.is_disabled() if post.count() else None}")
    if p.locator("[data-testid=btn-hide-kid]").count():
        p.click("[data-testid=btn-hide-kid]"); p.wait_for_timeout(800); pt2=post.inner_text(); rec("A1-03 'Ẩn bé đi' → hết cảnh báo, nút Đăng mở (không bấm)", "cần xử lý" not in pt2 and post.is_enabled(),pt2)
    p.screenshot(path=f"{S}/A1-after-hide-390.png",full_page=True)
    ctx.close()  # bỏ, không đăng
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
