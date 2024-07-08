import cv2
import tempfile
from roboflow import Roboflow

# 로보플로우 API 설정
rf = Roboflow(api_key="uU79vf8s9NUST3y2r3vl")
#d7LiJNpy5htM2c4GcPkY : 욜로 모델 키포인트를 ground truth로 해서 라벨링 version3가 키포인트는 꼬였으나 가장 성능 괜찮음
#wYU3g3bBqcZNZYNmWAxv : 7월 4일 라벨링 weight
#"uU79vf8s9NUST3y2r3vl" : 자체 이미지 292장 + 수집한 이미지 500여장 포함된거
project = rf.workspace("boda").project("bodaboda-5str8")
print(project)
# 웹캠 캡처 설정
cap = cv2.VideoCapture(1)

# 모델 로드
model = project.version(3).model

# 웹캠에서 프레임을 캡처하고 처리하는 루프
while True:
    ret, frame = cap.read()
    if not ret:
        cv2.waitKey()
        break

    # 임시 파일에 프레임 저장
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmpfile:
        cv2.imwrite(tmpfile.name, frame)
        temp_path = tmpfile.name

    # 모델을 사용하여 포즈 감지 수행
    prediction_results = model.predict(temp_path).json()
    
    # 예측 결과에서 키포인트와 객체명 추출
    if 'predictions' in prediction_results and prediction_results['predictions']:
        for prediction in prediction_results['predictions']:
            if 'predictions' in prediction and len(prediction['predictions']) > 0:
                bbox = prediction['predictions'][0]
                x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
                class_name = bbox['class']
            
                if class_name == 'Person':
                    box_color = (0, 255, 0)
                    text_color = (36, 255, 12)
                else : 
                    box_color = (0,0,255)
                    text_color = (0, 0, 255)
                # 객체 경계 상자 그리기
                cv2.rectangle(frame, (int(x - w / 2), int(y - h / 2)), (int(x + w / 2), int(y + h / 2)), box_color,2)
                cv2.putText(frame, class_name, (int(x - w / 2), int(y - h / 2) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, text_color, 2)

            # 키포인트 그리기
                for keypoint in bbox['keypoints']:
                    kp_x, kp_y = keypoint['x'], keypoint['y']
                    confidence = keypoint['confidence']
                    if confidence > 0.3:  # 신뢰도가 0.5 이상인 키포인트만 표시
                        cv2.circle(frame, (int(kp_x), int(kp_y)), 5, (0, 0, 255), -1)

    # 결과 프레임 보여주기
    cv2.imshow('frame', frame)

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()
