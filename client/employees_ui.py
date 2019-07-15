from PySide2.QtWidgets import QTableWidgetItem, QAbstractItemView
import re

import apputils
import database as db

employees_header_items = ['First Name', 'Last Name', 'Email', 'Phone',
                          'Slack User ID', 'ID']

name_re = re.compile(r'^\w+$')
email_re = re.compile(r'^[0-9a-z]+@[0-9a-z]+\.\w+')
phone_re = re.compile(r'^\d{7,}$')
slack_id_re = re.compile(r'^U[0-9A-Z]{8}$')

def employees_tablewidget_setup(main_window):
    tw = main_window.window.employees_tablewidget
    tw.setSelectionBehavior(QAbstractItemView.SelectRows)
    tw.setSelectionMode(QAbstractItemView.SingleSelection)
    tw.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tw.verticalHeader().setVisible(False)

def check_employee_fields(main_window, firstname, lastname,
                          email, phone, slack_id):
    if not bool(name_re.match(firstname)):
        main_window.show_error('Invalid first name: %s' %
                               '(blank)' if len(firstname) == 0
                               else firstname)
        return False
    if not bool(name_re.match(lastname)):
        main_window.show_error('Invalid last name: %s' %
                               '(blank)' if len(lastname) == 0
                               else lastname)
        return False
    if email and not bool(email_re.match(email)):
        main_window.show_error('Invalid email: %s' % email)
        return False
    if phone and not bool(phone_re.match(phone)):
        main_window.show_error('Invalid phone number: %s' % phone)
        return False
    if not bool(slack_id_re.match(slack_id)):
        main_window.show_error('Invalid Slack ID: %s' % slack_id)
        return False
    return True

def add_employee(main_window):
    firstname_te = main_window.window.employees_firstname_textedit
    lastname_te = main_window.window.employees_lastname_textedit
    email_te = main_window.window.employees_email_textedit
    phone_te = main_window.window.employees_phone_textedit
    slack_id_te = main_window.window.employees_slackid_textedit

    def inner():
        firstname = firstname_te.toPlainText().strip()
        lastname = lastname_te.toPlainText().strip()
        email = email_te.toPlainText().strip()
        phone = phone_te.toPlainText().strip()
        slack_id = slack_id_te.toPlainText().strip()
        if not check_employee_fields(main_window, firstname, lastname, email,
                                     phone, slack_id):
            return

        if db.employee_from_slack_id(slack_id):
            msg = 'An employee with Slack ID %s ' % slack_id
            msg += 'alread exists in the DB.'
            main_window.show_error(msg)
            return

        email = None if not email else email
        phone = None if not phone else int(phone)
        employee_id = apputils.str_id()
        employee = (firstname, lastname, email, phone, slack_id, employee_id)
        db.add_employee(employee)
        refresh_employees(main_window)()

    return inner

def delete_employee(main_window):
    tw = main_window.window.employees_tablewidget
    slack_id_te = main_window.window.employees_slackid_textedit

    def inner():
        slack_id = slack_id_te.toPlainText().strip()
        if not slack_id_re.match(slack_id):
            main_window.show_error('Invalid Slack ID: %s' % slack_id)
            return
        db.delete_employee(slack_id)
        refresh_employees(main_window)()
        tw.clearSelection()
        populate_employees_details(main_window)(-1, -1)

    return inner

def update_employee(main_window):
    firstname_te = main_window.window.employees_firstname_textedit
    lastname_te = main_window.window.employees_lastname_textedit
    email_te = main_window.window.employees_email_textedit
    phone_te = main_window.window.employees_phone_textedit
    slack_id_te = main_window.window.employees_slackid_textedit

    def inner():
        firstname = firstname_te.toPlainText().strip()
        lastname = lastname_te.toPlainText().strip()
        email = email_te.toPlainText().strip()
        phone = phone_te.toPlainText().strip()
        slack_id = slack_id_te.toPlainText().strip()
        if not check_employee_fields(main_window, firstname, lastname, email,
                                     phone, slack_id):
            return
        if not db.employee_from_slack_id(slack_id):
            msg = 'Employee %s %s not in database. ' % (firstname, lastname)
            msg += 'Please add them before updating their entry.'
            main_window.show_error(msg)
            return
        email = None if not email else email
        phone = None if not phone else int(phone)
        employee = (firstname, lastname, email, phone, slack_id)
        db.update_employee(employee)
        refresh_employees(main_window)()

    return inner

def populate_employees_details(main_window):
    tw = main_window.window.employees_tablewidget
    firstname_te = main_window.window.employees_firstname_textedit
    lastname_te = main_window.window.employees_lastname_textedit
    email_te = main_window.window.employees_email_textedit
    phone_te = main_window.window.employees_phone_textedit
    slack_id_te = main_window.window.employees_slackid_textedit

    def inner(row, column):
        if row == -1 and column == -1:
            firstname_te.setText('')
            lastname_te.setText('')
            email_te.setText('')
            phone_te.setText('')
            slack_id_te.setText('')
            return
        firstname_te.setText(tw.item(row, 0).text())
        lastname_te.setText(tw.item(row, 1).text())
        email_te.setText(tw.item(row, 2).text())
        phone_te.setText(tw.item(row, 3).text())
        slack_id_te.setText(tw.item(row, 4).text())

    return inner

def refresh_employees(main_window):
    employees_tablewidget_setup(main_window)
    tw = main_window.window.employees_tablewidget

    def inner():
        employees = db.get_employees()
        tw.setColumnCount(len(employees_header_items))
        tw.setRowCount(len(employees))
        tw.setHorizontalHeaderLabels(employees_header_items)
        for row in range(0, len(employees)):
            for column in range(0, len(employees[row])):
                text = employees[row][column]
                text = str(text) if text else None
                item = QTableWidgetItem(text)
                tw.setItem(row, column, item)
    inner()  # setup
    return inner