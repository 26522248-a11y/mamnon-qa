"""Helper đăng nhập dùng chung cho e2e. A2: phụ huynh lần đầu mở app bị hỏi 'Cho cô đăng hình con lên nhóm lớp?' (modal chặn,
data-testid=consent-ask) – login_ui tự trả lời một lần (mặc định 'Có'; consent=False → 'Không'; consent=None → để nguyên).
Hoặc gọi ensure_consent_api() trước khi mở UI để bỏ modal bằng API (ghi 1 dòng Lịch sử thay đổi/bé)."""
import requests
def login_ui(page,web,user,pw,consent=True,wait=3500):
    page.goto(web+"/login",timeout=90000); page.fill("input[autocomplete=username]",user); page.fill("input[type=password]",pw); page.click("button"); page.wait_for_timeout(wait)
    if consent is not None: answer_consent(page,consent)
    return page
def answer_consent(page,consent=True,tries=5):
    """Trả lời modal A2 nếu đang hiện (mỗi bé chưa hỏi 1 lần). Trả về số lần đã bấm."""
    n=0
    for _ in range(tries):
        m=page.locator("[data-testid=consent-ask]")
        try: m.wait_for(state="visible",timeout=1500)
        except Exception: break
        page.click("[data-testid=consent-yes]" if consent else "[data-testid=consent-no]"); page.wait_for_timeout(800); n+=1
    return n
def ensure_consent_api(api,token,consent=True):
    """API: bé nào asked=false thì PUT /children/{id}/photo-consent. Trả về danh sách childId đã trả lời."""
    H={"Authorization":"Bearer "+token}; done=[]
    for k in requests.get(api+"/children",headers=H).json().get("items",[]):
        r=requests.get(api+f"/children/{k['id']}/photo-consent",headers=H)
        if r.ok and r.json().get("asked") is False:
            requests.put(api+f"/children/{k['id']}/photo-consent",headers=H,json={"consent":consent}); done.append(k["id"])
    return done
