import os
import uuid
import sqlite3
from flask import Flask, request, render_template, redirect, session, url_for

from src.db_utils.menu import get_menu_by_id_from_name, get_all_menus
from src.db_utils.sales import insert_sales, get_today_sales_amount, get_today_sales_records, get_sales_amount_comparison

from webcam_app.face_capture import capture_face_from_webcam

# admin ID/PW 정의 .env 로드
from dotenv import load_dotenv
load_dotenv()
ADMIN_ID=os.getenv("ADMIN_ID")
ADMIN_PW=os.getenv("ADMIN_PW")

# DB 경로 지정
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.abspath(os.path.join(BASE_DIR, "../database/store_analysis.db"))

# flask 앱에 route 등록
def init_routes(app):
    
    # 사용자 ==========================================================================
    # index.html 랜더링
    @app.route("/")
    def index():
        return render_template("index.html")  

    # 사용자 주문 페이지 ==============================================================
    @app.route("/order", methods=["GET", "POST"])
    def order():
        # GET -> 얼굴 인식 후 주문 화면
        if request.method=="GET":
            # 성별, 연령대 추출
            gender, age_group=capture_face_from_webcam()
            # 메뉴 목록 DB에서 가져오기
            menu_list=get_all_menus(DB_PATH)
            # order.html에 인식 결과 및 메뉴 목록 전달
            return render_template("order.html", gender=gender, age_group=age_group, menu_list=menu_list)

        # POST -> 주문 정보 저장
        elif request.method=="POST":
            # form에서 넘어온 값 읽기
            gender=request.form["gender"]
            age_group=request.form["age_group"]
            menu_list=request.form.getlist("menu")  # 선택된 메뉴 이름 리스트

            # 메뉴를 하나도 선택하지 않았으면 에러 표시
            if not menu_list:
                menu_list_all=get_all_menus(DB_PATH)
                return render_template("order.html", gender=gender, age_group=age_group, menu_list=menu_list_all, error="하나 이상의 메뉴를 선택해주세요!")

            # 주문 ID 생성 -> 여러 메뉴 -> 한 주문으로 묶기
            order_id=str(uuid.uuid4())

            # 메뉴별 수량만큼 sales 테이블에 insert
            for menu_name in menu_list:
                quantity_str=request.form.get(f"quantity_{menu_name}", "1")
                try:
                    quantity=int(quantity_str)
                except ValueError:
                    quantity=1

                # 메뉴 이름은 -> ID 조회
                menu_info=get_menu_by_id_from_name(menu_name, DB_PATH)
                # 만약 DB에 없는 메뉴라면 로그만 남기도록
                if menu_info is None:
                    print(f"존재하지 않는 메뉴: {menu_name}")
                    continue

                menu_id=menu_info[0]
                # 선택된 수량만큼 insert_sales()
                for _ in range(quantity):
                    insert_sales(sex=gender, age_group=age_group, menu_id=menu_id, db_path=DB_PATH, order_id=order_id)
            # 주문 완료 페이지(order_done.html)로
            return render_template("order_done.html")

    # 관리자 ===================================================================
    @app.route("/admin")
    def admin_home():
        return redirect(url_for("admin_login"))
    # 관리자 로그인 ------------------------------------------------------------
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method=="POST":
            username=request.form["username"]
            password=request.form["password"]
            # ID/PW 확인
            if username==ADMIN_ID and password==ADMIN_PW:
                session["admin_logged_in"]=True
                return redirect("/admin/dashboard")
            else:
                return render_template("admin/login.html", error=True)  # 실패 시 에러 전달
        # 로그인 페이지
        return render_template("admin/login.html")
    # 관리자 로그아웃 ----------------------------------------------------------
    @app.route("/admin/logout")
    def admin_logout():
        session.pop("admin_logged_in", None)  # 관리자 로그아웃 처리
        return redirect("/admin/login")  # 다시 로그인 페이지로
    
    # 관리자 대시보드 ----------------------------------------------------------
    @app.route("/admin/dashboard")
    def admin_dashboard():
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        today_amount=get_today_sales_amount(DB_PATH)  # 오늘 총 매출(함수 내부에서 SQL 실행)
        sales_compare=get_sales_amount_comparison(DB_PATH)  # 오늘/어제 매출 비교 (딕셔너리형태 오늘 x, 어제 y)
        today_records=get_today_sales_records(DB_PATH)  # 오늘 주문 내역 표
        # dashboard.html로 해당 내용 전달
        return render_template("admin/dashboard.html", today_amount=today_amount, sales_compare=sales_compare, today_records=today_records)
    
    # 분석결과 조회 -------------------------------------------------------------
    @app.route("/admin/analyze")
    def admin_analyze():
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        # request 파라미터 get
        start=request.args.get("start_date", "")
        end=request.args.get("end_date", "")
        group_by=request.args.get("group_by", "weekday")
        gender=request.args.get("gender", "all")
        age_group=request.args.get("age_group", "all")
        metric=request.args.get("metric", "revenue")

        # 결과 초기화
        summary_rows=[]  # 요약
        detail_rows=[]  # 상세
        chart_data=[]  # -> Chart.js

        # 날짜 선택 해야지만 진행
        if start and end:
            # [WHERE 절 조립과정]
            cond=["1=1"]  # 항상 True 조건
            params=[]  # 파라미터 값 저장용            
            # 날짜 범위 between
            cond.append("DATE(s.timestamp) BETWEEN ? AND ?")
            params.extend([start, end])
            # 성별 필터링
            if gender != "all":
                cond.append("s.sex=?")
                params.append(gender)
            # 연령대 필터링
            if age_group != "all":
                cond.append("s.age_group=?")
                params.append(age_group)
            # 최종 where절 문자열
            where_clause=" AND ".join(cond)

            # [그룹 필드 매핑]
            group_map={
                "year": "strftime('%Y', s.timestamp)",
                "month": "strftime('%Y-%m', s.timestamp)",
                "weekday": "strftime('%w', s.timestamp)",  # 0~6
                "hour": "strftime('%H', s.timestamp)",
                "age_group": "s.age_group"
            }
            group_field=group_map[group_by]

            # 정렬 컬럼
            # revenue: 매출 합계, quantity: 판매 건수
            order_by="revenue" if metric == "revenue" else "quantity"
            # [집계 SQL문]
            # LIMIT 20: 상위 20개 그룹만
            sql=f"""
                SELECT
                    {group_field} AS gf,
                    COUNT(*) AS quantity,
                    SUM(m.price) AS revenue
                FROM sales s
                JOIN menu m ON s.menu_id = m.id
                WHERE {where_clause}
                GROUP BY gf
                ORDER BY {order_by} DESC
                LIMIT 20
            """
            # DB 접속 및 실행
            conn=sqlite3.connect(DB_PATH)
            corsor=conn.cursor()
            corsor.execute(sql, params)
            rows=corsor.fetchall()
            conn.close()

            # Chart.js용 데이터 변환
            chart_data=[
                {"gf": r[0], "quantity": r[1], "revenue": r[2]}
                for r in rows
            ]

            # 요약/상세 테이블
            # 그룹X성별 통합
            for gf, quantity, revenue in rows:
                summary_rows.append((gf, gender, quantity, revenue))
            # [메뉴별 상세 집계 SQL문]
            sql2=f"""
                SELECT
                    {group_field} AS gf,
                    s.sex,
                    m.name,
                    COUNT(*) AS quantity,
                    SUM(m.price) AS revenue
                FROM sales s
                JOIN menu m ON s.menu_id = m.id
                WHERE {where_clause}
                GROUP BY gf, s.sex, m.name
                ORDER BY gf, s.sex, {order_by} DESC
            """
            # DB 접속
            conn=sqlite3.connect(DB_PATH)
            corsor=conn.cursor()
            corsor.execute(sql2, params)
            # 상세 데이터 fetchall()
            for gf, sex, menu, quantity, revenue in corsor.fetchall():
                detail_rows.append((gf, sex, menu, quantity, revenue))
            conn.close()

        # [결과 analyze.html 렌더링]
        return render_template("admin/analyze.html", request_args=request.args, group_by=group_by, metric=metric,
                            summary_rows=summary_rows, detail_rows=detail_rows, chart_data=chart_data)

    # 메뉴 순서 조정 -------------------------------------------------------------
    @app.route("/admin/menu_edit", methods=["GET", "POST"])
    def menu_edit():
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")

        db_path=DB_PATH

        if request.method=="POST":
            menu_ids=request.form.getlist("menu_id")
            
            conn=sqlite3.connect(db_path)
            cursor=conn.cursor()
            # 선택된 ID 순서대로 display_order 업데이트하기
            for order_index, menu_id in enumerate(menu_ids, start=1):
                cursor.execute(
                    "UPDATE menu SET display_order = ? WHERE id = ?",
                    (order_index, int(menu_id))
                )
            conn.commit()
            conn.close()

            return redirect("/admin/dashboard")
        
        # GET -> 메뉴 목록 조회
        menu_list=get_all_menus(db_path)
        return render_template("admin/menu_edit.html", menu_list=menu_list)