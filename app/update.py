from verlib import NormalizedVersion
import version
import download
import utils


def versionCompared(currentVersion, netVersion):
    """Compare version number to check whether update.

    Arguments:
        currentVersion {str} -- current version
        netVersion {str} -- network version

    Returns:
        bool -- check program whether need update.
    """

    currentVersion = NormalizedVersion(currentVersion)
    netVersion = NormalizedVersion(netVersion)
    flag = False
    if netVersion > currentVersion:
        flag = True
    return flag


def update():
    
    html = download.getHtml(download.version_url)
    netVersion = download.getNetVersion(html)
    currentVersion = version.__version__
    if versionCompared(currentVersion, netVersion):
        zip_file = download.download(netVersion)
        utils.extractzip(zip_file)


def main():
    pass


if __name__ == '__main__':
    main()
