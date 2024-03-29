#CRANE
import itertools
from selenium import webdriver
import pyautogui as pag
import json, pathlib

USER_DATA = pathlib.Path().resolve() / 'Data'

if not USER_DATA.exists():
    USER_DATA.mkdir()

chromeOptions = webdriver.ChromeOptions()
# chromeOptions.add_argument('--headless')
chromeOptions.add_argument('--no-sandbox')
chromeOptions.add_argument('--disable-dev-shm-usage')


class ChromeNotFoundException(Exception):
    pass

try:
    # PYTHON Example
    winds = next(x for x in pag.getAllTitles() if "google chrome" in x.lower() and "wordle" in x.lower())

    if not winds:
        raise ChromeNotFoundException("Chrome not found!")
    print("Trying to access old Chrome Browser at Port: 9222")

    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={USER_DATA}")
    chrome_options.add_argument('log-level=3')
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    browser = webdriver.Chrome(options=chrome_options)
    print("Successfully accessed old Chrome Browser at Port: 9222")

except Exception:
    print("Failed to access old Chrome Browser at Port: 9222\nCreating new Chrome Browser")
    chrome_options1 = webdriver.ChromeOptions()
    chrome_options1.add_argument(f"user-data-dir={USER_DATA}")
    chrome_options1.add_argument('--remote-debugging-port=9222')
    chrome_options1.add_argument('log-level=3')
    browser = webdriver.Chrome(options=chrome_options1)


class Wordle:
    def __init__(self):
        self.url = "https://www.powerlanguage.co.uk/wordle/"
        self.potential = set()
        self.correct = {}
        with open("all_words.json", "r") as f:
            self.words = json.load(f) 
            
        
    def open(self):
        browser.get(self.url)
        
        while True:
            if len(self.correct.keys())==5:
                print(f"Word found: {self.potential.pop()}")
                break
            input("\nPress Enter after playing: ")
            board = browser.execute_script("return document.getElementsByTagName('game-app')[0].$board")
            
            self.correct  = {}
            self.all_rows, self.present, self.not_in = [], [], []
            self.rows = board.find_elements_by_tag_name('game-row')
            for i in range(5):
                if self.rows[i].text=="":
                    continue
                row = browser.execute_script("return arguments[0].$row", self.rows[i])            
                row_letters = row.find_elements_by_tag_name("game-tile")
                row_eval = [{rl.text.lower():rl.get_attribute("evaluation") for rl in row_letters}]
                self.all_rows.extend(row_eval)
            self.filter_words()
    def filter_words(self):
        to_check = self.potential or self.words
        for row in self.all_rows:
            letters = list(row.keys())
            self.correct.update({x.lower():letters.index(x) for x in letters if row[x] == 'correct'})
            self.wrong_pos = {x.lower():letters.index(x) for x in letters if row[x] == 'present'}
            self.present = list(set(self.present + [k for k,v in row.items() if v=="present"])) + list(self.correct.keys())
            self.not_in = list(set(self.not_in + [x for x in letters if x not in list(self.correct.keys())+self.present]))


        self.potential = {word for word in to_check if ({i: v for i, v in self.correct.items() if word[v] == i} == self.correct and not any(x for x in self.not_in if x in word) and sorted([x for x in self.present if x in word]) == sorted(self.present) and not [let for let, j in self.wrong_pos.items() if word[j] == let])}

        self.get_letter_freq()
    def get_letter_freq(self):
        self.letter_freq = {}
        check_list = self.potential or self.words
        for word in check_list:
            letters = list(word)
            for l in letters:
                self.letter_freq[l] = self.letter_freq.get(l, 0) + 1

        self.letter_freq = dict(sorted(self.letter_freq.items(), key=lambda x: x[1], reverse=True))


        self.ranked_pot = {}
        for word, (i, v) in itertools.product(check_list, self.letter_freq.items()):
            if i in word:
                self.ranked_pot[word] = self.ranked_pot.get(word, 0) + v
        self.ranked_pot = dict(sorted(self.ranked_pot.items(), key=lambda x: x[1], reverse=True))
        print(list(self.ranked_pot)[:50])
        print(self.letter_freq)
        

        


wordle = Wordle()
wordle.get_letter_freq()
wordle.open()


