import markdown
import datetime

class Post:

    category : str
    author : str
    date : datetime.datetime
    date_str : str
    body : str
    file : str
    title : str
    url : str

    def __init__(self, file_path):
        self.file = file_path

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        self.category = lines[1].split(":")[1].strip()
        self.author = lines[2].split(":")[1].strip()
        self.title = lines[6].replace('#', '').strip()
        self.url = '/post/' + self.title

        date = lines[3].split(":")[1].strip()
        self.date = datetime.datetime.strptime(date, "%d-%m-%Y")
        self.date_str = self.date.strftime("%B %d, %Y")

        self.body = markdown.markdown(f'# [{self.title}]({self.url})\n' + ''.join(lines[7:]), extensions=['footnotes'])
