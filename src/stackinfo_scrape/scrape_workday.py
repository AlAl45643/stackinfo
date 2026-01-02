import requests


def _get_tor_session():
    session = requests.session()
    session.proxies = {
        "http": "socks5://127.0.0.1:9050",
        "https": "socks5://127.0.0.1:9050",
    }
    return session



# create location
# loop over uri
# loop over job posting
# add tech count to list for job posting
# add stack count to list for job posting
# return tech and stack list
def _get_wday_data(day, wday_urls, techs, locations):
    pass


# create session
# retrieve wday technology count list
# retrieve wday stack count list
# return technology and stack list
def parse_wday_urls(day, wday_urls, techs, locations):
    pass
