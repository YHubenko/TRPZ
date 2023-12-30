class Snippet:
    def __init__(self, id, name, content):
        self.id = id
        self.name = name
        self.content = content


class SnippetFlyweightFactory:
    _snippets = {}

    @classmethod
    def get_snippet(cls, name, content, database_strategy=None):
        if name not in cls._snippets:
            # If snippet is not in the local cache, try fetching it from the database
            if database_strategy:
                db_snippet = database_strategy.get_snippet_by_name(name)
                if db_snippet:
                    snippet = Snippet(name=name, content=db_snippet.content)
                    cls._snippets[name] = snippet
                    return snippet

            # If snippet is not found in the database, create a new one
            snippet = Snippet(name=name, content=content)
            cls._snippets[name] = snippet
            return snippet
        else:
            return cls._snippets[name]
