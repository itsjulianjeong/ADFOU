# 실시간 예측 실행 스크립트
import cv2
import os
import time
import winsound  # windows 비프음
from webcam_app.predictor import predict_face

# 캡처 후 저장할 경로
RESULT_DIR=os.path.join("webcam_app", "result")
os.makedirs(RESULT_DIR, exist_ok=True)
SAVE_IMAGE_PATH=os.path.join(RESULT_DIR, "captured_face.jpg")
SAVE_PRED_PATH=os.path.join(RESULT_DIR, "prediction.txt")

def capture_face_from_webcam():
    # 웹캠 시작
    cap=cv2.VideoCapture(0)

    # 얼굴 감지 프레임 누적
    face_detected_frames=0
    required_face_frames=10  # 10프레임 연속 얼굴 감지 시 타이머 시작

    countdown_started=False
    countdown_start_time=None
    countdown_seconds=3

    captured=False  # 초기화
    last_countdown_value=None  # 효과음 중복 방지용

    while True:
        ret, frame=cap.read()
        if not ret:
            break
        
        # 좌우 반전 복원
        frame=cv2.flip(frame, 1)
        
        # 예측 및 얼굴 감지
        result_img, sex_text, age_text, label_text, has_face=predict_face(frame.copy())
        result_img_with_countdown=result_img.copy()  # 숫자 덧씌울 용

        # 얼굴 감지 누적
        if has_face:
            face_detected_frames+=1
        else:
            face_detected_frames=0
            countdown_started=False  # 얼굴 사라지면 타이머 리셋
            last_countdown_value=None  # 리셋
        
        # 얼굴 연속 감지되면 카운트다운 시작
        if face_detected_frames >= required_face_frames and not countdown_started:
            countdown_started=True
            countdown_start_time=time.time()
        
        # 타이머 진행 중이면 화면에 숫자 출력
        countdown=0
        if countdown_started:
            elapsed=time.time() - countdown_start_time
            countdown=max(0, countdown_seconds - int(elapsed))
            
            # 효과음 (1초마다 한 번만)
            if countdown != last_countdown_value:
                if countdown > 0:
                    winsound.Beep(1000, 300)  # 1000 hz, 0.3초
                elif countdown == 0:
                    winsound.Beep(1500, 500)  # 1500 hz 더 높은 소리 (촬영)
                last_countdown_value=countdown
            
            # 숫자 오버레이 (화면에만 보여줌)
            cv2.putText(result_img_with_countdown, f"{countdown}", (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)

        # 카운트다운 완료 -> 저장
        if countdown==0 and countdown_started and not captured:
            cv2.imwrite(SAVE_IMAGE_PATH, result_img)  # 숫자 안 그려진 이미지 저장
            with open(SAVE_PRED_PATH, "w", encoding="utf-8") as f:
                f.write("예측 결과:\n")
                f.write(f"- {label_text}\n")

            print(f"이미지 저장 완료! {SAVE_IMAGE_PATH}")
            print(f"예측 결과 저장 완료! {SAVE_PRED_PATH}")
            break  # 캡처 후 바로 종료

        # 화면 출력
        cv2.imshow("Webcam Prediction", result_img_with_countdown)  # 숫자 포함된 화면만 출력
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # 자원 해제
    cap.release()
    cv2.destroyAllWindows()
    
    # 예측 결과 반환
    return sex_text, age_text