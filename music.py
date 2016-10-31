import requests
import os

global dic
dic = {}
os.chdir("/media/anubhav/OS/music")
headers = {'Host': 'mp3.skull.to',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://mp3.skull.to/',
    'Connection': 'keep-alive'}
url = "https://mp3.skull.to/api/youtube/search?q="
down = "http://serve-skull.su/get?id=" #serve-skull.su/get?id=t2L2Dcoy3N4
#search = input("Please enter name of the song\n")
def so(search):

    page = requests.get(url + str(search))
    s = page.json()
    if s['items']:
        results = s['items']
        j = 0
        arr = []

        for i in results :
            global dic
            dic[j] = i['id']
            arr.append(i['title'])
            print("-->   " + str(j) + "   " + str(arr[j]))
            j += 1

        return arr
def download(choice, name):
    global dic
    while True:
        print(dic)
        d = requests.get(down + dic[int(choice)], stream=True, headers=headers)
        if str(d.url) == down+dic[int(choice)]:
            break
 #   name = input("Ok done\n So what is the name of this baby, eh?\n")

    with open(name + ".mp3", 'wb') as f:
        f.write(d.content)


