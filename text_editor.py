import os

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.python import PythonLexer
from pygments.styles import get_style_by_name

from command import CreateNewFileCommand, DisplayFileListCommand, OpenDatabaseFileCommand, ProcessBookmarksCommand, \
    GoToLineCommand
from hint_strategy import SimpleHintStrategy
from observer import EditorObserver, PathObserver


class TextEditor:
    def __init__(self, file_content="", encoding="utf-8"):
        super().__init__()
        self.current_file_id = None
        self.file_content = file_content
        self.encoding = encoding
        self.bookmark_strategy = None
        self.macro_strategy = None
        self.snippet_strategy = None
        self.hint_strategy = None
        self.database_strategy = None
        self.hints = []
        self.macros = []
        self.snippets = []
        self.commands = {}
        self.local_hints = []
        self.current_file_name = None
        self.current_file_path = None
        self.local_hint_id = 0
        self.observers = [EditorObserver()]
        self.pygments_style = get_style_by_name('default').styles

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, changes):
        for observer in self.observers:
            observer.update(changes)

    def open_file_by_path(self, file_path):
        try:
            self.current_file_path = file_path
            file_name = os.path.basename(file_path)
            file_name_without_extension = os.path.splitext(file_name)[0]

            with open(file_path, 'r') as file:
                self.file_content = file.read()

            if self.database_strategy and not self.database_strategy.connection:
                self.database_strategy.connect({
                    "dbname": "trpz",
                    "user": "postgres",
                    "password": "postgres",
                    "host": "localhost",
                    "port": "5432"
                })

            if self.database_strategy:
                if self.database_strategy.get_file_id(file_name_without_extension) is None:
                    self.database_strategy.create_file_in_database(file_name_without_extension, self.file_content)
                else:
                    self.database_strategy.save_to_database(file_name_without_extension, self.file_content)
                self.open_database_file(file_path)

        except Exception as e:
            print(f"An error occurred while opening the file: {e}")

    def go_to_line_template_method(self):
        try:
            line_number = int(input("Enter the line number to go to: "))
            self.display_highlighted_content(self.file_content.split('\n'), line_number)
        except ValueError:
            print("Invalid input. Please enter a valid line number.")

    def display_highlighted_content(self, lines, line_number):
        try:
            line_number = int(line_number)

            highlighted_lines = []
            for i, line in enumerate(lines, start=1):
                if i == line_number:
                    highlighted_lines.append(f"\033[93m{line}\033[0m")
                elif not any(code in line for code in ('\033[93m', '\033[0m')):
                    highlighted_line = highlight(line, PythonLexer(), TerminalFormatter())
                    highlighted_lines.append(highlighted_line.rstrip())
                else:
                    highlighted_lines.append(line)

            print("\nHighlighted Content:")
            print("\n".join(highlighted_lines).strip())
        except ValueError:
            print("Invalid input. Please enter a valid line number.")

    def process_bookmarks_template_method(self):
        if not self.current_file_name:
            print("No file opened. Please open a file first.")
            return

        lines, bookmark_lines = self.find_bookmark_lines()
        print("Processing bookmarks...")
        self.display_bookmarks(lines, bookmark_lines)

    def find_bookmark_lines(self):
        lines = self.file_content.split('\n')
        bookmark_lines = [index for index, line in enumerate(lines) if line.strip().lower() == '/bookmark']
        return lines, bookmark_lines

    def display_bookmarks(self, lines, bookmark_lines):
        if bookmark_lines:
            print("\nBookmarks:")
            for line_number in bookmark_lines:
                print(f"Line Number: {line_number}, Text: {lines[line_number - 1]}")
        else:
            print("No bookmarks found.")

    def set_macro_strategy(self, macro_strategy):
        self.macro_strategy = macro_strategy

    def set_snippet_strategy(self, snippet_strategy):
        self.snippet_strategy = snippet_strategy

    def set_hint_strategy(self, hint_strategy):
        self.hint_strategy = hint_strategy

    def set_database_strategy(self, database_strategy):
        self.database_strategy = database_strategy

    def open_database_file(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            file_name_without_extension = os.path.splitext(file_name)[0]

            if self.database_strategy and not self.database_strategy.connection:
                self.database_strategy.connect({
                    "dbname": "trpz",
                    "user": "postgres",
                    "password": "postgres",
                    "host": "localhost",
                    "port": "5432"
                })

            if self.database_strategy:
                file_content = self.database_strategy.get_file_content(file_name_without_extension)
                if file_content is not None:
                    self.file_content = file_content
                    print(f"File '{file_name_without_extension}' opened successfully. Content:")
                    print(highlight(file_content, PythonLexer(), TerminalFormatter()))
                    self.current_file_id = self.database_strategy.get_file_id(file_name_without_extension)
                    self.current_file_name = file_name_without_extension
                else:
                    print(f"File '{file_name_without_extension}' not found in the database.")
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

    def edit_mode(self):
        if not self.current_file_name:
            print("No file opened. Please open a file first.")
            return

        print("Entering edit mode. Type '/finish' to exit editing.")

        edit_option = input("Do you want to (R)eplace the entire content or (A)dd new text? ").lower()

        while True:
            new_text = input("")
            if new_text.strip().lower() == '/finish':
                self.update_file_in_database()
                break
            elif new_text.strip().lower() == '/hint':
                hint_text = input("Enter hint text: ")
                self.local_hints.append({'hint_text': hint_text})
                changes = f"Hint added: {hint_text}"
                self.notify_observers(changes)
            else:
                if edit_option == 'r':
                    self.file_content = new_text + '\n'
                    edit_option = None
                else:
                    self.file_content += new_text + '\n'

    def update_file_in_database(self):
        if self.database_strategy and self.current_file_name:
            file_name = self.current_file_name
            file_content = self.file_content
            current_file_path = None
            file_name_without_extension = None
            if self.current_file_path is not None:
                current_file_path = self.current_file_path
                file_name_by_path = os.path.basename(current_file_path)
                file_name_without_extension = os.path.splitext(file_name_by_path)[0]

            try:
                file_content = file_content.replace('/bookmark', '')

                if file_name_without_extension == file_name:
                    with open(current_file_path, 'w') as file:
                        file.write(self.file_content)
                self.database_strategy.save_to_database(file_name, file_content)
                for hint in self.local_hints:
                    self.database_strategy.save_hint_to_database(file_name, hint['hint_text'])
                print(f"File '{file_name}' updated and saved to the database successfully.")
            except Exception as e:
                print(f"An error occurred while saving to the database: {e}")
        else:
            print("Database strategy not set or no file is currently open.")

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

                print("Enter the content of the file. Enter '/finish' on a new line to finish:")
                lines = []
                while True:
                    line = input()
                    if line.strip().lower() == '/finish':
                        break
                    elif line.strip().lower() == '/hint':
                        hint_text = input("Enter text for hint: ")
                        self.local_hint_id += 1
                        self.local_hints.append({
                            'hint_id': self.local_hint_id,
                            'hint_text': hint_text
                        })
                        print(f"Hint '{hint_text}' saved.")
                        continue
                    lines.append(line)

                self.file_content = '\n'.join(lines)

                self.database_strategy.save_to_database(file_name, self.file_content)
                self.current_file_id = self.database_strategy.get_file_id(file_name)
                for hint in self.local_hints:
                    self.database_strategy.save_hint_to_database(file_name, hint['hint_text'])
                print(f"File '{file_name}' created and saved to the database successfully.")
            else:
                print("Database strategy not set. Unable to save to the database.")
        except Exception as e:
            print(f"An error occurred while saving to the database: {e}")

    def display_prompts(self):
        print("\nWelcome to the Text Editor!")
        print("Type 'menu' to display the menu.")
        print("Type 'exit' to exit.")

    def display_menu(self):
        print("\nMenu:")
        print("1. Create a new file")
        print("2. Open an existing file")
        print("3. Display current content")
        print("4. Display File List")
        print("5. Open File from Database")
        print("Type 'goto' to go to certain line")
        print("Type 'bookmarks' to check bookmarks in the current file")
        print("Type 'hints' to check hints for the current file")
        print("Type 'edit' to edit current file")

    def run_editor(self, db_strategy):
        self.set_database_strategy(db_strategy)
        hint_strategy = SimpleHintStrategy(self)
        self.add_observer(hint_strategy)
        self.add_observer(EditorObserver())
        path_observer = PathObserver(self)
        self.add_observer(path_observer)

        self.set_command("1", CreateNewFileCommand(self))
        self.set_command("4", DisplayFileListCommand(self))
        self.set_command("5", OpenDatabaseFileCommand(self))
        self.set_command("bookmarks", ProcessBookmarksCommand(self))
        self.set_command("goto", GoToLineCommand(self))
        self.display_prompts()

        while True:
            user_input = input("Enter a command: ")

            if user_input == "menu":
                self.display_menu()
            elif user_input in self.commands:
                self.commands[user_input].execute()
            elif user_input == "2":
                path = input("Enter path to file: ")
                self.open_file_by_path(path)
            elif user_input == "3":
                print("Current text content:")
                print(highlight(self.file_content, PythonLexer(), TerminalFormatter()))
            elif user_input == "edit":
                self.edit_mode()
            elif user_input == "exit":
                print("Exiting the text editor.")
                break
            elif user_input == "hints":
                if self.current_file_id:
                    hints = self.database_strategy.get_hints_by_file_id(self.current_file_id)
                    for hint in hints:
                        print(f"Hint ID: {hint['hint_id']}, Hint Text: {hint['hint_text']}")
                else:
                    print("Choose a file first!")
            elif user_input == "goto":
                self.go_to_line_template_method()
            else:
                print("Unknown command. Type 'menu' for the menu or 'exit' to exit.")

    def set_command(self, command_key, command):
        self.commands[command_key] = command
