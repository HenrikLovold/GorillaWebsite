from datetime import datetime, timezone

class Logger:

    def __init__(self):
        self.log_entries = []
        self.filename = "log.txt"
        self.file = open(self.filename, "a+")

    def log_entry(self, logstr: str):
        self.log_entries.append(logstr)
        timestamp = str(datetime.now(timezone.utc))
        self.file.write(timestamp + "\n")
        self.file.write(logstr)
        self.file.write("\n\n")

    def __del__(self):
        self.file.close()