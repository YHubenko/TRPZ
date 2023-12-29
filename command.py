class Command:
    def execute(self):
        pass


class DisplayFileListCommand(Command):
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        self.editor.display_file_list()


class CreateNewFileCommand(Command):
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        self.editor.create_new_file()


class OpenDatabaseFileCommand(Command):
    def __init__(self, editor):
        self.editor = editor

    def execute(self):
        file_name = input("Enter the name of the file: ")
        self.editor.open_database_file(file_name)


class ProcessBookmarksCommand:
    def __init__(self, text_editor):
        self.text_editor = text_editor

    def execute(self):
        self.text_editor.process_bookmarks_template_method()
