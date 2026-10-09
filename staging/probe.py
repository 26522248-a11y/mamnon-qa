import os,re,sys
from playwright.sync_api import sync_playwright
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
W=os.environ["WEB"]
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    for acc,path in [("SG","/attendance"),("SG","/notes"),("SA","/dashboard")]:
        ctx=b.new_context(viewport={"width":390,"height":844}); p=ctx.new_page(); login_ui(p,W,*os.environ[acc].split(":",1),consent=None)
        c=ctx.new_cdp_session(p); c.send("Network.enable"); c.send("Network.emulateNetworkConditions",{"offline":False,"latency":2500,"downloadThroughput":60000,"uploadThroughput":60000})
        try: p.goto(W+path,wait_until="commit",timeout=60000)
        except Exception: pass
        last=None
        for i in range(70):
            try: t=p.inner_text("main",timeout=400)
            except Exception: t=""
            s=re.sub(r"\s+"," ",t)[:160]
            if s!=last: print(acc,path,round(i*0.25,1),repr(s)); last=s
            if i==8: p.screenshot(path=f"/workspace/stg2/shots/probe{path.replace('/','_')}-2s.png")
            p.wait_for_timeout(250)
        print("  ctx '0 bé':",re.findall(r"[^\n]{0,40}0 bé[^\n]{0,20}",p.inner_text("main"))[:4])
        ctx.close()
    b.close()
