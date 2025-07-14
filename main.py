from PyQt5.QtWidgets import QApplication,QMessageBox
from views.main_window import MainWindow
import sys

from views.trial_manager import is_trial_expired


app = QApplication(sys.argv)

if is_trial_expired():
    QMessageBox.critical(None, "Trial Expired", "Your 14-day trial has ended.")
    sys.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
