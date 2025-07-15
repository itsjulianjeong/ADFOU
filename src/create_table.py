import os
import sqlite3

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.abspath(os.path.join(BASE_DIR, "../database/store_analysis.db"))

def create_tables(db_path=DB_PATH):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    # 메뉴 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price INTEGER NOT NULL,
            display_order INTEGER DEFAULT 100
        )
    """)

    # 판매 기록 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sex TEXT NOT NULL,
            age_group TEXT NOT NULL,
            menu_id INTEGER NOT NULL,
            order_id TEXT,  --  주문 단위 식별자
            FOREIGN KEY (menu_id) REFERENCES menu(id)
        )
    """)
    
    # master 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            sex TEXT,
            age_group TEXT,
            menu_id INTEGER,
            FOREIGN KEY (menu_id) REFERENCES menu(id)
        )
    """)

    conn.commit()
    conn.close()
    print("DB 테이블 생성 완료")

if __name__=="__main__":
    create_tables()