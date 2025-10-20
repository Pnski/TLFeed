import requests, json, os

API = "https://api-community.plaync.com/tl/board/notice_ko/article/search/moreArticle?isVote=true&moreSize=1&moreDirection=BEFORE&previousArticleId=0"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def main():
    state_file = "last_id.txt"

    # Get stored last_id if it exists
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            last_id = f.read().strip()
    else:
        last_id = None

    data = requests.get(API).json().get("data", [])
    if not data:
        print("No data from API")
        return

    latest = data[0]
    article_id = str(latest["articleId"])
    title = latest["title"]
    url = f"https://tl.plaync.com/ko-kr/board/notice/view?articleId={article_id}"

    if article_id != last_id:
        payload = {
            "embeds": [
                {
                    "title": title,
                    "url": url,
                    "color": 0x2ECC71,
                    "footer": {"text": "Throne and Liberty Notices"},
                }
            ]
        }
        r = requests.post(WEBHOOK, json=payload)
        if r.status_code == 204:
            print(f"Posted new article: {title}")
        else:
            print(f"Discord error: {r.text}")

        with open(state_file, "w") as f:
            f.write(article_id)
    else:
        print("No new articles.")

if __name__ == "__main__":
    main()