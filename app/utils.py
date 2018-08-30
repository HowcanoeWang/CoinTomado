import requests
from bs4 import BeautifulSoup
from verlib import NormalizedVersion

import version

version_url = 'https://www.sigmameow.com/app/wiz_statistics/version.html'
zip_url_base = 'https://www.sigmameow.com/app/wiz_statistics/'


def getHtml(url):
    """
    Using `requests` download html.

    Parameters
    ----------
    url : string 
        target url

    Returns
    -------
    string
        target html page
    """

    r = requests.get(version_url, timeout=2)
    return r.text


def getNetVersion(html):
    """
    From html get the the newest version (network version) number.

    Parameters
    ----------
    html : string
        target html page

    Returns
    -------
    string 
        the network version number
    """

    soup = BeautifulSoup(html, 'html.parser')
    NetVersion = soup.title.string
    return NetVersion


def versionCompared(netVersion):
    """
    Compare version number to check it whether or not need update.

    Parameters
    ----------
    netVersion : string
        the network version

    Returns
    -------
    bool 
        check program whether need update
    """

    currentVersion = NormalizedVersion(version.__version__)
    netVersion = NormalizedVersion(netVersion)
    flag = False
    if netVersion > currentVersion:
        flag = True
    return flag


def update():
    """
    Check it whether or not need update, 
    if yes than return a new version link.

    Returns
    -------
    string 
        new version download link
    """

    html = getHtml(version_url)
    netVersion = getNetVersion(html)
    res = versionCompared(netVersion)

    if res:
        zip_url = zip_url_base + "wizstat_{}.zip".format(netVersion)

        return zip_url
