import psycopg2
from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, hint_text):
        pass


class HintStrategy(Observer):
    @abstractmethod
    def get_hints(self, hints):
        pass


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


class SimpleHintStrategy(HintStrategy):
    def __init__(self, editor):
        self.editor = editor
        self.hint_text = ""

    def get_hints(self, hints):
        return [hint.hint_text for hint in hints]

    def update(self, hint_text):
        self.hint_text = hint_text
        print(f"Підказка додана: {hint_text}")


class AdvancedHintStrategy(HintStrategy):
    def get_hints(self, hints):
        pass


class SyntaxHighlighterStrategy:
    def highlight(self, text):
        pass


class PythonSyntaxHighlighter(SyntaxHighlighterStrategy):
    def highlight(self, text):
        pass


class DatabaseStrategy:
    def connect(self, connection_params):
        pass

    def save_to_database(self, file_content):
        pass


class PostgreSQLDatabaseStrategy(DatabaseStrategy):
    def __init__(self):
        self.connection = None

    def connect(self, connection_params):
        self.connection = psycopg2.connect(**connection_params)

    def save_to_database(self, file_name, file_content):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO text_files (file_name, content) VALUES (%s, %s)", (file_name, file_content))
            self.connection.commit()
        else:
            raise Exception("Not connected to the database.")

    def get_file_list(self):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT file_name FROM text_files ORDER BY file_name ASC")
                files = cursor.fetchall()
            return [{'file_name': file[0]} for file in files]
        else:
            raise Exception("Not connected to the database.")

    def get_file_content(self, file_name):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT content FROM text_files WHERE file_name = %s", (file_name,))
                result = cursor.fetchone()
            return result[0] if result else None
        else:
            raise Exception("Not connected to the database.")

    def save_hint_to_database(self, file_name, hint_text):
        if self.connection:
            file_id = self.get_file_id(file_name)

            if file_id is not None:
                with self.connection.cursor() as cursor:
                    cursor.execute("INSERT INTO hints (hint_text, file_id) VALUES (%s, %s)", (hint_text, file_id))
                self.connection.commit()
            else:
                raise Exception("Failed to get or create file_id.")
        else:
            raise Exception("Not connected to the database.")

    def get_file_id(self, file_name):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id FROM text_files WHERE file_name = %s", (file_name,))
                result = cursor.fetchone()
            return result[0] if result else None
        else:
            raise Exception("Not connected to the database.")

    def get_hints_by_file_id(self, file_id):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id, hint_text FROM hints WHERE file_id = %s", (file_id,))
                hints = cursor.fetchall()
            return [{'hint_id': hint[0], 'hint_text': hint[1]} for hint in hints]
        else:
            raise Exception("Not connected to the database.")


class BookmarkStrategy:
    def process_bookmarks(self, bookmarks):
        pass


class DefaultBookmarkStrategy(BookmarkStrategy):
    def process_bookmarks(self, bookmarks):
        pass


class MacroStrategy:
    def execute_macros(self, macros):
        pass


class DefaultMacroStrategy(MacroStrategy):
    def execute_macros(self, macros):
        pass


class SnippetStrategy:
    def apply_snippets(self, snippets):
        pass


class DefaultSnippetStrategy(SnippetStrategy):
    def apply_snippets(self, snippets):
        pass


