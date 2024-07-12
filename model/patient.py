class Patient():
    def __init__(self, id = None, time=None, patient=None, doc=None, docId=None, type=None, birthdate=None, reason=None, pressure=None):
        self.id = id
        self.time = time
        self.patient = patient
        self.doc = doc
        self.docId = docId
        self.type = type
        self.birthdate = birthdate
        self.reason = reason
        self.pressure = pressure