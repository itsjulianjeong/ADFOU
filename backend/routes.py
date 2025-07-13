import os
from datetime import datetime

import sqlite3
from flask import Flask, request, render_template, redirect, session, url_for

from src.db_utils import insert_visitor_log
from webcam_app.face_capture import capture_face_from_webcam

from dotenv import load_dotenv
load_dotenv()
ADMIN_ID=os.getenv("ADMIN_ID")
ADMIN_PW=os.getenv("ADMIN_PW")

def init_routes(app):
    # 사용자 메인
    @app.route("/")
    def index():
        return render_template("index.html")  

    @app.route("/order", methods=["GET", "POST"])
    def order():
        if request.method=="GET":
            gender, age_group=capture_face_from_webcam()
            return render_template("order.html", gender=gender, age_group=age_group)

        elif request.method=="POST":
            gender=request.form["gender"]
            age_group=request.form["age_group"]
            menu_list=request.form.getlist("menu")

            db_path=os.path.join("database", "visitor_logs.db")
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            year=datetime.now().strftime("%Y")
            year_month=datetime.now().strftime("%Y%m")

            order_id=f"{datetime.now().strftime('%Y%m%d%H%M%S')}"

            for menu_name in menu_list:
                quantity_str=request.form.get(f"quantity_{menu_name}", "1")
                try:
                    quantity=int(quantity_str)
                except ValueError:
                    quantity=1

                for table in ["master", f"{year}master", year_month]:
                    insert_visitor_log(
                        db_path=db_path,
                        table_name=table,
                        order_id=order_id,
                        timestamp=timestamp,
                        gender=gender,
                        age_group=age_group,
                        menu_name=menu_name,
                        quantity=quantity
                    )

            return render_template("order_done.html")

    # 관리자 로그인
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method=="POST":
            username=request.form["username"]
            password=request.form["password"]

            if username==ADMIN_ID and password==ADMIN_PW:
                session["admin_logged_in"]=True
                return redirect("/admin/analyze")  # 바로 분석 페이지로 이동
            else:
                return render_template("admin/login.html", error=True)  # 실패 시 에러 전달
            
        return render_template("admin/login.html")
    
    # 관리자 로그아웃
    @app.route("/admin/logout")
    def admin_logout():
        session.pop("admin_logged_in", None)
        return redirect("/admin/login")
    
    # 관리자 메인화면
    @app.route("/admin")
    def admin_home():
        return redirect("/admin/login")
    
    # 관리자 분석 페이지
    @app.route("/admin/analyze")
    def admin_analyze():
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")

        db_path=os.path.join("database", "visitor_logs.db")
        conn=sqlite3.connect(db_path)
        conn.row_factory=sqlite3.Row
        cursor=conn.cursor()

        cursor.execute("SELECT * FROM master ORDER BY timestamp ASC")
        logs=cursor.fetchall()
        conn.close()

        return render_template("admin/analyze.html", logs=logs)