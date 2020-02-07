# 김제민 테스트
from bs4 import BeautifulSoup
import requests
from selenium import webdriver as wd
from selenium.webdriver.common.keys import Keys
import openpyxl
from urllib.request import urlretrieve
import ssl
import time
import re
import pandas as pd

def getPageLinks(pageRange):
    links = []

    for pageNo in range(pageRange):
        url = "https://serieson.naver.com/movie/recentList.nhn?orderType=star_score&sortingType=&tagCode=" + str(pageNo + 1)
#https://series.naver.com/movie/recentList.nhn?orderType=sale&sortingType=&tagCode=&page=
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        movielinks = soup.select('div.lst_thum_wrap ul li a[href]')

        for movielink in movielinks:
            link = str(movielink.get('href'))
            links.append("https://series.naver.com"+link)
    return links

def getPageLinksWantRange(startPageNo, lastPageNo):
    links = []
    return_links = []

    for pageNo in range(startPageNo-1, lastPageNo):
        url = "https://serieson.naver.com/movie/recentList.nhn?orderType=star_score&sortingType=&tagCode=" + str(pageNo + 1)
#https://series.naver.com/movie/recentList.nhn?orderType=sale&sortingType=&tagCode=&page=
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        movielinks = soup.select('div.lst_thum_wrap ul li a[href]')

        for movielink in movielinks:
            link = str(movielink.get('href'))
            links.append("https://series.naver.com"+link)

    return links

def getMovieDataFromNaverSeries(links):
    title_infos = []
    content_infos = []
    genre_infos = []
    score_infos = []
    date_infos = []

    url2 = "https://www.naver.com"

    driver = wd.Chrome(executable_path="chromedriver.exe")
    driver.get(url2)
    time.sleep(3.0) #30

    driver.find_element_by_css_selector('body').send_keys(Keys.CONTROL + "t")

    for link in links:
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(0.1)
        driver.get(link)
        time.sleep(0.1)
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(0.3)

        html_source = driver.page_source

        html_soup = BeautifulSoup(html_source, 'lxml')

        flag - html_soup.text[0:10]

        newflag = "".join(flag)
        newflag = newflag.replace('\n', '')

        if newflag == '네이버':
            time.sleep(1.0)

            score = driver.find_element_by_css_selector('div.score_area > em ')

            score = float(score.text)
            score = int(score)
            score_infos.append(score)

            genre = driver.find_element_by_css_selector('li.info_lst > ul > li:nth-child(4)').get_attribute('textContent')
            genre = genre.replace('장르', '')
            genre = genre.split('/')
            genre_infos.append(genre)

            text = driver.find_element_by_css_selector('span.al_r > a') #.click()
# review_url = text.get_attribute('href')
# review_rul = review_url.replace('basic', 'pintWriteFromList'_
# review_rul = review_url + '&type=after&onlyActualPointYn=N&order=newest&page=1'

            movieInfoUrl = text.get_attribute('href')
            movie_req = requests.get(movieInfoUrl)
            movie_soup = BeautifulSoup(movie_req.text, 'lxml')
            titles = movie_soup.select('div.mv_info > h3.h_movie > a')

            temp_titles = []

            for title in titles:
                temp = title.text
                temp = temp.replace('상영중', '')
                temp = temp.replace('\n', '')
                temp_titles.append(temp)

            if '' in temp_titles or '' in temp_titles:
                temp_titles.remove('')

            temp_titles = set(temp_titles)
            temp_titles = list(temp_titles)
            temp_titles = [x for x in temp_titles if x is not '']
            title_infos.append(list(temp_titles)[0])

            contents_texts = movie_soup.select('div.story_area > p.con_tx')

            if len(contents_texts) == 0:
                content_infos.append("줄거리 오류")
            else:
                for contents in contents_texts:
                    temp = contents.text
                    temp = temp.replace('\r', '')
                    temp = temp.replace('\xa0', '')
                    content_infos.append(temp)


        elif newflag == '네이버 : ':
            adult_moives.append(link)
    print(len(score_infos), len(genre_infos), len(content_infos))
    driver.close()
    movie_dic = {"평점":score_infos, "장르":genre_infos,"줄거리":content_infos}
    movie_df = pd.DataFrame(movie_dic, index=title_infos)
    movie_df2 = movie_df.drop_duplicates("줄거리", keep='first')
    return movie_df2

def dftoCsv(movie_df, num):
    try:
        movie_df.to_csv(('movie_data'+str(num) +'csv'), sep=',', na_rep='NaN', encoding='utf-8')
    except:
        print("Error")