"""G6–G8 + H1 theo mamnon-backend/docs/api-g6-g8.md: API + web H1 (BGH bấm thông báo đơn nghỉ → trang duyệt, chọn cô trông thay, bấm Duyệt trên web).
Chạy: python api_g678.py [API] [WEB] [NGÀY_NGHỈ=2026-10-12 (thứ Hai)]   – tài khoản admin, gv1 (Cô Lan, Mầm 1), gv2, gv3 (Cô Hồng), ph1 (con ở Mầm 1), mk 123456.
Kết quả: PASS / FAIL / NOT_IMPLEMENTED (route 404 hoặc thiếu hẳn trường/kiểu thông báo trong spec).
[ghi] Trước khi chạy huỷ đơn chờ/đã duyệt của gv1/gv2 trong tuần ngày nghỉ (để chạy lại được). gv1 xin nghỉ ốm sáng NGÀY_NGHỈ, BGH duyệt + phân gv3 trên web;
gv2 đơn phép năm/việc riêng để test (huỷ/từ chối). 'Đã cho uống' chỉ làm được TRONG NGÀY dặn thuốc → G8 thuốc chạy với trông thay HÔM NAY (gv3, Mầm 1) + 1 dặn thuốc
hôm nay cho bé của ph1 (T7/CN API không cho dặn → chèn psql vào DB local); cuối script xoá trông thay hôm nay."""
import sys,re,datetime,subprocess,requests
from playwright.sync_api import sync_playwright
a=sys.argv+[None]*4
B=a[1] or "http://localhost:3001/api/v1"; U=a[2] or "http://localhost:3000"; MON=datetime.date.fromisoformat(a[3] or "2026-10-12")
DB="postgres://mamnon:mamnon@localhost:5432/mamnon"; S="/workspace/qa/shots/g678"; R=[]
import os; os.makedirs(S,exist_ok=True)
def rec(n,st,i=""):
    st={True:"PASS",False:"FAIL"}.get(bool(st) if not isinstance(st,str) else st,st); R.append((n,st,str(i)[:240])); print(R[-1],flush=True)
def ni(r): return r is not None and r.status_code==404 and "Cannot" in r.text
def chk(n,ok,i="",r=None,missing=False): rec(n,"NOT_IMPLEMENTED" if (ni(r) or missing) else bool(ok),i if (r is None or i) else f"{r.status_code} {r.text[:160]}")
tok=lambda u:requests.post(B+"/auth/login",json={"username":u,"password":"123456"}).json()["accessToken"]
H={u:{"Authorization":"Bearer "+tok(u)} for u in ["admin","gv1","gv2","gv3","ph1"]}
get=lambda u,p,**k:requests.get(B+p,headers=H[u],**k); post=lambda u,p,j=None:requests.post(B+p,headers=H[u],json=j or {}); patch=lambda u,p,j:requests.patch(B+p,headers=H[u],json=j)
me={u:get(u,"/auth/me").json() for u in H}; uid=lambda u:me[u].get("id") or me[u].get("user",{}).get("id")
def notes(u,typ): return [n for n in get(u,"/notifications",params={"limit":100}).json().get("items",[]) if n["type"]==typ]
T=(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)+datetime.timedelta(hours=7)).date(); dm=lambda d:d.strftime("%d/%m"); iso=lambda d:d.isoformat(); D=lambda k:MON+datetime.timedelta(k)
C1=[c for c in get("admin","/classes").json() if c["name"]=="Mầm 1"][0]["id"]
for l in get("admin","/staff/leaves").json()["items"]:   # dọn đơn cũ trong tuần (cho phép chạy lại)
    if l["status"] in ("pending","approved") and l["userId"] in (uid("gv1"),uid("gv2")) and l["fromDate"]<=iso(D(40)) and l["toDate"]>=iso(MON):
        for x in l.get("substitutions",[]): requests.delete(B+f"/staff/substitutions/{x['id']}",headers=H["admin"])
        post("admin",f"/staff/leaves/{l['id']}/cancel",{"note":"QA dọn"})
