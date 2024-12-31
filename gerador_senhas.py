import sys
import secrets
import bcrypt
import string
import json
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout,
    QCheckBox, QSpinBox, QPlainTextEdit, QFileDialog, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyperclip


class PasswordGenerator(QWidget):
    def __init__(self):
        super().__init__()

        # Configurações da janela
        self.setWindowTitle("Gerador de Senhas Seguras")
        self.setGeometry(100, 100, 600, 600)
        self.setStyleSheet("""
            background-color: #2C3E50;
            color: white;
            font-family: 'Arial', sans-serif;
        """)

        # Layout principal
        layout = QVBoxLayout()

        # Título
        self.label_title = QLabel("SecureGen")
        self.label_title.setFont(QFont("Arial", 20))
        self.label_title.setStyleSheet("color: #3498DB; text-align: center;")
        self.label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_title)

        # Caixa de texto para exibir a senha gerada
        self.password_display = QLineEdit()
        self.password_display.setFont(QFont("Courier New", 14))
        self.password_display.setStyleSheet("""
            background-color: #34495E;
            color: white;
            border: none;
            padding: 10px;
        """)
        self.password_display.setReadOnly(True)
        layout.addWidget(self.password_display)

        # Indicador de força da senha
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 5)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setStyleSheet("""
            QProgressBar {
                background-color: #34495E;
                border-radius: 5px;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: red;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.strength_bar)

        # Layout para controle do comprimento da senha
        length_layout = QHBoxLayout()
        self.label_length = QLabel("Comprimento da Senha:")
        self.label_length.setStyleSheet("color: white;")
        self.password_length = QSpinBox()
        self.password_length.setRange(8, 64)
        self.password_length.setValue(16)
        length_layout.addWidget(self.label_length)
        length_layout.addWidget(self.password_length)
        layout.addLayout(length_layout)

        # Layout para selecionar os tipos de caracteres
        self.include_upper = QCheckBox("Incluir Letras Maiúsculas")
        self.include_upper.setChecked(True)
        self.include_lower = QCheckBox("Incluir Letras Minúsculas")
        self.include_lower.setChecked(True)
        self.include_numbers = QCheckBox("Incluir Números")
        self.include_numbers.setChecked(True)
        self.include_special = QCheckBox("Incluir Caracteres Especiais")
        self.include_special.setChecked(True)

        layout.addWidget(self.include_upper)
        layout.addWidget(self.include_lower)
        layout.addWidget(self.include_numbers)
        layout.addWidget(self.include_special)

        # Layout para número de senhas geradas
        num_passwords_layout = QHBoxLayout()
        self.num_passwords_label = QLabel("Número de Senhas a Gerar:")
        self.num_passwords_label.setStyleSheet("color: white;")
        self.num_passwords = QSpinBox()
        self.num_passwords.setRange(1, 10)
        self.num_passwords.setValue(1)
        num_passwords_layout.addWidget(self.num_passwords_label)
        num_passwords_layout.addWidget(self.num_passwords)
        layout.addLayout(num_passwords_layout)

        # Botão para gerar senha
        self.generate_button = QPushButton("Gerar Senha(s)")
        self.configure_button(self.generate_button, "#3498DB", "#2980B9")
        self.generate_button.clicked.connect(self.generate_passwords)
        layout.addWidget(self.generate_button)

        # Caixa de texto para exibir múltiplas senhas geradas
        self.generated_passwords_display = QPlainTextEdit()
        self.generated_passwords_display.setFont(QFont("Courier New", 14))
        self.generated_passwords_display.setStyleSheet("""
            background-color: #34495E;
            color: white;
            padding: 10px;
        """)
        self.generated_passwords_display.setReadOnly(True)
        layout.addWidget(self.generated_passwords_display)

        # Layout para botões de ação
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar Senhas")
        self.configure_button(self.save_button, "#16A085", "#1ABC9C")
        self.save_button.clicked.connect(self.save_passwords_to_file)
        buttons_layout.addWidget(self.save_button)

        self.copy_button = QPushButton("Copiar Senhas")
        self.configure_button(self.copy_button, "#E74C3C", "#C0392B")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        buttons_layout.addWidget(self.copy_button)
        layout.addLayout(buttons_layout)

        # Rodapé
        self.footer_label = QLabel("Desenvolvido por Gabriel Barbosa")
        self.footer_label.setFont(QFont("Arial", 8))
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("color: #ebde34; margin-top: 20px;")
        layout.addWidget(self.footer_label)

        # Definindo o layout da janela
        self.setLayout(layout)

    def configure_button(self, button, background_color, hover_color):
        """Configura o estilo de um botão"""
        button.setFont(QFont("Arial", 12))
        button.setStyleSheet(f"""
            background-color: {background_color};
            color: white;
            border-radius: 10px;
            padding: 15px;
            min-width: 200px;
        """)
        button.setStyleSheet(f"""
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

    def generate_passwords(self):
        """Gera múltiplas senhas seguras com caracteres aleatórios"""
        num_passwords = self.num_passwords.value()
        password_length = self.password_length.value()
        all_characters = ""

        # Seleção dos tipos de caracteres
        if self.include_upper.isChecked():
            all_characters += string.ascii_uppercase
        if self.include_lower.isChecked():
            all_characters += string.ascii_lowercase
        if self.include_numbers.isChecked():
            all_characters += string.digits
        if self.include_special.isChecked():
            all_characters += string.punctuation

        if not all_characters:
            self.generated_passwords_display.setPlainText("Selecione pelo menos um tipo de caractere.")
            return

        passwords = []
        for _ in range(num_passwords):
            password = self.generate_secure_password(password_length, all_characters)
            passwords.append(password)

        self.generated_passwords_display.setPlainText("\n".join(passwords))
        self.update_strength_bar(passwords[0])

    def generate_secure_password(self, length, characters):
        """Gera uma senha segura usando a biblioteca secrets"""
        return ''.join(secrets.choice(characters) for _ in range(length))

    def update_strength_bar(self, password):
        """Atualiza a barra de força da senha e sua cor"""
        strength = self.check_password_strength(password)
        self.strength_bar.setValue(strength)

        # Muda a cor da barra com base na força da senha
        if strength <= 2:
            color = "red"
        elif strength <= 4:
            color = "orange"
        else:
            color = "green"

        self.strength_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #34495E;
                border-radius: 5px;
                height: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

    def check_password_strength(self, password):
        """Verifica a força da senha"""
        strength = 0
        if any(char.islower() for char in password):
            strength += 1
        if any(char.isupper() for char in password):
            strength += 1
        if any(char.isdigit() for char in password):
            strength += 1
        if any(char in string.punctuation for char in password):
            strength += 1
        if len(password) >= 12:
            strength += 1
        return strength

    def save_passwords_to_file(self):
        """Salva as senhas geradas em um arquivo de texto, JSON ou CSV"""
        options = QFileDialog.Options()
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self, "Salvar Senhas", "", "Text Files (*.txt);;JSON Files (*.json);;CSV Files (*.csv);;All Files (*)", options=options
        )

        if file_name:
            try:
                passwords = self.generated_passwords_display.toPlainText().split("\n")
                if selected_filter == "Text Files (*.txt)":
                    with open(file_name, 'w') as file:
                        file.write("\n".join(passwords))
                elif selected_filter == "JSON Files (*.json)":
                    with open(file_name, 'w') as file:
                        json.dump(passwords, file)
                elif selected_filter == "CSV Files (*.csv)":
                    with open(file_name, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(["Senhas"])
                        for password in passwords:
                            writer.writerow([password])
                self.generated_passwords_display.setPlainText(f"Senhas salvas em: {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo: {str(e)}")

    def copy_to_clipboard(self):
        """Copia as senhas geradas para a área de transferência"""
        pyperclip.copy(self.generated_passwords_display.toPlainText())
        self.generated_passwords_display.setPlainText("Senhas copiadas para a área de transferência!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordGenerator()
    window.show()
    sys.exit(app.exec_())