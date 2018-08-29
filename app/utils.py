import requests
from bs4 import BeautifulSoup
from verlib import NormalizedVersion

import version

version_url = 'https://www.sigmameow.com/app/wiz_statistics/version.html'
zip_url_base = 'https://www.sigmameow.com/app/wiz_statistics/'


def getHtml(url):
    """using `requests` download html.

    Arguments:
        url {str} -- target url.

    Returns:
        str -- target html page.
    """

    r = requests.get(version_url, timeout=2)
    return r.text


def getNetVersion(html):
    """from html get the the newest version.

    Arguments:
        html {str} -- target html page.

    Returns:
        str -- the newest version.
    """

    soup = BeautifulSoup(html, 'html.parser')
    NetVersion = soup.title.string
    return NetVersion


def versionCompared(netVersion):
    """Compare version number to check whether update.

    Arguments:
        netVersion {str} -- network version

    Returns:
        bool -- check program whether need update.
    """

    currentVersion = NormalizedVersion(version.__version__)
    netVersion = NormalizedVersion(netVersion)
    flag = False
    if netVersion > currentVersion:
        flag = True
    return flag


def update():
    """Return a net work version link.

    Returns:
        str -- download link
    """

    html = getHtml(version_url)
    netVersion = getNetVersion(html)
    res = versionCompared(netVersion)

    if res:
        zip_url = zip_url_base + "wizstat_{}.zip".format(netVersion)

        return zip_url
