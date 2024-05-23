import os
from flaskwebgui import FlaskUI
from datetime import date
from flask import Flask, redirect, request, render_template
import openpyxl

from models.record import Record

app = Flask(__name__, static_url_path="", static_folder=os.path.join(os.getcwd(), "flask_desktop_app/phrases"))

directory = os.getcwd()

@app.route("/")
def home():
    day = str(date.today())
    path=os.path.join(os.getcwd(), "records/medical.xlsx")
    wb = openpyxl.load_workbook(path)
    names = wb.sheetnames
    if (day not in names):
        return redirect('/assign')
    else:
        ws = wb["current"]
        header = [cell.value for cell in ws[1]]
        records=[]
        for i in range(2,ws.max_row+1):
            args =[cell.value for cell in ws[i]]
            record = Record(*args)
            records.append(record)
        return render_template('start.html', title="Список отчетов", tab = header, records = records)

@app.route('/assign')
def my_form():
    return render_template('assign.html')

@app.route('/assign', methods=['POST'])
def my_form_post():
    text = request.form['text']
    day = str(date.today())
    path=os.path.join(os.getcwd(), "records/medical.xlsx")
    wb = openpyxl.load_workbook(path)
    wb.create_sheet(day)
    new_data = [day, text, 0]
    ws = wb["current"]
    ws.append(new_data)
    wb.save("records/medical.xlsx")
    return redirect("/")

if __name__ == "__main__":
  FlaskUI(app=app, server="flask",  width= 700, height=700).run()
  