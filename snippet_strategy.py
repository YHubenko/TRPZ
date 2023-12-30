class SnippetStrategy:
    def apply_snippets(self, snippets):
        raise NotImplementedError("Subclasses must implement this method.")


class DefaultSnippetStrategy(SnippetStrategy):
    def apply_snippets(self, snippets):
        pass
