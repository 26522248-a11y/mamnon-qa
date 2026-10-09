# Luồng nghỉ G6/G7/H1 trên staging. Tài khoản đọc từ biến môi trường SA/SG (u:p) – không lưu trong file.
import os,re,requests,json
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
B=os.environ["API"];W=os.environ["WEB"];R=[];DAY="2026-10-12"
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:220]));print(R[-1],flush=True)
def tok(k): u,p=os.environ[k].split(":",1); return {"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":p}).json()["accessToken"]}
A,G=tok("SA"),tok("SG")
lid=None
try:
    r=requests.get(B+"/staff/leaves/preview",headers=G,params={"fromDate":DAY,"toDate":DAY,"session":"morning"}); rec("G6-01 preview nửa buổi = 0.5 ngày công",r.ok and r.json().get("days")==0.5,r.text[:100])
    r=requests.post(B+"/staff/leaves",headers=G,json={"type":"sick","fromDate":DAY,"toDate":"2026-10-13","session":"morning","reason":"QA test"}); rec("G6-02 nửa buổi nhiều ngày → 400 HALF_DAY_SINGLE_DATE",r.status_code==400 and "HALF_DAY" in r.text,r.text[:120])
    r=requests.post(B+"/staff/leaves",headers=G,json={"type":"sick","fromDate":DAY,"toDate":DAY,"session":"morning","reason":"QA test – sẽ huỷ ngay","handoverNote":"QA test bàn giao"})
    rec("G6-03 GV gửi đơn ốm sáng 12/10 → 201",r.status_code==201,r.text[:200]); v=r.json(); lid=v.get("id")
    rec("G6-04 LeaveView: typeLabel Ốm, sessionLabel Buổi sáng, days 0.5, handoverNote",v.get("typeLabel")=="Ốm" and v.get("sessionLabel")=="Buổi sáng" and float(v.get("days",0))==0.5 and v.get("handoverNote")=="QA test bàn giao",{k:v.get(k) for k in ["typeLabel","sessionLabel","days","status"]})
    r=requests.post(B+"/staff/leaves",headers=G,json={"type":"sick","fromDate":DAY,"toDate":DAY,"session":"morning","reason":"QA dup"}); rec("G6-05 trùng buổi → 409 LEAVE_OVERLAP",r.status_code==409 and "LEAVE_OVERLAP" in r.text,r.text[:120])
    if r.status_code==201: requests.post(B+f"/staff/leaves/{r.json()['id']}/cancel",headers=G,json={"note":"QA dọn"})
    n=requests.get(B+"/notifications?limit=30",headers=A).json(); items=n.get("items",n)
    nt=[x for x in items if x.get("type")=="staff_leave" and (x.get("data") or {}).get("leaveId")==lid]
    rec("G7-01 BGH nhận thông báo staff_leave, url /staff/leaves/<id>",bool(nt) and (nt[0].get("data") or {}).get("url")==f"/staff/leaves/{lid}",nt[0].get("title") if nt else [x.get("title") for x in items[:3]])
    d=requests.get(B+f"/staff/leaves/{lid}",headers=A).json(); cov=d.get("coverage") or []
    rec("G7-02 chi tiết có coverage (lớp Mầm 1, ca 'Ca ngày')",bool(cov) and cov[0].get("shift",{}).get("name")=="Ca ngày",[(c.get("class",{}).get("name"),c.get("shift",{}).get("name"),[s.get("name") for s in c.get("suggestions",[])]) for c in cov])
    rec("G9-staging chi tiết đơn không có 'Ca sáng'","Ca sáng" not in json.dumps(d,ensure_ascii=False))
    # H1 web: bấm thông báo → trang duyệt
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); p=b.new_page(viewport={"width":390,"height":844})
        login_ui(p,W,*os.environ["SA"].split(":",1),consent=None); p.goto(W+"/notifications"); p.wait_for_timeout(4000)
        it=p.get_by_text(re.compile(r"xin nghỉ ốm 12/10")).first
        if it.count(): it.click(); p.wait_for_timeout(4000)
        t=p.inner_text("body"); p.screenshot(path="/workspace/staging-run/H1-approve-390.png",full_page=True)
        rec("H1-01 bấm thông báo đơn nghỉ → mở /staff/leaves/<id>",f"/staff/leaves/{lid}" in p.url,p.url)
        rec("H1-02 trang có Duyệt, Từ chối và chọn cô trông thay",bool(re.search("Duyệt",t)) and "Từ chối" in t and bool(re.search("trông thay",t,re.I)),re.findall(r"[^\n]*(?:Duyệt|Từ chối|trông thay)[^\n]*",t)[:6])
        b.close()
    r=requests.post(B+f"/staff/leaves/{lid}/reject",headers=A,json={}); rec("G7-03 từ chối thiếu lý do → 400 NOTE_REQUIRED",r.status_code==400 and "NOTE_REQUIRED" in r.text,r.text[:100])
    r=requests.post(B+f"/staff/leaves/{lid}/approve",headers=A,json={"note":"QA duyệt thử (không phân trông thay)"}); rec("G7-04 duyệt không phân trông thay → 200 approved",r.ok and r.json().get("status")=="approved",r.text[:150])
    r=requests.post(B+f"/staff/leaves/{lid}/approve",headers=A,json={}); rec("G7-05 duyệt lần 2 → 409 ALREADY_DECIDED",r.status_code==409 and "ALREADY_DECIDED" in r.text,r.text[:100])
    n=requests.get(B+"/notifications?limit=30",headers=G).json(); items=n.get("items",n)
    nd=[x for x in items if x.get("type")=="staff_leave_decision" and (x.get("data") or {}).get("leaveId")==lid]
    rec("G7-06 GV nhận 'đã duyệt' (staff_leave_decision)",bool(nd),nd[0].get("title") if nd else [x.get("title") for x in items[:3]])
    r=requests.patch(B+f"/staff/leaves/{lid}",headers=G,json={"handoverNote":"QA sửa bàn giao"}); rec("G7-07 GV sửa ghi chú bàn giao khi đã duyệt",r.ok and r.json().get("handoverNote")=="QA sửa bàn giao",r.text[:120])
finally:
    if lid:
        r=requests.post(B+f"/staff/leaves/{lid}/cancel",headers=G,json={"note":"QA dọn"})
        if not r.ok: r=requests.post(B+f"/staff/leaves/{lid}/cancel",headers=A,json={"note":"QA dọn"})
        st=requests.get(B+f"/staff/leaves/{lid}",headers=A).json().get("status"); rec("CLEAN huỷ đơn QA",st=="cancelled",f"status={st} cancel_http={r.status_code}")
        subs=requests.get(B+"/staff/substitutions",headers=A,params={"from":DAY,"to":DAY}).text; rec("CLEAN không còn trông thay ngày 12/10",lid not in subs,subs[:120])
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
