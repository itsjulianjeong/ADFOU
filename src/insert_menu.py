import os
import sqlite3

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.abspath(os.path.join(BASE_DIR, "../database/store_analysis.db"))

def insert_menu(db_path=DB_PATH):
    conn=sqlite3.connect(db_path)
    cursor=conn.cursor()

    print("\n=== 🔧 메뉴 관리 도구 🔧 ===")

    while True:
        print("\n실행할 동작을 선택해주세요:")
        print("[1] 메뉴 추가")
        print("[2] 메뉴 수정 (메뉴 이름/가격 수정)")
        print("[3] 종료")

        choice=input("선택 [1/2/3] >>> ").strip()

        # 메뉴 추가
        if choice=="1":
            try:
                name=input("메뉴 이름 입력 >>> ").strip()
                price=int(input("메뉴 가격 입력 >>> ").strip())

                # 중복 확인
                cursor.execute("SELECT * FROM menu WHERE name=?", (name,))
                if cursor.fetchone():
                    print("이미 존재하는 메뉴입니다!")
                else:
                    cursor.execute("INSERT INTO menu (name, price) VALUES (?, ?)", (name, price))
                    conn.commit()
                    print(f"추가 완료: {name} ({price}원)")
            except ValueError:
                print("가격은 숫자로 입력해주세요.")

        # 메뉴 수정
        elif choice=="2":
            try:
                old_name=input("수정할 메뉴명을 입력해주세요 >>> ").strip()

                cursor.execute("SELECT * FROM menu WHERE name=?", (old_name,))
                row=cursor.fetchone()
                if not row:
                    print("해당 메뉴가 존재하지 않습니다!")
                    continue

                new_name=input("새 메뉴 이름 입력 >>> ").strip()
                new_price=int(input("새 가격 입력 >>> ").strip())

                cursor.execute("UPDATE menu SET name=?, price=? WHERE name=?", (new_name, new_price, old_name))
                conn.commit()
                print("수정 완료!")
            except ValueError:
                print("가격은 숫자로 입력해주세요.")

        # 메뉴 관리 도구 종료
        elif choice=="3":
            print("종료합니다.")
            break
        
        else:
            print("잘못된 입력입니다...")
    conn.close()

if __name__=="__main__":
    insert_menu()