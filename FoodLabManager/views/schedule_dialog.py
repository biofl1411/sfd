import os
import json
#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
스케줄 작성 팝업 창
'''

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                           QPushButton, QFormLayout, QComboBox, QDateEdit,
                           QSpinBox, QDoubleSpinBox, QGroupBox, QCompleter,
                           QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
                           QRadioButton, QButtonGroup, QWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

# 식품유형 선택 다이얼로그 클래스 추가
class FoodTypeSelectionDialog(QDialog):
    """식품유형 선택 다이얼로그"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("식품유형 선택")
        self.setMinimumWidth(600)  # 너비 증가
        self.setMinimumHeight(400)
        self.selected_food_type = None
        self.initUI()
        self.load_food_types()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # 검색 영역
        search_layout = QHBoxLayout()
        search_label = QLabel("식품유형 검색:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("식품유형 검색...")
        self.search_input.textChanged.connect(self.filter_food_types)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # 식품유형 목록 테이블
        self.food_type_table = QTableWidget()
        self.food_type_table.setColumnCount(6)  # 5에서 6으로 변경 (검사항목 추가)
        self.food_type_table.setHorizontalHeaderLabels([
            "식품유형", "카테고리", "설군여부", "열군여부", "성상", "검사항목"  # 검사항목 추가
        ])
        
        # 열 너비 조정 (검사항목 열을 좀 더 넓게 설정)
        self.food_type_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # 식품유형
        self.food_type_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 카테고리
        self.food_type_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # 설군여부
        self.food_type_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # 열군여부
        self.food_type_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # 성상
        self.food_type_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # 검사항목
        
        self.food_type_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.food_type_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.food_type_table.doubleClicked.connect(self.on_table_double_clicked)
        
        layout.addWidget(self.food_type_table)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        
        select_btn = QPushButton("선택")
        select_btn.clicked.connect(self.accept_selection)
        
        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(select_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def update_table(self, food_types):
        """테이블 업데이트"""
        self.food_type_table.setRowCount(len(food_types) if food_types else 0)
        
        if food_types:
            for row, food_type in enumerate(food_types):
                self.food_type_table.setItem(row, 0, QTableWidgetItem(food_type['type_name']))
                self.food_type_table.setItem(row, 1, QTableWidgetItem(food_type['category'] or ""))
                self.food_type_table.setItem(row, 2, QTableWidgetItem(food_type['sterilization'] or ""))
                self.food_type_table.setItem(row, 3, QTableWidgetItem(food_type['pasteurization'] or ""))
                self.food_type_table.setItem(row, 4, QTableWidgetItem(food_type['appearance'] or ""))
                self.food_type_table.setItem(row, 5, QTableWidgetItem(food_type['test_items'] or ""))  # 검사항목 추가
                
    def filter_food_types(self, text):
        """검색어에 따라 목록 필터링"""
        if not text:
            # 검색어가 없으면 전체 목록 표시
            self.update_table(self.all_food_types)
            return
            
        filtered_types = []
        for food_type in self.all_food_types:
            # 식품유형 이름에 검색어가 포함되어 있으면 필터링된 목록에 추가
            if text.lower() in food_type['type_name'].lower():
                filtered_types.append(food_type)
                
        self.update_table(filtered_types)
        
    def on_table_double_clicked(self, index):
        """테이블 더블클릭 시 해당 항목 선택"""
        self.accept_selection()
        
    def accept_selection(self):
        """선택한 식품유형 반환"""
        selected_indexes = self.food_type_table.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "선택 오류", "식품유형을 선택하세요.")
            return
            
        # 선택된 행 인덱스
        row = selected_indexes[0].row()
        
        # 선택된 식품유형 이름
        type_name = self.food_type_table.item(row, 0).text()
        
        # 선택된 식품유형 데이터 찾기
        for food_type in self.all_food_types:
            if food_type['type_name'] == type_name:
                self.selected_food_type = food_type
                self.accept()
                break

class ScheduleCreateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("스케줄 작성")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # 클라이언트 정보 목록 로드
        from models.clients import Client
        self.clients = Client.get_all()
        self.client_names = [client['name'] for client in self.clients] if self.clients else []
        
        # UI 초기화
        self.initUI()
    
    def initUI(self):
        """UI 초기화"""
        main_layout = QVBoxLayout(self)
        
        # 1. 업체 정보 섹션
        client_group = QGroupBox("업체 정보")
        client_layout = QVBoxLayout()
        
        # 업체 검색 필드
        search_layout = QHBoxLayout()
        search_label = QLabel("업체명:")
        self.client_search = QLineEdit()
        self.client_search.setPlaceholderText("업체명 검색...")
        completer = QCompleter(self.client_names)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.client_search.setCompleter(completer)
        
        self.search_btn = QPushButton("검색")
        self.search_btn.clicked.connect(self.search_client)
        
        self.new_client_btn = QPushButton("신규 등록")
        self.new_client_btn.clicked.connect(self.create_new_client)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.client_search)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.new_client_btn)
        
        client_layout.addLayout(search_layout)
        
        # 선택된 업체 정보 표시
        info_layout = QFormLayout()
        self.client_name_label = QLabel("-")
        self.client_contact_label = QLabel("-")
        self.client_phone_label = QLabel("-")
        
        info_layout.addRow("업체명:", self.client_name_label)
        info_layout.addRow("담당자:", self.client_contact_label)
        info_layout.addRow("연락처:", self.client_phone_label)
        
        client_layout.addLayout(info_layout)
        client_group.setLayout(client_layout)
        main_layout.addWidget(client_group)
        
        # 2. 실험 정보 섹션
        experiment_group = QGroupBox("실험 정보")
        experiment_layout = QVBoxLayout()
        
        # 샘플명
        sample_layout = QHBoxLayout()
        sample_label = QLabel("샘플명:")
        sample_label.setMinimumWidth(80)
        self.sample_name = QLineEdit()
        sample_layout.addWidget(sample_label)
        sample_layout.addWidget(self.sample_name)
        experiment_layout.addLayout(sample_layout)
        
        # 실험 방법 (라디오 버튼)
        method_layout = QHBoxLayout()
        method_label = QLabel("실험방법:")
        method_label.setMinimumWidth(80)
        
        self.method_group = QButtonGroup(self)
        self.real_method_radio = QRadioButton("실측실험")
        self.real_method_radio.setChecked(True)
        self.acceleration_method_radio = QRadioButton("가속실험")
        
        self.method_group.addButton(self.real_method_radio)
        self.method_group.addButton(self.acceleration_method_radio)
        
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.real_method_radio)
        method_layout.addWidget(self.acceleration_method_radio)
        method_layout.addStretch()
        
        experiment_layout.addLayout(method_layout)
        
        # 보관 온도 (버튼 방식)
        temp_label_layout = QHBoxLayout()
        temp_label = QLabel("보관온도:")
        temp_label.setMinimumWidth(80)
        temp_label_layout.addWidget(temp_label)
        temp_label_layout.addStretch()
        experiment_layout.addLayout(temp_label_layout)
        
        temp_button_layout = QHBoxLayout()
        
        self.temp_group = QButtonGroup(self)
        self.room_temp_radio = QRadioButton("실온")
        self.normal_temp_radio = QRadioButton("상온")
        self.refrigerated_radio = QRadioButton("냉장")
        self.frozen_radio = QRadioButton("냉동")
        self.custom_temp_radio = QRadioButton("의뢰자 요청 온도")
        
        self.temp_group.addButton(self.room_temp_radio)
        self.temp_group.addButton(self.normal_temp_radio)
        self.temp_group.addButton(self.refrigerated_radio)
        self.temp_group.addButton(self.frozen_radio)
        self.temp_group.addButton(self.custom_temp_radio)
        
        temp_button_layout.addWidget(self.room_temp_radio)
        temp_button_layout.addWidget(self.normal_temp_radio)
        temp_button_layout.addWidget(self.refrigerated_radio)
        temp_button_layout.addWidget(self.frozen_radio)
        temp_button_layout.addWidget(self.custom_temp_radio)
        temp_button_layout.addStretch()
        
        experiment_layout.addLayout(temp_button_layout)
        
        # 온도 입력 필드 (의뢰자 요청 온도일 때 표시)
        self.custom_temp_widget = QWidget()
        custom_temp_layout = QHBoxLayout(self.custom_temp_widget)
        custom_temp_layout.setContentsMargins(0, 0, 0, 0)
        
        # 실측실험 온도 입력 (1개)
        self.real_temp_widget = QWidget()
        real_temp_layout = QHBoxLayout(self.real_temp_widget)
        real_temp_layout.setContentsMargins(0, 0, 0, 0)
        
        real_temp_label = QLabel("온도(°C):")
        self.real_temp_input = QSpinBox()
        self.real_temp_input.setRange(-50, 100)
        self.real_temp_input.setValue(25)
        self.real_temp_input.setSuffix(" °C")
        
        real_temp_layout.addWidget(real_temp_label)
        real_temp_layout.addWidget(self.real_temp_input)
        real_temp_layout.addStretch()
        
        # 가속실험 온도 입력 (3개)
        self.accel_temp_widget = QWidget()
        accel_temp_layout = QHBoxLayout(self.accel_temp_widget)
        accel_temp_layout.setContentsMargins(0, 0, 0, 0)
        
        accel_temp_label = QLabel("온도(°C):")
        self.accel_temp_input1 = QSpinBox()
        self.accel_temp_input1.setRange(-50, 100)
        self.accel_temp_input1.setValue(25)
        self.accel_temp_input1.setSuffix(" °C")
        
        self.accel_temp_input2 = QSpinBox()
        self.accel_temp_input2.setRange(-50, 100)
        self.accel_temp_input2.setValue(35)
        self.accel_temp_input2.setSuffix(" °C")
        
        self.accel_temp_input3 = QSpinBox()
        self.accel_temp_input3.setRange(-50, 100)
        self.accel_temp_input3.setValue(45)
        self.accel_temp_input3.setSuffix(" °C")
        
        accel_temp_layout.addWidget(accel_temp_label)
        accel_temp_layout.addWidget(self.accel_temp_input1)
        accel_temp_layout.addWidget(self.accel_temp_input2)
        accel_temp_layout.addWidget(self.accel_temp_input3)
        accel_temp_layout.addStretch()
        
        # 초기 상태는 숨김
        self.real_temp_widget.hide()
        self.accel_temp_widget.hide()
        
        custom_temp_layout.addWidget(self.real_temp_widget)
        custom_temp_layout.addWidget(self.accel_temp_widget)
        
        experiment_layout.addWidget(self.custom_temp_widget)
        
        # 선택된 온도 표시 레이블
        self.selected_temp_label = QLabel("선택 온도: 실온 (25°C)")
        self.selected_temp_label.setStyleSheet("font-weight: bold; color: blue;")
        experiment_layout.addWidget(self.selected_temp_label)
        
        # 실험기간
        period_layout = QHBoxLayout()
        period_label = QLabel("실험기간:")
        period_label.setMinimumWidth(80)
        self.experiment_days = QSpinBox()
        self.experiment_days.setRange(1, 365)
        self.experiment_days.setValue(21)
        self.experiment_days.setSuffix(" 일")
        period_layout.addWidget(period_label)
        period_layout.addWidget(self.experiment_days)
        period_layout.addStretch()
        experiment_layout.addLayout(period_layout)
        
        # 샘플링 간격
        interval_layout = QHBoxLayout()
        interval_label = QLabel("샘플링 간격:")
        interval_label.setMinimumWidth(80)
        self.sampling_interval = QSpinBox()
        self.sampling_interval.setRange(1, 30)
        self.sampling_interval.setValue(3)
        self.sampling_interval.setSuffix(" 일")
        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.sampling_interval)
        interval_layout.addStretch()
        experiment_layout.addLayout(interval_layout)
        
        # 실험 시작일
        start_date_layout = QHBoxLayout()
        start_date_label = QLabel("실험 시작일:")
        start_date_label.setMinimumWidth(80)
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setCalendarPopup(True)
        start_date_layout.addWidget(start_date_label)
        start_date_layout.addWidget(self.start_date)
        start_date_layout.addStretch()
        experiment_layout.addLayout(start_date_layout)
        
        experiment_group.setLayout(experiment_layout)
        main_layout.addWidget(experiment_group)
        
        # 제품 정보 섹션
        product_group = QGroupBox("제품 정보")
        product_layout = QVBoxLayout()

        # 제품명
        product_name_layout = QHBoxLayout()
        product_name_label = QLabel("제품명:")
        product_name_label.setMinimumWidth(80)
        self.product_name = QLineEdit()
        product_name_layout.addWidget(product_name_label)
        product_name_layout.addWidget(self.product_name)
        product_layout.addLayout(product_name_layout)

        # 식품유형 선택 (콤보박스 대신 선택 버튼 사용)
        food_type_layout = QHBoxLayout()
        food_type_label = QLabel("식품유형:")
        food_type_label.setMinimumWidth(80)
        self.food_type_input = QLineEdit()
        self.food_type_input.setReadOnly(True)
        self.food_type_select_btn = QPushButton("선택")
        self.food_type_select_btn.clicked.connect(self.select_food_type)
        food_type_layout.addWidget(food_type_label)
        food_type_layout.addWidget(self.food_type_input)
        food_type_layout.addWidget(self.food_type_select_btn)
        product_layout.addLayout(food_type_layout)

        # 살균여부 필드
        sterilization_layout = QHBoxLayout()
        sterilization_label = QLabel("살균여부:")
        sterilization_label.setMinimumWidth(80)
        self.sterilization = QLineEdit()
        self.sterilization.setReadOnly(True)
        sterilization_layout.addWidget(sterilization_label)
        sterilization_layout.addWidget(self.sterilization)
        product_layout.addLayout(sterilization_layout)

        # 멸균여부 필드
        pasteurization_layout = QHBoxLayout()
        pasteurization_label = QLabel("멸균여부:")
        pasteurization_label.setMinimumWidth(80)
        self.pasteurization = QLineEdit()
        self.pasteurization.setReadOnly(True)
        pasteurization_layout.addWidget(pasteurization_label)
        pasteurization_layout.addWidget(self.pasteurization)
        product_layout.addLayout(pasteurization_layout)

        # 성상 필드
        appearance_layout = QHBoxLayout()
        appearance_label = QLabel("성상:")
        appearance_label.setMinimumWidth(80)
        self.appearance = QLineEdit()
        self.appearance.setReadOnly(True)
        appearance_layout.addWidget(appearance_label)
        appearance_layout.addWidget(self.appearance)
        product_layout.addLayout(appearance_layout)

        # 검사항목 필드
        test_items_layout = QHBoxLayout()
        test_items_label = QLabel("검사항목:")
        test_items_label.setMinimumWidth(80)
        self.test_items = QLabel("")
        self.test_items.setWordWrap(True)
        self.test_items.setStyleSheet("color: blue;")
        test_items_layout.addWidget(test_items_label)
        test_items_layout.addWidget(self.test_items)
        product_layout.addLayout(test_items_layout)

        product_group.setLayout(product_layout)
        main_layout.addWidget(product_group)
        
        # 3. 버튼 섹션
        button_layout = QHBoxLayout()

        # '미리보기' 대신 '세부 스케줄 조정' 버튼 추가
        self.detail_btn = QPushButton("세부 스케줄 조정")
        self.detail_btn.clicked.connect(self.open_schedule_detail)

        # 임시저장 버튼 추가
        self.temp_save_btn = QPushButton("임시저장")
        self.temp_save_btn.clicked.connect(self.save_temporary)

        self.confirm_btn = QPushButton("확인")
        self.confirm_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.detail_btn)
        button_layout.addWidget(self.temp_save_btn)
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)
        
        # 시그널 연결
        self.real_method_radio.toggled.connect(self.on_method_changed)
        self.acceleration_method_radio.toggled.connect(self.on_method_changed)
        
        self.room_temp_radio.toggled.connect(self.on_temp_option_changed)
        self.normal_temp_radio.toggled.connect(self.on_temp_option_changed)
        self.refrigerated_radio.toggled.connect(self.on_temp_option_changed)
        self.frozen_radio.toggled.connect(self.on_temp_option_changed)
        self.custom_temp_radio.toggled.connect(self.on_temp_option_changed)
        
        # 초기 상태 설정
        self.room_temp_radio.setChecked(True)  # 기본값: 실온
        self.on_method_changed()
        self.on_temp_option_changed()

    def select_food_type(self):
        """식품유형 선택 다이얼로그 표시"""
        dialog = FoodTypeSelectionDialog(self)
        if dialog.exec_():
            food_type = dialog.selected_food_type
            if food_type:
                # 식품유형 정보 UI에 표시
                self.food_type_input.setText(food_type['type_name'])
                self.sterilization.setText(food_type['sterilization'] or "")
                self.pasteurization.setText(food_type['pasteurization'] or "")
                self.appearance.setText(food_type['appearance'] or "")
                self.test_items.setText(food_type['test_items'] or "")
                
                # 선택한 식품유형 정보 저장
                self.selected_food_type = food_type
    
    def save_temporary(self):
        """현재 입력된 데이터를 임시 저장"""
        # 임시 저장할 데이터 수집
        schedule_data = self.collect_schedule_data()
        
        try:
            # 임시 저장 디렉토리 확인 및 생성
            temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            # 임시 파일 경로
            temp_file = os.path.join(temp_dir, "temp_schedule.json")
            
            # 데이터를 JSON으로 저장
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(schedule_data, f, ensure_ascii=False, indent=2)
                
            QMessageBox.information(self, "임시저장", "스케줄 데이터가 임시 저장되었습니다.")
        except Exception as e:
            QMessageBox.warning(self, "임시저장 실패", f"임시저장 중 오류가 발생했습니다: {str(e)}")

    def collect_schedule_data(self):
        """현재 UI에서 스케줄 데이터 수집"""
        schedule_data = {}
        
        # 업체 정보
        if hasattr(self, 'selected_client'):
            schedule_data["company"] = {
                "name": self.selected_client.get('name', ''),
                "contact_person": self.selected_client.get('contact_person', ''),
                "phone": self.selected_client.get('phone', ''),
                "mobile": self.selected_client.get('mobile', '')
            }
        else:
            schedule_data["company"] = {
                "name": "",
                "contact_person": "",
                "phone": "",
                "mobile": ""
            }
        
        # 실험 정보
        schedule_data["experiment"] = {
            "sample_name": self.sample_name.text(),
            "method": "실측실험" if self.real_method_radio.isChecked() else "가속실험",
            "storage_temp": self.get_storage_temp(),
            "experiment_days": self.experiment_days.value(),
            "sampling_interval": self.sampling_interval.value(),
            "start_date": self.start_date.date().toString("yyyy-MM-dd")
        }
        
        # 제품 정보
        schedule_data["product"] = {
            "name": self.product_name.text(),
            "food_type": self.food_type_input.text(),
            "sterilization": self.sterilization.text(),
            "pasteurization": self.pasteurization.text(),
            "appearance": self.appearance.text(),
            "test_items": self.test_items.text()
        }
        
        return schedule_data

    def open_schedule_detail(self):
        """세부 스케줄 조정 다이얼로그 열기"""
        # 임시 저장 먼저 수행
        schedule_data = self.collect_schedule_data()
        
        # 세부 스케줄 조정 다이얼로그 열기
        try:
            from .schedule_detail_dialog import ScheduleDetailDialog
            dialog = ScheduleDetailDialog(self, schedule_data)
            
            # 다이얼로그 실행 및 결과 처리
            if dialog.exec_():
                updated_data = dialog.get_updated_data()
                self.apply_updated_data(updated_data)
        except ImportError:
            # 다이얼로그 클래스가 없는 경우 기존 미리보기 함수 호출
            QMessageBox.information(self, "개발 중", "세부 스케줄 조정 기능은 현재 개발 중입니다.")
            self.preview_schedule()
    
    def apply_updated_data(self, updated_data):
        """세부 스케줄 조정 후 업데이트된 데이터 적용"""
        # 이 함수는 세부 스케줄 조정 다이얼로그에서 반환된 데이터를 UI에 반영
        # 실제 구현은 ScheduleDetailDialog 클래스가 완성된 후에 구현해야 함
        pass
        
    def on_method_changed(self):
        """실험 방법 변경 처리"""
        self.on_temp_option_changed()  # 온도 옵션 업데이트

    def on_temp_option_changed(self):
        """온도 옵션 변경 처리"""
        is_real_method = self.real_method_radio.isChecked()
        selected_temp = ""
        
        # 의뢰자 요청 온도인 경우 입력 필드 표시
        if self.custom_temp_radio.isChecked():
            self.custom_temp_widget.show()
            if is_real_method:
                self.real_temp_widget.show()
                self.accel_temp_widget.hide()
                selected_temp = f"의뢰자 요청 온도 ({self.real_temp_input.value()}°C)"
            else:
                self.real_temp_widget.hide()
                self.accel_temp_widget.show()
                selected_temp = f"의뢰자 요청 온도 ({self.accel_temp_input1.value()}°C, {self.accel_temp_input2.value()}°C, {self.accel_temp_input3.value()}°C)"
        else:
            self.custom_temp_widget.hide()
            
            # 각 온도 옵션에 따른 값 설정
            if self.room_temp_radio.isChecked():
                if is_real_method:
                    self.storage_temp_value = 25
                    selected_temp = "실온 (25°C)"
                else:
                    self.accel_temp_values = [25, 35, 45]
                    selected_temp = "실온 (25°C, 35°C, 45°C)"
            elif self.normal_temp_radio.isChecked():
                if is_real_method:
                    self.storage_temp_value = 15
                    selected_temp = "상온 (15°C)"
                else:
                    self.accel_temp_values = [15, 25, 35]
                    selected_temp = "상온 (15°C, 25°C, 35°C)"
            elif self.refrigerated_radio.isChecked():
                if is_real_method:
                    self.storage_temp_value = 10
                    selected_temp = "냉장 (10°C)"
                else:
                    self.accel_temp_values = [5, 10, 15]
                    selected_temp = "냉장 (5°C, 10°C, 15°C)"
            elif self.frozen_radio.isChecked():
                if is_real_method:
                    self.storage_temp_value = -18
                    selected_temp = "냉동 (-18°C)"
                else:
                    self.accel_temp_values = [-6, -12, -18]
                    selected_temp = "냉동 (-6°C, -12°C, -18°C)"
        
        self.selected_temp_label.setText(f"선택 온도: {selected_temp}")

    def get_storage_temp(self):
        """현재 선택된 보관 온도 값 반환"""
        if self.custom_temp_radio.isChecked():
            if self.real_method_radio.isChecked():
                return self.real_temp_input.value()
            else:
                # 가속실험에서는 첫 번째 온도 값만 반환 (미리보기용)
                return self.accel_temp_input1.value()
        else:
            if self.room_temp_radio.isChecked():
                return 25 if self.real_method_radio.isChecked() else 25
            elif self.normal_temp_radio.isChecked():
                return 15 if self.real_method_radio.isChecked() else 15
            elif self.refrigerated_radio.isChecked():
                return 10 if self.real_method_radio.isChecked() else 5
            elif self.frozen_radio.isChecked():
                return -18 if self.real_method_radio.isChecked() else -6
    
    def search_client(self):
        """업체 검색"""
        from models.clients import Client
        
        search_text = self.client_search.text().strip()
        if not search_text:
            QMessageBox.warning(self, "검색 오류", "검색할 업체명을 입력하세요.")
            return
        
        # 클라이언트 검색 (부분 일치)
        found_clients = Client.search(search_text)
        
        if not found_clients:
            reply = QMessageBox.question(
                self, "검색 결과", 
                f"'{search_text}' 업체를 찾을 수 없습니다. 신규 등록하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.create_new_client()
            return
        
        # 검색 결과가 1개면 바로 선택
        if len(found_clients) == 1:
            self.select_client(found_clients[0])
        else:
            # 검색 결과가 여러 개면 선택 다이얼로그 표시 (간단히 첫 번째 항목 선택으로 구현)
            self.select_client(found_clients[0])
            # 실제로는 여기서 업체 선택 다이얼로그를 표시해야 함
    
    def select_client(self, client):
        """업체 선택"""
        self.selected_client = client
        self.client_name_label.setText(client['name'])
        contact_info = ""
        if client['contact_person']:
            contact_info = client['contact_person']
            if client['mobile']:
                contact_info += f" ({client['mobile']})"
        self.client_contact_label.setText(contact_info or "-")
        self.client_phone_label.setText(client['phone'] or "-")
        
    def create_new_client(self):
        """신규 업체 등록"""
        # 여기서 ClientDialog를 직접 가져와서 사용
        from .client_tab import ClientDialog
        
        dialog = ClientDialog(self)
        if dialog.exec_():
            # 업체 목록 새로고침
            from models.clients import Client
            self.clients = Client.get_all()
            self.client_names = [client['name'] for client in self.clients] if self.clients else []
            
            # Completer 업데이트
            completer = QCompleter(self.client_names)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.client_search.setCompleter(completer)
            
            QMessageBox.information(self, "등록 완료", "새 업체가 등록되었습니다.")
    
    def preview_schedule(self):
        """스케줄 미리보기"""
        # 필수 입력 확인
        if not hasattr(self, 'selected_client'):
            QMessageBox.warning(self, "입력 오류", "업체를 선택해주세요.")
            return
        
        if not self.sample_name.text().strip():
            QMessageBox.warning(self, "입력 오류", "샘플명을 입력해주세요.")
            return
        
        if not self.product_name.text().strip():
            QMessageBox.warning(self, "입력 오류", "제품명을 입력해주세요.")
            return
        
        # 현재 선택된 온도 값 가져오기
        storage_temp = self.get_storage_temp()
        
        # 스케줄 미리보기 다이얼로그 생성
        is_real_method = self.real_method_radio.isChecked()
        method_text = "실측실험" if is_real_method else "가속실험"
        
        schedule_preview = SchedulePreviewDialog(
            client=self.selected_client,
            sample_name=self.sample_name.text(),
            product_name=self.product_name.text(),
            food_type_info={
                "type": self.food_type_input.text(),
                "sterilization": self.sterilization.text(),
                "pasteurization": self.pasteurization.text(),
                "appearance": self.appearance.text()
            },
            storage_temp=storage_temp,
            experiment_method=method_text,
            experiment_days=self.experiment_days.value(),
            sampling_interval=self.sampling_interval.value(),
            start_date=self.start_date.date(),
            food_type=self.food_type_input.text(),
            parent=self
        )
        
        result = schedule_preview.exec_()
        if result == QDialog.Accepted:
            self.confirm_btn.setEnabled(True)
    
    def save_schedule(self):
        """스케줄 저장"""
        # 여기에 스케줄 저장 로직 구현
        QMessageBox.information(self, "저장 완료", "스케줄이 저장되었습니다.")
        self.accept()

class SchedulePreviewDialog(QDialog):
    def __init__(self, client, sample_name, product_name, food_type_info, storage_temp, experiment_method, 
             experiment_days, sampling_interval, start_date, food_type, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("스케줄 미리보기")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # 스케줄 정보 저장
        self.client = client
        self.sample_name = sample_name
        self.product_name = product_name
        self.food_type_info = food_type_info
        self.storage_temp = storage_temp
        self.experiment_method = experiment_method
        self.experiment_days = experiment_days
        self.sampling_interval = sampling_interval
        self.start_date = start_date
        self.food_type = food_type
        
        # UI 초기화
        self.initUI()
        
        # 스케줄 생성
        self.generate_schedule()
    
    def initUI(self):
        """UI 초기화"""
        main_layout = QVBoxLayout(self)
        
        # 1. 정보 요약 섹션
        info_group = QGroupBox("실험 정보")
        info_layout = QFormLayout()
        
        info_layout.addRow("업체명:", QLabel(self.client['name']))
        info_layout.addRow("담당자:", QLabel(self.client['contact_person'] or "-"))
        info_layout.addRow("샘플명:", QLabel(self.sample_name))
        info_layout.addRow("제품명:", QLabel(self.product_name))
        info_layout.addRow("식품유형:", QLabel(self.food_type_info['type']))
        
        if self.food_type_info['sterilization']:
            info_layout.addRow("살균여부:", QLabel(self.food_type_info['sterilization']))
        if self.food_type_info['pasteurization']:
            info_layout.addRow("멸균여부:", QLabel(self.food_type_info['pasteurization']))
        if self.food_type_info['appearance']:
            info_layout.addRow("성상:", QLabel(self.food_type_info['appearance']))
        
        info_layout.addRow("실험방법:", QLabel(self.experiment_method))
        info_layout.addRow("보관온도:", QLabel(f"{self.storage_temp} °C"))
        info_layout.addRow("실험기간:", QLabel(f"{self.experiment_days} 일"))
        info_layout.addRow("샘플링 간격:", QLabel(f"{self.sampling_interval} 일"))
        info_layout.addRow("실험 시작일:", QLabel(self.start_date.toString("yyyy년 MM월 dd일")))
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
         
        # 2. 스케줄 테이블
        self.schedule_table = QTableWidget()
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 읽기 전용
        main_layout.addWidget(self.schedule_table)
        
        # 3. 버튼 섹션
        button_layout = QHBoxLayout()
        
        self.confirm_btn = QPushButton("확인")
        self.confirm_btn.clicked.connect(self.accept)
        
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
    
    def generate_schedule(self):
        """스케줄 테이블 생성"""
        # 1. 날짜 계산
        dates = []
        test_count = (self.experiment_days // self.sampling_interval) + 1
        for i in range(test_count):
            day = i * self.sampling_interval
            date = self.start_date.addDays(day)
            dates.append(date)
        
        # 2. 테이블 설정
        self.schedule_table.setRowCount(10)  # 고정 행 수
        self.schedule_table.setColumnCount(test_count + 1)  # 첫 열은 항목명
        
        # 3. 헤더 설정
        headers = ["구분"]
        for date in dates:
            headers.append(date.toString("MM월 dd일"))
        self.schedule_table.setHorizontalHeaderLabels(headers)
        
        # 4. 열 너비 설정
        self.schedule_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, test_count + 1):
            self.schedule_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 5. 실험 회차 행
        self.schedule_table.setSpan(0, 0, 1, 1)  # 첫 번째 셀 병합
        self.schedule_table.setItem(0, 0, QTableWidgetItem("회차"))
        
        for i in range(test_count):
            item = QTableWidgetItem(f"{i+1} 회")
            item.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setItem(0, i+1, item)
        
        # 6. 경과 일수 행
        self.schedule_table.setSpan(1, 0, 1, 1)
        self.schedule_table.setItem(1, 0, QTableWidgetItem("경과 일수"))
        
        for i in range(test_count):
            day = i * self.sampling_interval
            item = QTableWidgetItem(f"({day}일)")
            item.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setItem(1, i+1, item)
        
        # 7. 검사 항목 행
        test_items = ["일반세균", "대장균군", "진균수", "리스테리아", "살모넬라"]
        
        self.schedule_table.setSpan(2, 0, len(test_items), 1)
        self.schedule_table.setItem(2, 0, QTableWidgetItem("검사항목"))
        
        for row, item_name in enumerate(test_items, 2):
            # 항목명 셀
            name_cell = QTableWidgetItem(item_name)
            name_cell.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setItem(row, 0, name_cell)
            
            # O 표시 셀 - 각 항목별로 다른 패턴 적용
            for col in range(1, test_count + 1):
                # 임시 로직: 항목에 따라 패턴 적용
                show_mark = False
                if item_name == "일반세균" or item_name == "대장균군":
                    show_mark = True  # 모든 회차에 검사
                elif item_name == "진균수":
                    show_mark = (col % 2 == 1)  # 홀수 회차에만 검사
                elif item_name == "리스테리아":
                    show_mark = (col % 3 == 0)  # 3의 배수 회차에만 검사
                elif item_name == "살모넬라":
                    show_mark = (col == 1 or col == test_count)  # 첫 회차와 마지막 회차에만 검사
                
                cell = QTableWidgetItem("O" if show_mark else "")
                cell.setTextAlignment(Qt.AlignCenter)
                self.schedule_table.setItem(row, col, cell)
        
        # 8. 비용 행
        cost_row = 2 + len(test_items)
        self.schedule_table.setSpan(cost_row, 0, 1, 1)
        cost_label = QTableWidgetItem("회차별 비용")
        cost_label.setTextAlignment(Qt.AlignCenter)
        self.schedule_table.setItem(cost_row, 0, cost_label)
        
        # 회차별 비용 계산 (임시 로직)
        for col in range(1, test_count + 1):
            cost = 0
            if col == 1 or col == test_count:
                cost = 129000  # 첫 회차와 마지막 회차는 비용이 더 큼
            else:
                cost = 49000
            
            cost_item = QTableWidgetItem(f"{cost:,}")
            cost_item.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setItem(cost_row, col, cost_item)
        
        # 9. 기타 비용 행
        other_costs = [
            {"name": "검사비용", "desc": "소모품비용", "cost": 632000},
            {"name": "데이터 분석비용", "desc": "보고서 + 보고서작성", "cost": 300000}
        ]
        
        for i, cost_info in enumerate(other_costs):
            row = cost_row + 1 + i
            
            # 비용 항목 셀
            self.schedule_table.setItem(row, 0, QTableWidgetItem(cost_info["name"]))
            
            # 설명 셀 (병합)
            self.schedule_table.setSpan(row, 1, 1, test_count - 1)
            desc_item = QTableWidgetItem(cost_info["desc"])
            desc_item.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setItem(row, 1, desc_item)
            
            # 비용 셀
            cost_item = QTableWidgetItem(f"{cost_info['cost']:,}")
            cost_item.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setItem(row, test_count, cost_item)
        
        # 10. 총 비용 행
        total_row = cost_row + 1 + len(other_costs)
        
        self.schedule_table.setItem(total_row, 0, QTableWidgetItem("최종비용"))
        
        # 총액 계산
        total_cost = sum(49000 if col != 1 and col != test_count else 129000 for col in range(1, test_count + 1))
        total_cost += sum(cost_info["cost"] for cost_info in other_costs)
        
        # 총액 셀 (병합)
        self.schedule_table.setSpan(total_row, 1, 1, test_count - 1)
        total_desc = QTableWidgetItem("검사비용 + 데이터 분석비용")
        total_desc.setTextAlignment(Qt.AlignCenter)
        self.schedule_table.setItem(total_row, 1, total_desc)
        
        # 최종 비용 셀
        total_item = QTableWidgetItem(f"{total_cost:,}")
        total_item.setTextAlignment(Qt.AlignCenter)
        total_item.setBackground(Qt.yellow)
        self.schedule_table.setItem(total_row, test_count, total_item)
        
        # 11. 부가세 포함 금액 행
        vat_row = total_row + 1
        self.schedule_table.setItem(vat_row, 0, QTableWidgetItem(""))
        
        # 부가세 포함 금액 (테이블 아래에 표시)
        self.schedule_table.setSpan(vat_row, 1, 1, test_count)
        vat_total = total_cost * 1.1  # 부가세 10%
        vat_item = QTableWidgetItem(f"부가세 포함 금액: {vat_total:,.0f}원")
        vat_item.setTextAlignment(Qt.AlignRight)
        vat_item.setBackground(Qt.yellow)
        self.schedule_table.setItem(vat_row, 1, vat_item)
        
        # 12. 테이블 스타일 적용
        self.schedule_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d0d0d0;
            }
        """)