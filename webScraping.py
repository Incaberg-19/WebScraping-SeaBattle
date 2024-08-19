import tkinter as tk
from tkinter import ttk

from bs4 import BeautifulSoup
import requests

from abc import ABC, abstractmethod

class Invalid_URL_Exception(Exception):
    pass

class Request_Failed_Exception(Exception):
    pass

class Headlines_not_found(Exception):
    pass

class WebScraper(ABC):
    @abstractmethod
    def __init__(self, url):
        self.url = url

    @abstractmethod
    def get_html(self):
        return requests.post(self.url).text

class Modern_WebScraper(WebScraper):

    def __init__(self, url):
        if not url.startswith('http'):
            raise Invalid_URL_Exception("URL должен начинаться с http:// или https://")
        self.url = url

    def get_html(self):
        try:
            return requests.post(self.url).text
        except requests.RequestException as e:
            raise Request_Failed_Exception(f"Ошибка при выполнении запроса: {e}")

    def get_data(self):
        html = self.get_html()
        soup = BeautifulSoup(html, 'html.parser')
        head_list = soup.find_all('p', class_="card-top-avatar__text-SL")
        head_list = [element.get_text().replace('\xa0', ' ') for element in head_list]
        if len(head_list)==0:
            raise Headlines_not_found('На сайте отсутствуют заголовки')
        else:
            return head_list

class RgbString:
    def transformation(self,red,green,blue):
        return "#%02x%02x%02x" % (red, green, blue)

class Create_window(RgbString):
    def __init__(self,url):
        scraper = Modern_WebScraper(url)
        self.head_list = scraper.get_data()

        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=1280, height=720)  
        self.scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
    def run(self):
        i=0
        Color = RgbString.transformation(self,204,229,255)
        for text in self.head_list:
            self.rectangle = self.canvas.create_rectangle(1, 20 + i * 50, 1920, 70 + i * 50, fill=Color, tags=f"rectangle_{i}")
            self.label = self.canvas.create_text(5, 45 + i * 50, text=text, anchor="w")
            i=i+1

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.root.mainloop()

if __name__ == '__main__':
    Create_window('https://dzen.ru/news').run()
