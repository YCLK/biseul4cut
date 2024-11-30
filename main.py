import sys
import cv2
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QCheckBox, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
from PIL import Image
from datetime import datetime

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("비슬네컷")
        self.setGeometry(0, 0, 540, 960)  # 9:16 비율 설정
        self.setFixedSize(540, 960)  # 창 크기 고정

        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.title = QLabel("비슬네컷")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px;")

        self.start_button = QPushButton("시작하기")
        self.start_button.setFixedHeight(50)
        self.start_button.clicked.connect(self.show_frame_selection)

        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.start_button)

        self.setLayout(self.main_layout)

    def show_frame_selection(self):
        self.clear_layout(self.main_layout)

        frame_layout = QHBoxLayout()

        frame1_layout = QVBoxLayout()
        frame1_label = QLabel()
        frame1_pixmap = QPixmap("frame/frame1.png")
        if frame1_pixmap.isNull():
            frame1_label.setText("frame1.png 로드 실패")
        else:
            frame1_label.setPixmap(frame1_pixmap.scaled(180, 320, Qt.KeepAspectRatio))
        frame1_button = QPushButton("선택하기")
        frame1_button.clicked.connect(lambda: self.show_camera_window("frame1.png"))

        frame1_layout.addWidget(frame1_label)
        frame1_layout.addWidget(frame1_button)

        frame2_layout = QVBoxLayout()
        frame2_label = QLabel()
        frame2_pixmap = QPixmap("frame/frame2.png")
        if frame2_pixmap.isNull():
            frame2_label.setText("frame2.png 로드 실패")
        else:
            frame2_label.setPixmap(frame2_pixmap.scaled(180, 320, Qt.KeepAspectRatio))
        frame2_button = QPushButton("선택하기")
        frame2_button.clicked.connect(lambda: self.show_camera_window("frame2.png"))

        frame2_layout.addWidget(frame2_label)
        frame2_layout.addWidget(frame2_button)

        frame_layout.addLayout(frame1_layout)
        frame_layout.addLayout(frame2_layout)

        self.main_layout.addLayout(frame_layout)

    def show_camera_window(self, frame):
        self.camera_window = CameraWindow(frame)
        self.camera_window.show()
        self.close()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()