print("NGÀY_NGHỈ",MON,"hôm nay",T,"lớp",C1,flush=True)
# ───────── G6
r=post("gv1","/staff/leaves",{"type":"sick","fromDate":iso(MON),"toDate":iso(D(1)),"session":"morning"})
chk("G6-01 nửa ngày nhiều ngày → 400 HALF_DAY_SINGLE_DATE",r.status_code==400 and r.json().get("code")=="HALF_DAY_SINGLE_DATE",r=r)
r=post("gv1","/staff/leaves",{"type":"holiday","fromDate":iso(MON),"toDate":iso(MON)}); chk("G6-02 type sai → 400",r.status_code==400,r=r)
types={}
for t,lab,who,off in [("sick","Ốm","gv1",0),("annual","Phép năm","gv2",2),("personal","Việc riêng","gv2",3)]:
    body={"type":t,"fromDate":iso(D(off)),"toDate":iso(D(off)),"session":"morning" if t=="sick" else "full"}
    if t=="sick": body["handoverNote"]="QA: Bé Na dị ứng sữa; 10h tập văn nghệ"
    r=post(who,"/staff/leaves",body); j=r.json() if r.status_code<500 else {}; types[t]=j
    chk(f"G6-03 tạo đơn loại {t} → 201, typeLabel '{lab}'",r.status_code==201 and j.get("type")==t and j.get("typeLabel")==lab,f"{r.status_code} type={j.get('type')} label={j.get('typeLabel')} days={j.get('days')} buổi={j.get('sessionLabel')} {j.get('code','')}",missing=r.status_code==201 and "typeLabel" not in j)
L=types["sick"]; LID=L.get("id")
chk("G6-04 nghỉ sáng: days=0.5, 'Buổi sáng', reason mặc định 'Ốm', có handoverNote",L.get("days")==0.5 and L.get("sessionLabel")=="Buổi sáng" and L.get("reason")=="Ốm" and L.get("handoverNote"),{k:L.get(k) for k in ["days","sessionLabel","reason","handoverNote"]})
pm=post("gv1","/staff/leaves",{"type":"personal","fromDate":iso(MON),"toDate":iso(MON),"session":"afternoon"}); chk("G6-05 chiều cùng ngày không trùng đơn sáng → 201",pm.status_code==201,r=pm)
r=post("gv1","/staff/leaves",{"type":"personal","fromDate":iso(MON),"toDate":iso(MON)}); chk("G6-06 cả ngày trùng đơn sáng → 409 LEAVE_OVERLAP",r.status_code==409 and r.json().get("code")=="LEAVE_OVERLAP",r=r)
if pm.status_code==201: post("gv1",f"/staff/leaves/{pm.json()['id']}/cancel")
r=get("gv1","/staff/leaves/preview",params={"fromDate":iso(MON),"toDate":iso(D(6))}); chk("G6-07 preview T2→CN = 5 ngày công",r.status_code==200 and r.json().get("days")==5,r=r)
r=get("gv1","/staff/leaves/preview",params={"fromDate":iso(MON),"toDate":iso(MON),"session":"afternoon"}); chk("G6-08 preview nửa ngày = 0.5",r.status_code==200 and r.json().get("days")==0.5,r=r)
r=get("gv2","/staff/leaves/balance",params={"year":MON.year}); b=r.json() if r.status_code==200 else {}
chk("G6-09 balance: đơn phép năm chờ tính vào annualPending, remaining = allowance-used-pending",r.status_code==200 and b.get("annualPending",0)>=1 and b.get("annualRemaining")==b.get("annualAllowance",0)-b.get("annualUsed",0)-b.get("annualPending",0),b,r if r.status_code!=200 else None)
r=post("gv2","/staff/leaves",{"type":"annual","fromDate":iso(D(7)),"toDate":iso(D(27))}); chk("G6-10 phép năm vượt số còn lại → 409 ANNUAL_EXCEEDED + details.remaining",r.status_code==409 and r.json().get("code")=="ANNUAL_EXCEEDED" and "remaining" in (r.json().get("details") or {}),r=r)
r=get("gv2","/staff/leaves/balance",params={"userId":uid("gv1")}); chk("G6-11 GV xem balance người khác → 403",r.status_code==403,r=r)
if types["annual"].get("id"): post("gv2",f"/staff/leaves/{types['annual']['id']}/cancel")
# ───────── G7 + H1
n=[x for x in notes("admin","staff_leave") if (x.get("data") or {}).get("leaveId")==LID]
want=f"{me['gv1'].get('name') or me['gv1'].get('fullName')} xin nghỉ ốm {dm(MON)} (buổi sáng)"
chk("G7-01 BGH nhận staff_leave: tiêu đề '<cô> xin nghỉ ốm dd/mm (buổi sáng)' + 'Mầm 1 cần cô trông thay'",n and n[0]["title"]==want and "Mầm 1 cần cô trông thay" in n[0]["body"],(n[0]["title"]+" | "+n[0]["body"]) if n else "không có",missing=not n and not notes("admin","staff_leave"))
chk("H1-01 data.url = /staff/leaves/<id>",n and n[0]["data"].get("url")==f"/staff/leaves/{LID}",n[0]["data"] if n else "")
r=get("admin",f"/staff/leaves/{LID}"); pg=r.json() if r.status_code==200 else {}; cov=pg.get("coverage") or []
chk("G7-02 GET đơn (admin) có coverage Mầm 1 + ca + substitution=null + suggestions",r.status_code==200 and len(cov)==1 and cov[0]["class"]["id"]==C1 and cov[0].get("shift") and cov[0]["substitution"] is None,
    [{"date":c["date"],"shift":(c.get("shift") or {}).get("name"),"gợi ý":[s["name"] for s in c.get("suggestions",[])]} for c in cov] or r.text[:150],r if r.status_code!=200 else None,missing=r.status_code==200 and "coverage" not in pg)
