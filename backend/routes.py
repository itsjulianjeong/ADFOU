import os
from datetime import datetime

import sqlite3
from flask import request, render_template

from src.db_utils import insert_visitor_log
from webcam_app.face_capture import capture_face_from_webcam

def init_routes(app):
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
            menu_name=request.form["menu"]
            quantity=int(request.form["quantity"])

            db_path=os.path.join("database", "visitor_logs.db")
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 동적으로 연도 및 월 추출
            year=datetime.now().strftime("%Y")
            year_month=datetime.now().strftime("%Y%m")

            # master, YYYYmaster, YYYYMM에 모두 insert
            for table in ["master", f"{year}master", year_month]:
                insert_visitor_log(
                    db_path=db_path,
                    table_name=table,
                    timestamp=timestamp,
                    gender=gender,
                    age_group=age_group,
                    menu_name=menu_name,
                    quantity=quantity
                )

            return render_template("order_done.html")

    @app.route("/analyze")
    def analyze():
        db_path=os.path.join("database", "visitor_logs.db")
        conn=sqlite3.connect(db_path)
        conn.row_factory=sqlite3.Row
        cursor=conn.cursor()

        cursor.execute("SELECT * FROM master ORDER BY timestamp DESC")
        logs=cursor.fetchall()
        conn.close()

        return render_template("analyze.html", logs=logs)
