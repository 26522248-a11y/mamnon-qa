"""Góp ý giáo viên: G1 'Đã lưu' sau điểm danh, G4 giao bé không bắt tick đối chiếu (+SĐT, 📞, nhắc chụp ảnh lần đón đầu),
G5 trang đầu GV /home (teacher-home, btn-checkin, home-att, home-meds) + 'Ca ngày', U11 nút PH '🏠 Con nghỉ hôm nay' (peach, ~56px). Khổ 390px.
Chạy: python e2e_g145.py [WEB] [API] [GV u:p] [ADMIN u:p] [PH u:p]  (mặc định local gv1/admin/ph1; PH phải có con ở lớp của GV).
[ghi] điểm danh 1 bé 'có mặt', tạo 1 người đón 'QA G4 …' đã duyệt. Không bấm giao bé."""
import sys,re,uuid,datetime,requests
from playwright.sync_api import sync_playwright
a=sys.argv+[None]*6
U=a[1] or "http://localhost:3000";B=a[2] or "http://localhost:3001/api/v1"
import os; S="/workspace/qa/shots/g145"; os.makedirs(S,exist_ok=True)
GV,AD,PH=[(x or d).split(":",1) for x,d in zip(a[3:6],["gv1:123456","admin:123456","ph1:123456"])];R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:200]));print(R[-1],flush=True)
tok=lambda u,p:requests.post(B+"/auth/login",json={"username":u,"password":p}).json()["accessToken"]
A={"Authorization":"Bearer "+tok(*AD)};P={"Authorization":"Bearer "+tok(*PH)}
d=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=7)).date().isoformat()
kid=requests.get(B+"/children",headers=P).json()["items"][0];cls=kid.get("classId") or requests.get(B+f"/children/{kid['id']}",headers=A).json()["classId"]
requests.put(B+f"/classes/{cls}/attendance",headers=A,json={"date":d,"items":[{"childId":kid["id"],"status":"present"}]})
aid=[i for i in requests.get(B+f"/classes/{cls}/attendance",headers=A,params={"date":d}).json()["items"] if i["childId"]==kid["id"]][0]["attendanceId"]
pn="QA G4 "+uuid.uuid4().hex[:4]; PHN="0909"+str(uuid.uuid4().int)[:6]
pid=requests.post(B+f"/children/{kid['id']}/authorized-pickers",headers=P,data={"fullName":pn,"phone1":PHN}).json()["id"]
requests.post(B+f"/authorized-pickers/{pid}/approve",headers=A,json={})
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); g=b.new_page(viewport={"width":390,"height":844})
    g.goto(U+"/login",timeout=90000); g.fill("input[autocomplete=username]",GV[0]); g.fill("input[type=password]",GV[1]); g.click("button"); g.wait_for_timeout(4000)
    # G5: trang đầu sau đăng nhập là /home có Vào ca/Ra ca
    home=g.url; g.wait_for_selector("[data-testid=teacher-home]",timeout=15000) if "/home" in home else None; t=g.inner_text("body")
    rec("G5-00 GV đăng nhập xong vào /home",home.split("?")[0].rstrip("/").endswith("/home"),home)
    for tid in ["teacher-home","btn-checkin","home-att","home-meds"]:
        rec(f"G5-T {tid} hiển thị",g.locator(f"[data-testid={tid}]").count()>0 and g.locator(f"[data-testid={tid}]").first.is_visible())
    bt=g.locator("[data-testid=btn-checkin]"); bt=bt.first.inner_text() if bt.count() else ""
    rec("G5-01 trang đầu GV có nút Vào ca/Ra ca",re.search(r"Vào ca|Ra ca|Đã ra ca",t) is not None,f"btn-checkin='{bt}'")
    rec("G5-01b ô Điểm danh lớp / Dặn thuốc có số liệu (không kẹt 'Đang tải…')","Đang tải" not in g.locator("[data-testid=home-att]").inner_text()+g.locator("[data-testid=home-meds]").inner_text() if g.locator("[data-testid=home-meds]").count() else False,
        (g.locator("[data-testid=home-att]").inner_text() if g.locator("[data-testid=home-att]").count() else "")+" | "+(g.locator("[data-testid=home-meds]").inner_text() if g.locator("[data-testid=home-meds]").count() else ""))
    g.screenshot(path=S+"/G5-home-390.png",full_page=True)
    rec("G5-02a /home không có chữ 'Ca sáng'","Ca sáng" not in t)
    g.goto(U+"/staff"); g.wait_for_timeout(3000); t=g.inner_text("body")
    rec("G5-02 /staff không còn chữ 'Ca sáng'","Ca sáng" not in t)
    # G1: lưu điểm danh hiện 'Đã lưu'
    g.goto(U+"/attendance"); g.wait_for_timeout(3000)
    rows=g.locator("[data-testid=att-row]"); idx=[i for i in range(rows.count()) if "Chưa điểm" in rows.nth(i).inner_text()]
    if idx:
        rows.nth(idx[0]).click(); g.wait_for_timeout(500); g.click("[data-testid=att-save]")
        seen=False
        for _ in range(10):
            g.wait_for_timeout(300)
            if "Đã lưu" in g.inner_text("body"): seen=True; break
        rec("G1-01 lưu điểm danh hiện '✓ Đã lưu'",seen)
        g.wait_for_timeout(3000); m=g.locator("[data-testid=att-msg]")
        mt=m.first.inner_text() if m.count() and m.first.is_visible() else ""; mc=m.first.get_attribute("class") if m.count() else ""
        rec("G1-02 sau ~3s vẫn còn khung mint '✓ Đã lưu điểm danh (1 bé)'",mt.startswith("✓ Đã lưu điểm danh (1 bé)") and "bg-mint" in (mc or ""),f"'{mt}' class={mc}")
    else: rec("G1-01 lưu điểm danh hiện '✓ Đã lưu'",False,"không còn bé 'Chưa điểm' để thử")
    # G4: giao bé không bắt tick đối chiếu; thẻ có SĐT, 📞, nhắc chụp ảnh lần đón đầu
    g.goto(U+f"/pickups/handover/{aid}"); g.wait_for_timeout(3500); t=g.inner_text("body")
    rec("G4-01 tiêu đề/nút dùng chữ 'Giao bé'","Giao bé" in t,t[:120])
    rec("G4-02 không còn 'đối chiếu ảnh và căn cước'","đối chiếu ảnh và căn cước" not in t.lower() and "căn cước" not in t.lower())
    card=g.locator("[data-card=handover]").filter(has_text=pn)
    rec("G4-03 người đón đã duyệt hiện thành thẻ giao ngay (Đúng người đón → bấm Đã giao bé)",card.count()==1 and ("Đúng người đón" in t or card.count()==1),f"thẻ={card.count()}; 'Đúng người đón' {'có' if 'Đúng người đón' in t else 'không'} trên trang")
    if card.count():
        c0=card.first; ct=c0.inner_text(); card.first.scroll_into_view_if_needed(); g.screenshot(path=S+"/G4-handover-390.png",full_page=True)
        rec("G4-05 thẻ có SĐT người đón",PHN in ct.replace(" ",""),ct.replace("\n"," | ")[:150])
        call=c0.locator("a[href^='tel:'],button").filter(has_text="📞")
        href=c0.locator("a[href^='tel:']"); rec("G4-06 có nút gọi nhanh 📞",call.count()>0 or href.count()>0,f"📞={call.count()} tel:={[href.nth(i).get_attribute('href') for i in range(href.count())]}")
        ft=c0.locator("[data-testid=handover-first-time]")
        rec("G4-07 nhắc 'Lần đón đầu, chụp ảnh giúp' cho người đón lần đầu",ft.count()>0 and ft.first.is_visible(),ft.first.inner_text() if ft.count() else "")
        gv=c0.locator("[data-testid=handover-give]")
        rec("G4-04 nút '✓ Đã giao bé' bấm được ngay, không có ô tick bắt buộc",gv.count()>0 and gv.first.is_enabled() and c0.locator("input[type=checkbox]").count()==0 and g.locator("[data-testid=handover-checked]").count()==0,
            f"give={gv.count()} enabled={gv.first.is_enabled() if gv.count() else None} checkbox={c0.locator('input[type=checkbox]').count()}")
    else:
        for n in ["G4-04 nút giao bấm được","G4-05 SĐT","G4-06 📞","G4-07 nhắc chụp ảnh lần đầu"]: rec(n,False,"không thấy thẻ người đón "+pn)
    # U11: PH thấy nút '🏠 Con nghỉ hôm nay' nền peach, cao ~56px (bé chưa điểm danh hôm nay)
    pc=b.new_context(viewport={"width":390,"height":844}); q=pc.new_page()
    q.goto(U+"/login",timeout=90000); q.fill("input[autocomplete=username]",PH[0]); q.fill("input[type=password]",PH[1]); q.click("button"); q.wait_for_timeout(4000)
    q.goto(U+"/today"); q.wait_for_timeout(3500); ab=q.locator("[data-testid=btn-absent-today]")
    if ab.count():
        st=ab.first.evaluate("e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return {bg:s.backgroundColor,h:r.height,w:r.width,fw:s.fontWeight,t:e.innerText}}"); q.screenshot(path=S+"/U11-today-390.png",full_page=True)
        rgb=[float(x) for x in re.findall(r"[\d.]+",st["bg"])[:3]]
        peach=len(rgb)==3 and rgb[0]>200 and rgb[0]>rgb[2]+40 and 90<rgb[1]<200
        rec("U11-01 nút '🏠 Con nghỉ hôm nay' nền peach","Con nghỉ hôm nay" in st["t"] and peach,st)
        rec("U11-02 nút cao ~56px (≥52)",52<=st["h"]<=64,f"h={st['h']}")
    else: rec("U11-01 nút '🏠 Con nghỉ hôm nay'",False,"không thấy btn-absent-today (bé có thể đã điểm danh có mặt) | "+q.inner_text("body")[:150])
    pc.close()
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