if cov and cov[0].get("shift"): rec("G7-02c tên ca trong DB local là 'Ca ngày' (không còn 'Ca sáng')",cov[0]["shift"]["name"]!="Ca sáng",cov[0]["shift"]["name"])
r=get("gv2",f"/staff/leaves/{LID}"); chk("G7-03 GV khác xem đơn → 403",r.status_code==403,r=r)
ui_ok=False
with sync_playwright() as pw:
    br=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); g=br.new_page(viewport={"width":390,"height":844})
    g.goto(U+"/login",timeout=90000); g.fill("input[autocomplete=username]","admin"); g.fill("input[type=password]","123456"); g.click("button"); g.wait_for_timeout(3500)
    g.goto(U+"/notifications"); g.wait_for_timeout(4000); g.screenshot(path=S+"/H1-0-notifications-390.png")
    it=g.locator("[data-testid=notif-item][data-type=staff_leave]").filter(has_text=f"{dm(MON)} (buổi sáng)")
    if it.count():
        it.first.click(); g.wait_for_timeout(4000); g.screenshot(path=S+"/H1-1-approval-390.png",full_page=True); url=g.url
        rec("H1-02 bấm thông báo đơn nghỉ → mở /staff/leaves/<id>",url.split("?")[0].endswith(f"/staff/leaves/{LID}"),url)
        rec("H1-03 trang duyệt có '✓ Duyệt' + 'Từ chối'",g.locator("[data-testid=leave-approve-btn]").count()==1 and g.locator("[data-testid=leave-reject]").count()==1)
        ps=g.locator("[data-testid=pick-sub]"); rec("H1-04 có ô 'Chọn cô trông thay' (radio gợi ý)",ps.count()==1 and ps.locator("input[type=radio]").count()>=2,ps.inner_text().replace("\n"," | ")[:180] if ps.count() else "không có pick-sub")
        ct=g.inner_text("[data-testid=leave-card]") if g.locator("[data-testid=leave-card]").count() else ""
        rec("H1-05 thẻ đơn: 'Ốm', 0,5 ngày công, ghi chú bàn giao","Ốm" in ct and "0,5" in ct.replace(".",",") and "Bé Na" in ct,ct.replace("\n"," | ")[:200])
        if ps.count() and ps.get_by_text("Cô Hồng").count():
            ps.locator("label").filter(has_text="Cô Hồng").first.click(); g.click("[data-testid=leave-approve-btn]"); g.wait_for_timeout(4000); g.screenshot(path=S+"/H1-2-approved-390.png",full_page=True)
            msg=g.locator("[data-testid=leave-msg]").inner_text() if g.locator("[data-testid=leave-msg]").count() else g.inner_text("body")[:200]
            ui_ok="Đã duyệt" in msg; rec("G7-04w BGH chọn Cô Hồng + bấm '✓ Duyệt' trên web → 'Đã duyệt và phân trông thay…'",ui_ok,msg.replace("\n"," | ")[:200])
        else: rec("G7-04w chọn Cô Hồng trên web",False,"không có lựa chọn Cô Hồng")
    else: rec("H1-02 thông báo đơn nghỉ trên /notifications",False,"không thấy notif-item staff_leave "+dm(MON))
    br.close()
