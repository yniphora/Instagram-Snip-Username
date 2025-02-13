import sys
import json
import time
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QTextEdit, QLineEdit
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, InvalidSessionIdException, NoSuchWindowException

class InstagramBot(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self, username, password, profile, new_username):
        super().__init__()
        self.username = username
        self.password = password
        self.profile = profile
        self.new_username = new_username
        self.driver = None
        self.max_retries = 5
        self.retry_delay = 10

    def run(self):
        for attempt in range(self.max_retries):
            try:
                self.setup_driver()
                if self.login_to_instagram():
                    time.sleep(random.uniform(3, 5))
                    if self.navigate_to_profile():
                        while True:
                            self.change_username()
                            time.sleep(random.uniform(2, 4))
            except Exception as e:
                self.update_signal.emit(f"Error: {e}. Reintentando... (Intento {attempt + 1}/{self.max_retries})")
                self.cleanup_driver()
                time.sleep(self.retry_delay)
            else:
                break
        else:
            self.update_signal.emit("The maximum number of attempts has been reached. The bot will stop.")

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(80, 108)}.0.0.0 Safari/537.36")
        
        service = Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def cleanup_driver(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        self.driver = None

    def login_to_instagram(self):
        try:
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(random.uniform(2, 4))
            username_input = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.NAME, "username")))
            password_input = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.NAME, "password")))
            username_input.send_keys(self.username)
            time.sleep(random.uniform(0.5, 1))
            password_input.send_keys(self.password)
            time.sleep(random.uniform(0.5, 1))
            password_input.send_keys(Keys.RETURN)
            WebDriverWait(self.driver, 30).until(EC.url_contains("instagram.com/"))
            self.update_signal.emit("Successful login.")
            return True
        except Exception as e:
            self.update_signal.emit(f"Error durante el inicio de sesión: {e}")
            return False

    def navigate_to_profile(self):
        try:
            self.driver.get(f"https://accountscenter.instagram.com/profiles/{self.profile}/")
            time.sleep(random.uniform(3, 5))
            username_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Username')]"))
            )
            username_button.click()
            self.update_signal.emit("Clicked on the 'Username' button'.")
            return True
        except Exception as e:
            self.update_signal.emit(f"Error during navigation: {e}")
            return False

    def change_username(self):
        try:
            username_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'][value]"))
            )
            
            current_username = username_input.get_attribute('value')
            self.update_signal.emit(f"Current user name: {current_username}")
            
            username_input.clear()
            time.sleep(random.uniform(0.5, 1))
            username_input.send_keys(Keys.CONTROL + "a")
            time.sleep(random.uniform(0.5, 1))
            username_input.send_keys(Keys.DELETE)
            time.sleep(random.uniform(0.5, 1))
            for char in self.new_username:
                username_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            done_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Done')]"))
            )
            done_button.click()
            
            self.update_signal.emit(f"Attempted change to: {self.new_username}")
            time.sleep(random.uniform(2, 4))
            return True
        except Exception as e:
            self.update_signal.emit(f"Error when trying to change the user name: {e}")
            return False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instagram Username Changer GitHub yniphora")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QPushButton {
                background-color: #0077b5;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005f8f;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        title_label = QLabel("Instagram username changer")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Instagram Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Instagram Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.profile_input = QLineEdit()
        self.profile_input.setPlaceholderText("Profile ID")
        layout.addWidget(self.profile_input)

        self.new_username_input = QLineEdit()
        self.new_username_input.setPlaceholderText("New Username to Try")
        layout.addWidget(self.new_username_input)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_bot)
        layout.addWidget(self.start_button)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        central_widget.setLayout(layout)

    def start_bot(self):
        username = self.username_input.text()
        password = self.password_input.text()
        profile = self.profile_input.text()
        new_username = self.new_username_input.text()

        self.bot = InstagramBot(username, password, profile, new_username)
        self.bot.update_signal.connect(self.update_log)
        self.bot.start()

    def update_log(self, message):
        self.log_area.append(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())