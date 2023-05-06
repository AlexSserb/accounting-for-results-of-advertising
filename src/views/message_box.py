from PyQt5.QtWidgets import QMessageBox


def show_error_messagebox(error_text: str, more_info: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(error_text)
    msg.setInformativeText(more_info)
    msg.setWindowTitle("Error")
    msg.exec_()


def show_success_messagebox(msg_text: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(msg_text)
    msg.setWindowTitle("Executed successfully")
    msg.exec_()
