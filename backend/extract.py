from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
import json
from pathlib import Path

urls = ["https://nextjs.org/docs/app/getting-started/installation",
        "https://nextjs.org/docs/app/getting-started/project-structure",
        "https://nextjs.org/docs/app/getting-started/layouts-and-pages",
        "https://nextjs.org/docs/app/getting-started/layouts-and-pages",
        "https://nextjs.org/docs/app/getting-started/server-and-client-components",
        "https://nextjs.org/docs/app/getting-started/partial-prerendering",
        "https://nextjs.org/docs/app/getting-started/fetching-data",
        "https://nextjs.org/docs/app/getting-started/updating-data",
        "https://nextjs.org/docs/app/getting-started/caching-and-revalidating",
        "https://nextjs.org/docs/app/getting-started/error-handling",
        "https://nextjs.org/docs/app/getting-started/css",
        "https://nextjs.org/docs/app/getting-started/images",
        "https://nextjs.org/docs/app/getting-started/fonts",
        "https://nextjs.org/docs/app/getting-started/metadata-and-og-images",
        "https://nextjs.org/docs/app/getting-started/route-handlers-and-middleware",
        "https://nextjs.org/docs/app/getting-started/deploying",
        "https://nextjs.org/docs/app/getting-started/upgrading",
        "https://nextjs.org/docs/app/guides/analytics",
        "https://nextjs.org/docs/app/guides/authentication",
        "https://nextjs.org/docs/app/guides/backend-for-frontend",
        "https://nextjs.org/docs/app/guides/caching",
        "https://nextjs.org/docs/app/guides/ci-build-caching",
        "https://nextjs.org/docs/app/guides/content-security-policy",
        "https://nextjs.org/docs/app/guides/css-in-js",
        "https://nextjs.org/docs/app/guides/custom-server",
        "https://nextjs.org/docs/app/guides/data-security",
        "https://nextjs.org/docs/app/guides/debugging",
        "https://nextjs.org/docs/app/guides/draft-mode",
        "https://nextjs.org/docs/app/guides/environment-variables",
        "https://nextjs.org/docs/app/guides/forms",
        "https://nextjs.org/docs/app/guides/incremental-static-regeneration",
        "https://nextjs.org/docs/app/guides/instrumentation",
        "https://nextjs.org/docs/app/guides/internationalization",
        "https://nextjs.org/docs/app/guides/json-ld",
        "https://nextjs.org/docs/app/guides/lazy-loading",
        "https://nextjs.org/docs/app/guides/local-development",
        "https://nextjs.org/docs/app/guides/mdx",
        "https://nextjs.org/docs/app/guides/memory-usage",
        "https://nextjs.org/docs/app/guides/migrating/app-router-migration",
        "https://nextjs.org/docs/app/guides/migrating/from-create-react-app",
        "https://nextjs.org/docs/app/guides/migrating/from-vite",
        "https://nextjs.org/docs/app/guides/multi-tenant",
        "https://nextjs.org/docs/app/guides/multi-zones",
        "https://nextjs.org/docs/app/guides/open-telemetry",
        "https://nextjs.org/docs/app/guides/package-bundling",
        "https://nextjs.org/docs/app/guides/prefetching",
        "https://nextjs.org/docs/app/guides/production-checklist",
        "https://nextjs.org/docs/app/guides/progressive-web-apps",
        "https://nextjs.org/docs/app/guides/redirecting",
        "https://nextjs.org/docs/app/guides/sass",
        "https://nextjs.org/docs/app/guides/scripts",
        "https://nextjs.org/docs/app/guides/self-hosting",
        "https://nextjs.org/docs/app/guides/single-page-applications",
        "https://nextjs.org/docs/app/guides/static-exports",
        "https://nextjs.org/docs/app/guides/tailwind-css",
        "https://nextjs.org/docs/app/guides/third-party-libraries"
    ]

existing_urls = set()

docs_path = Path("next_js_docs.jsonl")

if docs_path.exists():
    with open(docs_path,"r",encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if "url" in data:
                    existing_urls.add(data["url"])
            except Exception as e:
                print(f"Error while inseting existing urls: {e}")


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
    
with open("next_js_docs.jsonl","a",encoding="utf-8") as f:
    for url in urls:
        if url in existing_urls:
            print(f"url already extracted: {url}")
        else:
            try:
                content = fetchPage(url)
                json.dump({"url": url, "content": content},f)
                f.write("\n")
                print(f"saved file for url: {url}")
            except Exception as e:
                print(f"Error saving file with url: {url} -- {e}")