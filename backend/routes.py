import os
from datetime import datetime

import uuid
import sqlite3
from flask import Flask, request, render_template, redirect, session, url_for

from src.db_utils.sales import insert_sales, get_sales_analysis
from src.db_utils.menu import get_menu_by_id_from_name, get_all_menus
from webcam_app.face_capture import capture_face_from_webcam

from dotenv import load_dotenv
load_dotenv()
ADMIN_ID=os.getenv("ADMIN_ID")
ADMIN_PW=os.getenv("ADMIN_PW")

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.abspath(os.path.join(BASE_DIR, "../database/store_analysis.db"))

def init_routes(app):
    # 사용자 메인
    @app.route("/")
    def index():
        return render_template("index.html")  

    @app.route("/order", methods=["GET", "POST"])
    def order():
        if request.method=="GET":
            gender, age_group=capture_face_from_webcam()
            menu_list=get_all_menus(DB_PATH)
            return render_template("order.html", gender=gender, age_group=age_group, menu_list=menu_list)

        elif request.method=="POST":
            gender=request.form["gender"]
            age_group=request.form["age_group"]
            menu_list=request.form.getlist("menu")

            if not menu_list:
                menu_list_all = get_all_menus(DB_PATH)
                return render_template(
                    "order.html",
                    gender=gender,
                    age_group=age_group,
                    menu_list=menu_list_all,
                    error="하나 이상의 메뉴를 선택해주세요!"
                )

            import uuid
            order_id=str(uuid.uuid4())  # 주문 전체에 동일한 ID 부여

            for menu_name in menu_list:
                quantity_str=request.form.get(f"quantity_{menu_name}", "1")
                try:
                    quantity=int(quantity_str)
                except ValueError:
                    quantity=1

                menu_info=get_menu_by_id_from_name(menu_name, DB_PATH)
                if menu_info is None:
                    print(f"존재하지 않는 메뉴: {menu_name}")
                    continue

                menu_id=menu_info[0]

                for _ in range(quantity):
                    insert_sales(sex=gender, age_group=age_group, menu_id=menu_id, db_path=DB_PATH, order_id=order_id)

            return render_template("order_done.html")

    # 관리자 로그인
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method=="POST":
            username=request.form["username"]
            password=request.form["password"]

            if username==ADMIN_ID and password==ADMIN_PW:
                session["admin_logged_in"]=True
                return redirect("/admin/dashboard")
            else:
                return render_template("admin/login.html", error=True)  # 실패 시 에러 전달
            
        return render_template("admin/login.html")
    
    # 관리자 로그아웃
    @app.route("/admin/logout")
    def admin_logout():
        session.pop("admin_logged_in", None)
        return redirect("/admin/login")
    
    # 관리자 대시보드
    @app.route("/admin/dashboard")
    def admin_dashboard():
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return render_template("admin/dashboard.html")
    
    # 관리자 메인화면
    @app.route("/admin")
    def admin_home():
        return redirect("/admin/login")
    
    # 관리자 분석 페이지
    @app.route("/admin/analyze")
    def admin_analyze():
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))

        result=get_sales_analysis()
        return render_template("admin/analyze.html", result=result)
    
    @app.route("/admin/menu_edit", methods=["GET", "POST"])
    def menu_edit():
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")

        db_path=DB_PATH

        if request.method=="POST":
            menu_ids=request.form.getlist("menu_id")
            
            conn=sqlite3.connect(db_path)
            cursor=conn.cursor()
            for idx, menu_id in enumerate(menu_ids):
                cursor.execute("UPDATE menu SET display_order=? WHERE id=?", (idx + 1, int(menu_id)))
            conn.commit()
            conn.close()

            return redirect("/admin/dashboard")
        
        from src.db_utils.menu import get_all_menus
        menu_list=get_all_menus(db_path)
        return render_template("admin/menu_edit.html", menu_list=menu_list)