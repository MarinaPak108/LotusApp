import os
import openpyxl
from datetime import date, datetime
from typing import TypeVar

class Service():
    T = TypeVar('T') 
    
    def getWB():
        path=os.path.join(os.getcwd(), "records/medical.xlsx")
        return openpyxl.load_workbook(path)

    def getDay():
        return str(date.today())

    def getTimestamp():
        return datetime.now()
    
    def fromExcelToList(T, ws):
        listObjects=[]
        for i in range(1,ws.max_row+1):
            args =[cell.value for cell in ws[i]]
            typeObject = T(*args)
            listObjects.append(typeObject)
        return listObjects
    
    def saveRecord(wb,name, new_data):
        ws=wb[name]
        ws.append(new_data)
        wb.save("records/medical.xlsx")
     
    def countPatients(wb, records, today):
        ws = wb['current']
        for i in  range(1, ws.max_row+1):
            if(records[i-1].patients == -1 or records[i-1].date == today):
                ws_current = wb[records[i-1].date]
                records[i-1].patients = ws_current.max_row-1
                ws.cell(row=i, column=3).value = records[i-1].patients
        wb.save("records/medical.xlsx")
                
                

    
            
    
    
        
                
         
        
    


