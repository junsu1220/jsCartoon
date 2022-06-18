from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@cluster0.6bd2d.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

# URL을 읽어서 HTML를 받아오고,
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://series.naver.com/v2/comic/top100List.series',headers=headers)

# HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
soup = BeautifulSoup(data.text, 'html.parser')
cartoons = soup.select('#__next > div > main > article > div.ComicTop100ListPage_container__veuV_ > section > div > ul > li')

cnt = 0
title_group = []
sub_title_group = []
image_group = []

for cartoon in cartoons:
    cnt+=1
    if(cnt>3): break;
    title = cartoon.select_one('div.RankedProductItem_detail__B9iwD > h3 > a').text
    sub_title = cartoon.select_one('div.RankedProductItem_detail__B9iwD > div > div').text
    image = cartoon.select_one('div.Poster_root__ny_RJ > div > span > img')['src']

    title_group.append(title)
    sub_title_group.append(sub_title)
    image_group.append(image)

@app.route('/')
def home():
  cartoons_main = list(db.cartoons.find({},{'_id':False}))[::-1]
  return render_template('index.html', cartoons_main=cartoons_main)

@app.route("/cartoon", methods=["POST"])
def cartoon_post():
    url_receive = request.form['url_give']
    num_receive = request.form['num_give']
    data2 = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data2.text, 'html.parser')
    card_image = soup.select_one('meta[property="og:image"]')['content']
    card_title = soup.select_one('#content > div.end_head > h2').text
    card_sub_title = soup.select_one('#content > div.end_dsc > div:nth-child(1)').text

    doc = {
        'c_number':num_receive,
        'c_image':card_image,
        'c_title':card_title,
        'c_sub_title':card_sub_title
    }

    db.cartoons.insert_one(doc)
    card_list =  list(db.cartoons.find({},{'_id':False}))
    return jsonify({'cartoons_post':card_list})

@app.route("/cartoon_delete", methods=["POST"])
def cartoon_delete():
    delete_receive = request.form['delete_give']
    db.cartoons.delete_one({'c_number': delete_receive})

@app.route("/cartoon", methods=["GET"])
def cartoon_get():
    title_list = title_group
    sub_title_list = sub_title_group
    image_list = image_group
    return jsonify({'titles':title_list,
                    'sub_titles':sub_title_list,
                    'images':image_list})

if __name__ == '__main__':
  app.run('0.0.0.0', port=5000, debug=True)