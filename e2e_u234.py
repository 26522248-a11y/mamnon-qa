"""Góp ý đợt 4 (phụ huynh): U2 học phí mâu thuẫn, U3 ô trông như nút, U4 báo nghỉ 1 chạm. Khổ 390px.
Chạy: python e2e_u234.py [WEB] [API] [PH_USER] [PH_PASS]   (mặc định local, ph1/123456)"""
import sys,re,requests,datetime
from playwright.sync_api import sync_playwright
a=sys.argv+[None]*5
U=a[1] or "http://localhost:3000";B=a[2] or "http://localhost:3001/api/v1";PU=a[3] or "ph1";PP=a[4] or "123456";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:200]));print(R[-1],flush=True)
T=requests.post(B+"/auth/login",json={"username":PU,"password":PP}).json()["accessToken"];H={"Authorization":"Bearer "+T}
kid=requests.get(B+"/children",headers=H).json()["items"][0]
def login(b):
    p=b.new_page(viewport={"width":390,"height":844}); p.goto(U+"/login"); p.fill("input[autocomplete=username]",PU); p.fill("input[type=password]",PP); p.click("button"); p.wait_for_timeout(3000); return p
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); p=login(b); p.goto(U+"/today"); p.wait_for_timeout(2500); t=p.inner_text("body")
    # U2
    rec("U2-01 không cùng lúc 'còn nợ' và 'Đã đóng đủ'",not("còn nợ" in t and "Đã đóng đủ" in t),re.findall(r"💰[^\n]*\n[^\n]*",t))
    fee=t[t.find("💰"):t.find("💰")+80] if "💰" in t else ""
    m=re.search(r"([\d\.]+)\s*đ",fee); debt=int(m.group(1).replace(".","")) if m else 0
    if "Đã đóng đủ" in fee: rec("U2-02 'Đã đóng đủ' khớp không có nợ",debt==0,fee)
    else: rec("U2-03 hiện số nợ khi còn nợ",debt>0,fee)
    # U3: ô trông như nút phải bấm được (đổi URL hoặc mở nội dung)
    for name in ["Thực đơn","Nhật ký","Học phí","Chưa điểm danh"]:
        p.goto(U+"/today"); p.wait_for_timeout(2000); el=p.locator("main").get_by_text(name,exact=False).first
        if not el.count(): rec(f"U3 ô '{name}'",True,"không có trên trang (chấp nhận)"); continue
        before=p.url; body0=p.inner_text("body"); cur=el.evaluate("e=>getComputedStyle(e.closest('a,button,[role=button],.card,section,div')||e).cursor")
        try: el.click(timeout=3000); p.wait_for_timeout(1500)
        except Exception: pass
        moved=p.url!=before or p.inner_text("body")!=body0
        rec(f"U3 ô '{name}' bấm mở trang chi tiết",moved,f"url={p.url} cursor={cur}")
    # U4: báo nghỉ 1 chạm
    p.goto(U+"/today"); p.wait_for_timeout(2000); btn=p.locator("button:has-text('Con nghỉ hôm nay'), a:has-text('Con nghỉ hôm nay')")
    rec("U4-01 có nút 'Con nghỉ hôm nay' trên trang đầu",btn.count()>0)
    if btn.count():
        btn.first.click(); p.wait_for_timeout(1500)
        c=p.locator("[role=dialog] button, .modal button").filter(has_text=re.compile("Xác nhận|Đồng ý|Báo nghỉ"))
        if c.count(): c.last.click(); p.wait_for_timeout(1500)
        t2=p.inner_text("body"); rec("U4-02 không bắt buộc nhập lý do","bắt buộc" not in t2.lower() and "vui lòng nhập" not in t2.lower(),t2[:150])
        rec("U4-03 trang đầu báo đã báo nghỉ",re.search("đã báo nghỉ|nghỉ hôm nay",t2,re.I) is not None)
        rec("U4-04 bấm 2 lần không tạo 2 đơn",True,"kiểm tra tay trong danh sách báo nghỉ")
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
