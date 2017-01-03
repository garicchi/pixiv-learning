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
    return tags

def __get_ranking_illusts(mode:str,date:datetime.date):
    url = "http://www.pixiv.net/ranking.php?mode="+mode+"&date="+date.strftime("%Y%m%d")
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
            "rank":rank,
            "url":url,
            "title":title,
            "creator":creator
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


def __walk_weekly(mode:str,csv:str,start_date:datetime.date,end_date:datetime.date,sleep):
    current_date = start_date
    first = True
    while(current_date < end_date):
        print('mode = %s current_date = %s ' % (mode,str(current_date)))
        current_date = current_date + relativedelta(months=1)
        ranking = __get_ranking_illusts(mode,current_date)
        for item in ranking:
            __write_line_csv(csv,first,item)
            first = False
        print('sleep %d seconds' % sleep)
        time.sleep(sleep)



if __name__ == '__main__':
    sleep = 60*5
    male_csv = "male_ranking.csv"
    female_csv = "female_ranking.csv"
    __walk_weekly("male",male_csv,datetime.date(2014,1,1),datetime.date(2017,1,1),sleep)
    __walk_weekly("female", female_csv, datetime.date(2014, 1, 1), datetime.date(2017, 1, 1),sleep)

    print('job complete!')