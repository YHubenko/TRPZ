from abc import abstractmethod
from observer import Observer


class HintStrategy(Observer):
    @abstractmethod
    def get_hints(self, hints):
        pass


class SimpleHintStrategy(HintStrategy):
    def __init__(self, editor):
        self.editor = editor
        self.hint_text = ""

    def get_hints(self, hints):
        return [hint.hint_text for hint in hints]

    def update(self, hint_text):
        if hint_text and hint_text.strip().lower() == '/hint':
            self.hint_text = hint_text
            print(f"Підказка додана: {self.hint_text}")


class AdvancedHintStrategy(HintStrategy):
    def get_hints(self, hints):
        pass