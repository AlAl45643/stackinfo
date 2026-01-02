# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "playwright",
# ]
# ///
from playwright.sync_api import sync_playwright, Playwright
import re
import sys


def _check_greenhouse_url(url):
    """Check if url is valid greenhouse jobs endpoint."""
    pattern = re.compile("^https://job-boards.greenhouse.io/.+/$")
    return re.match(pattern, url)


def _retrieve_endpoints(
        search_url, playwright, total_cycles, offset, validate_endpoint
):
    """Retrieve links from url if valid with validate_endpoint."""
    browser = playwright.chromium.launch(
        headless=False, proxy={"server": "socks5://127.0.0.1:9050"}
    )
    page = browser.new_page()
    uris = []
    try:
        page.goto(search_url)
        for offset in range(0, offset):
            page.wait_for_timeout(1000)
            # navgiate to next page
            page.click("text='Next'")
            
        for cycles in range(0, total_cycles):
            page.wait_for_timeout(1000)

            # retrieve greenhouse job page urls
            elements = page.query_selector_all(".result__url")

            if elements == []:
                raise Exception("Elements are empty.")
            for element in elements:
                path = str.strip(element.text_content())
                uri = f"https://{path}/"
                if _check_greenhouse_url(uri):
                    uris.append(uri)

            # navgiate to next page
            page.click("text='Next'")

        return list(set(uris))  # return only unique urls
    except Exception as e:
        print(e)
        return list(set(uris)), cycles
    finally:
        page.close()


def _retrieve_greenhouse_endpoints(cycles, offset):
    """Retrieve greenhouse uris."""
    search_url = (
        "https://html.duckduckgo.com/html?q=site%3Ajob-boards.greenhouse.io&ia=web"
    )
    with sync_playwright() as playwright:
        result = _retrieve_endpoints(
            search_url, playwright, cycles, offset, _check_greenhouse_url
        )
    return result


def main(cycles, offset) -> None:
    """Retrieve greenhouse uris."""
    result = _retrieve_greenhouse_endpoints(cycles, offset)
    print(result)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))



