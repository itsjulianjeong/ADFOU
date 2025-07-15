# 스마트 매장 방문자 분석 시스템
얼굴 인식 기반으로 방문자의 성별과 연령대를 예측하고, 이를 바탕으로 매장의 매출 데이터를 분석 및 시각화합니다.  
예를들어 어떤 시간대에 어떤 성별의 어떤 연령대 손님이 어떤 음료를 시키는지 등을 분석하여 판매를 촉진시키기 위해 특정 메뉴를 상단에 배치하는 등 다양한 운영 전략으로 사용할 수 있도록 하였습니다.  

## 모델
- EfficientNetB0 (Fine-tuned)
- 입력 이미지 크기: 224x224 RGB
- 배치 사이즈: 16
- 클래스 분류: 성별 (남성/여성), 연령대 (0s, 10s, 20s, ..., 60+)

## 기술
Python, PyTorch(EfficientNetB0), OpenCV, MediaPipe, SQLite, Flask

## 기능
- 방문자 얼굴 인식을 통한 성별, 연령대 예측
  - MediaPipe를 활용한 얼굴 감지 및 예측
  - 실시간 카메라 입력 -> 이미지 전처리 -> EfficientNetB0 모델 예측
- flask 기반 웹앱
- 메뉴 주문 및 매출 기록
- 관리자 페이지에서 분석 결과 확인
- 연도, 월, 요일, 시간, 연령대 필터링

## 프로젝트 구조
```
├── main.py                       
├── .gitignore                    
├── src/
│   ├── __init__.py
│   ├── db_utils/
│   │   ├── menu.py                   # 메뉴 관련 DB 함수
│   │   └── sales.py                  # 매출 관련 DB 함수
│   ├── create_table.py               # 초기 테이블 생성
│   ├── create_view\.py               # 뷰 생성
│   └── insert_menu.py                # 메뉴 삽입 및 수정용 파일
├── webcam_app/
│   ├── __init__.py
│   ├── face_capture.py               # 웹캠 얼굴 감지 및 캡처
│   ├── predictor.py                  # 학습된 모델 기반 예측
│   ├── utils/
│   │   ├── __init__.py
│   │   └── image_utils.py            # 모델 예측 전, 이미지 전처리 함수
│   └── test/
│       ├── run_test_image.py         # 연예인 이미지 기반 예측 테스트
│       ├── image/                    # 테스트 이미지 샘플
│       └── result/                   # 예측 결과 저장
│       └── prediction.txt
├── backend/
│   └── routes.py                     # flask 라우팅
├── frontend/
│   └── *.html                       # 사용자/관리자 페이지 템플릿
├── notebooks/
│   ├── data_preprocessing/          # 이미지 전처리
│   │   ├── 03_preprocessing.ipynb
│   │   └── 04_preprocessing.ipynb   # 정면 이미지 필터링
│   └── model_training/              # 모델 학습
│       └── 09_age_sex_cls.ipynb  # EfficientNetB0 모델 학습
├── src/models/
│   └── 09_efficientnetb0_best.pth  # 최종 모델
└── src/results/
    ├── 09_acc_loss_graph.jpg
    ├── 09_classification_report_clean.txt
    └── 09_confusion_matrix_clean.jpg
```

## 실행 방법
1. 데이터베이스 초기화
  - `python src/create_table.py`
  - `python src/insert_menu.py`
  - `python src/create_view.py`
2. python main.py
3. ID/PW: .env 파일 생성 후 설정