class Snippet:
    def __init__(self, name, content):
        self.name = name
        self.content = content


class SnippetFlyweightFactory:
    _snippets = {}

    @classmethod
    def get_snippet(cls, name, content):
        if name not in cls._snippets:
            snippet = Snippet(name, content)
            cls._snippets[name] = snippet
        return cls._snippets[name]




