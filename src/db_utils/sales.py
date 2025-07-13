# 판매 기록
import os
from datetime import datetime
import sqlite3
import uuid

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.abspath(os.path.join(BASE_DIR, "../../database/store_analysis.db"))

def insert_sales(sex, age_group, menu_id, db_path=DB_PATH, order_id=None):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if order_id is None:
        order_id=str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO sales (timestamp, sex, age_group, menu_id, order_id)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, sex, age_group, menu_id, order_id))

    conn.commit()
    conn.close()
    print(f"판매 기록 저장 완료! {timestamp}, {sex}, {age_group}, menu_id={menu_id}, order_id={order_id}")

def get_sales_analysis(db_path=DB_PATH):
    from collections import OrderedDict

    today=datetime.today()
    year=str(today.year)
    month=f"{today.month:02d}"
    view_name=f"view_{year}{month}"

    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    # 주문 단위로 정렬된 raw 결과 가져오기
    # 시간 오름차순으로 정렬
    cursor.execute(f"""
        SELECT s.order_id, MIN(s.timestamp), s.sex, s.age_group, m.name, COUNT(*) as quantity
        FROM {view_name} s
        JOIN menu m ON s.menu_id=m.id
        GROUP BY s.order_id, s.sex, s.age_group, m.name
        ORDER BY MIN(s.timestamp) ASC
    """)
    raw=cursor.fetchall()
    conn.close()

    # order_id -> 정렬순서로 번호 부여
    order_map=OrderedDict()
    result=[]

    current_order_number=1
    for row in raw:
        order_id=row[0]
        if order_id not in order_map:
            order_map[order_id]=current_order_number
            current_order_number+=1

        readable_order_num=order_map[order_id]

        result.append((
            readable_order_num,  # 1, 2, 3...
            row[1],  # timestamp
            row[2],  # sex
            row[3],  # age_group
            row[4],  # menu name
            row[5]   # quantity
        ))

    return result