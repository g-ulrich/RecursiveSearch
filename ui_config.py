from PyQt5.QtCore import QTimer, QTime
from PyQt5 import QtWidgets
from pyautogui import position
import os, os.path, pathlib
from datetime import datetime
from PyPDF2 import PdfReader
import docx2txt


# from bs4 import BeautifulSoup as bs


def current_time():
    t = QTime.currentTime().toString()
    am_pm = "pm" if 12 < int(t[:2]) < 23 else "am"
    return t + " " + am_pm


class Presets:
    def start(self):
        # Welcome message
        Presets.event_log(self, "[INFO] Welcome!")

        # new variables
        self.ui.selected_directory = "/"
        self.ui.directory_count = 0
        self.ui.file_count = 0
        self.ui.full_readable_file_paths = []
        self.ui.full_none_readable_file_paths = []
        self.ui.readable_file_exts = ['pdf', 'docx', 'txt']

        # Init... presets only once.
        self.ui.btn_select_dir.clicked.connect(lambda: Presets.select_directory(self))
        self.ui.btn_search.clicked.connect(lambda: Presets.start_search(self))
        self.ui.edit_search.returnPressed.connect(lambda: Presets.start_search(self))
        self.ui.log.itemClicked.connect(lambda: Presets.log_item_clicked(self))

        self.ui.timer = QTimer()
        self.ui.timer.timeout.connect(lambda: Presets.mouse_loop(self))
        self.ui.timer.start(200)

    def start_search_job(self):
        # this function does the most intensive search for this application.
        self.ui.temp_timer.stop()
        s = datetime.now()
        Presets.count_files_recursively(self)
        Presets.find_search_phrase_in_file_titles(self)

        e = datetime.now()
        Presets.event_log(self, f"[INFO] Finished in {round((e - s).total_seconds(), 2)} seconds! With {self.ui.log.count()} line items.")

    def start_search(self):
        # initiates the search and checks for paramets
        self.ui.log.clear()
        search_text = self.ui.edit_search.text()
        if self.ui.selected_directory == "":
            self.ui.selected_directory = "/"
        if search_text.strip() != "":
            Presets.event_log(self, "[INFO] Starting search!")
            Presets.event_log(self, f"Loading results for '{search_text}'...")
            self.ui.temp_timer = QTimer()
            self.ui.temp_timer.timeout.connect(lambda: Presets.start_search_job(self))
            self.ui.temp_timer.start(1000)
        else:
            Presets.event_log(self, "[ERROR] Please enter something to search for.")

    def log_item_clicked(self):
        selected_text = self.ui.log.currentItem().text()
        if "/" in selected_text or selected_text.split(".")[-1] in self.ui.readable_file_exts:
            path = '/'.join(selected_text.split("/")[0:-1]).strip()
            file = selected_text.split("/")[-1]
            os.chdir(path)
            os.system(f'"{file}"')
            os.chdir(self.ui.selected_directory)

    def find_search_phrase_in_file_titles(self):
        search_text = self.ui.edit_search.text()
        readable = self.ui.full_readable_file_paths
        none_readable = self.ui.full_none_readable_file_paths
        Presets.event_log(self, "")
        Presets.event_log(self, f"[INFO] Checking {len(readable) + len(none_readable)} file titles.")
        for title in readable + none_readable:
            if search_text in title.split("/")[-1]:
                t = title.replace('\\', '/').replace('./', '')
                Presets.event_log(self, f"{self.ui.selected_directory}/{t}")

        Presets.event_log(self, "")
        Presets.event_log(self,
                          f"[INFO] Checking {len(readable) + len(none_readable)} Readable file contents ({', '.join(self.ui.readable_file_exts)}).")
        for title in readable:
            ext = title.split("/")[-1].split(".")[-1]
            if ext == "txt":
                try:
                    with open(title, encoding='utf-8') as f:
                        contents = f.readlines()
                        for i, content in enumerate(contents, 0):
                            if search_text.lower() in content.lower():
                                text = content.strip().replace('\\n', '')
                                t = title.replace('.\\', '')
                                Presets.event_log(self, f"{self.ui.selected_directory}/{t}")
                                Presets.event_log(self,
                                                  f"     Line {i}. {text.replace(search_text, '[' + search_text.upper() + ']')}")
                    f.close()
                except Exception as e:
                    Presets.event_log(self, f"[ERROR] txt: {e}")
            elif ext == "pdf":
                try:
                    reader = PdfReader(title)
                    for i in range(reader.getNumPages()):
                        page = reader.pages[i]
                        text = page.extract_text()
                        if search_text.lower() in text.lower():
                            text = text.strip().replace('\\n', '').replace('\\t', '')
                            t = title.replace('.\\', '')
                            Presets.event_log(self, f"{self.ui.selected_directory}/{t}")
                            ind = text.index(search_text)
                            text = text[ind - 10: len(search_text) + ind + 10]
                            Presets.event_log(self,
                                              f"     Page {i}. {text.replace(search_text, '[' + search_text.upper() + ']')}")
                except Exception as e:
                    Presets.event_log(self, f"[ERROR] pdf: {e}")
            elif ext == "doc":
                try:
                    pass
                    # soup = bs(open(title).read())
                    # [s.extract() for s in soup(['style', 'script'])]
                    # tmpText = soup.get_text()
                    # text = "".join("".join(tmpText.split('\t')).split('\n')).encode('utf-8').strip()
                    # print(text)
                    # quit()
                except Exception as e:
                    Presets.event_log(self, f"[ERROR] doc: {e}")
            elif ext == "docx":
                try:
                    text = docx2txt.process(title)
                    text = text.strip()
                    if search_text.lower() in text.lower():
                        text = text.strip().replace('\\n', '').replace('\\t', '')
                        t = title.replace('.\\', '')
                        Presets.event_log(self, f"{self.ui.selected_directory}/{t}")
                        ind = text.index(search_text)
                        text = text[ind - 10: len(search_text) + ind + 10]
                        Presets.event_log(self,
                                          f"     {text.replace(search_text, '[' + search_text.upper() + ']')}")
                except Exception as e:
                    Presets.event_log(self, f"[ERROR] docx: {e}")

    def count_files_recursively(self):

        os.chdir(self.ui.selected_directory)
        total = [*map(lambda x: x.is_dir(), pathlib.Path(self.ui.selected_directory).rglob('*'))]
        self.ui.directory_count = sum(total)
        self.ui.file_count = len(total) - sum(total)
        Presets.event_log(self, f"{self.ui.directory_count} directories and {self.ui.file_count} files.")

        # compile file paths, readable and none readable
        full_readable_paths = []
        full_readable_paths_app = full_readable_paths.append
        full_none_readable_paths = []
        full_none_readable_paths_app = full_none_readable_paths.append
        for dir, dirs, files in os.walk('.'):
            for f in files:
                if '.' in f:
                    if f.split(".")[-1] in self.ui.readable_file_exts:
                        full_readable_paths_app(dir + "/" + f)
                    else:
                        full_none_readable_paths_app(dir + "/" + f)
        self.ui.full_readable_file_paths = full_readable_paths
        self.ui.full_none_readable_file_paths = full_none_readable_paths
        Presets.event_log(self, f"Readable files: {len(self.ui.full_readable_file_paths)}")
        Presets.event_log(self, f"None Readable files: {len(self.ui.full_none_readable_file_paths)}")

        # complicated one line nested for loop for all extensions.
        exts = set(f.split('.')[-1] for dir, dirs, files in os.walk('.') for f in files if '.' in f)
        Presets.event_log(self, f"Unique file extensions: {len(exts)}")

        # details on readable files
        pdf = [*map(lambda x: x.is_file(), pathlib.Path(self.ui.selected_directory).rglob('*.pdf'))]
        Presets.event_log(self, f"     PDF: {len(pdf)}")
        doc = [*map(lambda x: x.is_file(), pathlib.Path(self.ui.selected_directory).rglob('*.doc'))]
        Presets.event_log(self, f"     DOC: {len(doc)}")
        docx = [*map(lambda x: x.is_file(), pathlib.Path(self.ui.selected_directory).rglob('*.docx'))]
        Presets.event_log(self, f"     DOCX: {len(docx)}")
        txt = [*map(lambda x: x.is_file(), pathlib.Path(self.ui.selected_directory).rglob('*.txt'))]
        Presets.event_log(self, f"     TXT: {len(txt)}")

    def select_directory(self):
        try:
            self.ui.selected_directory = QtWidgets.QFileDialog.getExistingDirectory()
            if len(self.ui.selected_directory) > 40:
                format = self.ui.selected_directory[:10] + "..." + self.ui.selected_directory[-20:]
            else:
                format = self.ui.selected_directory
            self.ui.label_directory.setText(format)
            Presets.event_log(self, f"[INFO] Selected Directory: {self.ui.selected_directory}.")
        except Exception as e:
            Presets.event_log(self, f"[ERROR] {e}")
            Presets.event_log(self, "[INFO] Please select a directory.")
            self.ui.label_directory.setText(self.ui.selected_directory)

    def event_log(self, message):
        t, c = current_time(), self.ui.log.count()
        self.ui.log.setCurrentRow(c - 1)
        self.ui.label_last_update.setText(f"{t}")
        if "[INFO]" in message:
            self.ui.log.takeItem(c - 1)
            self.ui.log.addItem(message)
            self.ui.log.addItem("")
        elif "[ERROR]" in message:
            self.ui.log.takeItem(c - 1)
            self.ui.log.addItem(f"{t}: {message}")
            self.ui.log.addItem("")
        else:
            self.ui.log.takeItem(c - 1)
            self.ui.log.addItem(f"    {message}")
            self.ui.log.addItem("")

    def mouse_loop(self):
        self.ui.label_current_time.setText(current_time())
        pos = position()
        self.ui.label_mouse_pos.setText(f"({pos[0]}, {pos[1]})")
