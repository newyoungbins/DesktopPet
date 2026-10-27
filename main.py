
import sys
import random
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QTransform
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QMenu,
    QMessageBox
)


# ==========================================
# 공통 이미지 불러오기
# ==========================================

def load_image(path, width=150, height=150):

    image = QPixmap(str(path))

    if image.isNull():
        raise FileNotFoundError(
            f"이미지를 찾을 수 없습니다: {path}"
        )

    return image.scaled(
        width,
        height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )


# ==========================================
# 특별 이벤트에 등장하는 새로운 캐릭터
# ==========================================

class EventCharacter(QWidget):

    def __init__(self, assets_path):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowTransparentForInput
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFixedSize(160, 160)

        self.character_label = QLabel(self)
        self.character_label.setGeometry(0, 0, 160, 160)
        self.character_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # 달리기 이미지
        self.run_frames = [
            load_image(
                assets_path / f"event_run{i}.png"
            )
            for i in range(1, 5)
        ]

        # 소리 지르기 이미지
        self.shout_frames = [
            load_image(
                assets_path / f"event_shout{i}.png"
            )
            for i in range(1, 5)
        ]

        self.frame_index = 0
        self.state = "Run"

        # True면 오른쪽을 바라보도록 좌우 반전
        self.face_right = False

        self.update_image()

    def set_state(self, state, face_right=False):

        self.state = state
        self.face_right = face_right
        self.frame_index = 0

        self.update_image()

    def animate(self):

        self.frame_index = (
            self.frame_index + 1
        ) % 4

        self.update_image()

    def update_image(self):

        if self.state == "Shout":
            frame = self.shout_frames[self.frame_index]
        else:
            frame = self.run_frames[self.frame_index]

        if self.face_right:
            frame = frame.transformed(
                QTransform().scale(-1, 1)
            )

        self.character_label.setPixmap(frame)


# ==========================================
# 데스크톱 펫
# ==========================================

