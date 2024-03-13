import markdown
import datetime

class Post:

    category : str
    author : str
    date : datetime.datetime
    body : str
    file : str

    def __init__(self, file_path):
        self.file = file_path

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        self.category = lines[1].split(":")[1].strip()
        self.author = lines[2].split(":")[1].strip()

        date = lines[3].split(":")[1].strip()
        self.date = datetime.datetime.strptime(date, "%d-%m-%Y")

        self.body = markdown.markdown(''.join(lines[6:]))

