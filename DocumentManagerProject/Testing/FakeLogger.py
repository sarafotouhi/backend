# Fake of Logger class

class FakeLogger:

    def __init__(self):
        self.logs = []

    def log(self, logMessage):
        self.logs.append(logMessage)
