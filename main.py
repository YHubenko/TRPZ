from text_editor import TextEditor
from database_strategy import PostgreSQLDatabaseStrategy


def main():
    db_strategy = PostgreSQLDatabaseStrategy()
    editor = TextEditor()
    editor.run_editor(db_strategy)


if __name__ == "__main__":
    main()
