# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "playwright",
# ]
# ///
from playwright.sync_api import sync_playwright
import re
import sys


def _check_workday_endpoint(url):
    """Check if url is valid workday jobs endpoint."""
    pattern = re.compile(".+?/wday/cxs/.+?/jobs")
    return re.match(pattern, url)


def _retrieve_endpoints(
    search_url, playwright, total_cycles, start_offset, validate_endpoint
):
    """Retrieve links from url if valid with validate_endpoint."""
    browser = playwright.chromium.launch(
        headless=False, proxy={"server": "socks5://127.0.0.1:9050"}
    )

    page = browser.new_page()
    endpoints = []

    try:
        for cycles in range(start_offset, total_cycles):
            page.goto(search_url)

            # navgiate through pagination
            for j in range(0, cycles):
                page.click("text='Next'")
                page.wait_for_timeout(1000)

            # retrieve workday job page urls
            urls = []
            elements = page.query_selector_all(".result__url")
            if elements == []:
                raise Exception("Elements are empty.")
            for element in elements:
                urls.append(str.strip(element.text_content()))

            # collect endpoints from workday job pages
            for url in urls:
                page.goto(f"https://{url}")
                page.on(
                    "request",
                    lambda request: endpoints.append(request.url)
                    if validate_endpoint(str(request))
                    else None,
                )

                # wait for request to complete
                page.wait_for_timeout(3000)

        return list(set(endpoints))  # return only unique urls
    except Exception as e:
        print(e)
        return list(set(endpoints)), cycles
    finally:
        page.close()


def _retrieve_workday_endpoints(cycles, offset):
    """Retrieve workday uris."""
    search_url = "https://html.duckduckgo.com/html?q=site%3Amyworkdayjobs.com&ia=web"
    with sync_playwright() as playwright:
        result = _retrieve_endpoints(
            search_url, playwright, cycles, offset, _check_workday_endpoint
        )
        return result


def main(cycles, offset) -> None:
    """Retrieve workday uris."""
    result = _retrieve_workday_endpoints(cycles, offset)
    print(result)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
