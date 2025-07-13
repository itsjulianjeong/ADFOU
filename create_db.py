import sqlite3
import os

# tb 정의
def create_table(cursor, table_name):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            timestamp TEXT,
            gender TEXT,
            age_group TEXT,
            menu_name TEXT,
            quantity INTEGER
        )
    """)

# db 초기화
def initialize_db(year, create_yearly=True, create_monthly=True):
    DB_DIR="database"
    os.makedirs(DB_DIR, exist_ok=True)
    DB_PATH=os.path.join(DB_DIR, "visitor_logs.db")

    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()

    # 전체 master tb
    create_table(cursor, "master")

    # 연도별 master tb
    # 2025master
    if create_yearly:
        create_table(cursor, f"{year}master")

    # 월별 tb
    # 202501
    if create_monthly:
        for m in range(1, 13):
            table_name=f"{year}{m:02d}"
            create_table(cursor, table_name)

    conn.commit()
    conn.close()
    print(f"{year}년 기준 테이블 생성 완료 ({DB_PATH})")

if __name__=="__main__":
    year=input("생성할 연도를 입력하세요 (YYYY): ").strip()
    
    if not year.isdigit() or len(year) != 4:
        print("!!! 4자리 숫자로 입력하세요 !!!")
    else:
        initialize_db(year)