#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from downloaddata import Librus, Attendance


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Librus Attendance Calc'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 340
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create loginbox
        self.loginbox = QLineEdit(self)
        self.loginbox.move(20, 20)
        self.loginbox.resize(280, 40)
        self.loginbox.setText('Twój login')
        # Create passwordbox
        self.pwdbox = QLineEdit(self)
        self.pwdbox.setText('Twoje hasło')
        #self.pwdbox.setEchoMode(QLineEdit.Password)
        self.pwdbox.move(20, 80)
        self.pwdbox.resize(280, 40)

        # Create semesterbox
        self.sembox = QLineEdit(self)
        self.sembox.move(20, 140)
        self.sembox.resize(280, 40)
        self.sembox.setText('Semestr (1, 2, 0 - oba)')

        # Create a button in the window
        self.button = QPushButton('Show text', self)
        self.button.move(20, 200)

        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()

    @pyqtSlot()
    def on_click(self):
        loginboxValue = self.loginbox.text()
        pwdboxValue = self.pwdbox.text()
        semboxValue = self.sembox.text()
        #QMessageBox.question(self, 'Allert', "Login: " + loginboxValue
        #                     + "\nHasło: " + pwdboxValue,
        #                    QMessageBox.Ok,QMessageBox.Ok)

        l = Librus(loginboxValue, pwdboxValue)
        att = l.get_api_response(Librus.URL_UNATTENDANCE)['Attendances']
        lessons = dict()
        semester_id = int(semboxValue)
        for i, a in enumerate(att):
            x = Attendance(l, json=a)
            if not semester_id or x.semester_id == semester_id:
                if not x.lesson.subject.name in lessons:
                    lessons[x.lesson.subject.name] = {'ob': 0, 'nb': 0}
                if x.type.is_presence_kind:
                    lessons[x.lesson.subject.name]['ob'] += 1
                else:
                    lessons[x.lesson.subject.name]['nb'] += 1
        result = ""
        for lesson in lessons:
            print(lesson)
            result += lesson + '\n'
            ob = lessons[lesson]['ob']
            nb = lessons[lesson]['nb']
            result += '\tObecności: ' + str(ob) + '\n'
            result += '\tNieobecności: ' + str(nb) + '\n'
            result += '\tProcentowa frekwencja: ' + str(round(((ob * 100) / (nb + ob) * 100) / 100, 2)) + '%\n'
            print('\tObecności: %s' % ob)
            print('\tNieobecności: %s' % nb)
            print('\tProcentowa frekwencja: %2.2f%%' % (((ob * 100) / (nb + ob) * 100) / 100))

        QMessageBox.information(self, 'Result', result, QMessageBox.Ok, QMessageBox.Ok)
        self.loginbox.setText("")
        self.pwdbox.setText("")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
