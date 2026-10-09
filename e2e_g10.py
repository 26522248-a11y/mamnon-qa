"""G10: câu lỗi tiếng Việt. Giả lập lỗi bằng page.route (không dừng backend): abort, 500, 403/404 câu tiếng Anh, 400 câu tiếng Việt giữ nguyên.
Màn: GV lưu điểm danh, PH báo nghỉ (trang Hôm nay), Kế toán/Admin danh sách học phí (/fees). Chạy: python e2e_g10.py [WEB]   Tài khoản qua biến môi trường G10_GV / G10_PH / G10_ADMIN = "u:p" (mặc định local gv1/ph1/admin, mk 123456); G10_GV=skip để bỏ màn đó."""
import sys,re,os,json
from playwright.sync_api import sync_playwright
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from qa_login import login_ui
U=(sys.argv+[None])[1] or "http://localhost:3002";ACC={k:os.environ.get("G10_"+k,d) for k,d in [("GV","gv1:123456"),("PH","ph1:123456"),("ADMIN","admin:123456")]};S="/workspace/g10-shots";os.makedirs(S,exist_ok=True);R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:220]));print(R[-1],flush=True)
NET="Không kết nối được máy chủ. Kiểm tra mạng rồi thử lại nhé."; BUSY="Máy chủ đang bận hoặc gặp sự cố"
VI="Bé đã được điểm danh bởi cô khác (QA)"
CASES=[("abort",None,NET),("500",{"status":500,"body":{"statusCode":500,"message":"Internal server error"}},BUSY),
       ("403",{"status":403,"body":{"statusCode":403,"message":"Forbidden resource"}},"Bạn không có quyền làm việc này."),
       ("404",{"status":404,"body":{"statusCode":404,"message":"Not Found"}},"Không tìm thấy dữ liệu, có thể đã bị xoá."),
       ("400vi",{"status":400,"body":{"statusCode":400,"message":VI}},VI)]
ENG=re.compile(r"Failed to fetch|Internal server error|Forbidden|Not Found|NetworkError|Load failed|TypeError")
def handler(case,method):
    def h(r):
        if r.request.method!=method: return r.continue_()
        if case[1] is None: return r.abort()
        r.fulfill(status=case[1]["status"],content_type="application/json",body=json.dumps(case[1]["body"]))
    return h
def run(p,name,pat,method,prep,act,read):
    for c in CASES:
        prep(); p.route(pat,handler(c,method)); act(); p.wait_for_timeout(1500); t=read(); p.screenshot(path=f"{S}/{name}-{c[0]}.png"); p.unroute(pat)
        rec(f"G10 {name} {c[0]} → '{c[2][:45]}'",c[2] in t and not ENG.search(t),t)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    # 1) GV điểm danh (route chặn PUT → không ghi dữ liệu thật)
    if ACC["GV"]!="skip":
     p=b.new_context(viewport={"width":390,"height":844}).new_page(); login_ui(p,U,*ACC["GV"].split(":",1),consent=None)
     def prep1(): p.goto(U+"/attendance"); p.wait_for_selector("[data-testid=att-row]"); p.wait_for_timeout(1200); p.locator("[data-testid=att-row]").first.locator("button").first.click()
     run(p,"attendance",re.compile(r".*/classes/[^/]+/attendance$"),"PUT",prep1,lambda:p.click("[data-testid=att-save]"),lambda:p.locator("[data-testid=att-msg]").inner_text() if p.locator("[data-testid=att-msg]").count() else "")
     o=p.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth"); rec("OVF[390] attendance khung lỗi",o<=0,o)
     p.context.close()
    # 2) PH báo nghỉ hôm nay
    if ACC["PH"]!="skip":
     p=b.new_context(viewport={"width":390,"height":844}).new_page(); login_ui(p,U,*ACC["PH"].split(":",1))
     def prep2():
         p.goto(U+"/today"); p.wait_for_timeout(2500); p.locator("button:has-text('Con nghỉ hôm nay')").first.click(); p.wait_for_timeout(800)
     def act2(): p.locator("[data-testid=absence-dialog] button").filter(has_text=re.compile("Báo nghỉ|Xác nhận|Gửi")).last.click()
     run(p,"ph-absence",re.compile(r".*/children/[^/]+/absences$"),"POST",prep2,act2,lambda:p.locator("[data-testid=absence-dialog]").inner_text() if p.locator("[data-testid=absence-dialog]").count() else p.inner_text("body"))
     o=p.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth"); rec("OVF[390] today hộp báo nghỉ lỗi",o<=0,o)
     p.context.close()
    # 3) Admin danh sách hoá đơn (/fees, tab hoá đơn)
    if ACC["ADMIN"]!="skip":
     p=b.new_context(viewport={"width":390,"height":844}).new_page(); login_ui(p,U,*ACC["ADMIN"].split(":",1),consent=None)
     def prep3(): pass
     def act3(): p.goto(U+"/fees"); p.wait_for_timeout(2500)
     run(p,"fees-admin",re.compile(r".*/api/v1/(debts|invoices)\?.*"),"GET",prep3,act3,lambda:p.inner_text("main"))
     p.context.close()
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
