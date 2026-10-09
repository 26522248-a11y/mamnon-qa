from playwright.sync_api import sync_playwright
U="http://localhost:3000"
with sync_playwright() as pw:
    b=pw.chromium.launch();p=b.new_page(viewport={"width":390,"height":844})
    p.goto(U+"/login");p.fill("input[placeholder='Tên đăng nhập']","admin");p.fill("input[type=password]","123456");p.click("button:has-text('Đăng nhập')");p.wait_for_timeout(2500)
    p.goto(U+"/holidays");p.wait_for_timeout(2500)
    p.click("text=Đóng cửa đột xuất");p.wait_for_timeout(2500)
    t=p.inner_text("body");print("có khung gọi điện:","gọi điện" in t,"| nhãn chưa có SĐT:","Chưa có số điện thoại" in t,"| tel links:",p.locator("a[href^='tel:']").count())
    p.screenshot(path="/workspace/qa/emg1.png")
    x=p.locator("text=/Xem tất cả/").first;print("có Xem tất cả:",x.count()>0)
    if x.count(): x.click();p.wait_for_timeout(1000)
    btn=p.locator("button:has-text('Đóng cửa ngay')").first;bb=btn.bounding_box()
    print("nút Đóng cửa ngay:",bb,"trong màn:",bb and bb["y"]>=0 and bb["y"]+bb["height"]<=844,"disabled khi chưa lý do:",btn.is_disabled())
    print("QA Không SĐT:","QA Không SĐT" in p.inner_text("body"));p.wait_for_timeout(1500);print("sau Xem tất cả, nhãn chưa SĐT:","Chưa có số điện thoại" in p.inner_text("body"))
    p.screenshot(path="/workspace/qa/emg2.png")
    h=p.locator("button:has-text('Hủy')").last.bounding_box();print("nút Hủy trong màn:",h and h["y"]+h["height"]<=844)
    p.keyboard.press("Escape")
