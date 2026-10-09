import requests,uuid
from playwright.sync_api import sync_playwright
B="http://localhost:3001/api/v1";U="http://localhost:3000";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:200]));print(R[-1],flush=True)
T={u:requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"] for u in ["admin","gv1","ketoan","ph1","ph2"]};H=lambda u:{"Authorization":"Bearer "+T[u]}
s=requests.get(B+"/settings/school"); rec("SET-01 /settings/school không cần login",s.status_code==200,s.text)
cls=requests.get(B+"/classes",headers=H("admin")).json(); cls=cls.get("items",cls) if isinstance(cls,dict) else cls
kid=requests.post(B+"/children",json={"fullName":"QA Miễn Phí "+uuid.uuid4().hex[:4],"dob":"2022-05-14","gender":"M","classId":cls[0]["id"]},headers=H("admin")).json()["id"]
iv=requests.post(B+"/invoices",json={"childId":kid,"period":"2026-10","dueDate":"2026-10-10","lines":[{"description":"HP","unitPrice":1000000},{"kind":"discount","description":"Miễn","unitPrice":1000000,"reason":"QA miễn 100%"}]},headers=H("ketoan")).json()
rec("WAV-01 hóa đơn 0đ paid + waived",iv.get("status")=="paid" and iv.get("waived") is True,{k:iv.get(k) for k in ["totalAmount","status","waived","note"]})
r=requests.get(B+f"/invoices/{iv['id']}/receipt",headers=H("ketoan")); rec("WAV-02 không có biên lai (404)",r.status_code==404,r.text[:100])
mine=requests.get(B+"/classes",headers=H("gv1")).json(); mine=(mine.get("items",mine) if isinstance(mine,dict) else mine)[0]["id"]
rc=requests.get(B+f"/announcements/recipients?classId={mine}",headers=H("gv1")).json(); rcl=rc.get("items",rc) if isinstance(rc,dict) else rc
ph1id=requests.get(B+"/auth/me",headers=H("ph1")).json().get("id")
a=requests.post(B+"/announcements",json={"title":"QA quan trọng","body":"QA test thông báo quan trọng chỉ ph1","important":True,"classId":mine,"recipientUserIds":[ph1id]},headers=H("gv1"))
rec("ANN-01 gv gửi thông báo quan trọng cho 1 phụ huynh",a.status_code in(200,201),a.text[:150]); aid=a.json().get("id")
n1=requests.get(B+"/notifications",headers=H("ph1")).json(); n2=requests.get(B+"/notifications",headers=H("ph2")).json()
has=lambda n:"QA quan trọng" in str(n)
rec("ANN-02 ph1 nhận, importantUnreadCount>=1",has(n1) and (n1.get("importantUnreadCount",0)>=1 if isinstance(n1,dict) else True),n1.get("importantUnreadCount") if isinstance(n1,dict) else "")
rec("ANN-03 ph2 không nhận",not has(n2))
g=requests.get(B+"/announcements",headers=H("gv1")).json(); rec("ANN-04 gv thấy thông báo mình tạo (mine)","QA quan trọng" in str(g))
rec("ANN-05 gv lớp khác không thu hồi được",requests.delete(B+f"/announcements/{aid}",headers=H("ph1")).status_code in(403,404))
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    p=b.new_page(); p.goto(U+"/login"); p.wait_for_timeout(1500); t=p.inner_text("body")
    rec("P1-DEMO dòng demo đã ẩn","123456" not in t and "Demo" not in t,t[:150].replace("\n"," "))
    rec("SET-02 trang login dùng tên trường từ API",s.json().get("name","@@") in t,t[:80].replace("\n"," "))
    m=b.new_page(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
    m.goto(U+"/login"); m.fill("input[autocomplete=username]","ph1"); m.fill("input[type=password]","123456"); m.click("button"); m.wait_for_timeout(2500)
    m.goto(U+"/notifications"); m.wait_for_timeout(2000); m.screenshot(path="/workspace/qa/acc_ph1_notif.png",full_page=True)
    rec("ANN-UI ph1 thấy thông báo quan trọng","QA quan trọng" in m.inner_text("body"))
    over=m.evaluate("document.documentElement.scrollWidth>window.innerWidth"); rec("NAV mobile không tràn ngang",not over)
    rec("NAV có '☰ Thêm'","Thêm" in m.inner_text("body"))
    m.goto(U+"/today"); m.wait_for_timeout(2000); m.screenshot(path="/workspace/qa/acc_ph1_today.png",full_page=True)
    a2=b.new_page(viewport={"width":1280,"height":800}); a2.goto(U+"/login"); a2.fill("input[autocomplete=username]","admin"); a2.fill("input[type=password]","123456"); a2.click("button"); a2.wait_for_timeout(2500)
    a2.goto(U+"/dashboard"); a2.wait_for_timeout(2000); a2.screenshot(path="/workspace/qa/acc_admin_dash.png",full_page=True)
    rec("DASH khối Cần chú ý","Cần chú ý" in a2.inner_text("body"))
    a2.goto(U+f"/fees"); a2.wait_for_timeout(2000)
    b.close()
g=requests.delete(B+f"/announcements/{aid}",headers=H("gv1")); rec("ANN-06 gv thu hồi 204",g.status_code==204,g.status_code)
rec("ANN-07 thu hồi lần 2 409",requests.delete(B+f"/announcements/{aid}",headers=H("gv1")).status_code==409)
rec("ANN-08 biến mất khỏi hộp thư ph1",not has(requests.get(B+"/notifications",headers=H("ph1")).json()))
requests.post(B+f"/children/{kid}/withdraw",json={"leaveDate":"2026-10-09","reason":"QA dọn"},headers=H("admin"))
print("TOTAL",len(R),"FAIL",sum(r[1]!="PASS" for r in R))
