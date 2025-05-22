import sqlite3
import pymysql

# SQLite 연결
sqlite_conn = sqlite3.connect("/Users/seongjujeong/Downloads/real_estate_final.db")
sqlite_cursor = sqlite_conn.cursor()

# MySQL 연결
mysql_conn = pymysql.connect(
    host="127.0.0.1",
    port=3307,
    user="root",
    password="1234",
    db="malhaebang",
    charset="utf8mb4"

)
mysql_cursor = mysql_conn.cursor()

# 데이터 조회
sqlite_cursor.execute("SELECT * FROM house")
rows = sqlite_cursor.fetchall()

# MySQL에 INSERT
insert_sql = """
INSERT INTO house (
    title, price, address, floor, deposit_type,
    management_fee, availabe_from, house_num, agent_comm, agent_info,
    rooms_count, options, posted_at, gu, dong, img_url, area_size,
    direction, built_date, parking, building_type, house_feature,
    house_explanations, apt_name
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# house_id는 제외
rows = [row[1:] for row in rows]

mysql_cursor.executemany(insert_sql, rows)

mysql_conn.commit()

print(f"{mysql_cursor.rowcount} rows inserted.")

# 연결 종료
sqlite_conn.close()
mysql_conn.close()