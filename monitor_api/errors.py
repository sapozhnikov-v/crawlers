class GetSourceError(Exception):
    def __init__(self, text):
        self.text = text


class PostError(Exception):
    def __init__(self, text):
        self.text = text
