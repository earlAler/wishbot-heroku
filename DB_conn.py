import config
import psycopg2
import uuid

try:

    conn = psycopg2.connect(host=config.host,
                            user=config.user,
                            password=config.password,
                            port=config.port,
                            database=config.db_name)
    conn.autocommit = True

    uid1 = str(uuid.uuid1())
    uid = str(uid1)
    print(uid)

    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT COUNT(*) FROM "BoxWishes";"""
        )
        count_wish = cursor.fetchone()

    c = count_wish[0]
    print("frfr ", count_wish[0])
except Exception as exc:
    print("Error while working: ", exc)
finally:
    if conn:
        conn.close()
        print("Connection closed")