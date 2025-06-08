import  sqlite3

db = sqlite3.connect("NaCGame.db")  # можно придумать своё название, только потом ещё везде поменять
cursor = db.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY,
        full_name VARCHAR,
        username VARCHAR,
        score BIGINT
        )
""")

db.commit()
db.close()