class CameraWindow(QWidget):
    def __init__(self, frame):
        super().__init__()

        self.setWindowTitle("카메라")
        self.setGeometry(0, 0, 540, 960)  # 9:16 비율 설정
        self.setFixedSize(540, 960)  # 창 크기 고정

        self.frame = frame
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()

        self.countdown_label = QLabel("10초 후에 촬영을 시작합니다")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("font-size: 24px;")
        self.main_layout.addWidget(self.countdown_label)

        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)  # 카메라 화면 중앙 정렬
        self.main_layout.addWidget(self.camera_label)

        self.photo_count_label = QLabel("0/8장 촬영됨")
        self.photo_count_label.setAlignment(Qt.AlignCenter)
        self.photo_count_label.setStyleSheet("font-size: 24px;")
        self.main_layout.addWidget(self.photo_count_label)

        self.setLayout(self.main_layout)

        self.photo_counter = 0
        self.max_photos = 8
        self.countdown_time = 10  # 각 촬영 사이의 카운트다운 시간

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.counter = self.countdown_time
        self.timer.start(1000)  # 1초마다 타이머 업데이트

        self.cap = cv2.VideoCapture(0)
        self.show_camera_feed()

        # temp 폴더 생성
        if not os.path.exists("temp"):
            os.makedirs("temp")

    def update_countdown(self):
        self.counter -= 1
        if self.counter == 0:
            self.capture_photo()
            self.counter = self.countdown_time  # 다음 촬영을 위한 카운트다운 초기화
            self.photo_counter += 1
            self.photo_count_label.setText(f"{self.photo_counter}/{self.max_photos}장 촬영됨")
            if self.photo_counter >= self.max_photos:
                self.timer.stop()
                self.countdown_label.setText("촬영 완료!")
                self.cap.release()  # 카메라 해제
                self.show_photo_selection()
        else:
            self.countdown_label.setText(f"{self.counter}초 후에 촬영을 시작합니다")

    def show_camera_feed(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)  # 좌우반전
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            converted_Qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(converted_Qt_image))
        if self.photo_counter < self.max_photos:
            QTimer.singleShot(30, self.show_camera_feed)

    def capture_photo(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)  # 좌우반전
            photo_path = f"temp/photo_{self.photo_counter + 1}.png"
            cv2.imwrite(photo_path, frame)
            print(f"{photo_path} 저장 완료")

    def show_photo_selection(self):
        self.clear_layout(self.main_layout)

        photo_selection_layout = QVBoxLayout()

        instruction_label = QLabel("촬영된 8장의 사진 중 4장을 선택하세요")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet("font-size: 24px;")
        photo_selection_layout.addWidget(instruction_label)

        grid_layout = QGridLayout()
        self.checkboxes = []

        for i in range(8):
            photo_label = QLabel()
            photo_pixmap = QPixmap(f"temp/photo_{i + 1}.png")
            if not photo_pixmap.isNull():
                photo_label.setPixmap(photo_pixmap.scaled(180, 320, Qt.KeepAspectRatio))
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.checkbox_state_changed)  # 체크박스 상태 변경 시 이벤트 연결
            self.checkboxes.append(checkbox)

            grid_layout.addWidget(photo_label, i // 4, (i % 4) * 2)
            grid_layout.addWidget(checkbox, i // 4, (i % 4) * 2 + 1)

        photo_selection_layout.addLayout(grid_layout)

        submit_button = QPushButton("선택 완료")
        submit_button.clicked.connect(self.submit_selection)
        photo_selection_layout.addWidget(submit_button)

        self.main_layout.addLayout(photo_selection_layout)

    def checkbox_state_changed(self, state):
        if state == Qt.Checked:
            selected_count = sum(checkbox.isChecked() for checkbox in self.checkboxes)
            if selected_count > 4:
                QMessageBox.warning(self, "경고", "4장을 초과하여 선택할 수 없습니다.")
                sender = self.sender()
                sender.blockSignals(True)  # 신호 차단
                sender.setChecked(False)
                sender.blockSignals(False)  # 신호 재개

    def submit_selection(self):
        selected_photos = [i + 1 for i, checkbox in enumerate(self.checkboxes) if checkbox.isChecked()]
        if len(selected_photos) == 4:
            print(f"선택된 사진: {selected_photos}")
            self.merge_and_save_photos(selected_photos)
            self.cleanup_temp_folder()
            self.show_completion_window()
        else:
            QMessageBox.warning(self, "경고", "4장의 사진을 선택하세요.")

    def merge_and_save_photos(self, selected_photos):
        images = [Image.open(f"temp/photo_{i}.png") for i in selected_photos]
        widths, heights = zip(*(i.size for i in images))

        total_height = sum(heights)
        max_width = max(widths)

        new_image = Image.new("RGB", (max_width, total_height))

        y_offset = 0
        for im in images:
            new_image.paste(im, (0, y_offset))
            y_offset += im.size[1]

        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        self.output_path = f"output/biseul-{timestamp}.png"
        new_image.save(self.output_path)
        print(f"{self.output_path} 저장 완료")

    def cleanup_temp_folder(self):
        for filename in os.listdir("temp"):
            file_path = os.path.join("temp", filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"{file_path} 삭제 완료")

    def show_completion_window(self):
        self.completion_window = CompletionWindow(self.output_path)
        self.completion_window.show()
        self.close()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()

class CompletionWindow(QWidget):
    def __init__(self, output_path):
        super().__init__()

        self.setWindowTitle("촬영 완료")
        self.setGeometry(0, 0, 540, 960)  # 9:16 비율 설정
        self.setFixedSize(540, 960)  # 창 크기 고정

        self.output_path = output_path
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()

        completion_label = QLabel("촬영이 완료되었습니다! 아래 QR 코드를 스캔하여\n사진을 다운로드하세요.")
        completion_label.setAlignment(Qt.AlignCenter)
        completion_label.setStyleSheet("font-size: 24px;")
        self.main_layout.addWidget(completion_label)

        # QR 코드 이미지 생성 (임시로 QR 코드 생성 부분 생략)
        qr_label = QLabel()
        qr_pixmap = QPixmap("qr/qr_code.png")
        qr_label.setPixmap(qr_pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        qr_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(qr_label)

        return_button = QPushButton("돌아가기")
        return_button.setFixedHeight(50)
        return_button.clicked.connect(self.return_to_main)

        self.main_layout.addWidget(return_button)
        self.setLayout(self.main_layout)

    def return_to_main(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())
