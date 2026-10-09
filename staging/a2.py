import os,re,sys,requests,json
from playwright.sync_api import sync_playwright
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
W=os.environ["WEB"];B=os.environ["API"];S="/workspace/stg2/shots";R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:300]));print(R[-1],flush=True)
def tok(k): u,p=os.environ[k].split(":",1); return {"Authorization":"Bearer "+requests.post(B+"/auth/login",json={"username":u,"password":p}).json()["accessToken"]}
A,P,G=tok("SA"),tok("SP"),tok("SG")
s=requests.get(B+"/classes/da948ed1-e420-450a-a65a-ccce44c09c09/photo-consent-summary",headers=G).json(); print("Mầm1 consent",[(x["fullName"],x["photoConsent"]) for x in s["items"] if x["photoConsent"]])
cid="f85c3be7-92ac-40e8-ac2d-8646f6563a4e"; orig=requests.get(B+f"/children/{cid}/photo-consent",headers=P).json()["consent"]; print("orig",orig)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    ctx=b.new_context(viewport={"width":390,"height":844}); p=ctx.new_page(); login_ui(p,W,*os.environ["SP"].split(":",1),consent=None); p.goto(W+"/today"); p.wait_for_timeout(5000)
    rec("A2-01 context mới: không hỏi lại câu đăng hình (đã trả lời)",p.locator("[data-testid=consent-ask]").count()==0)
    p.goto(W+"/account"); p.wait_for_timeout(5000); c=p.locator("[data-testid=account-consent]")
    w0=p.locator("[data-testid=account-consent-when]").inner_text() if c.count() else ""
    rec("A2-02 Tài khoản có 'Cho cô đăng hình con lên nhóm lớp' + lần đổi gần nhất",c.count()==1 and "Đổi lúc" in w0,f"{c.inner_text()[:150] if c.count() else ''!r}")
    target="no" if orig else "yes"; p.click(f"[data-testid=account-consent-{target}]"); p.wait_for_timeout(3000); w1=p.locator("[data-testid=account-consent-when]").inner_text(); p.screenshot(path=f"{S}/A2-account-toggled-390.png",full_page=True)
    rec("A2-03 bấm đổi → lưu ngay, hiện '✓ Đã lưu' + giờ đổi mới",("Đã lưu" in w1) and w1!=w0,f"trước={w0!r} sau={w1!r}")
    now=requests.get(B+f"/children/{cid}/photo-consent",headers=P).json()["consent"]; rec("A2-04 API đã đổi giá trị",now==(not orig),now)
    au=requests.get(B+"/audit/sensitive?limit=10",headers=A).json(); items=au.get("items",au); row=next((x for x in items if "consent" in json.dumps(x,ensure_ascii=False).lower() or "đăng hình" in json.dumps(x,ensure_ascii=False).lower()),None)
    rec("A2-05 /audit/sensitive có dòng mới: cũ/mới, bé, người đổi, giờ",bool(row),json.dumps(row,ensure_ascii=False)[:300] if row else [x.get("action") for x in items[:5]])
    ctx2=b.new_context(viewport={"width":1280,"height":900}); q=ctx2.new_page(); login_ui(q,W,*os.environ["SA"].split(":",1),consent=None); q.goto(W+"/sensitive-changes"); q.wait_for_timeout(6000)
    t=q.inner_text("main"); q.screenshot(path=f"{S}/A2-sensitive-changes-1280.png"); first=re.findall(r"[^\n]*(?:đăng hình|Đồng ý đăng)[^\n]*(?:\n[^\n]*){0,4}",t)[:1]
    rec("A2-06 trang Lịch sử thay đổi hiện dòng đồng ý đăng hình (Phúc, Phụ huynh demo, Có→Không)",bool(first) and "Phúc" in t,first)
    ctx2.close()
    p.click(f"[data-testid=account-consent-{'yes' if orig else 'no'}]"); p.wait_for_timeout(3000)
    back=requests.get(B+f"/children/{cid}/photo-consent",headers=P).json()["consent"]; rec("CLEAN trả lại giá trị ban đầu",back==orig,back)
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
