import time
import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_content_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, features="html.parser")
    return soup


def get_anime_score(soup):
    # title = soup.find("h1").text
    # upload_time = soup.find("p", "uploadtime").text.split("：")[-1]
    # view_count = soup.find("span", "newanime-count").find("span").text
    score = soup.find("div", "score-overall-number").text.strip(";")
    score_count = soup.find("div", "score-overall-people").text
    five_stars_ratio = soup.find("div", "scored-line").get("style").split()[-1]

    # Clean strings
    score_count = score_count.strip("人評價").replace(",", "")
    five_stars_ratio = five_stars_ratio.strip("%;")

    return {
        # "title": title,
        # "upload_time": upload_time,
        # "view_count": view_count,
        "score": score,
        "score_count": score_count,
        "five_stars_ratio": five_stars_ratio,
    }


def get_anime_list(url):
    soup = get_content_soup(url)
    anime_list = soup.find_all("a", "theme-list-main")
    return anime_list


def get_anime_info(anime):
    name, yyyymm, episodes = (
        anime.find("div", "theme-info-block").text.strip().split("\n\n")
    )
    view_count = anime.find("div", "show-view-number").find("p").text

    # Clean strings
    yyyymm = yyyymm.strip("年份：")
    episodes = episodes.strip("共").strip("集")
    view_count = view_count.strip("萬")

    anime_url = f"https://ani.gamer.com.tw/{anime.get('href')}"
    return {
        "name": name,
        "yyyymm": yyyymm,
        "episodes": episodes,
        "view_count": view_count,
        "anime_url": anime_url,
    }


def main():
    url_pages = [1, 2]
    all_anime_list = []
    for page in url_pages:
        url = f"https://ani.gamer.com.tw/animeList.php?page={page}"
        anime_list = get_anime_list(url)
        all_anime_list += anime_list
        time.sleep(2)

    all_anime_info = []
    for anime in all_anime_list:
        anime_info = get_anime_info(anime)
        anime_soup = get_content_soup(anime_info["anime_url"])
        score_info = get_anime_score(anime_soup)
        anime_info.update(score_info)
        print(anime_info)

        all_anime_info.append(anime_info)
        time.sleep(1)

    df = pd.DataFrame(all_anime_info)
    df = df.sort_values(by="score", ascending=False)
    df.to_csv("data/anime_info.csv")


if __name__ == "__main__":
    main()
