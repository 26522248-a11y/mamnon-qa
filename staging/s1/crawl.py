"""Hồi quy S1 (Next 15): mỗi vai trò đăng nhập UI, đi qua mọi link nội bộ trong app, ghi lỗi console/trang lỗi/404/redirect về /login."""
import os,re,sys,json
sys.path.insert(0,"/workspace/mamnon/mamnon-qa"); from qa_login import login_ui
from playwright.sync_api import sync_playwright
W="https://mamnon-web.vercel.app"; R=[]
def rec(n,ok,i=""): R.append((n,"PASS" if ok else "FAIL",str(i)[:300]));print(R[-1],flush=True)
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    for acc in ["SA","SG","SK","SP"]:
        for vw in [(390,844),(1280,900)]:
            c=b.new_context(viewport={"width":vw[0],"height":vw[1]}); p=c.new_page(); errs=[]
            p.on("console",lambda m: errs.append(m.text[:150]) if m.type=="error" else None); p.on("pageerror",lambda e: errs.append("PAGEERR "+str(e)[:150]))
            u,pw_=os.environ[acc].split(":",1); login_ui(p,W,u,pw_,consent=True)
            start=p.url; hrefs=set()
            for h in p.eval_on_selector_all("a[href^='/']","els=>els.map(e=>e.getAttribute('href'))"): hrefs.add(h.split("?")[0].split("#")[0])
            seen=set(); queue=sorted(hrefs)
            while queue and len(seen)<45:
                h=queue.pop(0)
                if h in seen or h in ("/logout",) : continue
                seen.add(h); errs.clear()
                try: resp=p.goto(W+h,timeout=60000); p.wait_for_timeout(2500)
                except Exception as e: rec(f"NAV {acc} {vw[0]} {h}",False,e); continue
                t=p.inner_text("body")[:3000]
                bad=("Application error" in t) or ("This page could not be found" in t) or ("404" in t[:200] and "không tìm" in t.lower()) or "/login" in p.url
                rec(f"NAV {acc} {vw[0]} {h}",not bad and not [e for e in errs if "PAGEERR" in e],{"url":p.url,"status":resp.status if resp else None,"errs":errs[:3]} if (bad or errs) else p.url)
                for x in p.eval_on_selector_all("a[href^='/']","els=>els.map(e=>e.getAttribute('href'))"):
                    x=x.split("?")[0].split("#")[0]
                    if x not in seen and x not in queue and not re.search(r"/[0-9a-f]{8}-[0-9a-f]{4}",x) and x!="/logout": queue.append(x)
            rec(f"NAV {acc} {vw[0]} tổng trang",True,f"{len(seen)} trang từ {start}")
            c.close()
    b.close()
print("TOTAL",len(R),"FAIL",sum(x[1]=="FAIL" for x in R))