if not ui_ok:
    r=post("admin",f"/staff/leaves/{LID}/approve",{"note":"QA duyệt (API dự phòng)","substituteUserId":uid("gv3"),"force":True}); print("API approve fallback",r.status_code,r.text[:150])
ap=get("admin",f"/staff/leaves/{LID}").json()
chk("G7-04 đơn approved, substitutions = Cô Hồng · Mầm 1 · buổi sáng · "+dm(MON),ap.get("status")=="approved" and any(s["substituteTeacher"]["id"]==uid("gv3") and s.get("session")=="morning" and s["date"]==iso(MON) for s in ap.get("substitutions",[])),f"{ap.get('status')} {[(s['date'],s['class']['name'],s['substituteTeacher']['name'],s.get('session')) for s in ap.get('substitutions',[])]}")
r=post("admin",f"/staff/leaves/{LID}/approve",{"substituteUserId":uid("gv3")}); chk("G7-05 duyệt lần 2 → 409 ALREADY_DECIDED",r.status_code==409 and r.json().get("code")=="ALREADY_DECIDED",r=r)
d=[x for x in notes("gv1","staff_leave_decision") if (x.get("data") or {}).get("leaveId")==LID]
chk("G7-06 GV nhận '✓ Đơn nghỉ ốm dd/mm (buổi sáng) đã duyệt' + 'Cô trông thay: Cô Hồng' + url",d and d[0]["title"]==f"✓ Đơn nghỉ ốm {dm(MON)} (buổi sáng) đã duyệt" and "Cô trông thay: Cô Hồng" in d[0]["body"] and d[0]["data"].get("url")==f"/staff/leaves/{LID}",(d[0]["title"]+" | "+d[0]["body"]) if d else "",missing=not d)
s=[x for x in notes("gv3","substitution") if (x.get("data") or {}).get("leaveId")==LID]
chk("G7-07 cô trông thay nhận 'Trông thay lớp Mầm 1 · dd/mm buổi sáng' + 'Bàn giao: …', url /home",s and s[-1]["title"]==f"Trông thay lớp Mầm 1 · {dm(MON)} buổi sáng" and "Bé Na dị ứng sữa" in s[-1]["body"] and s[-1]["data"].get("url")=="/home",(s[-1]["title"]+" | "+s[-1]["body"].replace("\n"," / ")) if s else "",missing=not s)
r=get("gv3",f"/staff/leaves/{LID}"); sv=r.json() if r.status_code==200 else {}
chk("G7-08 cô trông thay xem đơn: thấy ghi chú bàn giao, KHÔNG thấy lý do",r.status_code==200 and "Bé Na" in (sv.get("handoverNote") or "") and "reason" not in sv,f"handoverNote={sv.get('handoverNote')!r}; có reason={'reason' in sv}",r if r.status_code!=200 else None)
n0=len(notes("gv3","substitution")); r=patch("gv1",f"/staff/leaves/{LID}",{"handoverNote":"QA: Bé Na dị ứng sữa; nhớ cho bé uống nước"}); n1=len(notes("gv3","substitution"))
chk("G7-09 GV sửa ghi chú bàn giao sau duyệt → 200 + báo cô trông thay",r.status_code==200 and n1==n0+1,f"{r.status_code}; tin gv3 {n0}→{n1}",r if r.status_code==404 else None)
SUBS={x["id"] for x in ap.get("substitutions",[])}; p=[x for x in notes("ph1","substitute_teacher") if (x.get("data") or {}).get("substitutionId") in SUBS]
chk("G8-01 PH Mầm 1 nhận đúng 1 tin '↔ Cô trông thay ngày dd/mm' (classId, session, substituteName)",len(p)==1 and p[0]["title"]==f"↔ Cô trông thay ngày {dm(MON)}" and p[0]["data"].get("classId")==C1 and p[0]["data"].get("session")=="morning" and p[0]["data"].get("substituteName")=="Cô Hồng",
    (f"{len(p)} tin: "+p[0]["title"]+" | "+p[0]["body"]) if p else "",missing=not p and not notes("ph1","substitute_teacher"))
