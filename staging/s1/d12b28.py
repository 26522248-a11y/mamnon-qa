"""D1 (thẻ 'Bé đã được đón' ẩn khung ảnh khi ảnh mất), D2 (trang đầu PH sau khi đón), B28 (/pickups không 401). An đã được đón 02:20, ảnh mất sau deploy 2:44."""
import os,re,sys
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
from playwright.sync_api import sync_playwright
W="https://mamnon-web.vercel.app"; S="/workspace/stg/s1"; R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:260]));print(R[-1],flush=True)
cr=lambda k: os.environ[k].split(":",1)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    c=b.new_context(viewport={"width":390,"height":844}); p=c.new_page(); errs=[]; p.on("pageerror",lambda e: errs.append(str(e)[:150]))
    login_ui(p,W,*cr("SP"),consent=True); p.goto(W+"/today"); p.wait_for_timeout(6000); t=p.inner_text("main"); p.screenshot(path=f"{S}/D2-today-390.png",full_page=True)
    rec("D2-01 PH: bé đã đón → không còn ô 'Bé đã đến lớp' (tile-attendance)",p.locator("[data-testid=tile-attendance]").count()==0,p.locator("[data-testid=tile-attendance]").count())
    rec("D2-02 không còn nút 'Con nghỉ hôm nay'",p.locator("[data-testid=btn-absent-today]").count()==0 and "Con nghỉ hôm nay" not in t)
    m=re.findall(r"[^\n]*đón lúc[^\n]*",t); rec("D2-03 có dòng 'Đã được … đón lúc …' (1 lần)",len([x for x in m if "Đã được" in x])==1,m)
    p.goto(W+"/notifications"); p.wait_for_timeout(5000); p.screenshot(path=f"{S}/D1-notif-390.png",full_page=True)
    card=p.get_by_text(re.compile("đã được đón")).first
    if card.count(): card.click(); p.wait_for_timeout(4000)
    p.screenshot(path=f"{S}/D1-detail-390.png",full_page=True); t=p.inner_text("main")
    rec("D1-01 ảnh mất → không có khung ảnh/ 'Chưa có ảnh' trong thẻ đã đón",p.locator("[data-testid=picked-up-photo]").count()==0 and "Chưa có ảnh" not in t,{"photo":p.locator("[data-testid=picked-up-photo]").count(),"url":p.url})
    rec("D1-02 vẫn có nội dung đón + nút Gọi trường","đón lúc" in t and "Gọi trường" in t,re.findall(r"[^\n]*(?:đón lúc|Gọi trường)[^\n]*",t)[:3])
    rec("D-JS không lỗi JS (PH)",not errs,errs[:3]); c.close()
    for acc in ["SG","SA","SK"]:
        c=b.new_context(viewport={"width":390,"height":844}); p=c.new_page(); bad=[]
        p.on("response",lambda r: bad.append((r.status,r.url.split('/api/v1')[-1])) if r.status==401 else None)
        login_ui(p,W,*cr(acc),consent=None); bad.clear(); p.goto(W+"/pickups"); p.wait_for_timeout(5000)
        p.reload(); p.wait_for_timeout(5000)
        q=c.new_page(); q.on("response",lambda r: bad.append((r.status,r.url.split('/api/v1')[-1])) if r.status==401 else None); q.goto(W+"/pickups"); q.wait_for_timeout(5000)
        rec(f"B28 {acc} /pickups (tải, tải lại, tab mới) không có 401",not bad,bad); c.close()
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
