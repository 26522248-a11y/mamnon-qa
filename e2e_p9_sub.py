"""P9 (nhánh design/p9-sub): thẻ '↔ <ngày> <cô> trông bé X' ở trang đầu PH, từ thông báo substitute_teacher. Khổ 390px.
Chạy: python e2e_p9_sub.py [WEB=http://localhost:3008]  – ph1 (Mầm 1, có trông thay 12/10 Cô Hồng buổi sáng), ph2 (Chồi 1). Chỉ đọc; dùng page.route để giả lập thông báo."""
import sys,re,json,datetime
from playwright.sync_api import sync_playwright
from qa_login import login_ui
U=sys.argv[1] if len(sys.argv)>1 else "http://localhost:3008"; S="/workspace/qa/shots/p9"; import os; os.makedirs(S,exist_ok=True); R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:260])); print(R[-1],flush=True)
T=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=7)).date()
NOTIF=re.compile(r"/api/v1/notifications\?limit=50")
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); V={"width":390,"height":844}
    def page(u):
        c=b.new_context(viewport=V); p=c.new_page(); login_ui(p,U,u,"123456",consent=True); return c,p
    c,p=page("ph1"); p.goto(U+"/today"); p.wait_for_timeout(4000)
    card=p.locator("[data-testid=today-substitute]"); txt=card.inner_text() if card.count() else ""; p.screenshot(path=S+"/P9-ph1-390.png",full_page=True)
    rec("P9-01 có thẻ '↔ Thứ Hai 12/10 Cô Hồng trông bé An'","↔ Thứ Hai 12/10 Cô Hồng trông bé An" in txt,txt.replace("\n"," | "))
    blk=re.search(r"↔ Thứ Hai 12/10[^\n]*\n?[^\n]*",txt); rec("P9-02 thẻ 12/10 nói rõ 'buổi sáng'",bool(blk) and "buổi sáng" in blk.group(0),blk.group(0).replace("\n"," | ") if blk else "")
    if card.count():
        bg=card.locator(".card").first.evaluate("e=>getComputedStyle(e).borderLeftColor")
        rec("P9-03 thẻ màu peach (viền trái)",bg.replace(" ","")=="rgb(255,138,76)",bg)
        y=lambda s:p.locator(s).first.bounding_box()["y"]; rec("P9-04 nằm trên ô điểm danh",y("[data-testid=today-substitute]")<y("[data-testid=tile-attendance]"),f"thẻ y={y('[data-testid=today-substitute]')} ô điểm danh y={y('[data-testid=tile-attendance]')}")
    rec("P9-05 thẻ 'Hôm nay' 10/10 (trông thay đã bị XOÁ) không nên hiện","Hôm nay" not in txt,"thẻ lấy từ thông báo, không kiểm tra trông thay còn hay không: "+txt.replace("\n"," | ")[:120])
    rec("OVF[390] ph1 /today",p.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=0)
    kid_cls=p.evaluate("async()=>{const r=await fetch('/api/v1/children',{headers:{Authorization:'Bearer '+(localStorage.getItem('accessToken')||'')}});return r.status}")
    def fake(items):
        def h(rt): rt.fulfill(status=200,content_type="application/json",body=json.dumps({"items":items,"total":len(items),"unreadCount":0}))
        p.unroute(NOTIF); p.route(NOTIF,h); p.goto(U+"/today"); p.wait_for_timeout(3500)
        return p.locator("[data-testid=today-substitute]").inner_text() if p.locator("[data-testid=today-substitute]").count() else ""
    y_=(T-datetime.timedelta(1)).isoformat(); f_=(T+datetime.timedelta(3)).isoformat()
    n=lambda i,d,cls="05e9ffd9-1e38-4a22-a6f4-487417040c29",nm="Cô Test":{"id":i,"type":"substitute_teacher","data":{k:v for k,v in {"substitutionId":i,"classId":cls,"date":d,"session":"full","substituteName":nm}.items() if v is not None}}
    t=fake([n("a",y_,nm="Cô Hôm Qua")]); rec("P9-06 ngày đã qua không hiện","Hôm Qua" not in t,t)
    t=fake([n("b",f_,cls="e68aa771-eee9-471b-9968-e02c3c9db31f",nm="Cô Lớp Khác")]); rec("P9-07 thông báo của lớp khác (classId khác) không hiện","Lớp Khác" not in t,t)
    t=fake([n("c",f_,cls=None,nm="Cô Không Lớp")]); rec("P9-08 [thông tin] thông báo THIẾU classId: hiện cho mọi bé (không lọc được lớp)",True,f"hiện thẻ: {'Không Lớp' in t} → {t[:100]}")
    c.close()
    c,p=page("ph2"); p.goto(U+"/today"); p.wait_for_timeout(4000); t=p.locator("[data-testid=today-substitute]").count()
    rec("P9-09 PH lớp khác (ph2, Chồi 1) không thấy thẻ trông thay Mầm 1",t==0,p.locator("[data-testid=today-substitute]").inner_text() if t else ""); p.screenshot(path=S+"/P9-ph2-390.png")
    c.close(); b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
