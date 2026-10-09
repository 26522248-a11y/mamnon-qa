"""G14 (e72bfb6+): Có mặt chạm → Vắng; Vắng / Đi muộn / Vắng có phép / Chưa điểm chạm 1 lần → Có mặt (xoá lý do muộn/vắng). Cũ: 1 chạm Có mặt ↔ Vắng, không hỏi lý do; chạm lần 2 về Có mặt; lý do / Đi muộn thêm sau qua 'Ghi lý do · sửa ›' (att-why → att-reasons / att-late).
Lưu → kiểm qua API. Khổ 390px. Chạy: python e2e_g14.py [WEB=http://localhost:3000] [API]
[ghi] dùng 2 bé đang 'Có mặt' hôm nay của lớp gv1; cuối script trả lại 'Có mặt' (API) và kiểm lại."""
import sys,re,datetime,requests
from playwright.sync_api import sync_playwright
from qa_login import login_ui
a=sys.argv+[None]*3; U=a[1] or "http://localhost:3000"; B=a[2] or "http://localhost:3001/api/v1"; S="/workspace/qa/shots/g14"; import os; os.makedirs(S,exist_ok=True); R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:240])); print(R[-1],flush=True)
G={"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":"gv1","password":"123456"}).json()["accessToken"]}
d=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=7)).date().isoformat()
c=requests.get(B+"/classes",headers=G).json(); C=(c.get("items",c) if isinstance(c,dict) else c)[0]["id"]
att=lambda:{i["childId"]:i for i in requests.get(B+f"/classes/{C}/attendance",headers=G,params={"date":d}).json()["items"]}
orig=att(); two=[k for k,v in orig.items() if v["status"]=="present" and not v.get("note")][:2]
rec("G14-00 có ≥2 bé 'Có mặt' hôm nay để thử",len(two)==2,len(two))
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); p=b.new_page(viewport={"width":390,"height":844}); dlg=[]; p.on("dialog",lambda x:(dlg.append(x.message),x.dismiss()))
    login_ui(p,U,"gv1","123456",consent=None); p.goto(U+"/attendance"); p.wait_for_selector("[data-testid=att-row]",timeout=20000); p.wait_for_timeout(1500)
    rows=p.locator("[data-testid=att-row]"); names=[orig[k]["fullName"] for k in two]
    row=lambda n:rows.filter(has_text=n).first; st=lambda n:row(n).get_attribute("data-status"); tap=lambda n:(row(n).locator("button").first.click(),p.wait_for_timeout(250))
    A,Bn=names
    tap(A); modal=p.locator("[role=dialog],[data-testid=att-reasons]").count()
    rec("G14-01 1 chạm: Có mặt → Vắng, không hộp thoại / không mở bảng lý do",st(A)=="absent" and not dlg and modal==0,f"status={st(A)} dialog={dlg} modal={modal}")
    rec("G14-02 sau khi chuyển Vắng có nút 'Ghi lý do · sửa ›'",row(A).locator("[data-testid=att-why]").count()==1,row(A).locator("[data-testid=att-why]").inner_text() if row(A).locator("[data-testid=att-why]").count() else "")
    p.screenshot(path=S+"/G14-1-absent-390.png",full_page=True)
    tap(A); rec("G14-03 chạm lần 2: về Có mặt",st(A)=="present" and not dlg,st(A))
    sv=p.locator("[data-testid=att-save]"); rec("G14-03b chạm 2 lần về như cũ → không còn thay đổi chờ lưu",sv.is_disabled(),sv.inner_text())
    tap(Bn); row(Bn).locator("[data-testid=att-why]").click(); p.wait_for_timeout(300); rs=row(Bn).locator("[data-testid=att-reasons]")
    chips=[x for x in rs.locator("button").all_inner_texts() if x not in ("Đi muộn","Có phép")]
    rec("G14-04 bấm 'Ghi lý do' → hiện các lý do + 'Đi muộn'",rs.count()==1 and bool(chips) and rs.locator("[data-testid=att-late]").count()==1,rs.locator("button").all_inner_texts() if rs.count() else "")
    reason=chips[0] if chips else None
    if reason: rs.locator("button",has_text=reason).first.click(); p.wait_for_timeout(250)
    tap(A); row(A).locator("[data-testid=att-why]").click(); p.wait_for_timeout(250); row(A).locator("[data-testid=att-late]").click(); p.wait_for_timeout(250)
    rec("G14-05 'Đi muộn' qua att-why → att-late",st(A)=="late",st(A)); p.screenshot(path=S+"/G14-2-edit-390.png",full_page=True)
    o=p.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth"); rec("OVF[390] /attendance (đang mở lý do)",o<=0,o)
    sv.click(); p.wait_for_timeout(3000); now=att()
    rec("G14-06 lưu → API: A 'late'",now[two[0]]["status"]=="late",now[two[0]]["status"])
    rec(f"G14-07 lưu → API: B 'absent' + lý do '{reason}'",now[two[1]]["status"]=="absent" and now[two[1]].get("note")==reason,(now[two[1]]["status"],now[two[1]].get("note")))
    p.reload(); p.wait_for_selector("[data-testid=att-row]"); p.wait_for_timeout(1500)
    w=row(Bn).locator("[data-testid=att-why]"); rec("G14-08 tải lại: trạng thái giữ đúng, B hiện 'Lý do: …'",st(A)=="late" and st(Bn)=="absent" and w.count() and reason in w.inner_text(),(st(A),st(Bn),w.inner_text() if w.count() else ""))
    tap(A); rec("G14-09 từ Đi muộn chạm 1 lần → Có mặt (luật mới e72bfb6)",st(A)=="present",st(A))
    o=p.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth"); rec("OVF[390] /attendance",o<=0,o); b.close()
