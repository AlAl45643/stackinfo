from playwright.sync_api import sync_playwright, Playwright
import re


def check_workday_endpoint(url):
    pattern = re.compile(".+?/wday/cxs/.+?/jobs")
    return re.match(pattern, url)


def retrieve_links(search, playwright: Playwright, count, offset):
    try:
        chromium = playwright.chromium
        browser = chromium.launch(headless=False)
        page = browser.new_page()
        results = []
        for cycles in range(offset, count):
            page.goto(search)
            for j in range(0, cycles):
                page.click("text='Next'")
                page.wait_for_timeout(2000)
            elements = page.query_selector_all(".result__url")
            if len(elements) == 0:
                raise Exception("Elements is empty.")
            urls = []
            for element in elements:
                urls.append(str.strip(element.text_content()))
            for url in urls:
                page.goto(f"https://{url}")
                page.on("request", lambda request: results.append(
                    request.url) if check_workday_endpoint(str(request)) else None)
                page.wait_for_timeout(3000)
        return list(set(results))
    except BaseException as e:
        print(e)
        return (list(set(results)), cycles)
    finally:
        page.close()


url = "https://html.duckduckgo.com/html?q=site%3Amyworkdayjobs.com&ia=web"
cycles = 10
offset = 0
with sync_playwright() as playwright:
    result = retrieve_links(url, playwright, cycles, offset)
    print(result)
