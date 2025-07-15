# 매달 1일 실행

import os
import sqlite3
from datetime import datetime

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.abspath(os.path.join(BASE_DIR, "../database/store_analysis.db"))

# Yearly VIEW
def create_yearly_view(year: str, db_path=DB_PATH):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    view_name=f"view_{year}"
    cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
    cursor.execute(f"""
        CREATE VIEW {view_name} AS
        SELECT * FROM sales
        WHERE strftime('%Y', timestamp)='{year}'
    """)
    conn.commit()
    conn.close()
    print(f"{view_name} 뷰 생성 완료")

# Monthly VIEW
def create_monthly_view(year: str, month: str, db_path=DB_PATH):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    view_name=f"view_{year}{month}"
    cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
    cursor.execute(f"""
        CREATE VIEW {view_name} AS
        SELECT * FROM sales
        WHERE strftime('%Y', timestamp)='{year}'
        AND strftime('%m', timestamp)='{month}'
    """)
    conn.commit()
    conn.close()
    print(f"{view_name} 뷰 생성 완료")

# 오늘 날짜 기준으로 월별 뷰 자동 생성
def create_monthly_view_for_today(db_path=DB_PATH):
    today=datetime.today()
    year=str(today.year)
    month=f"{today.month:02d}"
    create_monthly_view(year, month, db_path)

if __name__=="__main__":
    today=datetime.today()
    create_yearly_view(str(today.year))
    create_monthly_view_for_today()