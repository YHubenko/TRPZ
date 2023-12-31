def main():
	db_strategy = PostgreSQLDatabaseStrategy()
	editor = TextEditor()
	editor.run_editor(db_strategy)