__author__ = 'jiayiliu'

import urllib.request as ur
from html.parser import HTMLParser


class WebPage:
    def __init__(self, url, isURL=True):
        """
        Create connection to read html page.
        :param url: URL or file path
        :param isURL: True for URL, False for file
        :return: Webpage class contains html source content
        """
        if isURL:
            self.web = ur.urlopen(url)
            self.doc = str(self.web.read())
        else:
            with open(url, 'r') as f:
                self.doc = ''.join(f.readlines())


class TargetHTMLParser(HTMLParser):
    def __init__(self, is_target):
        """
        Create HTML Parser to extract download file list

        :param is_target: function to determine whether to download file
        :return:
        """
        super().__init__()
        self.download = []
        self.is_target = is_target

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        for attr in attrs:
            if 'href' != attr[0]:
                continue
            if is_target(attr[1]):
                self.download.append(attr[1])


class downloadFile():
    def __init__(self, link, path='./', file=None):
        """
        initiate download file class

        :param link: download url
        :param path: download path, default ./
        :param file: download file default url file name
        """
        if file is None:
            self.file = path + link.split('/')[-1]
        else:
            self.file = path + file
        self.link = link

    def download(self):
        """
        initiate downloading
        """
        ur.urlretrieve(self.link, self.file)

def is_target(url):
    """
    simple function to determine whether the given link is download target
    :param url: download link to be determined
    :return: True / False
    """
    if name[-3:] == 'pdf' and name[:4] == 'http':
        return True
    else:
        return False

if __name__ == "__main__":
    w = WebPage("./temp.html", isURL=False)
    parser = TargetHTMLParser(is_target)
    parser.feed(w.doc)
    for name in parser.download:
        downloadFile(name, path='./').download()