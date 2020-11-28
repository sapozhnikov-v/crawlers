class CrawlerError(Exception):
    def __init__(self, text):
        self.text = text


class LinkError(CrawlerError):
    def __init__(self, text):
        self.text = text


class ExtractIdError(CrawlerError):
    def __init__(self, text):
        self.text = text


class GetInfoError(CrawlerError):
    def __init__(self, text):
        self.text = text


class RequestError(CrawlerError):
    def __init__(self, text):
        self.text = text
