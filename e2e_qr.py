from playwright.sync_api import sync_playwright
import requests
B="http://localhost:3001/api/v1";U="http://localhost:3000"
def tk(u): return {"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"]}
K,P1=tk("ketoan"),tk("ph1")
j=requests.get(B+"/children",headers=P1).json();kid=(j.get("items",j))[0]["id"]
I=requests.post(B+"/invoices",json={"childId":kid,"period":"2027-07","dueDate":"2027-07-10","lines":[{"description":"QA QR UI","unitPrice":800000}]},headers=K).json()["id"]
def login(p,u):
    p.goto(U+"/login");p.fill("input[placeholder='Tên đăng nhập']",u);p.fill("input[type=password]","123456");p.click("button:has-text('Đăng nhập')");p.wait_for_timeout(2500)
try:
  with sync_playwright() as pw:
    b=pw.chromium.launch();p=b.new_page(viewport={"width":390,"height":844});login(p,"ph1");p.goto(U+"/fees");p.wait_for_timeout(3000);p.click("text=Tháng 7/2027");p.wait_for_timeout(2000)
    t=p.inner_text("body");print("Dữ liệu mẫu:","Dữ liệu mẫu" in t,"| 800.000:","800.000" in t,"| nút Tôi đã chuyển:",p.locator("button:has-text('Tôi đã chuyển')").count(),"| img/canvas QR:",p.locator("svg, canvas, img[alt*='QR']").count())
    p.screenshot(path="/workspace/qa/qr_ph1.png",full_page=True)
    btn=p.locator("button:has-text('Tôi đã chuyển')").first
    if btn.count():
        btn.click();p.wait_for_timeout(1500)
        cf=p.locator("[role=dialog] button:has-text('Tôi đã chuyển'), [role=dialog] button:has-text('Xác nhận'), [role=dialog] button:has-text('Gửi')")
        if cf.count(): cf.first.click();p.wait_for_timeout(2000)
        t=p.inner_text("body");print("sau bấm: đang kiểm tra:","đang kiểm tra" in t.lower() or "chờ" in t.lower(),"| nút còn:",p.locator("button:has-text('Tôi đã chuyển')").count())
        p.screenshot(path="/workspace/qa/qr_ph1_pending.png",full_page=True)
    k=b.new_page();login(k,"ketoan");k.goto(U+"/fees");k.wait_for_timeout(3000);print("kế toán thấy hàng chờ:","chờ" in k.inner_text("body").lower());k.screenshot(path="/workspace/qa/qr_kt.png",full_page=True)
finally:
    print("void",requests.post(B+f"/invoices/{I}/void",json={"reason":"QA dọn"},headers=K).status_code)
