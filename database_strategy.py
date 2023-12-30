import psycopg2


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

    def create_file_in_database(self, file_name, file_content):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO text_files (file_name, content) VALUES (%s, %s)", (file_name, file_content))
            self.connection.commit()
        else:
            raise Exception("Not connected to the database.")

    def update_file_in_database(self, file_name, file_content):
        if self.connection:
            file_id = self.get_file_id(file_name)

            if file_id is not None:
                with self.connection.cursor() as cursor:
                    cursor.execute("UPDATE text_files SET content = %s WHERE id = %s", (file_content, file_id))
                self.connection.commit()
            else:
                raise Exception("Failed to get file_id for update.")
        else:
            raise Exception("Not connected to the database.")

    def save_to_database(self, file_name, file_content):
        if self.connection:
            if self.get_file_id(file_name) is not None:
                self.update_file_in_database(file_name, file_content)
            else:
                self.create_file_in_database(file_name, file_content)
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

    def delete_all_files(self):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM text_files")
        self.connection.commit()

    def delete_file(self, file_id):
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM text_files WHERE id = %s", (file_id,))
        self.connection.commit()