# ── phần 2: Đi muộn có lý do → Có mặt (xoá lý do); PH báo nghỉ có phép → Có mặt; Chưa điểm → Có mặt
import subprocess
DB="postgres://mamnon:mamnon@localhost:5432/mamnon"; q=lambda sql:subprocess.run(["psql",DB,"-Atc",sql],capture_output=True,text=True).stdout.strip()
PH={"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":"ph1","password":"123456"}).json()["accessToken"]}
kid=requests.get(B+"/children",headers=PH).json()["items"][0]["id"]
A0=two[0]; requests.put(B+f"/classes/{C}/attendance",headers=G,json={"date":d,"items":[{"childId":A0,"status":"late","note":"Kẹt xe"}]})
rec("G14-10 chuẩn bị: bé A Đi muộn + lý do 'Kẹt xe' (API)",att()[A0]["status"]=="late" and att()[A0].get("note")=="Kẹt xe",(att()[A0]["status"],att()[A0].get("note")))
r=requests.post(B+f"/children/{kid}/absences",headers=PH,json={"from":d,"reason":"sick","note":"QA G14 sốt"}); how="API PH"
if r.status_code==201: absid=r.json()["id"]
else:
    how=f"psql (API {r.status_code} {r.json().get('code')})"
    absid=q(f"INSERT INTO absences (child_id,class_id,from_date,to_date,reason,note,created_by) SELECT '{kid}','{C}','{d}','{d}','sick','QA G14 sốt',g.user_id FROM guardians g JOIN users u ON u.id=g.user_id WHERE u.username='ph1' AND g.child_id='{kid}' LIMIT 1 RETURNING id").split()[0]
    q(f"INSERT INTO absence_days (absence_id,child_id,date,refund_eligible) VALUES ('{absid}','{kid}','{d}',true)")
    requests.put(B+f"/classes/{C}/attendance",headers=G,json={"date":d,"items":[{"childId":kid,"status":"absent"}]})
