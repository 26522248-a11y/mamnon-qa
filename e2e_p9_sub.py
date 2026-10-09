"""P9 (design/p9-sub, cf164c1+): thẻ '↔ <ngày> <cô> trông bé X' ở trang đầu PH, lấy từ GET /children/:id/substitutions (backend 23b8863+). Khổ 390px.
Chạy: python e2e_p9_sub.py [WEB=http://localhost:3008] [API=http://localhost:3001/api/v1]
Cần sẵn: trông thay 12/10 Mầm 1 Cô Hồng buổi sáng (đơn nghỉ đã duyệt của Cô Lan) – script KHÔNG đụng vào lượt này.
[ghi] tạo tạm: trông thay 13/10 (rồi xoá), đơn nghỉ Cô Lan 14/10 sáng duyệt + Cô Hồng (rồi huỷ đơn, xoá lượt), trông thay hôm qua (rồi xoá). PH lớp Mầm 1 sẽ nhận thông báo của các lượt tạm."""
import sys,re,datetime,requests
from playwright.sync_api import sync_playwright
from qa_login import login_ui
a=sys.argv+[None]*3; U=a[1] or "http://localhost:3008"; B=a[2] or "http://localhost:3001/api/v1"
S="/workspace/qa/shots/p9"; import os; os.makedirs(S,exist_ok=True); R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:260])); print(R[-1],flush=True)
H={u:{"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"]} for u in ["admin","gv1","gv2","gv3","ph1","ph2"]}
uid=lambda u:requests.get(B+"/auth/me",headers=H[u]).json()["id"]
T=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=7)).date(); iso=lambda d:d.isoformat()
k1=requests.get(B+"/children",headers=H["ph1"]).json()["items"][0]; k2=requests.get(B+"/children",headers=H["ph2"]).json()["items"][0]
C1=k1["classId"] if k1.get("classId") else requests.get(B+f"/children/{k1['id']}",headers=H["admin"]).json()["classId"]
first=k1["fullName"].split()[-1]; subs=lambda u,k:requests.get(B+f"/children/{k}/substitutions",headers=H[u])
shift=[x for x in requests.get(B+"/staff/shifts",headers=H["admin"]).json()["items"] if x["isActive"]][0]
def mk(d,sess="full"): r=requests.post(B+"/staff/substitutions",headers=H["admin"],json={"date":iso(d),"shiftId":shift["id"],"classId":C1,"substituteUserId":uid("gv3"),"absentUserId":uid("gv1"),"session":sess,"force":True}); return r
dl=lambda i:requests.delete(B+f"/staff/substitutions/{i}",headers=H["admin"]).status_code
nxt=lambda wd:T+datetime.timedelta((wd-T.weekday())%7 or 7)   # thứ trong tuần sắp tới (0=T2)
D12=datetime.date(2026,10,12) if T<=datetime.date(2026,10,12) else nxt(0)
# ── API quyền
r=subs("ph1",k1["id"]); it=r.json().get("items",[]) if r.ok else []
base=[x for x in it if x["date"]==iso(D12)]
rec("API-01 PH đọc trông thay của con mình → 200, có lượt 12/10 Cô Hồng buổi sáng",r.status_code==200 and any(x["substituteName"]=="Cô Hồng" and x["session"]=="morning" for x in base),f"{r.status_code} {it}")
r=subs("ph1",k2["id"]); rec("API-02 PH đọc trông thay của bé KHÔNG phải con mình → 403/404",r.status_code in (403,404),f"{r.status_code} {r.text[:80]}")
r=subs("ph2",k2["id"]); rec("API-03 PH lớp khác (ph2) đọc con mình → 200, không có lượt Mầm 1",r.status_code==200 and all(x.get("classId")!=C1 for x in r.json()["items"]),r.text[:120])
r=subs("gv1",k1["id"]); rec("API-04 GV chủ nhiệm đọc bé lớp mình → 200",r.status_code==200,r.status_code)
r=subs("gv2",k1["id"]); rec("API-05 GV lớp khác đọc bé Mầm 1 → 403",r.status_code==403,f"{r.status_code} {r.text[:80]}")
r=subs("admin",k1["id"]); rec("API-06 admin đọc → 200",r.status_code==200,r.status_code)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); V={"width":390,"height":844}
    c=b.new_context(viewport=V); p=c.new_page(); login_ui(p,U,"ph1","123456",consent=True)
    def card(): p.goto(U+"/today"); p.wait_for_timeout(3500); l=p.locator("[data-testid=today-substitute]"); return l.inner_text() if l.count() else ""
    t=card(); p.screenshot(path=S+"/P9-ph1-390.png",full_page=True)
    WD=["Thứ Hai","Thứ Ba","Thứ Tư","Thứ Năm","Thứ Sáu","Thứ Bảy","Chủ nhật"]; lab=lambda d:f"{WD[d.weekday()]} {d.strftime('%d/%m')}"
    blk=re.search(rf"↔ {lab(D12)} Cô Hồng trông bé {first}[^\n]*\n?[^\n]*",t)
    rec(f"P9-01 thẻ '↔ {lab(D12)} Cô Hồng trông bé {first}' + 'buổi sáng'",bool(blk) and "buổi sáng" in blk.group(0),t.replace("\n"," | "))
    rec("P9-02 không còn thẻ 'Hôm nay' của lượt 10/10 đã xoá","Hôm nay" not in t,t.replace("\n"," | ")[:120])
    if p.locator("[data-testid=today-substitute]").count():
        y=lambda s:p.locator(s).first.bounding_box()["y"]; bc=p.locator("[data-testid=today-substitute] .card").first.evaluate("e=>getComputedStyle(e).borderLeftColor")
        rec("P9-03 thẻ viền peach, nằm trên ô điểm danh",bc.replace(" ","")=="rgb(255,138,76)" and y("[data-testid=today-substitute]")<y("[data-testid=tile-attendance]"),f"{bc}")
    rec("OVF[390] ph1 /today",p.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=0)
    # xoá lượt trông thay → thẻ mất
    d13=D12+datetime.timedelta(1); r=mk(d13); s13=r.json().get("id")
    t=card(); rec(f"P9-04 tạo trông thay {lab(d13)} → thẻ hiện sau khi tải lại",lab(d13) in t,f"tạo {r.status_code}; {t.replace(chr(10),' | ')[:160]}")
    print("xoá lượt",dl(s13)) if s13 else None
    t=card(); rec(f"P9-05 xoá trông thay {lab(d13)} → thẻ mất sau khi tải lại",lab(d13) not in t,t.replace("\n"," | ")[:160])
    # huỷ đơn nghỉ → thẻ mất
    d14=D12+datetime.timedelta(2); lv=requests.post(B+"/staff/leaves",headers=H["gv1"],json={"type":"personal","fromDate":iso(d14),"toDate":iso(d14),"session":"morning"}).json()
    ap=requests.post(B+f"/staff/leaves/{lv.get('id')}/approve",headers=H["admin"],json={"substituteUserId":uid("gv3"),"force":True})
    t=card(); rec(f"P9-06 duyệt đơn nghỉ {lab(d14)} + Cô Hồng → thẻ hiện",lab(d14) in t,f"duyệt {ap.status_code}; {t.replace(chr(10),' | ')[:160]}")
    cr=requests.post(B+f"/staff/leaves/{lv.get('id')}/cancel",headers=H["admin"],json={"note":"QA huỷ"})
    t=card(); rec(f"P9-07 huỷ đơn nghỉ {lab(d14)} → thẻ mất sau khi tải lại",lab(d14) not in t,f"huỷ {cr.status_code}; {t.replace(chr(10),' | ')[:160]}")
    for x in (ap.json().get("substitutions",[]) if ap.ok else []): print("dọn lượt của đơn huỷ",dl(x["id"]))
    # ngày đã qua
    r=mk(T-datetime.timedelta(1)); sy=r.json().get("id"); it=subs("ph1",k1["id"]).json()["items"]
    t=card(); rec("P9-08 trông thay HÔM QUA không trả về API và không hiện thẻ",all(x["date"]>=iso(T) for x in it) and lab(T-datetime.timedelta(1)) not in t and "Hôm qua" not in t,f"tạo {r.status_code}; API dates={[x['date'] for x in it]}")
    if sy: print("xoá lượt hôm qua",dl(sy))
    c.close()
    c=b.new_context(viewport=V); p=c.new_page(); login_ui(p,U,"ph2","123456",consent=True); p.goto(U+"/today"); p.wait_for_timeout(3500)
    n=p.locator("[data-testid=today-substitute]").count(); rec("P9-09 PH lớp khác (ph2) không thấy thẻ",n==0,p.locator("[data-testid=today-substitute]").inner_text() if n else ""); p.screenshot(path=S+"/P9-ph2-390.png")
    rec("OVF[390] ph2 /today",p.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")<=0); c.close(); b.close()
left=[x for x in subs("admin",k1["id"]).json()["items"]]; rec("DỌN: chỉ còn lượt 12/10 Cô Hồng buổi sáng",[(x["date"],x["substituteName"],x["session"]) for x in left]==[(iso(D12),"Cô Hồng","morning")],left)
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
