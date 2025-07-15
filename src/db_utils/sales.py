# 판매 기록
import os
from datetime import datetime, timedelta
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
        SELECT s.order_id, MAX(s.timestamp) as timestamp, s.sex, s.age_group, m.name, COUNT(*) as quantity
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

def get_today_sales_amount(db_path):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    today=datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT SUM(m.price)
        FROM sales s
        JOIN menu m ON s.menu_id=m.id
        WHERE DATE(s.timestamp)=?
    """, (today,))
    total=cursor.fetchone()[0]
    conn.close()
    return total or 0

def get_today_sales_records(db_path):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()
    today=datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        SELECT 
            s.order_id,
            s.timestamp,
            s.sex,
            s.age_group,
            m.name,
            COUNT(*) AS quantity,
            m.price * COUNT(*) AS total_price
        FROM sales s
        JOIN menu m ON s.menu_id=m.id
        WHERE DATE(s.timestamp)=?
        GROUP BY s.order_id, m.id
        ORDER BY s.timestamp ASC
    """, (today,))
    raw_rows=cursor.fetchall()
    conn.close()

    # order_id -> 순번 매핑
    order_map={}
    seq=1
    processed=[]
    for order_id, timestamp, sex, age_group, menu_name, qty, total_price in raw_rows:
        if order_id not in order_map:
            order_map[order_id]=seq
            seq+=1
        processed.append((
            order_map[order_id],
            timestamp,
            sex,
            age_group,
            menu_name,
            qty,
            total_price
        ))
    return processed

def get_sales_amount_comparison(db_path):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    # 오늘 날짜
    today=datetime.now().date()
    # 어제 날짜
    yesterday=today - timedelta(days=1)

    # 오늘 매출
    cursor.execute(
        """
        SELECT COALESCE(SUM(m.price), 0)
        FROM sales s
        JOIN menu m ON s.menu_id=m.id
        WHERE DATE(s.timestamp)=?
        """,
        (today.strftime("%Y-%m-%d"),)
    )
    today_amount=cursor.fetchone()[0]

    # 어제 매출
    cursor.execute(
        """
        SELECT COALESCE(SUM(m.price), 0)
        FROM sales s
        JOIN menu m ON s.menu_id=m.id
        WHERE DATE(s.timestamp)=?
        """,
        (yesterday.strftime("%Y-%m-%d"),)
    )
    yesterday_amount=cursor.fetchone()[0]

    conn.close()

    return {"today": today_amount, "yesterday": yesterday_amount}