k0=att()[kid]; rec(f"G14-11 chuẩn bị: bé của ph1 'Vắng có phép' do PH báo ({how})",k0["status"]=="absent" and k0["excused"] and k0.get("absenceId")==absid,{x:k0.get(x) for x in ["status","excused","excusedBy","absenceId","refundEligible"]})
un=[k for k,v in att().items() if v["status"] is None][:1]
n0=len(requests.get(B+"/notifications",headers=PH,params={"limit":100}).json()["items"])
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); p=b.new_page(viewport={"width":390,"height":844}); dlg=[]; p.on("dialog",lambda x:(dlg.append(x.message),x.accept()))
    login_ui(p,U,"gv1","123456",consent=None); p.goto(U+"/attendance"); p.wait_for_selector("[data-testid=att-row]",timeout=20000); p.wait_for_timeout(1500)
    rows=p.locator("[data-testid=att-row]"); nm=lambda k:orig[k]["fullName"]; row=lambda k:rows.filter(has_text=nm(k)).first; st=lambda k:row(k).get_attribute("data-status"); tap=lambda k:(row(k).locator("button").first.click(),p.wait_for_timeout(300))
    rec("G14-12 UI: bé PH báo nghỉ hiện 'excused'",st(kid)=="excused",st(kid)); p.screenshot(path=S+"/G14-3-before-390.png",full_page=True)
    tap(A0); rec("G14-13 Đi muộn chạm 1 lần → Có mặt",st(A0)=="present",st(A0))
    tap(kid); rec("G14-14 Vắng có phép (PH báo) chạm 1 lần → Có mặt",st(kid)=="present",f"{st(kid)}; hộp thoại={dlg}")
    if un: tap(un[0]); rec("G14-15 Chưa điểm chạm 1 lần → Có mặt",st(un[0])=="present",st(un[0]))
    p.locator("[data-testid=att-save]").click(); p.wait_for_timeout(3500); p.screenshot(path=S+"/G14-4-saved-390.png",full_page=True)
    msg=p.locator("[data-testid=att-msg]").inner_text() if p.locator("[data-testid=att-msg]").count() else ""; b.close()
now=att(); rec("G14-16 API: A 'present', lý do muộn đã xoá",now[A0]["status"]=="present" and not now[A0].get("note"),(now[A0]["status"],now[A0].get("note")))
rec("G14-17 API: bé PH báo nghỉ → 'present', hết 'excused'",now[kid]["status"]=="present" and not now[kid]["excused"],{x:now[kid].get(x) for x in ["status","note","excused","absenceId","refundEligible"]})
if un: rec("G14-18 API: bé Chưa điểm → 'present'",now[un[0]]["status"]=="present",now[un[0]]["status"])
ad=q(f"SELECT overridden, refund_eligible, cancelled_at IS NOT NULL FROM absence_days WHERE absence_id='{absid}'"); ab=q(f"SELECT cancelled_at IS NOT NULL FROM absences WHERE id='{absid}'")
nn=requests.get(B+"/notifications",headers=PH,params={"limit":100}).json()["items"]; new=nn[:max(0,len(nn)-n0)]
rec("G14-19 [hành vi] đơn báo nghỉ của PH sau khi cô điểm Có mặt",True,f"hộp thoại cô thấy={dlg}; khung lưu='{msg}'; absence_days(overridden,refund,cancelled)={ad}; absences.cancelled={ab}; PH nhận {len(new)} tin mới: {[(x['type'],x['title']) for x in new][:3]}")
# dọn
q(f"DELETE FROM absence_days WHERE absence_id='{absid}'"); q(f"DELETE FROM absence_events WHERE absence_id='{absid}'"); q(f"DELETE FROM absences WHERE id='{absid}'")
if un: q(f"DELETE FROM attendance WHERE child_id='{un[0]}' AND date='{d}'")
r=requests.put(B+f"/classes/{C}/attendance",headers=G,json={"date":d,"items":[{"childId":k,"status":"present","note":None} for k in set(two+[kid])]}); fin=att()
if un: rec("DỌN: bé Chưa điểm trả về chưa điểm",fin[un[0]]["status"] is None,fin[un[0]]["status"])
rec("DỌN: 2 bé về 'Có mặt', không lý do",all(fin[k]["status"]=="present" and not fin[k].get("note") for k in two),f"PUT {r.status_code} {[(fin[k]['status'],fin[k].get('note')) for k in two]}")
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