class TextEditor:
    def __init__(self, file_content="", encoding="utf-8"):
        self.current_file_id = None
        self.file_content = file_content
        self.encoding = encoding
        self.syntax_highlighter_strategy = None
        self.bookmark_strategy = None
        self.macro_strategy = None
        self.snippet_strategy = None
        self.hint_strategy = None
        self.database_strategy = None
        self.hints = []
        self.bookmarks = []
        self.macros = []
        self.snippets = []
        self.commands = {}
        self.observers = []
        self.local_hints = []
        self.current_file_name = None
        self.local_hint_id = 0

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, hint_text):
        for observer in self.observers:
            observer.update(hint_text)

    def set_syntax_highlighter_strategy(self, syntax_highlighter_strategy):
        self.syntax_highlighter_strategy = syntax_highlighter_strategy

    def set_bookmark_strategy(self, bookmark_strategy):
        self.bookmark_strategy = bookmark_strategy

    def set_macro_strategy(self, macro_strategy):
        self.macro_strategy = macro_strategy

    def set_snippet_strategy(self, snippet_strategy):
        self.snippet_strategy = snippet_strategy

    def set_hint_strategy(self, hint_strategy):
        self.hint_strategy = hint_strategy

    def set_database_strategy(self, database_strategy):
        self.database_strategy = database_strategy

    def open_database_file(self, file_name):
        try:
            if self.database_strategy and not self.database_strategy.connection:
                self.database_strategy.connect({
                    "dbname": "trpz",
                    "user": "postgres",
                    "password": "postgres",
                    "host": "localhost",
                    "port": "5432"
                })

            if self.database_strategy:
                file_content = self.database_strategy.get_file_content(file_name)
                if file_content is not None:
                    self.file_content = file_content
                    print(f"File '{file_name}' opened successfully. Content:")
                    print(file_content)
                    self.current_file_id = self.database_strategy.get_file_id(file_name)
                else:
                    print(f"File '{file_name}' not found in the database.")
            else:
                print("Database strategy not set. Unable to fetch file content.")
        except Exception as e:
            print(f"An error occurred while opening the file from the database: {e}")

    def get_file_content_from_database(self, file_name):
        try:
            with self.database_strategy.connection.cursor() as cursor:
                cursor.execute("SELECT content FROM text_files WHERE file_name = %s", (file_name,))
                result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"An error occurred while getting file content: {e}")
            return None

    def edit_text(self, changes):
        pass

    def execute_syntax_highlighting(self):
        if self.syntax_highlighter_strategy:
            self.syntax_highlighter_strategy.highlight(self.file_content)

    def process_bookmarks(self):
        if self.bookmark_strategy:
            self.bookmark_strategy.process_bookmarks(self.bookmarks)

    def execute_macros(self):
        if self.macro_strategy:
            self.macro_strategy.execute_macros(self.macros)

    def apply_snippets(self):
        if self.snippet_strategy:
            self.snippet_strategy.apply_snippets(self.snippets)

    def get_hints(self):
        if self.hint_strategy:
            self.hints = self.hint_strategy.get_hints(self.hints)
            return self.hints

    def input_text(self):
        while True:
            new_text = input("Enter text: ")
            if new_text.strip().lower() == '/finish':
                break
            elif new_text.strip().lower() == '/hint':
                hint_text = input("Enter hint text: ")
                self.local_hints.append(hint_text)
            else:
                self.file_content += new_text + '\n'

    def display_file_list(self):
        try:
            if self.database_strategy and not self.database_strategy.connection:
                self.database_strategy.connect({
                    "dbname": "trpz",
                    "user": "postgres",
                    "password": "postgres",
                    "host": "localhost",
                    "port": "5432"
                })

            if self.database_strategy:
                files = self.database_strategy.get_file_list()
                print("\nFile List:")
                for file_info in files:
                    print(f"File Name: {file_info['file_name']}")
            else:
                print("Database strategy not set. Unable to fetch file list.")
        except Exception as e:
            print(f"An error occurred while fetching the file list: {e}")

    def create_new_file(self):
        file_name = input("Enter the name of the new file: ")
        self.current_file_name = file_name

        try:
            if self.database_strategy:
                db_params = {
                    "dbname": "trpz",
                    "user": "postgres",
                    "password": "postgres",
                    "host": "localhost",
                    "port": "5432"
                }
                self.database_strategy.connect(db_params)

                # Введення тексту вручну
                print("Enter the content of the file. Enter '/finish' on a new line to finish:")
                lines = []
                while True:
                    line = input()
                    if line.strip().lower() == '/finish':
                        break
                    elif line.strip().lower() == '/hint':
                        hint_text = input("Введіть текст підказки: ")
                        self.local_hint_id += 1
                        # file_id = self.database_strategy.get_file_id(file_name)
                        # self.database_strategy.save_hint_to_database(file_id, hint_text)
                        self.local_hints.append({
                            'hint_id': self.local_hint_id,
                            'hint_text': hint_text
                        })
                        print(f"Підказка '{hint_text}' збережена.")
                        continue
                    lines.append(line)

                # Об'єднання рядків у вміст файла
                self.file_content = '\n'.join(lines)

                # Збереження вмісту у базу даних
                self.database_strategy.save_to_database(file_name, self.file_content)
                self.current_file_id = self.database_strategy.get_file_id(file_name)
                for hint in self.local_hints:
                    self.database_strategy.save_hint_to_database(file_name, hint.hint_text)
                print(f"File '{file_name}' created and saved to the database successfully.")
            else:
                print("Database strategy not set. Unable to save to the database.")
        except Exception as e:
            print(f"An error occurred while saving to the database: {e}")

    def display_prompts(self):
        print("\nWelcome to the Text Editor!")
        print("Type '/menu' to display the menu.")
        print("Type '/exit' to exit.")

    def display_menu(self):
        print("\nMenu:")
        print("1. Create a new file")
        # print("2. Open an existing file")
        print("3. Display current content")
        print("4. Display File List")
        print("5. Open File from Database")
        print("Type '/hints' to check for current file")

    def run_editor(self):
        self.set_command("1", CreateNewFileCommand(self))
        # self.set_command("2", OpenFileCommand(self, ""))
        self.set_command("4", DisplayFileListCommand(self))
        self.set_command("5", OpenDatabaseFileCommand(self))

        while True:
            user_input = input("Enter a command: ")

            if user_input == "/menu":
                self.display_menu()
            elif user_input in self.commands:
                self.commands[user_input].execute()
            elif user_input == "3":
                print("Current text content:", self.file_content)
            elif user_input == "/exit":
                print("Exiting the text editor.")
                break
            elif user_input == "/hints":
                if self.current_file_id:
                    hints = db_strategy.get_hints_by_file_id(self.current_file_id)
                    for hint in hints:
                        print(f"Hint ID: {hint['hint_id']}, Hint Text: {hint['hint_text']}")
                else:
                    print("Choose a file first!")
            else:
                print("Unknown command. Type '/menu' for the menu or '/exit' to exit.")

    def set_command(self, command_key, command):
        self.commands[command_key] = command


editor = TextEditor()
db_strategy = PostgreSQLDatabaseStrategy()
editor.set_database_strategy(db_strategy)
hint_strategy = SimpleHintStrategy(editor)
editor.add_observer(hint_strategy)
editor.display_prompts()
editor.run_editor()
