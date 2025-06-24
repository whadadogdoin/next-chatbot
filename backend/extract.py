from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
import json

urls = ["https://nextjs.org/docs/app/getting-started/installation",
        "https://nextjs.org/docs/app/getting-started/project-structure",
        "https://nextjs.org/docs/app/getting-started/layouts-and-pages",
        "https://nextjs.org/docs/app/getting-started/layouts-and-pages",
        "https://nextjs.org/docs/app/getting-started/server-and-client-components"
    ]

def fetchPage(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        main = page.query_selector("main")
        html = main.inner_html() if main else "not found"
        browser.close()
        
        soup = BeautifulSoup(html,"html.parser")
        text = soup.get_text()
        idx = text.find("Scroll to top App Router") + len("Scroll to top  App Router Getting Started")
        core_text = text[idx:]
        cleaned_text = re.sub(r'\n\s*\n+','\n\n',core_text)
        stripped = cleaned_text.strip()
        return stripped
    
with open("next-js-docs.jsonl","w",encoding="utf-8") as f:
    for url in urls:
        try:
            content = fetchPage(url)
            json.dump({"url": url, "content": content},f)
            f.write("\n")
            print(f"saved file for url: {url}")
        except Exception as e:
            print(f"Error saving file with url: {url} -- {e}")