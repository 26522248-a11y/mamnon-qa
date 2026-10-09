"""Hồi quy S1 phần ảnh và in: ảnh người đón ở trang giao bé (không bấm giao), đăng ảnh lớp (caption 'QA S1'), in phiếu thu."""
import os,re,io,sys,requests
from PIL import Image
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
from playwright.sync_api import sync_playwright
W="https://mamnon-web.vercel.app"; B="https://mamnon-api.onrender.com/api/v1"; S="/workspace/stg/s1"; R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:300]));print(R[-1],flush=True)
cr=lambda k: os.environ[k].split(":",1)
def tok(k): u,p=cr(k); return {"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":p}).json()["accessToken"]}
img=io.BytesIO(); Image.new("RGB",(640,480),(80,160,220)).save(img,"JPEG"); open("/tmp/qa_s1.jpg","wb").write(img.getvalue())
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    # 1. Ảnh ở trang giao bé
    c=b.new_context(viewport={"width":390,"height":844}); p=c.new_page(); errs=[]; p.on("pageerror",lambda e: errs.append(str(e)[:150]))
    login_ui(p,W,*cr("SG"),consent=None); p.goto(W+"/pickups"); p.wait_for_timeout(5000)
    links=p.locator("[data-testid=handover-link]"); rec("PK-00 /pickups có danh sách giao bé",links.count()>0,f"{links.count()} bé")
    done=False
    for i in range(min(links.count(),12)):
        p.goto(W+"/pickups"); p.wait_for_timeout(3500); l=p.locator("[data-testid=handover-link]").nth(i); l.click(); p.wait_for_timeout(4000)
        inp=p.locator("[data-testid=handover-photo-input]")
        if inp.count() and p.locator("[data-testid=handover-done]").count()==0:
            ups=[]; p.on("response",lambda r: ups.append((r.request.method,r.url.split('/api/v1')[-1],r.status)) if r.request.method in("POST","PUT","PATCH") else None)
            inp.first.set_input_files("/tmp/qa_s1.jpg"); p.wait_for_timeout(6000)
            p.screenshot(path=f"{S}/PK-photo-390.png",full_page=True)
            ims=p.eval_on_selector_all("[data-testid=handover-detail] img","els=>els.map(e=>[e.src.slice(0,60),e.naturalWidth])")
            rec("PK-01 chọn ảnh ở trang giao bé: tải lên thành công",any(s<300 for _,_,s in ups) and not [x for x in ups if x[2]>=400],ups)
            rec("PK-02 ảnh hiện trong khung (naturalWidth>0)",any(w>0 for _,w in ims),ims)
            p.reload(); p.wait_for_timeout(5000); ims2=p.eval_on_selector_all("[data-testid=handover-detail] img","els=>els.map(e=>[e.src.slice(0,60),e.naturalWidth])")
            rec("PK-03 tải lại trang vẫn thấy ảnh (cùng bản deploy)",any(w>0 for _,w in ims2),ims2); done=True; break
    if not done: rec("PK-01 tìm được bé chưa giao có ô chụp ảnh",False,"không có")
    rec("PK-04 không có lỗi JS",not errs,errs[:3]); c.close()
    # 2. Đăng ảnh lớp
    c=b.new_context(viewport={"width":390,"height":844}); p=c.new_page(); errs=[]; p.on("pageerror",lambda e: errs.append(str(e)[:150]))
    login_ui(p,W,*cr("SG"),consent=None); p.goto(W+"/photos"); p.wait_for_timeout(5000)
    p.locator("[data-testid=file-input]").first.set_input_files("/tmp/qa_s1.jpg"); p.wait_for_timeout(3000)
    if p.locator("[data-testid=caption]").count(): p.fill("[data-testid=caption]","QA S1 – ảnh test, sẽ xoá")
    for _ in range(5):
        if p.locator("[data-testid=btn-drop-flagged]").count() and p.locator("[data-testid=btn-drop-flagged]").first.is_visible(): break
        hk=p.locator("[data-testid=btn-hide-kid]")
        if hk.count() and hk.first.is_visible(): hk.first.click(); p.wait_for_timeout(600)
        else: break
    post=p.locator("[data-testid=btn-post]"); pt=post.inner_text() if post.count() else ""
    if post.count() and post.is_enabled():
        post.click(); p.wait_for_timeout(8000)
        ok=p.locator("[data-testid=post-ok]").count()>0; p.screenshot(path=f"{S}/PH-post-390.png",full_page=True)
        rec("PH-01 đăng ảnh lớp thành công",ok,p.inner_text("main")[:200])
    else: rec("PH-01 nút Đăng bấm được",False,pt)
    rec("PH-02 không có lỗi JS",not errs,errs[:3]); c.close()
    # 3. In phiếu thu
    vid="43889ca4-5502-4444-84bf-5371e6c15ad4"
    c=b.new_context(viewport={"width":1280,"height":900}); p=c.new_page(); errs=[]; p.on("pageerror",lambda e: errs.append(str(e)[:150]))
    login_ui(p,W,*cr("SA"),consent=None)
    if vid:
        p.add_init_script("window.__printed=0;window.print=()=>{window.__printed++}")
        p.goto(W+f"/fees/receipt/{vid}"); p.wait_for_timeout(6000)
        sn=p.locator("[data-testid=print-school-name]"); amt=p.locator("[data-testid=print-amount]")
        rec("RC-01 phiếu thu hiện tên trường và số tiền",sn.count()>0 and amt.count()>0,(sn.first.inner_text() if sn.count() else "", amt.first.inner_text() if amt.count() else "", p.url))
        bp=p.locator("[data-testid=btn-print]")
        if bp.count(): bp.first.click(); p.wait_for_timeout(1500)
        rec("RC-02 bấm In gọi lệnh in của trình duyệt",p.evaluate("window.__printed")>0,f"btn={bp.count()}")
        p.emulate_media(media="print"); p.screenshot(path=f"{S}/RC-receipt-print.png",full_page=True)
    else: rec("RC-00 tìm được phiếu thu có sẵn",False,"không có payment")
    rec("RC-03 không có lỗi JS",not errs,errs[:3]); c.close(); b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
