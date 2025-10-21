import requests
import os
import json

file = "ids.json"
Notification_API = "https://api-community.plaync.com/tl/board/notice_ko/noticeArticle"
#Board_API = r"https://api-community.plaync.com/tl/board/notice_ko/article/search/moreArticle?isVote=true&moreSize=1&moreDirection=BEFORE&previousArticleId=0"
WEBHOOKS = os.getenv("DISCORD_WEBHOOKS", "").split(",")
WEBHOOKS = [w.strip() for w in WEBHOOKS if w.strip()]

# -------- Google Translate API --------
def google_translate(text, source="auto", target="en"):
    url = (
        "https://translate.googleapis.com/translate_a/single?client=gtx"
        f"&sl={source}&tl={target}&dt=t&q={requests.utils.quote(text)}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data[0][0][0]  # Translated text
        except Exception:
            return None
    return None


# -------- ID Storage --------
def getId():
    if os.path.exists(file):
        with open(file, encoding="utf-8") as f:
            try:
                return set(json.load(f))  # use a set for fast lookup
            except json.JSONDecodeError:
                return set()
    return set()


def setId(id_set):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(list(id_set), f, indent=0, ensure_ascii=False)


# -------- Fetch notices --------
def getContentList():
    response = requests.get(Notification_API)
    if response.status_code == 200:
        return response.json().get("noticesList", [])
    return []


# -------- Post to Discord --------
def postContent(title, description, id, color=0x2ECC71):
    translated_title = google_translate(title, "ko", "en")
    if not translated_title:
        translated_title = title
    translated_summary = google_translate(description, "ko", "en")
    if not translated_summary:
        translated_summary = description

    print(f"https://tl.plaync.com/ko-kr/board/notice/view?articleId={id}&isNotice=1")

    payload = {
        "embeds": [
            {
                "title": translated_title,
                "description": translated_summary,
                "url": f"https://tl.plaync.com/ko-kr/board/notice/view?articleId={id}&isNotice=1",
                "color": color,
                "footer": {"text": "Throne and Liberty Notices"},
            }
        ]
    }
    for WEBHOOK in WEBHOOKS:
        r = requests.post(WEBHOOK, json=payload)
        if r.status_code != 204:
            return False
    return True


def main():
    solvedContent = getId()
    data = getContentList()

    for content in data:
        content = content.get("articleMeta")
        article_id = content.get("id")
        title = content.get("title", "No title")
        summary = content.get("summary", "No summary")

        if article_id not in solvedContent:
            status = postContent(title, summary, article_id)
            if status == True:
                solvedContent.add(article_id)
            else:
                print("Error in at least one response! Try again later.")

    setId(solvedContent)

if __name__ == "__main__":
    main()