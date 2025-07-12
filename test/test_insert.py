# DB 입력 테스트
import os
import sqlite3
from datetime import datetime

base_dir=os.path.dirname(os.path.abspath(__file__))
db_path=os.path.join(base_dir, "../database/visitor_logs.db")

conn=sqlite3.connect(db_path)
cursor=conn.cursor()

# 테스트 데이터
timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
gender="male"
age_group="20s"
menu_name="아메리카노"
quantity=2
# INSERT 문
cursor.execute("""
    INSERT INTO visitor_logs (timestamp, gender, age_group, menu_name, quantity)
    VALUES (?, ?, ?, ?, ?)
""", (timestamp, gender, age_group, menu_name, quantity))

# 저장 및 종료
conn.commit()
conn.close()

print("입력완료")