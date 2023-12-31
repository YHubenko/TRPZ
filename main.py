from text_editor import TextEditor
from database_strategy import PostgreSQLDatabaseStrategy
from simple_server import run_server


def main():
    db_strategy = PostgreSQLDatabaseStrategy()
    editor = TextEditor()
    editor.set_database_strategy(db_strategy)

    from threading import Thread
    server_thread = Thread(target=run_server)
    server_thread.start()

    editor.run_editor(db_strategy)

    server_thread.join()


if __name__ == "__main__":
    main()
