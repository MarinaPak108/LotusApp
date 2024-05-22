import os
from flaskwebgui import FlaskUI
from datetime import date
from flask import Flask, redirect, request, render_template
import random
import openpyxl

app = Flask(__name__, static_url_path="", static_folder=os.path.join(os.getcwd(), "flask_desktop_app/phrases"))

directory = os.getcwd()

@app.route("/")
def home():
    day = str(date.today())
    path=os.path.join(os.getcwd(), "records/medical.xlsx")
    wb = openpyxl.load_workbook(path)
    names = wb.sheetnames
    ws = wb["current"]
    if (day not in names):
        return redirect('/assign')
    return render_template('start.html',title="Список отчетов", tab = zip(titles), fileNames = zip(names))

@app.route('/assign')
def my_form():
    return render_template('assign.html')

@app.route('/assign', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.upper()
    day = str(date.today())
    path=os.path.join(os.getcwd(), "records/medical.xlsx")
    wb = openpyxl.load_workbook(path)
    wb.create_sheet(day)
    new_data = [day, text, 0]
    ws = wb["current"]
    ws.append(new_data)
    wb.save("records/medical.xlsx")
    return processed_text

if __name__ == "__main__":
  FlaskUI(app=app, server="flask",  width= 700, height=700).run()
  