from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path="/usr/bin/google-chrome"); p=b.new_page()
    p.on("console",lambda m: m.type=="error" and print("CONSOLE",m.text[:300]))
    p.on("pageerror",lambda e: print("PAGEERR",str(e)[:300]))
    for path in ["/login","/children","/users","/reports"]:
        if path=="/children":
            p.fill("input[autocomplete=username]","admin"); p.fill("input[type=password]","123456"); p.click("button"); p.wait_for_timeout(2500)
        p.goto("http://localhost:3000"+path); p.wait_for_timeout(2000); print(path, p.url, p.inner_text("body")[:80].replace("\n"," "))
    b.close()
