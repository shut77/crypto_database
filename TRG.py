import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
#import sqlite3
import psycopg2
from config import host, user, password, db_name


# Класс для диалогового окна успеха
class SuccessDialog(QtWidgets.QMessageBox):
    def __init__(self, parent=None, flag=0):
        super(SuccessDialog, self).__init__(parent)
        if flag==1:
            self.setWindowTitle("Информационное окно")
            self.setText("Виртуальная биржа TriGaDa balance создана в рамках итоговой работы по БД и СМРП\n\nАвторы:\nАрсёнов Данил\nКучеровский Артём\nГалкин Никита\n")


            # Добавление иконки и галочки
            self.setIconPixmap(QtGui.QPixmap("checkmark.png").scaled(120, 120))
            self.setStyleSheet("""
                        QMessageBox {
                            background-color: black;
                            color: white;
                        }
                        QLabel {
                            color: orange;
                            font-size: 34px;
                        }
                        QPushButton {
                            background-color: green;
                            color: white;
                            border: none;
                            padding: 16px 600px;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: darkgreen;
                        }
                    """)
        return
        if flag==0:
            # Настройка содержимого сообщения
            self.setWindowTitle("Успех!")
            self.setText("Операция успешно завершена!")

            # Добавление иконки и галочки
            self.setIconPixmap(QtGui.QPixmap("checkmark.png").scaled(32, 32))

        # Настройка стиля для черного фона и других элементов
        self.setStyleSheet("""
            QMessageBox {
                background-color: black;
                color: white;
            }
            QLabel {
                color: green;
                font-size: 14px;
            }
            QPushButton {
                background-color: green;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: darkgreen;
            }
        """)

