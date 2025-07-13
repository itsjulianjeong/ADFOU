import sqlite3

def insert_visitor_log(db_path, table_name, order_id, timestamp, gender, age_group, menu_name, quantity):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    cursor.execute(f"""
        INSERT INTO "{table_name}" (order_id, timestamp, gender, age_group, menu_name, quantity)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (order_id, timestamp, gender, age_group, menu_name, quantity))

    conn.commit()
    conn.close()