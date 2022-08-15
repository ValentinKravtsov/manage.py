import MySQLdb


def write_db(db, table, status):
    db = MySQLdb.connect(host="localhost", user="root", passwd="", db=db, charset='utf8')
    cursor = db.cursor()
    message = f"INSERT INTO {table}(status) VALUES ('{status}')"
    cursor.execute(message)

    db.commit()
    db.close()

def read_db(db, table):
    db = MySQLdb.connect(host="localhost", user="root", passwd="", db=db, charset='utf8')
    cursor = db.cursor()
    message = f"SELECT date,status FROM `{table}` ORDER BY id DESC LIMIT 3"
    cursor.execute(message)
    results = cursor.fetchmany(size=3)
    db.close()
    return results
