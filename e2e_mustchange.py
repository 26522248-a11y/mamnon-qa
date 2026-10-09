import requests,datetime,base64,io,openpyxl,uuid
from playwright.sync_api import sync_playwright
B="http://localhost:3001/api/v1";U="http://localhost:3000";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:220]));print(R[-1],flush=True)
tok=lambda u,p="123456":requests.post(B+"/auth/login",json={"username":u,"password":p}).json().get("accessToken")
A,G=tok("admin"),tok("gv1");H=lambda t:{"Authorization":"Bearer "+t}
ph="09870"+str(uuid.uuid4().int)[:5]; nm="QA Đổi MK "+ph[-3:]
wb=openpyxl.load_workbook("import/ok_openpyxl.xlsx"); ws=wb["Học sinh"]
for c in range(1,17): ws.cell(3,c).value=None
ws["A2"]=nm; ws["I2"]="QA PH "+ph[-3:]; ws["K2"]=ph; wb.save("import/mc.xlsx")
j=requests.post(B+"/imports/children?dryRun=false",headers=H(A),files={"file":open("import/mc.xlsx","rb")}).json()
x=openpyxl.load_workbook(io.BytesIO(base64.b64decode(j["resultFile"]["base64"])))["Mật khẩu tạm (in phát)"]
pw=[r for r in x.iter_rows(values_only=True) if r[1]==ph][0][3]
P=tok(ph,pw); kid=requests.get(B+"/children",headers=H(P)).json()
rec("PH mới (chưa đổi MK) gọi /children → 403 PASSWORD_CHANGE_REQUIRED?","PASSWORD_CHANGE_REQUIRED" in str(kid),str(kid)[:120])
kids=requests.get(B+"/children?limit=100",headers=H(A)).json()["items"]; kid=[k for k in kids if k["fullName"]==nm][0]["id"]
d=datetime.date.today().isoformat(); c=requests.get(B+"/classes",headers=H(G)).json(); c=(c.get("items",c) if isinstance(c,dict) else c)[0]["id"]
requests.put(B+f"/classes/{c}/attendance",json={"date":d,"items":[{"childId":kid,"status":"present"}]},headers=H(G))
a=[i for i in requests.get(B+f"/classes/{c}/attendance?date={d}",headers=H(G)).json()["items"] if i["childId"]==kid][0]; aid=a.get("attendanceId") or a.get("id")
q=requests.post(B+f"/attendance/{aid}/pickup-requests",json={"pickerName":"QA Người Lạ MK","pickerPhone":"0909121212","note":"QA","relation":"Bác"},headers=H(G)).json()["id"]
with sync_playwright() as p_:
    b=p_.chromium.launch(executable_path="/usr/bin/google-chrome"); p=b.new_page(viewport={"width":390,"height":844})
    p.goto(U+"/login"); p.fill("input[autocomplete=username]",ph); p.fill("input[type=password]",pw); p.click("button"); p.wait_for_timeout(3000)
    p.screenshot(path="/workspace/qa/mc_1.png",full_page=True); t=p.inner_text("body")
    rec("MC-1 vào màn đổi MK","/change-password" in p.url,p.url)
    rec("MC-2 thẻ đón trẻ trên đầu màn đổi MK","QA Người Lạ MK" in t and t.find("QA Người Lạ MK")<t.find("Sau đó"),t[:200].replace("\n"," | "))
    rec("MC-3 không lộ thông tin khác của bé (dị ứng, học phí, nhật ký)",not any(k in t for k in ["Dị ứng","Học phí","Nhật ký","Thực đơn"]))
    p.click("button:has-text('Đúng, cho đón')"); p.wait_for_timeout(2000); t=p.inner_text("body"); p.screenshot(path="/workspace/qa/mc_2.png",full_page=True)
    rec("MC-4 thu lại thành 'Đã xác nhận · Chờ nhà trường duyệt'","Chờ nhà trường duyệt" in t,t[:200].replace("\n"," | "))
    p.goto(U+"/today"); p.wait_for_timeout(2000); rec("MC-5 gõ /today vẫn bị giữ ở đổi MK","/change-password" in p.url,p.url)
    ins=p.locator("input[type=password]"); vals=["QaMoi@2026x"]*ins.count()
    if ins.count()>=2:
        if ins.count()==3: ins.nth(0).fill(pw); ins.nth(1).fill("QaMoi@2026x"); ins.nth(2).fill("QaMoi@2026x")
        else: ins.nth(0).fill("QaMoi@2026x"); ins.nth(1).fill("QaMoi@2026x")
        p.click("button:has-text('Lưu mật khẩu')"); p.wait_for_timeout(3000)
    p.goto(U+"/today"); p.wait_for_timeout(2500); p.screenshot(path="/workspace/qa/mc_3.png",full_page=True)
    rec("MC-6 /today hiện dòng vàng 'Chờ nhà trường duyệt người đón'",p.locator("[data-testid=pickup-school-pending]").count()>0,p.url)
    b.close()
print("TOTAL",len(R),"FAIL",sum(r[1]!="PASS" for r in R),"PH",ph,"KID",nm)