class ErrorDialog(QtWidgets.QMessageBox):
    def __init__(self, parent=None, flag=0):
        super(ErrorDialog, self).__init__(parent)

        # Настройка содержимого сообщения
        self.setWindowTitle("Ошибка!")
        if(flag==1):
            self.setText("Недостаточно средств!")
        if (flag == 2):
            self.setText("Заполните все поля!")

        # Добавление иконки и галочки
        self.setIconPixmap(QtGui.QPixmap("error.png").scaled(32, 32))

        # Настройка стиля для черного фона и других элементов
        self.setStyleSheet("""
            QMessageBox {
                background-color: black;
                color: white;
            }
            QLabel {
                color: red;
                font-size: 14px;
            }
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # Основные настройки окна
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1900, 1000)
        MainWindow.setWindowState(QtCore.Qt.WindowMaximized)  # Запуск в полноэкранном режиме
        MainWindow.setStyleSheet("background-color: rgb(0, 0, 0);")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Stacked Widget для переключения страниц
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, MainWindow.width(), MainWindow.height()))

        # Страница 1: Главная страница
        self.main_page = QtWidgets.QWidget()
        self.frame_main = QtWidgets.QFrame(self.main_page)
        self.frame_main.setGeometry(QtCore.QRect(0, 0, MainWindow.width(), MainWindow.height()))
        self.frame_main.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.frame_main.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_main.setFrameShadow(QtWidgets.QFrame.Raised)

        # Текстовое поле
        self.trgb = QtWidgets.QLabel(self.frame_main)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(56)
        font.setBold(True)
        font.setItalic(True)
        self.trgb.setFont(font)
        self.trgb.setAlignment(QtCore.Qt.AlignCenter)
        self.trgb.setText('<font color="orange">TriGaDa Balance</font>')
        self.trgb.setObjectName("trgb")
        self.trgb.setGeometry(QtCore.QRect(30, 100, int(MainWindow.width() * 0.4), 100))

        # Картинка
        self.pic1 = QtWidgets.QLabel(self.frame_main)
        self.pic1.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.8), 0, int(MainWindow.width() * 0.2), int(MainWindow.height())))
        self.pic1.setText("")
        self.pic1.setPixmap(QtGui.QPixmap("C://Users//Artem//Downloads//shap.jpg"))
        self.pic1.setScaledContents(True)
        self.pic1.setObjectName("pic1")

        # Кнопка "войти"
        self.pushButton = QtWidgets.QPushButton(self.frame_main)
        self.pushButton.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.3), int(MainWindow.height() * 0.7), int(MainWindow.width() * 0.4),
                         50))
        self.pushButton.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.pushButton.setText("войти")

        # Кнопка "зарегистрироваться" (переход на страницу регистрации)
        self.reg_button = QtWidgets.QPushButton(self.frame_main)
        self.reg_button.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.3), int(MainWindow.height() * 0.8), int(MainWindow.width() * 0.4),
                         50))
        self.reg_button.setStyleSheet("background-color: rgb(255, 170, 0);")
        self.reg_button.setText("зарегистрироваться")

        # Кнопка "информация о бирже"
        self.bir = QtWidgets.QPushButton(self.frame_main)
        self.bir.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.46), int(MainWindow.height() * 0.93),
                         int(MainWindow.width() * 0.08),
                         25))
        self.bir.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.bir.setText("информация о бирже")

        # Добавляем главную страницу в StackedWidget
        self.stackedWidget.addWidget(self.main_page)

        # Страница 2: Страница регистрации
        self.registration_page = QtWidgets.QWidget()
        self.frame_reg = QtWidgets.QFrame(self.registration_page)
        self.frame_reg.setGeometry(QtCore.QRect(0, 0, MainWindow.width(), MainWindow.height()))
        self.frame_reg.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.frame_reg.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_reg.setFrameShadow(QtWidgets.QFrame.Raised)

        # Картинка на странице регистрации
        self.pic1_reg = QtWidgets.QLabel(self.frame_reg)
        self.pic1_reg.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.8), 0, int(MainWindow.width() * 0.2), int(MainWindow.height())))
        self.pic1_reg.setText("")
        self.pic1_reg.setPixmap(QtGui.QPixmap("C://Users//Artem//Downloads//shap.jpg"))
        self.pic1_reg.setScaledContents(True)
        self.pic1_reg.setObjectName("pic1_reg")

        # Поле ввода имени
        self.username_input = QtWidgets.QLineEdit(self.frame_reg)
        self.username_input.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.3), int(MainWindow.height() * 0.4), int(MainWindow.width() * 0.2),
                         40))
        self.username_input.setStyleSheet("background-color: white;")
        self.username_input.setPlaceholderText("Введите имя пользователя")

        # Поле ввода пароля
        self.password_input = QtWidgets.QLineEdit(self.frame_reg)
        self.password_input.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.3), int(MainWindow.height() * 0.5), int(MainWindow.width() * 0.2),
                         40))
        self.password_input.setStyleSheet("background-color: white;")
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # Кнопка "Зарегистрироваться"
        self.register_button = QtWidgets.QPushButton(self.frame_reg)
        self.register_button.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.3), int(MainWindow.height() * 0.6), int(MainWindow.width() * 0.2),
                         50))
        self.register_button.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.register_button.setText("Зарегистрироваться")

        # Кнопка "Назад"
        self.back_button = QtWidgets.QPushButton(self.frame_reg)
        self.back_button.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.3), int(MainWindow.height() * 0.7), int(MainWindow.width() * 0.2),
                         50))
        self.back_button.setStyleSheet("background-color: rgb(255, 170, 0);")
        self.back_button.setText("Назад")

        # Добавляем страницу регистрации в StackedWidget
        self.stackedWidget.addWidget(self.registration_page)

        # Страница 3: Личный кабинет пользователя
        self.profile_page = QtWidgets.QWidget()
        self.frame_profile = QtWidgets.QFrame(self.profile_page)
        self.frame_profile.setGeometry(QtCore.QRect(0, 0, MainWindow.width(), MainWindow.height()))
        self.frame_profile.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.frame_profile.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_profile.setFrameShadow(QtWidgets.QFrame.Raised)

        # Картинка на странице профиля
        self.pic1_profile = QtWidgets.QLabel(self.frame_profile)
        self.pic1_profile.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.8), 0, int(MainWindow.width() * 0.2), int(MainWindow.height())))
        self.pic1_profile.setText("")
        self.pic1_profile.setPixmap(
            QtGui.QPixmap("C://Users//Artem//Downloads//shap.jpg"))
        self.pic1_profile.setScaledContents(True)
        self.pic1_profile.setObjectName("pic1_profile")

        # Приветственное сообщение
        self.welcome_message = QtWidgets.QLabel(self.frame_profile)
        self.welcome_message.setGeometry(QtCore.QRect(50, 50, int(MainWindow.width() * 0.6), 100))
        self.welcome_message.setStyleSheet("color: orange; font-size: 24px;")
        self.welcome_message.setAlignment(QtCore.Qt.AlignCenter)

        # Баланс пользователя
        self.balance_label = QtWidgets.QLabel(self.frame_profile)
        self.balance_label.setGeometry(QtCore.QRect(50, 150, int(MainWindow.width() * 0.6), 50))
        self.balance_label.setStyleSheet("color: green; font-size: 20px;")
        self.balance_label.setAlignment(QtCore.Qt.AlignCenter)

        # Кнопка "Купить"
        self.buy_button = QtWidgets.QPushButton(self.frame_profile)
        self.buy_button.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.4), int(MainWindow.height() * 0.8), int(MainWindow.width() * 0.2),
                         50))
        self.buy_button.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.buy_button.setText("Купить")

        # Кнопка "Вернуться на главную"
        self.return_main_button = QtWidgets.QPushButton(self.frame_profile)
        self.return_main_button.setGeometry(
            QtCore.QRect(int(MainWindow.width() * 0.4), int(MainWindow.height() * 0.9), int(MainWindow.width() * 0.2),
                         50))
        self.return_main_button.setStyleSheet("background-color: rgb(255, 170, 0);")
        self.return_main_button.setText("Вернуться на главную")

        # Добавляем страницу профиля в StackedWidget
        self.stackedWidget.addWidget(self.profile_page)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TriGaDa Balance"))


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Подключение базы данных PostgreSQL
        try:
            self.conn = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            self.cursor = self.conn.cursor()

        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")


        # Подключение обработчиков событий
        self.reg_button.clicked.connect(self.show_registration_page)
        self.bir.clicked.connect(self.show_info)
        self.back_button.clicked.connect(self.return_to_main_page)
        self.register_button.clicked.connect(self.register_user)
        self.pushButton.clicked.connect(self.login_user)
        self.return_main_button.clicked.connect(self.return_to_main_page)
        self.buy_button.clicked.connect(self.buy_coin)

    def show_registration_page(self):
        """Переход на страницу регистрации"""
        self.stackedWidget.setCurrentIndex(1)
    def show_info(self):
        inf = SuccessDialog(self,1)
        inf.exec_()


    def return_to_main_page(self):
        """Возврат на главную страницу и очистка полей"""
        self.username_input.clear()
        self.password_input.clear()
        self.welcome_message.setText("")  # Очистка приветственного сообщения
        self.balance_label.setText("")  # Очистка баланса
        self.show_main_page()

    def show_main_page(self):
        """Возврат на главную страницу"""
        self.stackedWidget.setCurrentIndex(0)

    def register_user(self):
        """Логика регистрации пользователя"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            error_dialog = ErrorDialog(self,2)
            error_dialog.exec_()

            return

        try:
            # Добавление пользователя в базу данных
            self.cursor.execute("""
                    INSERT INTO users (real_wallet_adress, demo_wallet_adress, ton_usdt, obt_usdt, plume_usdt, balance, username, password)
                    VALUES (NULL, NULL, 0, 0, 0, 0, %s, %s)
                    RETURNING id_users
                """, (username, password))
            new_user_id = self.cursor.fetchone()[0]  # Получаем ID нового пользователя

            print(f"Новый пользователь добавлен с ID: {new_user_id}")
            self.conn.commit()

            # Вывод содержимого базы данных
            self.cursor.execute("SELECT * FROM users")
            users = self.cursor.fetchall()

            # Проверка, что данные действительно записались
            if not users:
                raise ValueError("База данных пуста!")

            # Формирование сообщения для диалогового окна
            message = "Список пользователей:\n"
            for user in users:
                message += f"ID: {user[0]}, Имя: {user[1]}, Пароль: {user[2]}\n"

            # Вывод в терминал
            print("Содержимое базы данных:")
            for user in users:
                print(f"ID: {user[0]}, Имя: {user[1]}, Пароль: {user[2]}")

            # Показать диалог успешной регистрации
            success_dialog = SuccessDialog(self)
            success_dialog.exec_()



            # Очистка полей ввода
            self.username_input.clear()
            self.password_input.clear()

            # Возврат на главную страницу
            self.show_main_page()

        except Exception as e:
            # Показать диалог ошибки
            error_dialog = QMessageBox()
            error_dialog.setStyleSheet("background-color: white; color: black;")
            error_dialog.setIcon(QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}"))
            error_dialog.setWindowTitle("Ошибка")
            error_dialog.setText("Произошла ошибка при регистрации!")
            error_dialog.setStyleSheet("background-color: white; color: black;")
            error_dialog.exec_()

            #QtWidgets.QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
            #self.username_input.clear()
            #self.password_input.clear()

    def login_user(self):
        """Логика входа пользователя"""
        # Создаем пользовательский диалог для входа
        login_dialog = QtWidgets.QDialog(self)
        login_dialog.setWindowTitle("Вход")
        login_dialog.setStyleSheet("background-color: black;")  # Черный фон диалога

        # Создаем layout для диалога
        layout = QtWidgets.QVBoxLayout()

        # Поле ввода имени пользователя
        username_label = QtWidgets.QLabel("Имя пользователя:")
        username_label.setStyleSheet("color: white;")
        self.username_input_login = QtWidgets.QLineEdit()
        self.username_input_login.setStyleSheet("background-color: white; color: black;")
        layout.addWidget(username_label)
        layout.addWidget(self.username_input_login)

        # Поле ввода пароля
        password_label = QtWidgets.QLabel("Пароль:")
        password_label.setStyleSheet("color: white;")
        self.password_input_login = QtWidgets.QLineEdit()
        self.password_input_login.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_input_login.setStyleSheet("background-color: white; color: black;")
        layout.addWidget(password_label)
        layout.addWidget(self.password_input_login)

        # Кнопки "Войти" и "Отмена"
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal,
            login_dialog
        )
        button_box.button(QtWidgets.QDialogButtonBox.Ok).setText("Войти")
        button_box.button(QtWidgets.QDialogButtonBox.Ok).setStyleSheet("background-color: green; color: white;")
        button_box.button(QtWidgets.QDialogButtonBox.Cancel).setStyleSheet("background-color: red; color: white;")
        button_box.accepted.connect(login_dialog.accept)
        button_box.rejected.connect(login_dialog.reject)
        layout.addWidget(button_box)

        # Устанавливаем layout для диалога
        login_dialog.setLayout(layout)

        # Показываем диалог
        if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
            username = self.username_input_login.text().strip()
            password = self.password_input_login.text().strip()

            if not username or not password:
                error_dialog = ErrorDialog(self, 2)
                error_dialog.exec_()
                return

            try:
                # Проверка существования пользователя
                self.cursor.execute("SELECT username, password, balance FROM users WHERE username = %s AND password = %s", (username, password))
                user = self.cursor.fetchone()

                if user is None:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", "Неверное имя пользователя или пароль!")
                    return

                # Сохраняем текущего пользователя
                #username, password = user
                self.current_user = user

                # Переход на страницу профиля
                self.stackedWidget.setCurrentIndex(2)

                # Отображение приветственного сообщения и баланса
                self.welcome_message.setText(f"Привет, {user[0]}!")
                self.balance_label.setText(f"Ваш баланс: {user[2]}")

                self.cursor.execute("""
                SELECT ton_usdt, obt_usdt, plume_usdt from users
                """, (user[0],))
                user_coins = self.cursor.fetchall()
                if user_coins:
                    coins_text = "Ваши монеты:\n"
                    for coin in user_coins:
                        coins_text += f"{coin[0]}: {coin[1]}\n"
                else:
                    coins_text = "У вас пока нет монет."

                self.coins_label = QtWidgets.QLabel(self.frame_profile)
                self.coins_label.setGeometry(QtCore.QRect(500, 200, int(self.width() * 0.6), 400))
                self.coins_label.setStyleSheet("color: white; font-size: 16px;")
                self.coins_label.setText(coins_text)
                self.coins_label.show()


            except Exception as e:

                print(f"Ошибка при выполнении запроса: {e}")

                QtWidgets.QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def buy_coin(self):
        """Логика покупки монеты"""
        try:
            # Получаем список монет из базы данных
            self.cursor.execute("SELECT id, short_name, current_price FROM all_token")
            coins = self.cursor.fetchall()

            if not coins:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Нет доступных монет для покупки!")
                return

            # Создаем диалог для выбора монеты
            coin_dialog = QtWidgets.QDialog(self)
            coin_dialog.setWindowTitle("Купить монету")
            coin_dialog.setStyleSheet("background-color: black; color: white;")

            layout = QtWidgets.QVBoxLayout()

            # Выбор монеты
            coin_label = QtWidgets.QLabel("Выберите монету:")
            coin_label.setStyleSheet("color: white;")
            layout.addWidget(coin_label)

            self.coin_combo = QtWidgets.QComboBox()
            for coin in coins:
                self.coin_combo.addItem(f"{coin[1]} - {coin[2]} USD")
            layout.addWidget(self.coin_combo)

            # Кнопки "Купить" и "Отмена"
            button_box = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
                QtCore.Qt.Horizontal,
                coin_dialog
            )
            button_box.button(QtWidgets.QDialogButtonBox.Ok).setText("Купить")
            button_box.button(QtWidgets.QDialogButtonBox.Ok).setStyleSheet("background-color: green; color: white;")
            button_box.button(QtWidgets.QDialogButtonBox.Cancel).setStyleSheet("background-color: red; color: white;")
            button_box.accepted.connect(coin_dialog.accept)
            button_box.rejected.connect(coin_dialog.reject)
            layout.addWidget(button_box)

            coin_dialog.setLayout(layout)

            if coin_dialog.exec_() == QtWidgets.QDialog.Accepted:
                selected_coin_index = self.coin_combo.currentIndex()
                selected_coin = coins[selected_coin_index]

                # Проверяем баланс пользователя
                if self.current_user[3] < selected_coin[2]:
                    error_dialog = ErrorDialog(self, 1)
                    error_dialog.exec_()
                    return

                # Обновляем баланс пользователя
                new_balance = self.current_user[3] - selected_coin[2]
                self.cursor.execute("UPDATE users SET balance = %s WHERE id = %s", (new_balance, self.current_user[0]))
                self.conn.commit()

                # Обновляем отображение баланса
                self.balance_label.setText(f"Ваш баланс: {new_balance}")

                self.cursor.execute("""
                                    INSERT INTO users (id, short_name, ton_usdt)
                                    VALUES (%s, %s, 1)
                                    ON CONFLICT (user_id, coin_id) DO UPDATE
                                    SET ton_usdt = users.ton_usdt + 1
                                """, (self.current_user[0], selected_coin[0]))
                self.conn.commit()

                # Показываем сообщение об успешной покупке
                success_dialog = SuccessDialog(self)
                success_dialog.setText(f"Вы успешно купили {selected_coin[1]} за {selected_coin[2]} USD!")
                success_dialog.exec_()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def closeEvent(self, event):
        # Закрытие соединения с базой данных при закрытии приложения
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())