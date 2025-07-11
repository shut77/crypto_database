import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QDialog,
                             QVBoxLayout, QLabel, QPushButton, QLineEdit,
                             QFormLayout, QDialogButtonBox, QTableWidget,
                             QTableWidgetItem, QSpinBox, QHBoxLayout)
import psycopg2
from config import host, user, password, db_name
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PyQt5.QtCore import QDateTime

class SuccessDialog(QMessageBox):
    def __init__(self, parent=None, text="Операция успешно завершена!"):
        super().__init__(parent)
        self.setWindowTitle("Успех")
        self.setText(text)
        self.setStyleSheet("""
            QMessageBox {
                background-color: #222;
                color: white;
                font-size: 18px;
            }
            QLabel {
                color: #4CAF50;
                font-size: 18px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-size: 16px;
                border-radius: 4px;
                min-width: 100px;
            }
        """)


class ErrorDialog(QMessageBox):
    def __init__(self, parent=None, text="Произошла ошибка!"):
        super().__init__(parent)
        self.setWindowTitle("Ошибка")
        self.setText(text)
        self.setStyleSheet("""
            QMessageBox {
                background-color: #222;
                color: white;
                font-size: 18px;
            }
            QLabel {
                color: #F44336;
                font-size: 18px;
            }
            QPushButton {
                background-color: #F44336;
                color: white;
                padding: 8px 16px;
                font-size: 16px;
                border-radius: 4px;
                min-width: 100px;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TriGaDa Balance")
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.current_user = None

        # Подключение к БД
        try:
            self.conn = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            ErrorDialog(self, "Не удалось подключиться к базе данных!").exec_()
            sys.exit(1)

        # stacked widget для страниц
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Создаем страницы
        self.create_main_page()
        self.create_login_page()
        self.create_register_page()
        self.create_profile_page()

        # главная страница
        self.stacked_widget.setCurrentIndex(0)

    def create_main_page(self):
        # Создаём главный контейнер
        page = QtWidgets.QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        # Левая часть (3/4)
        left_widget = QtWidgets.QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(QtCore.Qt.AlignCenter)
        left_layout.setSpacing(30)

        # Заголовок
        title = QLabel("TriGaDa Balance")
        title.setStyleSheet("""
            color: orange;
            font-size: 72px;
            font-weight: bold;
            margin-bottom: 50px;
        """)
        left_layout.addWidget(title, alignment=QtCore.Qt.AlignCenter)

        # Кнопки
        buttons = [
            ("Войти", self.show_login_page, "green"),
            ("Зарегистрироваться", self.show_register_page, "orange"),
            ("О бирже", self.show_info, "white")
        ]

        for text, handler, color in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {'black' if color == 'white' else 'white'};
                    font-size: 36px;
                    padding: 25px;
                    min-width: 400px;
                    border-radius: 15px;
                    margin: 10px;
                }}
                QPushButton:hover {{
                    background-color: {'dark' + color if color != 'white' else 'lightgray'};
                }}
            """)
            btn.clicked.connect(handler)
            left_layout.addWidget(btn)

        # Правая часть (1/4)
        right_widget = QtWidgets.QLabel()
        right_widget.setPixmap(QtGui.QPixmap("C://Users//Artem//Downloads//shap.jpg"))
        right_widget.setScaledContents(True)

        # Распределяем пространство (3:1 соотношение)
        main_layout.addWidget(left_widget, 3)  # 3/4 ширины
        main_layout.addWidget(right_widget, 1)  # 1/4 ширины

        self.stacked_widget.addWidget(page)

    def create_login_page(self):
        #  главный контейнер
        page = QtWidgets.QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        # Левая часть (3/4) - форма входа
        left_widget = QtWidgets.QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(QtCore.Qt.AlignCenter)
        left_layout.setSpacing(30)

        # Форма входа
        form = QFormLayout()
        form.setSpacing(20)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Имя пользователя")
        self.login_username.setStyleSheet("""
            font-size: 24px;
            padding: 15px;
            min-width: 300px;
            max-width: 800px;
        """)
        form.addRow("Имя пользователя:", self.login_username)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setStyleSheet("""
            font-size: 24px;
            padding: 15px;
            min-width: 300px;
            max-width: 800px;
        """)
        form.addRow("Пароль:", self.login_password)

        left_layout.addLayout(form)

        # Кнопки
        btn_box = QDialogButtonBox()
        btn_box.setStyleSheet("font-size: 24px;")

        login_btn = btn_box.addButton("Войти", QDialogButtonBox.AcceptRole)
        login_btn.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 15px;
            min-width: 200px;
        """)

        cancel_btn = btn_box.addButton("Отмена", QDialogButtonBox.RejectRole)
        cancel_btn.setStyleSheet("""
            background-color: #F44336;
            color: white;
            padding: 15px;
            min-width: 200px;
        """)

        def clear_fields():
            self.login_username.clear()
            self.login_password.clear()

        #  входа
        def handle_login_and_clear():
            # Проверяем заполненность полей перед обработкой
            if not self.login_username.text() or not self.login_password.text():
                QMessageBox.warning(page, "Ошибка", "Заполните все поля")
                return


            try:
                if self.handle_login():  # Предполагаем, что возвращает True при успехе
                    clear_fields()  # Очищаем только после успешного входа
            except Exception as e:
                QMessageBox.critical(page, "Ошибка", f"Ошибка входа: {str(e)}")

        # Очистка только при нажатии Отмена
        btn_box.rejected.connect(clear_fields)
        btn_box.rejected.connect(self.show_main_page)

        # Новая логика для кнопки входа
        btn_box.accepted.connect(handle_login_and_clear)

        left_layout.addWidget(btn_box, alignment=QtCore.Qt.AlignCenter)

        # Правая часть (1/4) - изображение
        right_widget = QtWidgets.QLabel()
        right_widget.setPixmap(QtGui.QPixmap("C://Users//Artem//Downloads//shap.jpg"))
        right_widget.setScaledContents(True)

        # Распределяем пространство (3:1 соотношение)
        main_layout.addWidget(left_widget, 3)  # 3/4 ширины
        main_layout.addWidget(right_widget, 1)  # 1/4 ширины

        # Сохраняем ссылку на страницу
        self.login_page = page
        self.stacked_widget.addWidget(page)

        # Перехватываем переход на главную страницу для очистки
        original_show_main_page = self.show_main_page

        def show_main_page_with_clear():
            clear_fields()
            original_show_main_page()

        self.show_main_page = show_main_page_with_clear

    def create_register_page(self):
        # Создаём главный контейнер с горизонтальной компоновкой
        page = QtWidgets.QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        # Левая часть (3/4) - форма регистрации
        left_widget = QtWidgets.QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setAlignment(QtCore.Qt.AlignCenter)
        left_layout.setSpacing(30)

        # Форма регистрации
        form = QFormLayout()
        form.setSpacing(20)

        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Имя пользователя")
        self.reg_username.setStyleSheet("""
            font-size: 24px;
            padding: 15px;
            min-width: 300px;
            max-width: 1100px;
        """)
        form.addRow("Имя пользователя:", self.reg_username)

        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Пароль")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setStyleSheet("""
            font-size: 24px;
            padding: 15px;
            min-width: 300px;
            max-width: 1100px;
        """)
        form.addRow("Пароль:", self.reg_password)

        left_layout.addLayout(form)

        # Кнопки
        btn_box = QDialogButtonBox()
        btn_box.setStyleSheet("font-size: 24px;")

        reg_btn = btn_box.addButton("Зарегистрироваться", QDialogButtonBox.AcceptRole)
        reg_btn.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            padding: 15px;
            min-width: 200px;
        """)

        cancel_btn = btn_box.addButton("Отмена", QDialogButtonBox.RejectRole)
        cancel_btn.setStyleSheet("""
            background-color: #F44336;
            color: white;
            padding: 15px;
            min-width: 200px;
        """)

        def clear_fields():
            self.reg_username.clear()
            self.reg_password.clear()

        # Модифицированный обработчик регистрации
        def handle_register_and_clear():
            # Проверяем заполненность полей перед обработкой
            if not self.reg_username.text() or not self.reg_password.text():
                QMessageBox.warning(page, "Ошибка", "Заполните все поля")
                return

            # Если поля заполнены, пробуем зарегистрировать
            try:
                if self.handle_register():  # Предполагаем, что возвращает True при успехе
                    clear_fields()  # Очищаем только после успешной регистрации
            except Exception as e:
                QMessageBox.critical(page, "Ошибка", f"Ошибка регистрации: {str(e)}")

        # Очистка только при нажатии Отмена
        btn_box.rejected.connect(clear_fields)
        btn_box.rejected.connect(self.show_main_page)

        # Новая логика для кнопки регистрации
        btn_box.accepted.connect(handle_register_and_clear)

        left_layout.addWidget(btn_box, alignment=QtCore.Qt.AlignCenter)

        # Правая часть (1/4) - изображение
        right_widget = QtWidgets.QLabel()
        right_widget.setPixmap(QtGui.QPixmap("C://Users//Artem//Downloads//shap.jpg"))
        right_widget.setScaledContents(True)

        # Распределяем пространство (3:1 соотношение)
        main_layout.addWidget(left_widget, 3)  # 3/4 ширины
        main_layout.addWidget(right_widget, 1)  # 1/4 ширины

        # Сохраняем ссылку на страницу
        self.register_page = page
        self.stacked_widget.addWidget(page)

        # Перехватываем переход на главную страницу для очистки
        original_show_main_page = self.show_main_page

        def show_main_page_with_clear():
            clear_fields()
            original_show_main_page()

        self.show_main_page = show_main_page_with_clear

    def create_profile_page(self):
        page = QtWidgets.QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(100, 50, 100, 50)

        # Приветствие
        self.welcome_label = QLabel()
        self.welcome_label.setStyleSheet("""
            color: orange;
            font-size: 36px;
            font-weight: bold;
        """)
        layout.addWidget(self.welcome_label, alignment=QtCore.Qt.AlignCenter)

        # Баланс
        balance_layout = QHBoxLayout()
        balance_layout.setSpacing(20)

        self.balance_label = QLabel()
        self.balance_label.setStyleSheet("""
            color: #4CAF50;
            font-size: 34px;
        """)
        balance_layout.addWidget(self.balance_label)

        self.add_balance_btn = QPushButton("+100$")
        self.add_balance_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 26px;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.add_balance_btn.clicked.connect(self.add_balance)
        balance_layout.addWidget(self.add_balance_btn)

        # Кнопка перевода
        self.transfer_btn = QPushButton("Перевести")
        self.transfer_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-size: 26px;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        self.transfer_btn.clicked.connect(self.show_transfer_dialog)
        balance_layout.addWidget(self.transfer_btn)

        layout.addLayout(balance_layout)

        # Таблица активов
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(3)
        self.assets_table.setHorizontalHeaderLabels(["Монета", "Количество", "Действия"])
        self.assets_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                font-size: 50px;
                padding: 10px;
                background-color: #444;
            }
        """)
        self.assets_table.verticalHeader().setVisible(False)
        self.assets_table.setStyleSheet("""
            QTableWidget {
                background-color: #333;
                color: white;
                font-size: 50px;
                border: 1px solid #444;
                gridline-color: #444;
                margin: 50px;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)

        layout.addWidget(self.assets_table)

        # Кнопки действий
        action_layout = QHBoxLayout()
        action_layout.setSpacing(20)

        self.buy_btn = QPushButton("Купить")
        self.buy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 26px;
                padding: 15px;
                min-width: 150px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.buy_btn.clicked.connect(self.show_buy_dialog)
        action_layout.addWidget(self.buy_btn)

        self.sell_btn = QPushButton("Продать")
        self.sell_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 26px;
                padding: 15px;
                min-width: 150px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.sell_btn.clicked.connect(self.show_sell_dialog)
        action_layout.addWidget(self.sell_btn)

        self.logout_btn = QPushButton("Выйти")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: black;
                font-size: 26px;
                padding: 15px;
                min-width: 150px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e68a00;
            }
        """)
        self.logout_btn.clicked.connect(self.show_main_page)
        action_layout.addWidget(self.logout_btn)

        # Установка размеров столбцов
        self.assets_table.setColumnWidth(0, 500)
        self.assets_table.setColumnWidth(1, 600)
        self.assets_table.setColumnWidth(2, 350)

        layout.addLayout(action_layout)

        self.stacked_widget.addWidget(page)

        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.main_splitter.addWidget(self.assets_table)

        # Создаем панель с информацией о монете
        self.coin_info_panel = QtWidgets.QWidget()
        self.coin_info_layout = QVBoxLayout(self.coin_info_panel)

        # Заголовок панели
        self.coin_info_label = QLabel("Информация о монете")
        self.coin_info_label.setStyleSheet("""
                font-size: 36px;
                font-weight: bold;
                color: orange;
                margin-bottom: 20px;
            """)
        self.coin_info_layout.addWidget(self.coin_info_label)

        self.chart_view = QChartView()
        self.chart_view.setMinimumHeight(500)
        self.chart_view.setStyleSheet("background-color: #333;")
        self.coin_info_layout.addWidget(self.chart_view)

        # Поле для отображения информации
        self.coin_info_text = QtWidgets.QTextBrowser()
        self.coin_info_text.setStyleSheet("""
                font-size: 36px;
                background-color: #333;
                padding: 15px;
                border: 1px solid #444;
            """)
        self.coin_info_text.setMinimumHeight(700)
        self.coin_info_layout.addWidget(self.coin_info_text)

        # Добавляем панель в сплиттер
        self.main_splitter.addWidget(self.coin_info_panel)
        layout.addWidget(self.main_splitter)

        # Подключаем обработчик клика по названию монеты
        self.assets_table.cellClicked.connect(self.show_coin_info)

    def show_transfer_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Перевод монет")
        dialog.setFixedSize(600, 400)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)

        # Поля формы
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Выбор монеты для перевода
        self.transfer_coin_combo = QtWidgets.QComboBox()
        self.transfer_coin_combo.setStyleSheet("font-size: 24px; padding: 10px;")

        # Заполняем комбобокс доступными монетами пользователя
        for coin in ['BTC', 'ETH', 'OBT', 'PLUME', 'OM', 'LINK', 'DAI', 'UNI',
                     'PEPE', 'NEAR', 'ONDO', 'MNT', 'TRUMP', 'AMI', "SUI", "APEX", "S", "GRASS", "WLD", "ARB", "WAL",  "CAKE",  "AI16Z",
           "W", "CMETH", "POPCAT", "RENDER", 'TIA', 'WIF', "VIRTUAL", "JASMY", "GALA", "XTER", "DYDX",  "ZRO",  "SONIC",
           "INJ", "PENDLE", "LDO", "PARTI", "C98", "JUP", "ORDI"]:
            if self.current_user['coins'][coin] > 0:
                self.transfer_coin_combo.addItem(coin, coin)

        if self.transfer_coin_combo.count() == 0:
            ErrorDialog(self, "У вас нет монет для перевода!").exec_()
            return

        form_layout.addRow("Монета:", self.transfer_coin_combo)

        # Получатель
        self.transfer_recipient = QLineEdit()
        self.transfer_recipient.setStyleSheet("font-size: 24px; padding: 10px;")
        self.transfer_recipient.setPlaceholderText("Имя пользователя")
        form_layout.addRow("Получатель:", self.transfer_recipient)

        # Количество
        self.transfer_amount = QLineEdit()
        self.transfer_amount.setStyleSheet("font-size: 24px; padding: 10px;")
        self.transfer_amount.setPlaceholderText("Количество")
        self.transfer_amount.setValidator(QtGui.QDoubleValidator(0.01, 1000000, 2))
        form_layout.addRow("Количество:", self.transfer_amount)

        # Примечание
        self.transfer_note = QLineEdit()
        self.transfer_note.setStyleSheet("font-size: 24px; padding: 10px;")
        self.transfer_note.setPlaceholderText("Примечание (необязательно)")
        form_layout.addRow("Примечание:", self.transfer_note)

        layout.addLayout(form_layout)

        # Кнопки
        btn_box = QDialogButtonBox()
        transfer_btn = btn_box.addButton("Перевести", QDialogButtonBox.AcceptRole)
        cancel_btn = btn_box.addButton("Отмена", QDialogButtonBox.RejectRole)

        transfer_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 24;
                padding: 10px;
                min-width: 150px;
            }
        """)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 24px;
                padding: 10px;
                min-width: 150px;
            }
        """)

        btn_box.accepted.connect(lambda: self.handle_transfer(dialog))
        btn_box.rejected.connect(dialog.reject)

        layout.addWidget(btn_box)

        dialog.exec_()

    def handle_transfer(self, dialog):
        coin = self.transfer_coin_combo.currentData()
        coin_name = self.transfer_coin_combo.currentText()
        recipient = self.transfer_recipient.text().strip()
        amount = self.transfer_amount.text().strip()
        note = self.transfer_note.text().strip()

        if not recipient or not amount:
            ErrorDialog(self, "Укажите получателя и сумму").exec_()
            return

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")

            # Проверяем существование получателя
            self.cursor.execute("SELECT id_users FROM users WHERE username = %s", (recipient,))
            recipient_id = self.cursor.fetchone()

            if not recipient_id:
                ErrorDialog(self, "Пользователь не найден").exec_()
                return

            if recipient == self.current_user['username']:
                ErrorDialog(self, "Нельзя переводить самому себе").exec_()
                return

            # Проверяем достаточность средств
            if amount > self.current_user['coins'][coin]:
                ErrorDialog(self, "Недостаточно средств").exec_()
                return

            # Выполняем перевод
            coin_column = f"{coin.lower()}_usdt"

            # Уменьшаем баланс отправителя
            self.cursor.execute(f"""
                UPDATE users 
                SET {coin_column} = {coin_column} - %s 
                WHERE id_users = %s
            """, (amount, self.current_user['id']))

            # Увеличиваем баланс получателя
            self.cursor.execute(f"""
                UPDATE users 
                SET {coin_column} = {coin_column} + %s 
                WHERE id_users = %s
            """, (amount, recipient_id[0]))

            # Записываем транзакцию в историю (если есть соответствующая таблица)
            try:
                self.cursor.execute("""
                    INSERT INTO transactions 
                    (sender_id, receiver_id, coin, amount, note, timestamp) 
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """, (self.current_user['id'], recipient_id[0], coin, amount, note))
            except Exception as e:
                print(f"Не удалось записать транзакцию: {e}")

            self.conn.commit()

            # Обновляем данные текущего пользователя
            self.current_user['coins'][coin] -= amount

            self.update_profile()
            dialog.close()

            SuccessDialog(self, f"Вы перевели {amount} {coin_name} пользователю {recipient}").exec_()

        except ValueError as e:
            ErrorDialog(self, str(e)).exec_()
        except Exception as e:
            ErrorDialog(self, f"Ошибка перевода: {str(e)}").exec_()
            self.conn.rollback()



    def show_coin_info(self, row, column):
        if column != 0:  # Только при клике на первый столбец (название монеты)
            return

        # Получаем символ монеты
        coin_symbol = self.assets_table.item(row, 0).text()

        try:

            self.cursor.execute("""
                    SELECT hp.timestamp, hp.close
                    FROM historical_prices hp
                    JOIN all_token at ON hp.token_id = at.id
                    WHERE at.symbol = %s
                    ORDER BY hp.timestamp
                    LIMIT 1000
                """, (coin_symbol,))
            price_data = self.cursor.fetchall()

            # Создаем график
            chart = QChart()
            chart.setTitle(f"История цен {coin_symbol}")
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.legend().hide()

            # Создаем серию данных
            series = QLineSeries()

            for timestamp, price in price_data:
                #  timestamp в миллисекунды
                msecs = timestamp.timestamp() * 1000
                series.append(msecs, price)

            chart.addSeries(series)

            #  оси
            axisX = QDateTimeAxis()
            axisX.setFormat("dd.MM hh:mm")
            axisX.setTitleText("Дата")
            chart.addAxis(axisX, QtCore.Qt.AlignBottom)
            series.attachAxis(axisX)

            axisY = QValueAxis()
            axisY.setTitleText("Цена (USD)")
            chart.addAxis(axisY, QtCore.Qt.AlignLeft)
            series.attachAxis(axisY)

            # стили
            chart.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("#333")))
            chart.setTitleBrush(QtGui.QBrush(QtGui.QColor("orange")))

            # график в chart_view
            self.chart_view.setChart(chart)







            #  информацию о монете из all_token
            self.cursor.execute("""
                    SELECT name, date_launched, platform, website, description 
                    FROM all_token 
                    WHERE symbol = %s
                """, (coin_symbol,))
            coin_info = self.cursor.fetchone()

            if not coin_info:
                self.coin_info_text.setPlainText(f"Информация о {coin_symbol} не найдена")
                return

            name, date_launched, platform, website, description = coin_info

            #  данные о ценах и объемах за последние 10 часов
            self.cursor.execute("""
                    SELECT hp.timestamp, hp.close, hp.volume
                    FROM historical_prices hp
                    JOIN all_token at ON hp.token_id = at.id
                    WHERE at.symbol = %s
                    ORDER BY hp.timestamp DESC
                    LIMIT 10
                """, (coin_symbol,))
            price_data = self.cursor.fetchall()

            # Формируем текст с информацией
            info_text = f"""
                <h2>{name} ({coin_symbol})</h2>
                <p><b>Дата запуска:</b> {date_launched.strftime('%Y-%m-%d') if date_launched else 'Неизвестно'}</p>
                <p><b>Платформа:</b> {platform or 'Неизвестно'}</p>
                <p><b>Вебсайт:</b> <a href="{website or '#'}">{website or 'Недоступен'}</a></p>
                <p><b>Описание:</b> {description or 'Нет описания'}</p>
                """

            # Добавляем информацию о ценах и объемах
            if len(price_data) >= 2:
                current = price_data[0]
                previous = price_data[1]

                price_change = current[1] - previous[1]
                price_pct = (price_change / previous[1]) * 100 if previous[1] != 0 else 0
                price_direction = "↑" if price_change >= 0 else "↓"
                price_color = "green" if price_change >= 0 else "red"

                volume_change = current[2] - previous[2]
                volume_pct = (volume_change / previous[2]) * 100 if previous[2] != 0 else 0
                volume_direction = "↑" if volume_change >= 0 else "↓"
                volume_color = "green" if volume_change >= 0 else "red"

                info_text += f"""
                    <h3>Изменения за последние 10 часов:</h3>
                    <p><b>Текущая цена:</b> ${current[1]:.4f} 
                    <span style="color:{price_color}">
                        ({price_direction}${abs(price_change):.4f}, {abs(price_pct):.2f}%)
                    </span></p>
                    <p><b>Объем торгов:</b> {current[2]:.2f} 
                    <span style="color:{volume_color}">
                        ({volume_direction}{abs(volume_change):.2f}, {abs(volume_pct):.2f}%)
                    </span></p>
                    """
            elif price_data:
                info_text += f"""
                    <h3>Текущие данные:</h3>
                    <p><b>Цена:</b> ${price_data[0][1]:.4f}</p>
                    <p><b>Объем:</b> {price_data[0][2]:.2f}</p>
                    """
            else:
                info_text += "<p>Нет данных о ценах</p>"

            self.coin_info_text.setHtml(info_text)

        except Exception as e:
            self.coin_info_text.setPlainText(f"Ошибка при получении информации: {str(e)}")
            self.coin_info_text.setPlainText(f"Ошибка при построении графика: {str(e)}")



    # Навигация
    def show_main_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_login_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_register_page(self):
        self.stacked_widget.setCurrentIndex(2)

    def show_profile_page(self):
        self.update_profile()
        self.stacked_widget.setCurrentIndex(3)

    def show_info(self):
        info = QMessageBox(self)
        info.setWindowTitle("О бирже")
        info.setText("""
            Виртуальная биржа TriGaDa Balance

            Авторы:
            - Арсёнов Данил
            - Кучеровский Артём
            - Галкин Никита
        """)
        info.setStyleSheet("""
            QMessageBox {
                background-color: #222;
                color: white;
                font-size: 18px;
            }
            QLabel {
                color: white;
                font-size: 18px;
            }
        """)
        info.exec_()


    def handle_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()

        if not username or not password:
            ErrorDialog(self, "Заполните все поля!").exec_()
            return

        try:
            self.cursor.execute("""
                SELECT id_users, username, balance, 
                btc_usdt, eth_usdt, obt_usdt, plume_usdt, om_usdt, 
                link_usdt, dai_usdt, uni_usdt, pepe_usdt,
                near_usdt, ondo_usdt, mnt_usdt, trump_usdt, ami_usdt, sui_usdt, apex_usdt, s_usdt, grass_usdt, wld_usdt, arb_usdt,
                wal_usdt, cake_usdt, ai16z_usdt, w_usdt, cmeth_usdt, popcat_usdt, render_usdt, tia_usdt, wif_usdt, virtual_usdt, jasmy_usdt,
                gala_usdt, xter_usdt, dydx_usdt, zro_usdt, sonic_usdt, inj_usdt, pendle_usdt, ldo_usdt, parti_usdt, c98_usdt, jup_usdt, ordi_usdt
                FROM users 
                WHERE username = %s AND password = %s
            """, (username, password))
            user = self.cursor.fetchone()

            if not user:
                ErrorDialog(self, "Неверное имя пользователя или пароль!").exec_()
                return



            self.current_user = {
                'id': user[0],
                'username': user[1],
                'balance': float(user[2]),
                'coins': {
                    'BTC': float(user[3]),
                    'OBT': float(user[4]),
                    'PLUME': float(user[5]),
                    'OM': float(user[6]),
                    'LINK': float(user[7]),
                    'DAI': float(user[8]),
                    'UNI': float(user[9]),
                    'PEPE': float(user[10]),
                    'NEAR': float(user[11]),
                    'ONDO': float(user[12]),
                    'MNT': float(user[13]),
                    'TRUMP': float(user[14]),
                    'AMI': float(user[15]),
                    'SUI': float(user[16]),
                    'APEX': float(user[17]),
                    'S': float(user[18]),
                    'GRASS': float(user[19]),
                    'WLD': float(user[20]),
                    'ARB': float(user[21]),
                    'WAL': float(user[22]),
                    'CAKE': float(user[23]),
                    'AI16Z': float(user[24]),
                    'W': float(user[25]),
                    'CMETH': float(user[26]),
                    'POPCAT': float(user[27]),
                    'RENDER': float(user[28]),
                    'TIA': float(user[29]),
                    'WIF': float(user[30]),
                    'VIRTUAL': float(user[31]),
                    'JASMY': float(user[32]),
                    'GALA': float(user[33]),
                    'XTER': float(user[34]),
                    'DYDX': float(user[35]),
                    'ZRO': float(user[36]),
                    'SONIC': float(user[37]),
                    'INJ': float(user[38]),
                    'PENDLE': float(user[39]),
                    'LDO': float(user[40]),
                    'PARTI': float(user[41]),
                    'C98': float(user[42]),
                    'JUP': float(user[43]),
                    'ORDI': float(user[44]),
                    'ETH': float(user[45])
                }
            }





            self.show_profile_page()
            SuccessDialog(self, "Вход выполнен успешно!").exec_()

        except Exception as e:
            ErrorDialog(self, f"Ошибка при входе: {str(e)}").exec_()

    def handle_register(self):
        username = self.reg_username.text().strip()
        password = self.reg_password.text().strip()

        if not username or not password:
            ErrorDialog(self, "Заполните все поля!").exec_()
            return

        try:
            #  существует ли пользователь
            self.cursor.execute("SELECT id_users FROM users WHERE username = %s", (username,))
            if self.cursor.fetchone():
                ErrorDialog(self, "Пользователь с таким именем уже существует!").exec_()
                return

            # Создаем нового пользователя
            self.cursor.execute("""
                INSERT INTO users (username, password, balance, btc_usdt, eth_usdt,
                 obt_usdt, plume_usdt, om_usdt, link_usdt, dai_usdt,
                  uni_usdt, pepe_usdt, near_usdt, ondo_usdt,
                   mnt_usdt, trump_usdt, ami_usdt, sui_usdt, apex_usdt, s_usdt, 
                   grass_usdt, wld_usdt, arb_usdt, wal_usdt, cake_usdt, ai16z_usdt,
                    w_usdt, cmeth_usdt, popcat_usdt, render_usdt, tia_usdt, wif_usdt,
                     virtual_usdt, jasmy_usdt, gala_usdt, xter_usdt, dydx_usdt, zro_usdt,
                      sonic_usdt, inj_usdt, pendle_usdt, ldo_usdt, parti_usdt, c98_usdt, jup_usdt, ordi_usdt)
                VALUES (%s, %s, 1000, 0, 0, 0)
                RETURNING id_users
            """, (username, password))
            self.conn.commit()

            SuccessDialog(self, "Регистрация прошла успешно! Начальный баланс: $1000").exec_()
            self.show_main_page()

        except Exception as e:
            ErrorDialog(self, f"Ошибка при регистрации: {str(e)}").exec_()

    def update_profile(self):
        if not self.current_user:
            return

        self.assets_table.cellClicked.disconnect()  # Отключаем старые соединения
        self.assets_table.cellClicked.connect(self.show_coin_info)

        self.welcome_label.setText(f"Добро пожаловать, {self.current_user['username']}!")
        self.balance_label.setText(f"Баланс: ${self.current_user['balance']:.2f}")

        # Получаем текущие цены
        prices = self.get_current_prices()

        # Обновляем таблицу активов
        self.assets_table.setRowCount(43)

        coins = [
            ('BTC', self.current_user['coins']['BTC']),
            ('ETH', self.current_user['coins']['ETH']),
            ('OBT', self.current_user['coins']['OBT']),
            ('PLUME', self.current_user['coins']['PLUME']),
            ('OM', self.current_user['coins']['OM']),
            ('LINK', self.current_user['coins']['LINK']),
            ('DAI', self.current_user['coins']['DAI']),
            ('UNI', self.current_user['coins']['UNI']),
            ('PEPE', self.current_user['coins']['PEPE']),
            ('NEAR', self.current_user['coins']['NEAR']),
            ('ONDO', self.current_user['coins']['ONDO']),
            ('MNT', self.current_user['coins']['MNT']),
            ('TRUMP', self.current_user['coins']['TRUMP']),
            ('AMI', self.current_user['coins']['AMI']),
            ('SUI', self.current_user['coins']['SUI']),
            ('APEX', self.current_user['coins']['APEX']),
            ('S', self.current_user['coins']['S']),
            ('GRASS', self.current_user['coins']['GRASS']),
            ('WLD', self.current_user['coins']['WLD']),
            ('ARB', self.current_user['coins']['ARB']),
            ('WAL', self.current_user['coins']['WAL']),
            ('CAKE', self.current_user['coins']['CAKE']),
            ('AI16Z', self.current_user['coins']['AI16Z']),
            ('W', self.current_user['coins']['W']),
            ('CMETH', self.current_user['coins']['CMETH']),
            ('POPCAT', self.current_user['coins']['POPCAT']),
            ('RENDER', self.current_user['coins']['RENDER']),
            ('TIA', self.current_user['coins']['TIA']),
            ('WIF', self.current_user['coins']['WIF']),
            ('VIRTUAL', self.current_user['coins']['VIRTUAL']),
            ('JASMY', self.current_user['coins']['JASMY']),
            ('GALA', self.current_user['coins']['GALA']),
            ('XTER', self.current_user['coins']['XTER']),
            ('DYDX', self.current_user['coins']['DYDX']),
            ('ZRO', self.current_user['coins']['ZRO']),
            ('SONIC', self.current_user['coins']['SONIC']),
            ('INJ', self.current_user['coins']['INJ']),
            ('PENDLE', self.current_user['coins']['PENDLE']),
            ('LDO', self.current_user['coins']['LDO']),
            ('PARTI', self.current_user['coins']['PARTI']),
            ('C98', self.current_user['coins']['C98']),
            ('JUP', self.current_user['coins']['JUP']),
            ('ORDI', self.current_user['coins']['ORDI'])
        ]




        for row, (coin, amount) in enumerate(coins):
            price = prices.get(coin, 0)
            total = price * amount

            self.assets_table.setItem(row, 0, QTableWidgetItem(coin))
            self.assets_table.setItem(row, 1, QTableWidgetItem(
                f"{amount:.4f} (${total:.2f})" if amount > 0 else "0"
            ))

            # Кнопка продажи
            if amount > 0:
                btn = QPushButton("Продать")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f44336;
                        color: white;
                        font-size: 34px;
                        padding: 1px;
                        min-width: 90px;
                    }
                """)
                btn.clicked.connect(lambda _, c=coin: self.sell_coin(c))
                self.assets_table.setCellWidget(row, 2, btn)
            else:
                self.assets_table.setItem(row, 2, QTableWidgetItem(""))

        self.assets_table.resizeColumnsToContents()

    def get_current_prices(self):
        prices = {}
        try:
            for coin in ['BTC', 'ETH', 'OBT', 'PLUME', 'OM', 'LINK', 'DAI', 'UNI',
                     'PEPE', 'NEAR', 'ONDO', 'MNT', 'TRUMP', 'AMI', "SUI", "APEX", "S", "GRASS", "WLD", "ARB", "WAL",  "CAKE",  "AI16Z",
                        "W", "CMETH", "POPCAT", "RENDER", 'TIA', 'WIF', "VIRTUAL", "JASMY", "GALA", "XTER", "DYDX",  "ZRO",  "SONIC",
                            "INJ", "PENDLE", "LDO", "PARTI", "C98", "JUP", "ORDI"]:
                # Получаем ID токена
                self.cursor.execute("SELECT id FROM all_token WHERE symbol = %s", (coin,))
                token_id = self.cursor.fetchone()

                if token_id:
                    # Получаем последнюю цену
                    self.cursor.execute("""
                        SELECT close FROM historical_prices 
                        WHERE token_id = %s 
                        ORDER BY timestamp DESC 
                        LIMIT 1
                    """, (token_id[0],))
                    price = self.cursor.fetchone()
                    prices[coin] = float(price[0]) if price else 0.0
                else:
                    prices[coin] = 0.0
        except Exception as e:
            print(f"Ошибка при получении цен: {e}")

        return prices

    def show_buy_dialog(self):
        if not self.current_user:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Купить монету")
        dialog.resize(500, 300)

        layout = QVBoxLayout(dialog)

        # Выбор монеты
        coin_label = QLabel("Выберите монету:")
        coin_label.setStyleSheet("font-size: 38px;")
        layout.addWidget(coin_label)

        self.buy_coin_combo = QtWidgets.QComboBox()
        prices = self.get_current_prices()

        for coin in ['BTC', 'ETH', 'OBT', 'PLUME', 'OM', 'LINK', 'DAI', 'UNI',
                     'PEPE', 'NEAR', 'ONDO', 'MNT', 'TRUMP', 'AMI', "SUI", "APEX", "S", "GRASS", "WLD", "ARB", "WAL",  "CAKE",  "AI16Z",
           "W", "CMETH", "POPCAT", "RENDER", 'TIA', 'WIF', "VIRTUAL", "JASMY", "GALA", "XTER", "DYDX",  "ZRO",  "SONIC",
           "INJ", "PENDLE", "LDO", "PARTI", "C98", "JUP", "ORDI"]:
            price = prices.get(coin, 0)
            self.buy_coin_combo.addItem(f"{coin} - ${price:.4f}", coin)

        layout.addWidget(self.buy_coin_combo)

        # Количество
        amount_label = QLabel("Количество:")
        amount_label.setStyleSheet("font-size: 38px;")
        layout.addWidget(amount_label)

        self.buy_amount = QSpinBox()
        self.buy_amount.setMinimum(1)
        self.buy_amount.setMaximum(10000)
        self.buy_amount.setStyleSheet("font-size: 38px;")
        layout.addWidget(self.buy_amount)

        # Кнопки
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(lambda: self.buy_coin(dialog))
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)

        dialog.exec_()

    def buy_coin(self, dialog):
        coin = self.buy_coin_combo.currentData()
        amount = self.buy_amount.value()
        prices = self.get_current_prices()
        price = prices.get(coin, 0)
        total = price * amount

        if total > self.current_user['balance']:
            ErrorDialog(self, "Недостаточно средств!").exec_()
            return

        try:
            # Обновляем баланс и количество монет
            new_balance = self.current_user['balance'] - total
            coin_column = f"{coin.lower()}_usdt"

            self.cursor.execute(f"""
                UPDATE users 
                SET balance = %s, {coin_column} = {coin_column} + %s 
                WHERE id_users = %s
            """, (new_balance, amount, self.current_user['id']))
            self.conn.commit()

            # Обновляем данные пользователя
            self.current_user['balance'] = new_balance
            self.current_user['coins'][coin] += amount

            self.update_profile()
            dialog.close()

            SuccessDialog(self, f"Вы купили {amount} {coin} за ${total:.2f}").exec_()

        except Exception as e:
            ErrorDialog(self, f"Ошибка при покупке: {str(e)}").exec_()

    def show_sell_dialog(self):
        if not self.current_user:
            return

        # Проверяем, есть ли монеты для продажи
        if not any(amount > 0 for amount in self.current_user['coins'].values()):
            ErrorDialog(self, "У вас нет монет для продажи!").exec_()
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Продать монету")
        dialog.resize(500, 300)

        layout = QVBoxLayout(dialog)

        # Выбор монеты
        coin_label = QLabel("Выберите монету:")
        coin_label.setStyleSheet("font-size: 38px;")
        layout.addWidget(coin_label)

        self.sell_coin_combo = QtWidgets.QComboBox()

        for coin, amount in self.current_user['coins'].items():
            if amount > 0:
                self.sell_coin_combo.addItem(coin, coin)

        layout.addWidget(self.sell_coin_combo)

        # Количество
        amount_label = QLabel("Количество:")
        amount_label.setStyleSheet("font-size: 38px;")
        layout.addWidget(amount_label)

        self.sell_amount = QSpinBox()
        self.sell_amount.setMinimum(1)
        self.sell_amount.setMaximum(int(self.current_user['coins'][self.sell_coin_combo.currentData()]))
        self.sell_amount.setStyleSheet("font-size: 38px;")
        layout.addWidget(self.sell_amount)

        # Обновляем максимум при изменении выбранной монеты
        def update_max():
            coin = self.sell_coin_combo.currentData()
            self.sell_amount.setMaximum(int(self.current_user['coins'][coin]))

        self.sell_coin_combo.currentIndexChanged.connect(update_max)

        # Кнопки
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(lambda: self.sell_selected_coin(dialog))
        btn_box.rejected.connect(dialog.reject)
        layout.addWidget(btn_box)

        dialog.exec_()

    def sell_selected_coin(self, dialog):
        coin = self.sell_coin_combo.currentData()
        amount = self.sell_amount.value()
        self.sell_coin(coin, amount)
        dialog.close()

    def sell_coin(self, coin, amount=None):
        if not amount:
            max_amount = int(self.current_user['coins'][coin])
            amount, ok = QtWidgets.QInputDialog.getInt(
                self, "Продажа", f"Сколько {coin} продать? (макс: {max_amount})",
                min=1, max=max_amount
            )
            if not ok:
                return

        prices = self.get_current_prices()
        price = prices.get(coin, 0)
        total = price * amount

        try:
            # Обновляем баланс и количество монет
            new_balance = self.current_user['balance'] + total
            coin_column = f"{coin.lower()}_usdt"

            self.cursor.execute(f"""
                UPDATE users 
                SET balance = %s, {coin_column} = {coin_column} - %s 
                WHERE id_users = %s
            """, (new_balance, amount, self.current_user['id']))
            self.conn.commit()

            # Обновляем данные пользователя
            self.current_user['balance'] = new_balance
            self.current_user['coins'][coin] -= amount

            self.update_profile()

            SuccessDialog(self, f"Вы продали {amount} {coin} за ${total:.2f}").exec_()

        except Exception as e:
            ErrorDialog(self, f"Ошибка при продаже: {str(e)}").exec_()

    def add_balance(self):
        if not self.current_user:
            return

        try:
            new_balance = self.current_user['balance'] + 100

            self.cursor.execute("""
                UPDATE users SET balance = %s WHERE id_users = %s
            """, (new_balance, self.current_user['id']))
            self.conn.commit()

            self.current_user['balance'] = new_balance
            self.balance_label.setText(f"Баланс: ${new_balance:.2f}")

            SuccessDialog(self, "Баланс пополнен на $100!").exec_()

        except Exception as e:
            ErrorDialog(self, f"Ошибка при пополнении баланса: {str(e)}").exec_()

    def closeEvent(self, event):
        if hasattr(self, 'conn'):
            self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Глобальные стили
    app.setStyleSheet("""
        QWidget {
            background-color: #111;
            color: white;
            font-size: 26px;
        }
        QLineEdit {
            background-color: #333;
            color: white;
            border: 1px solid #444;
            padding: 8px;
            font-size: 16px;
        }
        QComboBox {
            background-color: #333;
            color: white;
            border: 1px solid #444;
            padding: 8px;
            font-size: 26px;
        }
        QSpinBox {
            background-color: #333;
            color: white;
            border: 1px solid #444;
            padding: 8px;
            font-size: 26px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
