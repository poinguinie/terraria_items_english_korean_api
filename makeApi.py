from bs4 import BeautifulSoup
import requests, json, os, urllib
from tqdm import tqdm

def getHtmlFile(filename, url):
    with requests.get(url) as response:
        if response.status_code != 200:
            print(response.status_code)
            exit(0)

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        with open(filename, 'w', encoding="utf-8") as file:
            file.write(str(soup))

def makeJson(filename, jsonFile):
    localUrl = "http://127.0.0.1:5500/%EC%89%AC%EB%A8%B8/{}".format(filename)

    data = {}

    with requests.get(localUrl) as response:
        if response.status_code != 200:
            print(response.status_code)
            exit(0)

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        boxs = soup.select('div[style="display:inline-block;width:210px;text-align:center;vertical-align:top"]')
        for box in boxs:
            english = box.select('div')[0].text
            korean  = box.select('div')[1].text
            if korean != None and english != None:
                data[english] = korean

        boxs = soup.select('div[class="wiki-paragraph"]')
        for box in boxs:
            korean  = box.select_one('span[class="wiki-size-down-2"]')
            english = box.select_one('span[class="wiki-size-down-3"]')
            if korean != None and english != None:
                english = english.text.replace('(', '').replace(')', '')
                if not english in data:
                    data[english] = korean.text

        with open(jsonFile, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent='\t')

def makeJsonFiles():
    with open('items.txt', 'r', encoding='utf-8') as itemsFile:
        items = itemsFile.readlines()
        for i, item in tqdm(enumerate(items), desc="Json 파일 생성 중..."):
            no = i + 1
            htmlFile = f"html/{no}.html"
            jsonFile = f"json/{no}.json"
            namuUrl = f"https://namu.wiki/w/{urllib.parse.quote(item)}"

            if not os.path.exists(htmlFile):
                getHtmlFile(htmlFile, namuUrl)

            if not os.path.exists(htmlFile):
                print("ERROR")
                exit(0)

            makeJson(htmlFile, jsonFile)

def readJsonFiles():
    _from = dict()

    with open('items.txt', 'r', encoding='utf-8') as itemsFile:
        items = itemsFile.readlines()
        for i, item in enumerate(items):
            no = i + 1
            jsonFile = f"json/{no}.json"
            with open(jsonFile, 'r', encoding='utf-8') as file:
                _from = dict(_from, **json.load(file))
    
    return _from

def compareItems(english, _from):
    korean = list()

    for row in english:
        _to = {'from': row['from'], 'to': row['to']}
        for key, value in row.items():
            if value in _from:
                _to[key] = _from[value]
        korean.append(_to)

    return korean

def makeMapJsonFile(_from):
    with open('items.json', 'w', encoding='utf-8') as file:
        json.dump(_from, file, ensure_ascii=False, indent='\t')

if __name__ == "__main__":
    jsons = os.listdir('json')
    if len(jsons) < 27:
        print("Json 파일들 생성중...")
        makeJsonFiles()

    print("아이템 json 파일 읽는 중...")
    _from = readJsonFiles()

    makeMapJsonFile(_from)