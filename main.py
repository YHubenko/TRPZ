from psycopg2 import sql
from DatabaseConnection import get_database_connection, conn

cur = conn.cursor()

def insert_col(table_name, data):
    insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(sql.Identifier, data.keys())),
        sql.SQL(', ').join(sql.Placeholder() * len(data))
    )
    cur.execute(insert_query, list(data.values()))
    conn.commit()


data_to_insert = {
    "name": "table",
    "func": "<table></table>"
}
insert_col("macros", data_to_insert)

cur.execute('SELECT * FROM macros')
result = cur.fetchall()
print(result)

cur.close()
conn.close()