import requests
from bs4 import BeautifulSoup

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


def download(version):
    """Download network version zip file.

    Arguments:
        version {str} -- network version number

    Returns:
        str -- zip file name
    """

    zip_file = 'wizstat_{}.zip'.format(version)
    zip_url = zip_url_base + zip_file
    r = requests.get(zip_url)
    with open(zip_file, 'w') as f:
        f.write(r.content)

    return zip_file


def main():
    html = getHtml(version_url)
    currentVersion = getNetVersion(html)
    

if __name__ == '__main__':
    main()
