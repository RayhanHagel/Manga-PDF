import requests                         # Scrape Website
from bs4 import BeautifulSoup as bts    # Parse The Data
import urllib.parse                     # To Encode URL
import time                             # To Sleep
import os                               # Create Folder
from PIL import Image                   # PDF Document


class Manga():
    def __init__(self):
        self.mangkakalot = "https://ww4.mangakakalot.tv/"
        self.parsed = {}
        self.parsed2 = {}
        self.title = None
        self.path = 'C:/Users/Admin/Desktop/Python/Mangakakalot/Download/'
        
        
    def search(self, keyword):
        # Get Keyword
        keyword = urllib.parse.quote(keyword)
        path_mangakakalot = self.mangkakalot + 'search/' + keyword
        
        # Search Mangakakalot for results
        search_page = requests.get(path_mangakakalot)
        parsed_search_page = bts(search_page.text, "html.parser")
        
        # Process Results
        link_result = parsed_search_page.find_all('div', class_="story_item_right")
        for panel in link_result:
            auv = panel.find_all('span')
            
            # Get Contents
            title = panel.h3.a.text
            link = self.mangkakalot + panel.h3.a['href']
            author = auv[0].get_text(strip=True).split(':')[1]
            author = ' ' + ' '.join(author.split())
            updated = auv[1].get_text(strip=True).split(':')[1].split(' -')[0].replace(',',', ')
            view = auv[2].get_text(strip=True).split(':')[1]
            
            # Append To Dictionary
            self.parsed[title] = {'link': link, 'author': author, 'updated': updated, 'view': view }


    def show(self):
        print("================================================")
        for index, key in enumerate(self.parsed):
            print(key)
            print('    • Index    :', index)
            print('    • Author   :' + self.parsed[key]['author'])
            print('    • Updated  :' + self.parsed[key]['updated'])
            print('    • View     :' + self.parsed[key]['view'])
            # time.sleep(.8)
            print("================================================")
        
        
    def get_index(self):
        try: 
            index = input("Which manga do you want to scrape?\nInsert Index: ")
            index = int(index)
        except:
            while type(index) != 'int':
                try:
                    index = int(input("\nError occured: Please insert integer\nInsert Index: "))
                    break
                except: pass
                
        # Iterate Dictionary to get Title
        for ind, title in enumerate(self.parsed):
            if ind == index: self.title = title
            
                
    def search_result(self):
        # Scrape Page
        manga_link = self.parsed[self.title]['link']
        manga_page = requests.get(manga_link)
        
        # Parse the scraped page
        page_parsed = bts(manga_page.text, "lxml")
        page_parsed = page_parsed.find('div', class_='chapter-list')
        page_parsed = page_parsed.find_all('div', class_='row')
        
        # Show Amount of Chapter
        print("================================================")
        amount_of_chapter = page_parsed[0].span.a.get_text(strip=True).replace(':', '').replace('-', '').split(' ')
        for i in amount_of_chapter:
            try: 
                amount_of_chapter = float(i)
                break
            except: 
                pass
        print(f"There are {int(amount_of_chapter)} chapters")
        self.page_parsed = page_parsed
        
        
    def range_chapter(self):
        get_input, range_chapter = None, None
        while True:
            try:
                get_input = input("Insert range of chapter to scrape: ").replace(' ', '', 10).split('-')
                if len(get_input) == 1:
                    range_chapter = [int(get_input[0]), int(get_input[0])]
                elif len(get_input) == 2:
                    if int(get_input[1]) > int(get_input[0]):
                        range_chapter = [int(get_input[0]), int(get_input[1])]
                    else:
                        range_chapter = [int(get_input[1]), int(get_input[0])]
                break
            except:
                print("\nError occured: Please insert integer\ne.g 123-245")
            print("================================================")
        self.range_chapter = range_chapter

    def get_chapter(self):      
        # Get Chapter from Range
        for chapter in self.page_parsed:
            check = float(chapter.span.a['href'].split('-')[-1:][0])
            if check <= self.range_chapter[1] and check >= self.range_chapter[0]:
                print("================================================")
                
                # Chapter Name
                chapter_name = chapter.span.get_text(strip=True)
                for to_remove in [':', '*', '?', '<', '>', '|']:
                    chapter_name = chapter_name.replace(to_remove, '')
                    self.title = self.title.replace(to_remove, '')
                print(f"■ {chapter_name}")
                    
                # Create Folder
                path = f"{self.path}{self.title}/"
                path2 = f"{path}{chapter_name}/"
                if os.path.exists(path) != True:  os.mkdir(path, 0o666)
                if os.path.exists(path2) != True: os.mkdir(path2, 0o666)
                
                # Get Chapter
                chapter_link = self.mangkakalot + chapter.span.a['href'][1:]
                page_chapter = requests.get(chapter_link)
                parsed_page_chapter = bts(page_chapter.text, 'lxml')
                image_link = parsed_page_chapter.find_all('img', class_='img-loading')

                # Image Process
                for image in image_link:
                    image_name = image['alt']
                    for to_remove in [':', '*', '?', '<', '>', '|']:
                        image_name = image_name.replace(to_remove, '')
                    
                    print(f"    • {image_name}")
                    image_data = requests.get(image['data-src']).content
                    image_name = path2 + image_name + '.jpg'
                    with open(image_name, 'wb') as handler:
                        handler.write(image_data)
                
                # Create PDF
                image_list, images = os.listdir(path2), []
                for f in image_list:
                    images.append(Image.open(path2 + f))
                PDF_Name = path + chapter_name[:-1] + '.pdf'
                images[0].save(PDF_Name, "PDF", resolution=100, save_all=True, append_images=images[1:])
                print(f"    • Image combined into PDF file")      
                
            elif float(check) < self.range_chapter[0]:
                break
            



    def main(self, keyword):
        print("Searching results...")
        self.search(keyword)
        self.show()
        self.get_index()
        self.search_result()
        self.range_chapter()
        self.get_chapter()

               
Program = Manga()
Program.main(input("Manga to search: "))