class DesktopPet(QWidget):

    def __init__(self):
        super().__init__()

        # ======================================
        # 1. 기본 정보
        # ======================================

        self.pet_name = "햄찌"

        self.level = 1
        self.exp = 0
        self.max_exp = 100

        self.hunger = 90
        self.happiness = 90
        self.cleanliness = 0

        self.state = "Walk"

        self.direction = -1
        self.speed = 2
        self.frame_index = 0

        # 마우스
        self.drag_position = None
        self.press_position = None
        self.is_dragging = False
        self.is_menu_open = False

        self.message_version = 0

        # ======================================
        # 2. 특별 이벤트 변수
        # ======================================

        self.event_active = False

        # 이벤트가 여러 개 예약될 경우 순서대로 실행
        self.event_queue = []

        self.event_phase = None

        self.event_character = None

        self.event_target_x = 0
        self.event_exit_x = 0

        # 이벤트 중 펫 위치 고정
        self.event_pet_position = None

        # ======================================
        # 3. 창 설정
        # ======================================

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setFixedSize(160, 180)

        # 펫 이미지
        self.pet = QLabel(self)
        self.pet.setGeometry(0, 20, 160, 160)
        self.pet.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.pet.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        # 상태 문구
        self.state_label = QLabel(self)
        self.state_label.setGeometry(0, 0, 160, 25)

        self.state_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.state_label.setStyleSheet(
            "color: white;"
            "background-color: rgba(40,40,40,150);"
            "border-radius: 8px;"
        )

        self.state_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )

        # ======================================
        # 4. 이미지 경로
        # ======================================

        if getattr(sys, "frozen", False):
            self.assets_path = (
                Path(sys._MEIPASS) / "assets"
            )
        else:
            self.assets_path = (
                Path(__file__).parent / "assets"
            )

        # ======================================
        # 5. 기존 이미지
        # ======================================

        self.clean_walk_frames = [
            load_image(
                self.assets_path / f"clean_walk{i}.png"
            )
            for i in range(1, 5)
        ]

        self.dirty_walk_frames = [
            load_image(
                self.assets_path / f"walk{i}.png"
            )
            for i in range(1, 5)
        ]

        self.dirty_frames = [
            load_image(
                self.assets_path / f"dirty{i}.png"
            )
            for i in range(1, 5)
        ]

        self.eat_frames = [
            load_image(
                self.assets_path / f"eat{i}.png"
            )
            for i in range(1, 5)
        ]

        # 놀기 애니메이션 (4장)
        self.play_frames = [
            load_image(self.assets_path / f"play{i}.png")
            for i in range(1, 5)
        ]

        self.idle_image = load_image(
            self.assets_path / "idle.png"
        )

        self.sleep_image = load_image(
            self.assets_path / "sleep.png"
        )

        self.happy_image = load_image(
            self.assets_path / "happy.png"
        )

        self.angry_image = load_image(
            self.assets_path / "angry.png"
        )

        self.hungry_image = load_image(
            self.assets_path / "hungry.png"
        )

        self.wash_image = load_image(
            self.assets_path / "wash.png"
        )

        # ======================================
        # 6. 귀 막는 애니메이션
        # ======================================

        self.cover_ears_frames = [
            load_image(
                self.assets_path / f"cover_ears{i}.png"
            )
            for i in range(1, 5)
        ]

        # ======================================
        # 7. 화면 위치
        # ======================================

        screen = QApplication.primaryScreen()
        self.screen_rect = screen.availableGeometry()

        self.move(
            self.screen_rect.center().x()
            - self.width() // 2,
            self.screen_rect.bottom()
            - self.height() + 1
        )

        # ======================================
        # 8. 기존 타이머
        # ======================================

        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.walk)
        self.move_timer.start(30)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(
            self.animate
        )
        self.animation_timer.start(150)

        self.state_timer = QTimer(self)
        self.state_timer.setSingleShot(True)
        self.state_timer.timeout.connect(
            self.change_state
        )

        self.interaction_timer = QTimer(self)
        self.interaction_timer.setSingleShot(True)
        self.interaction_timer.timeout.connect(
            self.finish_interaction
        )

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(
            self.update_status
        )
        self.status_timer.start(10000)

        # ======================================
        # 9. 이벤트 타이머
        # ======================================

        # 새로운 캐릭터 이동
        self.event_move_timer = QTimer(self)
        self.event_move_timer.timeout.connect(
            self.move_event_character
        )

        # 이벤트 애니메이션
        self.event_animation_timer = QTimer(self)
        self.event_animation_timer.timeout.connect(
            self.animate_event_character
        )

        # 소리 지르기 종료 타이머
        self.event_shout_timer = QTimer(self)
        self.event_shout_timer.setSingleShot(True)
        self.event_shout_timer.timeout.connect(
            self.start_event_exit
        )

        self.update_image()
        self.update_state_label()
        self.schedule_next_state()

    # ======================================
    # 상태 확인
    # ======================================

    def is_dirty(self):
        return self.cleanliness <= 0

    def is_angry(self):
        return self.happiness <= 0

    def is_hungry(self):
        return self.hunger <= 0

    def get_need_state(self):
        # 포만도 0이 행복도 0보다 우선
        if self.is_hungry():
            return "Hungry"
        if self.is_angry():
            return "Angry"
        return None

    # ======================================
    # 이미지 변경
    # ======================================

    def update_image(self):

        if self.state == "Walk":

            if self.is_dirty():
                frames = self.dirty_walk_frames
            else:
                frames = self.clean_walk_frames

            frame = frames[self.frame_index]

            if self.direction == 1:
                frame = frame.transformed(
                    QTransform().scale(-1, 1)
                )

        elif self.state == "Dirty":
            frame = self.dirty_frames[self.frame_index]

        elif self.state == "Eat":
            frame = self.eat_frames[self.frame_index]

        elif self.state == "Play":
            frame = self.play_frames[self.frame_index]

        elif self.state == "CoverEars":
            frame = self.cover_ears_frames[
                self.frame_index
            ]

        elif self.state == "Idle":
            frame = self.idle_image

        elif self.state == "Sleep":
            frame = self.sleep_image

        elif self.state == "Happy":
            frame = self.happy_image

        elif self.state == "Wash":
            frame = self.wash_image

        elif self.state == "Angry":
            frame = self.angry_image

        elif self.state == "Hungry":
            frame = self.hungry_image

        else:
            return

        self.pet.setPixmap(frame)

    # ======================================
    # 펫 애니메이션
    # ======================================

    def animate(self):

        if self.drag_position is not None:
            return

        if self.is_menu_open and not self.event_active:
            return

        animated_states = [
            "Walk",
            "Dirty",
            "Eat",
            "Play",
            "CoverEars"
        ]

        if self.state in animated_states:

            self.frame_index = (
                self.frame_index + 1
            ) % 4

            self.update_image()

    # ======================================
    # 걷기
    # ======================================

    def walk(self):

        if self.event_active:
            return

        if self.drag_position is not None:
            return

        if self.is_menu_open:
            return

        if self.state != "Walk":
            return

        new_x = (
            self.x()
            + self.speed * self.direction
        )

        left = self.screen_rect.left()

        right = (
            self.screen_rect.right()
            - self.width() + 1
        )

        if new_x >= right:

            new_x = right
            self.direction = -1
            self.update_image()

        elif new_x <= left:

            new_x = left
            self.direction = 1
            self.update_image()

        self.move(new_x, self.y())

    # ======================================
    # 다음 행동 예약
    # ======================================

    def schedule_next_state(self):

        if self.event_active:
            return

        if self.state == "Walk":
            duration = random.randint(2000, 5000)

        elif self.state == "Dirty":
            duration = random.randint(3000, 6000)

        elif self.state == "Idle":
            duration = random.randint(2000, 4000)

        elif self.state == "Sleep":
            duration = random.randint(4000, 7000)

        else:
            return

        self.state_timer.start(duration)

    # ======================================
    # 랜덤 행동 변경
    # ======================================

    def change_state(self):

        if self.event_active:
            return

        if self.is_menu_open:
            self.state_timer.start(500)
            return

        if self.state in [
            "Eat", "Happy", "Wash", "Play"
        ]:
            return

        need_state = self.get_need_state()
        if need_state:
            self.set_state(need_state)
            return

        if self.is_dirty():
            states = ["Walk", "Dirty"]
        else:
            states = ["Walk", "Idle", "Sleep"]

        candidates = [
            state for state in states
            if state != self.state
        ]

        self.set_state(
            random.choice(candidates)
        )

        if self.state == "Walk":
            self.direction = random.choice([-1, 1])
            self.update_image()

        self.schedule_next_state()

    # ======================================
    # 상태 변경
    # ======================================

    def set_state(self, new_state):

        self.state = new_state
        self.frame_index = 0

        # 놀기만 300ms, 나머지 애니메이션은 기존 150ms
        self.animation_timer.setInterval(300 if new_state == "Play" else 150)

        self.update_image()
        self.update_state_label()

    # ======================================
    # 경험치 및 레벨업
    # ======================================

    
    def gain_exp(self, amount):

        self.exp += amount

        while self.exp >= self.max_exp:

            self.exp -= self.max_exp
            self.level += 1
            self.max_exp = self.level * 100

            self.show_message(
                f"🎉 레벨 업! Lv.{self.level}"
            )

            # 레벨업할 때마다 특별 이벤트 예약
            self.event_queue.append(self.level)

        # 이벤트가 예약되어 있으면 실행
        if self.event_queue and not self.event_active:

            # 현재 상호작용이 끝난 다음 실행
            if not self.interaction_timer.isActive():
                self.start_special_event()


    # ======================================
    # 특별 이벤트 시작
    # ======================================

    def start_special_event(self):

        if self.event_active:
            return

        if not self.event_queue:
            return

        if self.is_menu_open:
            QTimer.singleShot(
                300,
                self.start_special_event
            )
            return

        event_level = self.event_queue.pop(0)

        self.event_active = True
        self.event_phase = "Enter"

        # 기존 행동 중지
        self.state_timer.stop()
        self.interaction_timer.stop()

        # 이벤트 중 펫은 제자리에 고정
        self.event_pet_position = QPoint(
            self.x(), self.y()
        )

        # 펫은 우선 쉬는 상태
        self.set_state("Idle")

        self.show_message(
            f"🎉 Lv.{event_level} 특별 이벤트!"
        )

        # 새로운 캐릭터 생성
        if self.event_character is None:
            self.event_character = EventCharacter(
                self.assets_path
            )

        self.event_character.set_state(
            "Run",
            face_right=False
        )

        # 펫의 오른쪽에서 등장
        start_x = self.x() + 330

        # 펫 옆에 멈출 위치
        self.event_target_x = self.x() + 125

        # 퇴장 위치
        self.event_exit_x = self.x() + 330

        # 캐릭터의 바닥을 펫과 맞춤
        event_y = self.y() + 20

        self.event_character.move(
            start_x,
            event_y
        )

        self.event_character.show()

        # 이동 시작
        self.event_move_timer.start(30)

        # 애니메이션 시작
        self.event_animation_timer.start(150)

    # ======================================
    # 이벤트 캐릭터 이동
    # ======================================

    def move_event_character(self):

        if not self.event_active:
            return

        if self.event_character is None:
            return

        current_x = self.event_character.x()

        # 오른쪽에서 왼쪽으로 달려오기
        if self.event_phase == "Enter":

            new_x = current_x - 5

            if new_x <= self.event_target_x:

                new_x = self.event_target_x

                self.event_character.move(
                    new_x,
                    self.event_character.y()
                )

                self.start_event_shout()
                return

            self.event_character.move(
                new_x,
                self.event_character.y()
            )

        # 오른쪽으로 달려 나가기
        elif self.event_phase == "Exit":

            new_x = current_x + 5

            if new_x >= self.event_exit_x:

                self.finish_special_event()
                return

            self.event_character.move(
                new_x,
                self.event_character.y()
            )

    # ======================================
    # 소리 지르기 시작
    # ======================================

    def start_event_shout(self):

        self.event_phase = "Shout"

        # 이동 중지
        self.event_move_timer.stop()

        # 새 캐릭터 소리 지르기
        self.event_character.set_state(
            "Shout"
        )

        # 펫이 귀 막기
        self.set_state("CoverEars")

        self.show_message(
            "😱 저리가!!!"
        )

        # 2초 동안 소리 지르는 애니메이션
        self.event_shout_timer.start(2000)

    # ======================================
    # 새로운 캐릭터 애니메이션
    # ======================================

    def animate_event_character(self):

        if not self.event_active:
            return

        if self.event_character is None:
            return

        self.event_character.animate()

    # ======================================
    # 퇴장 시작
    # ======================================

    def start_event_exit(self):

        if not self.event_active:
            return

        self.event_phase = "Exit"

        # 새 캐릭터가 오른쪽으로 달려감
        self.event_character.set_state(
            "Run",
            face_right=True
        )

        # 펫은 귀를 계속 막고 있음
        self.event_move_timer.start(30)

    # ======================================
    # 특별 이벤트 종료
    # ======================================

    def finish_special_event(self):

        self.event_move_timer.stop()
        self.event_animation_timer.stop()
        self.event_shout_timer.stop()

        if self.event_character is not None:
            self.event_character.hide()

        self.event_active = False
        self.event_phase = None
        self.event_pet_position = None

        # 이벤트 종료 후 상태 복귀
        need_state = self.get_need_state()
        if need_state:
            self.set_state(need_state)

        elif self.is_dirty():
            self.set_state("Dirty")
            self.schedule_next_state()

        else:
            self.set_state("Idle")
            self.schedule_next_state()

        # 다음 이벤트가 예약되어 있다면 실행
        if self.event_queue:
            QTimer.singleShot(
                500,
                self.start_special_event
            )

    # ======================================
    # Angry 상태
    # ======================================

    def check_angry(self):
        # 기존 함수 이름 유지: 배고픔/화남을 함께 확인
        need_state = self.get_need_state()

        if self.event_active:
            return need_state is not None

        if need_state:
            if self.state not in ["Eat", "Happy", "Wash", "Play"]:
                self.state_timer.stop()
                if self.state != need_state:
                    self.set_state(need_state)
            return True

        if self.state in ["Angry", "Hungry"]:
            self.set_state("Dirty" if self.is_dirty() else "Idle")
            self.schedule_next_state()

        return False

    # ======================================
    # 상호작용
    # ======================================

    def play_interaction(self, new_state):

        if self.event_active:
            return

        self.state_timer.stop()

        self.set_state(new_state)

        self.interaction_timer.start(3000 if new_state == "Play" else 2000)

    def finish_interaction(self):

        if self.event_active:
            return

        was_playing = self.state == "Play"

        need_state = self.get_need_state()
        if need_state:
            self.set_state(need_state)

        else:
            self.set_state(
                "Dirty" if self.is_dirty() else "Idle"
            )

            self.schedule_next_state()

        # 놀기 애니메이션이 끝나면 경험치만 +20
        if was_playing:
            self.gain_exp(20)

        # 상호작용 종료 후 특별 이벤트 실행
        if self.event_queue:
            QTimer.singleShot(
                100,
                self.start_special_event
            )

    # ======================================
    # 상태 문구
    # ======================================

    def update_state_label(self):

        labels = {
            "Walk": "🐾 걷는 중",
            "Idle": "💛 쉬는 중",
            "Sleep": "💤 Zzz...",
            "Dirty": "💩 시궁창에 빠져버렸어!",
            "Eat": "🍎 짭쪼롬하니 마싯따~",
            "Play": "🎮 이야 이야다이야다!",
            "Happy": "💕 행복해!",
            "Wash": "🛁 씻는 중",
            "Angry": "😠 나 위로해줘!",
            "Hungry": "🍽️ 배가 너무 고파!",
            "CoverEars": "🙉 귀 막는 중!"
        }

        self.state_label.setText(
            labels.get(self.state, "")
        )

    # ======================================
    # 육성 수치 감소
    # ======================================

    def update_status(self):

        was_dirty = self.is_dirty()

        self.hunger = max(
            0, self.hunger - 2
        )

        self.happiness = max(
            0, self.happiness - 1
        )

        self.cleanliness = max(
            0, self.cleanliness - 1
        )

        # 이벤트 중에는 애니메이션을 방해하지 않음
        if self.event_active:
            return

        if self.get_need_state():
            self.check_angry()
            return

        if not was_dirty and self.is_dirty():

            if self.state not in [
                "Eat", "Happy", "Wash", "Play"
            ]:

                self.state_timer.stop()
                self.set_state("Dirty")
                self.schedule_next_state()

        self.check_angry()

    # ======================================
    # 밥 주기
    # ======================================

    def feed_pet(self):

        if self.event_active or self.interaction_timer.isActive():
            return

        self.hunger = min(
            100, self.hunger + 20
        )

        self.play_interaction("Eat")
        self.gain_exp(10)

        self.show_message(
            "냠냠! 🍎"
        )

    # ======================================
    # 쓰다듬기
    # ======================================

    def pet_pet(self):

        if self.event_active or self.interaction_timer.isActive():
            return

        self.happiness = min(
            100, self.happiness + 15
        )

        self.play_interaction("Happy")
        self.gain_exp(15)

        self.show_message(
            "기분이 좋아졌어! 💕"
        )

    # ======================================
    # 씻기기
    # ======================================

    def wash_pet(self):

        if self.event_active or self.interaction_timer.isActive():
            return

        self.cleanliness = 100

        self.play_interaction("Wash")
        self.gain_exp(10)

        self.show_message(
            "🛁 푸르르르르! ✨"
        )

    # ======================================
    # 놀기 (경험치만 +20)
    # ======================================

    def play_pet(self):

        if self.event_active or self.interaction_timer.isActive():
            return

        self.play_interaction("Play")
        self.show_message("🎮 싫어~싫어싫~어!")

    # ======================================
    # 상태 확인
    # ======================================

    def show_status(self):

        message = (
            f"이름: {self.pet_name}\n"
            f"레벨: {self.level}\n"
            f"경험치: {self.exp}/{self.max_exp}\n"
            f"포만도: {self.hunger}/100\n"
            f"행복도: {self.happiness}/100\n"
            f"청결도: {self.cleanliness}/100\n"
            f"현재 행동: {self.state}\n"
            f"위생 상태: "
            f"{'더러움' if self.is_dirty() else '깨끗함'}"
        )

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("펫 상태 확인")
        msg_box.setText(message)

        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Ok
        )

        self.is_menu_open = True
        msg_box.exec()
        self.is_menu_open = False

    # ======================================
    # 메시지 표시
    # ======================================

    def show_message(self, message):

        self.message_version += 1

        version = self.message_version

        self.state_label.setText(message)

        def restore():

            if version == self.message_version:
                self.update_state_label()

        QTimer.singleShot(
            1500,
            restore
        )

    # ======================================
    # 클릭 메뉴
    # ======================================

    def show_pet_menu(self):

        if self.is_menu_open:
            return

        # 이벤트 중에는 메뉴를 열지 않음
        if self.event_active:
            return

        self.is_menu_open = True

        menu = QMenu(self)

        feed_action = menu.addAction("🍎 밥 주기")
        pet_action = menu.addAction("💕 쓰다듬기")
        play_action = menu.addAction("🎮 놀기")
        wash_action = menu.addAction("🛁 씻기기")
        status_action = menu.addAction("📊 상태 확인")

        menu.addSeparator()

        quit_action = menu.addAction("❌ 종료하기")

        selected = menu.exec(
            self.mapToGlobal(
                self.rect().center()
            )
        )

        self.is_menu_open = False

        if selected == feed_action:
            self.feed_pet()

        elif selected == pet_action:
            self.pet_pet()

        elif selected == play_action:
            self.play_pet()

        elif selected == wash_action:
            self.wash_pet()

        elif selected == status_action:
            self.show_status()

        elif selected == quit_action:
            self.quit_program()

    # ======================================
    # 종료
    # ======================================

    def quit_program(self):

        self.event_move_timer.stop()
        self.event_animation_timer.stop()
        self.event_shout_timer.stop()

        if self.event_character is not None:
            self.event_character.close()

        QApplication.instance().quit()

    # ======================================
    # 마우스 이벤트
    # ======================================

    def mousePressEvent(self, event):

        if self.event_active:
            return

        if event.button() == Qt.MouseButton.LeftButton:

            self.press_position = (
                event.globalPosition().toPoint()
            )

            self.drag_position = (
                self.press_position
                - self.frameGeometry().topLeft()
            )

            self.is_dragging = False

    def mouseMoveEvent(self, event):

        if self.event_active:
            return

        if (
            self.drag_position is not None
            and event.buttons()
            & Qt.MouseButton.LeftButton
        ):

            current = (
                event.globalPosition().toPoint()
            )

            if (
                current - self.press_position
            ).manhattanLength() > 5:

                self.is_dragging = True

            if self.is_dragging:
                self.move(
                    current - self.drag_position
                )

    def mouseReleaseEvent(self, event):

        if self.event_active:
            return

        if event.button() == Qt.MouseButton.LeftButton:

            was_dragging = self.is_dragging

            self.drag_position = None
            self.press_position = None
            self.is_dragging = False

            if not was_dragging:
                self.show_pet_menu()

    def contextMenuEvent(self, event):

        self.show_pet_menu()


# ==========================================
# 프로그램 실행
# ==========================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)

    pet = DesktopPet()
    pet.show()

    sys.exit(app.exec())
