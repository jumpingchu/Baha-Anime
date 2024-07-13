import random
import time
from datetime import datetime

import pandas as pd
import pandas_gbq
import requests
import streamlit as st
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials


def get_content_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, features="html.parser")
    return soup


def get_anime_score(soup):
    score = soup.find("div", "score-overall-number").text.strip(";")
    score_count = soup.find("div", "score-overall-people").text
    five_stars_ratio = soup.find("div", "scored-line").get("style").split()[-1]

    # Clean strings
    score_count = score_count.strip("人評價").replace(",", "")
    five_stars_ratio = five_stars_ratio.strip("%;")

    return {
        "score": score,
        "score_count": score_count,
        "five_stars_ratio": five_stars_ratio,
    }


def get_anime_list(url):
    soup = get_content_soup(url)
    anime_in_a_tags = soup.find_all("a", "theme-list-main")
    return anime_in_a_tags


def get_anime_info(anime_a_tag):
    name, yyyymm, episodes = (
        anime_a_tag.find("div", "theme-info-block").text.strip().split("\n\n")
    )
    view_count = anime_a_tag.find("div", "show-view-number").find("p").text

    # Clean strings
    yyyymm = yyyymm.strip("年份：")
    episodes = episodes.strip("共").strip("集")
    if "萬" in view_count:
        view_count = float(view_count.strip("萬")) * 10000  # 2.7萬 -> 27000
    view_count = str(view_count)

    anime_url = f"https://ani.gamer.com.tw/{anime_a_tag.get('href')}"
    return {
        "name": name,
        "yyyymm": yyyymm,
        "episodes": episodes,
        "view_count": view_count,
        "anime_url": anime_url,
    }


def write_dataframe_to_pickle_file(dataframe):
    dataframe.to_pickle("data/anime_info.pkl")
    print("寫入 Pickle 完成!")


def write_dataframe_to_bigquery(dataframe):
    print("正在寫入 BigQuery...")

    # BQ details
    gcp_secrets = st.secrets["gcp"]
    project_id = gcp_secrets["project_id"]
    dataset_id = gcp_secrets["dataset_id"]
    table_name = gcp_secrets["table_name"]
    credentials_path = gcp_secrets["credentials_path"]

    # Authenticate with the service account credentials
    credentials = Credentials.from_service_account_file(credentials_path)

    # Write the DataFrame to BigQuery
    pandas_gbq.to_gbq(
        dataframe,
        f"{dataset_id}.{table_name}",
        project_id=project_id,
        if_exists="append",
        credentials=credentials,
    )
    print("寫入 BigQuery 完成")

def main():
    url_pages = [1, 2]
    all_anime_in_a_tags = []
    for page in url_pages:
        url = f"https://ani.gamer.com.tw/animeList.php?page={page}"
        anime_in_a_tags = get_anime_list(url)
        all_anime_in_a_tags += anime_in_a_tags
        print(f"已取得第 {page} 頁 {len(all_anime_in_a_tags)} 筆動畫資料")
        sleep_seconds = random.randint(2, 3)
        time.sleep(sleep_seconds)

    all_anime_info = []
    for anime_a_tag in all_anime_in_a_tags:
        anime_info = get_anime_info(anime_a_tag)
        anime_soup = get_content_soup(anime_info["anime_url"])
        score_info = get_anime_score(anime_soup)
        anime_info.update(score_info)
        print(anime_info)

        all_anime_info.append(anime_info)
        sleep_seconds = random.randint(1, 2)
        time.sleep(sleep_seconds)

    df = pd.DataFrame(all_anime_info)
    df = df.sort_values(by="score", ascending=False)
    df["created_at"] = datetime.now()

    write_dataframe_to_pickle_file(df)
    write_dataframe_to_bigquery(df)


if __name__ == "__main__":
    main()
