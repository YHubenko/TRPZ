import os
from abc import abstractmethod, ABC


class Observer(ABC):
    @abstractmethod
    def update(self, hint_text):
        pass


class PathSubject:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, file_path):
        for observer in self.observers:
            observer.update(file_path)


class EditorObserver(Observer):
    def update(self, changes):
        print(f"Editor received an update: {changes}")

    def start_edit_mode(self):
        print("Entering edit mode. Type '/finish' to exit editing.")

    def end_edit_mode(self):
        print("Exiting edit mode.")

    def open_file_by_path(self, file_path):
        print(f"Opening file by path: {file_path}")


class PathObserver(Observer):
    def __init__(self, editor):
        self.editor = editor

    def update(self, file_path):
        if file_path and os.path.exists(file_path):
            self.editor.open_file_by_path(file_path)