OID=types["personal"].get("id")
r=post("admin",f"/staff/leaves/{OID}/reject"); chk("G7-10 từ chối không lý do → 400 NOTE_REQUIRED",r.status_code==400 and r.json().get("code")=="NOTE_REQUIRED",r=r)
r=post("admin",f"/staff/leaves/{OID}/reject",{"note":"QA trùng hội giảng"}); rj=[x for x in notes("gv2","staff_leave_decision") if (x.get("data") or {}).get("leaveId")==OID]
chk("G7-11 từ chối có lý do → GV nhận 'Đơn nghỉ việc riêng dd/mm bị từ chối' + 'Lý do: …'",r.status_code==200 and rj and rj[0]["title"]==f"Đơn nghỉ việc riêng {dm(D(3))} bị từ chối" and "QA trùng hội giảng" in rj[0]["body"],(rj[0]["title"]+" | "+rj[0]["body"]) if rj else r.text[:120])
r=get("admin","/staff/attendance",params={"from":iso(MON),"to":iso(MON),"userId":uid("gv1")}); row=[x for x in (r.json().get("items",[]) if r.status_code==200 else []) if x["user"]["id"]==uid("gv1")]
c0=row[0]["days"][0] if row else {}
chk("G6-12 bảng công: ô nghỉ sáng leaveType=sick, leaveSession=morning, leaveDays=0.5; totals.leave=0.5",row and c0.get("leaveType")=="sick" and c0.get("leaveSession")=="morning" and c0.get("leaveDays")==0.5 and row[0]["totals"].get("leave")==0.5,
    f"ô={ {k:c0.get(k) for k in ['status','leaveType','leaveSession','leaveDays']} } totals.leave={row[0]['totals'].get('leave') if row else ''}",r if r.status_code!=200 else None,missing=bool(row) and "leaveDays" not in c0)
# ───────── G8 thuốc (hôm nay)
kid=get("ph1","/children").json()["items"][0]
r=requests.post(B+f"/children/{kid['id']}/medicines",headers=H["ph1"],json={"date":iso(T),"name":"QA Hạ sốt","dose":"5ml","times":["10:00"]})
if r.status_code==201: mid=r.json()["id"]; dose=r.json()["doses"][0]["id"]; how="API"
else:
    out=subprocess.run(["psql",DB,"-Atc",f"WITH m AS (INSERT INTO medicines (child_id,class_id,date,name,dose) VALUES ('{kid['id']}','{C1}','{iso(T)}','QA Hạ sốt','5ml') RETURNING id) INSERT INTO medicine_doses (medicine_id,time) SELECT id,'10:00' FROM m RETURNING medicine_id||' '||id"],capture_output=True,text=True).stdout.split()
    mid,dose=out[0],out[1]; how=f"psql (API {r.status_code} {r.json().get('code')})"
print("dặn thuốc",mid,"dose",dose,"qua",how,flush=True)
subs=get("admin","/staff/substitutions",params={"from":iso(T),"to":iso(T)}).json(); subs=subs.get("items",subs) if isinstance(subs,dict) else subs
for x in subs:
    if ((x.get("class") or {}).get("id") or x.get("classId"))==C1: requests.delete(B+f"/staff/substitutions/{x['id']}",headers=H["admin"])
