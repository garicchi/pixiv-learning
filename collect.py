import urllib.request
import lxml.html
import datetime
import time
from dateutil.relativedelta import relativedelta

def __get_tags(url):
    with urllib.request.urlopen(url) as res:
        html = res.read().decode("utf-8")

    root = lxml.html.fromstring(html)
    tags_t = root.cssselect('.tag')
    tags = [t.cssselect('.text')[0].text_content() for t in tags_t if t.text_content().count('users入り') == 0]
    #time.sleep(1)
    return tags

def __get_ranking_illusts(mode:str,date:datetime.date):
    date_str = date.strftime("%Y%m%d")
    url = "http://www.pixiv.net/ranking.php?mode="+mode+"&date="+date_str
    with urllib.request.urlopen(url) as res:
        html = res.read().decode("utf-8")

    root = lxml.html.fromstring(html)
    ranking_items = root.cssselect('.ranking-item')
    result_items = []
    for ranking in ranking_items:
        rank = ranking.cssselect('.rank')[0].text_content().rstrip('位')
        url ="http://www.pixiv.net/"+ranking.cssselect('.ranking-image-item')[0].cssselect('a')[0].attrib['href']
        title = ranking.cssselect('.title')[0].text_content()
        creator = ranking.cssselect('.icon-text')[0].text_content()
        tags = __get_tags(url)
        item = {
            "date":date.strftime("%Y-%m-%d"),
            "rank":rank,
            "url":url,
            "title":title,
            "creator":creator,
            "category":mode
        }
        for i in range(10):
            if i < len(tags):
                item["tag"+str(i)] = tags[i]
            else:
                item["tag"+str(i)] = ""

        result_items.append(item)
    return result_items

def __write_line_csv(file:str,first:bool,content:dict):
    mode = 'a'
    if first:
        mode = 'w'

    with open(file,mode) as f:
        if first:
            f.write(",".join(content.keys())+"\n")
        line = ""
        for key in content.keys():
            line = line + content[key]+","
        line = line.rstrip(',')
        f.write(line+"\n")

def __collect(csv:str,start_date:datetime.date,end_date:datetime.date):
    current_date = start_date
    first = True
    start_time = time.time()
    amount = 0
    while(current_date < end_date):
        elapsed = time.time() - start_time
        print('[%d SEC]\tDATE: %s\tAMOUNT: %d' % (elapsed,str(current_date),amount))
        current_date = current_date + relativedelta(months=1)
        ranking_male = __get_ranking_illusts('male',current_date)
        ranking_female = __get_ranking_illusts('female', current_date)
        ranking_male.extend(ranking_female)
        amount += len(ranking_male)

        for item in ranking_male:
            __write_line_csv(csv,first,item)
            first = False

if __name__ == '__main__':
    csv = "pixiv.csv"
    __collect(csv,datetime.date(2014,1,1),datetime.date(2017,1,1))

    print('job complete!')