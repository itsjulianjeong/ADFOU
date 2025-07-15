# 메뉴 조회
import os
import sqlite3

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.abspath(os.path.join(BASE_DIR, "../../database/store_analysis.db"))

def get_all_menus(db_path=DB_PATH):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    # display_order가 NULL인 경우 대비해 COALESCE 처리
    cursor.execute("""
        SELECT id, name, price FROM menu
        ORDER BY COALESCE(display_order, 100) ASC, id ASC
    """)
    results=cursor.fetchall()

    conn.close()
    return results

def get_menu_by_id(menu_id, db_path=DB_PATH):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    cursor.execute("SELECT id, name, price FROM menu WHERE id=?", (menu_id,))
    result=cursor.fetchone()
    conn.close()
    return result

def get_menu_by_id_from_name(name, db_path=DB_PATH):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    cursor.execute("SELECT id, name, price FROM menu WHERE name=?", (name,))
    result=cursor.fetchone()

    conn.close()
    return result
