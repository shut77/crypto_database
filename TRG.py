import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QDialog,
                             QVBoxLayout, QLabel, QPushButton, QLineEdit,
                             QFormLayout, QDialogButtonBox, QTableWidget,
                             QTableWidgetItem, QSpinBox, QHBoxLayout)
import psycopg2
from config import host, user, password, db_name


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

        # Создаем stacked widget для страниц
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Создаем страницы
        self.create_main_page()
        self.create_login_page()
        self.create_register_page()
        self.create_profile_page()

        # Показываем главную страницу
        self.stacked_widget.setCurrentIndex(0)

    def create_main_page(self):
        page = QtWidgets.QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(30)

        # Заголовок
        title = QLabel("TriGaDa Balance")
        title.setStyleSheet("""
            color: orange;
            font-size: 72px;
            font-weight: bold;
            margin-bottom: 50px;
        """)
        layout.addWidget(title, alignment=QtCore.Qt.AlignCenter)

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
            layout.addWidget(btn)

        self.stacked_widget.addWidget(page)

    def create_login_page(self):
        page = QtWidgets.QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(30)

        # Форма
        form = QFormLayout()
        form.setSpacing(20)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Имя пользователя")
        self.login_username.setStyleSheet("font-size: 24px; padding: 15px;")
        form.addRow("Имя пользователя:", self.login_username)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setStyleSheet("font-size: 24px; padding: 15px;")
        form.addRow("Пароль:", self.login_password)

        layout.addLayout(form)

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

        btn_box.accepted.connect(self.handle_login)
        btn_box.rejected.connect(self.show_main_page)
        layout.addWidget(btn_box, alignment=QtCore.Qt.AlignCenter)

        self.stacked_widget.addWidget(page)

    def create_register_page(self):
        page = QtWidgets.QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setSpacing(30)

        # Форма
        form = QFormLayout()
        form.setSpacing(20)

        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Имя пользователя")
        self.reg_username.setStyleSheet("font-size: 24px; padding: 15px;")
        form.addRow("Имя пользователя:", self.reg_username)

        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Пароль")
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setStyleSheet("font-size: 24px; padding: 15px;")
        form.addRow("Пароль:", self.reg_password)

        layout.addLayout(form)

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

        btn_box.accepted.connect(self.handle_register)
        btn_box.rejected.connect(self.show_main_page)
        layout.addWidget(btn_box, alignment=QtCore.Qt.AlignCenter)

        self.stacked_widget.addWidget(page)

    def create_profile_page(self):
        page = QtWidgets.QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)

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
            font-size: 24px;
        """)
        balance_layout.addWidget(self.balance_label)

        self.add_balance_btn = QPushButton("+100$")
        self.add_balance_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 18px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        self.add_balance_btn.clicked.connect(self.add_balance)
        balance_layout.addWidget(self.add_balance_btn)

        layout.addLayout(balance_layout)

        # Таблица активов
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(3)
        self.assets_table.setHorizontalHeaderLabels(["Монета", "Количество", "Действия"])
        self.assets_table.horizontalHeader().setStyleSheet("font-size: 18px;")
        self.assets_table.verticalHeader().setVisible(False)
        self.assets_table.setStyleSheet("""
            QTableWidget {
                background-color: #333;
                color: white;
                font-size: 16px;
                border: 1px solid #444;
                gridline-color: #444;
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
                font-size: 18px;
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
                font-size: 18px;
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
                font-size: 18px;
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

        layout.addLayout(action_layout)

        self.stacked_widget.addWidget(page)

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

    # Обработчики
    def handle_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()

        if not username or not password:
            ErrorDialog(self, "Заполните все поля!").exec_()
            return

        try:
            self.cursor.execute("""
                SELECT id_users, username, balance, ton_usdt, obt_usdt, plume_usdt 
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
                    'TON': float(user[3]),
                    'OBT': float(user[4]),
                    'PLUME': float(user[5])
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
            # Проверяем, существует ли пользователь
            self.cursor.execute("SELECT id_users FROM users WHERE username = %s", (username,))
            if self.cursor.fetchone():
                ErrorDialog(self, "Пользователь с таким именем уже существует!").exec_()
                return

            # Создаем нового пользователя
            self.cursor.execute("""
                INSERT INTO users (username, password, balance, ton_usdt, obt_usdt, plume_usdt)
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

        self.welcome_label.setText(f"Добро пожаловать, {self.current_user['username']}!")
        self.balance_label.setText(f"Баланс: ${self.current_user['balance']:.2f}")

        # Получаем текущие цены
        prices = self.get_current_prices()

        # Обновляем таблицу активов
        self.assets_table.setRowCount(3)

        coins = [
            ('TON', self.current_user['coins']['TON']),
            ('OBT', self.current_user['coins']['OBT']),
            ('PLUME', self.current_user['coins']['PLUME'])
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
                        font-size: 14px;
                        padding: 5px;
                        min-width: 80px;
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
            for coin in ['TON', 'OBT', 'PLUME']:
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
        coin_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(coin_label)

        self.buy_coin_combo = QtWidgets.QComboBox()
        prices = self.get_current_prices()

        for coin in ['TON', 'OBT', 'PLUME']:
            price = prices.get(coin, 0)
            self.buy_coin_combo.addItem(f"{coin} - ${price:.4f}", coin)

        layout.addWidget(self.buy_coin_combo)

        # Количество
        amount_label = QLabel("Количество:")
        amount_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(amount_label)

        self.buy_amount = QSpinBox()
        self.buy_amount.setMinimum(1)
        self.buy_amount.setMaximum(10000)
        self.buy_amount.setStyleSheet("font-size: 18px;")
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
        coin_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(coin_label)

        self.sell_coin_combo = QtWidgets.QComboBox()

        for coin, amount in self.current_user['coins'].items():
            if amount > 0:
                self.sell_coin_combo.addItem(coin, coin)

        layout.addWidget(self.sell_coin_combo)

        # Количество
        amount_label = QLabel("Количество:")
        amount_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(amount_label)

        self.sell_amount = QSpinBox()
        self.sell_amount.setMinimum(1)
        self.sell_amount.setMaximum(int(self.current_user['coins'][self.sell_coin_combo.currentData()]))
        self.sell_amount.setStyleSheet("font-size: 18px;")
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
            font-size: 16px;
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
            font-size: 16px;
        }
        QSpinBox {
            background-color: #333;
            color: white;
            border: 1px solid #444;
            padding: 8px;
            font-size: 16px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())