r=post("gv3",f"/medicine-doses/{dose}/given"); chk("G8-02 chưa trông thay: gv3 'Đã cho uống' lớp Mầm 1 → 403",r.status_code==403,r=r)
r=get("gv3",f"/classes/{C1}/parent-messages"); chk("G8-03 chưa trông thay: gv3 xem dặn thuốc Mầm 1 → 403",r.status_code==403,r=r)
shift=[x for x in get("admin","/staff/shifts").json()["items"] if x["isActive"]][0]; n0=len(notes("ph1","substitute_teacher"))
r=post("admin","/staff/substitutions",{"date":iso(T),"shiftId":shift["id"],"classId":C1,"substituteUserId":uid("gv3"),"absentUserId":uid("gv1"),"force":True}); SID=r.json().get("id") if r.status_code==201 else None
chk("G8-04 phân trông thay hôm nay (Cô Hồng → Mầm 1) → 201",r.status_code==201,r=r)
p=notes("ph1","substitute_teacher"); new=p[:max(0,len(p)-n0)]
chk("G8-05 PH nhận '↔ Cô trông thay hôm nay' + 'Cô Hồng trông lớp Mầm 1 …'",any(x["title"]=="↔ Cô trông thay hôm nay" and x["body"].startswith("Cô Hồng trông lớp Mầm 1") for x in new),[(x["title"],x["body"]) for x in new][:2])
r=get("gv3","/staff/me/substitutions/today"); it=[x for x in (r.json().get("items",[]) if r.status_code==200 else []) if x["class"]["id"]==C1]
meds=it[0].get("medicines",[]) if it else []; md=[m for m in meds if m.get("id")==mid]
chk("G8-06 cô trông thay thấy dặn thuốc của lớp (/staff/me/substitutions/today), GV vắng Cô Lan",it and it[0]["absentTeacher"]["id"]==uid("gv1") and md and md[0]["doses"][0]["givenAt"] is None,f"items={len(it)} thuốc={[ (m.get('childName'),m.get('name')) for m in meds]}",r if r.status_code!=200 else None)
r=get("gv3",f"/classes/{C1}/parent-messages"); chk("G8-07 trông thay: gv3 GET parent-messages lớp → 200",r.status_code==200,r=r)
r=get("gv3",f"/children/{kid['id']}/medicines"); chk("G8-08 trông thay: gv3 GET /children/:id/medicines → 200",r.status_code==200,r=r)
r=get("gv2",f"/classes/{C1}/parent-messages"); chk("G8-09 gv2 (không trông thay) vẫn 403",r.status_code==403,r=r)
r=post("gv2",f"/medicine-doses/{dose}/given"); chk("G8-10 gv2 'Đã cho uống' lớp khác → 403",r.status_code==403,r=r)
m0=len(notes("ph1","medicine_given"))
r=post("gv3",f"/medicine-doses/{dose}/given"); gd=[x for x in (r.json().get("doses",[]) if r.status_code==200 else []) if x["id"]==dose]
chk("G8-11 cô trông thay bấm 'Đã cho uống' → 200, ghi givenAt + givenByName 'Cô Hồng'",r.status_code==200 and gd and gd[0]["givenAt"] and gd[0]["givenByName"]=="Cô Hồng",{k:gd[0].get(k) for k in ["givenAt","givenByName"]} if gd else "",r if r.status_code!=200 else None)
r=post("gv3",f"/medicine-doses/{dose}/given"); e=r.json() if r.status_code==409 else {}
chk("G8-12 bấm lần 2 → 409 ALREADY_GIVEN + givenAt, givenByName",r.status_code==409 and e.get("code")=="ALREADY_GIVEN" and (e.get("details") or {}).get("givenByName"),r=r)
mg=notes("ph1","medicine_given"); newm=mg[:max(0,len(mg)-m0)]; first=kid["fullName"].split()[-1]
chk(f"G8-13 PH nhận đúng 1 tin 'Bé {first} đã được cho uống thuốc lúc HH:MM' + '(cô trông thay)'",len(newm)==1 and re.fullmatch(rf"Bé {first} đã được cho uống thuốc lúc \d\d:\d\d",newm[0]["title"]) and "(cô trông thay)" in newm[0]["body"],[(x["title"],x["body"]) for x in newm],missing=not mg)
if SID: print("dọn trông thay hôm nay",requests.delete(B+f"/staff/substitutions/{SID}",headers=H["admin"]).status_code)
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R),"NOT_IMPLEMENTED",sum(x[1]=="NOT_IMPLEMENTED" for x in R))
