import json
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

project_id = 9158  # 云平台项目ID
authorization = ""  # 云平台Token


def translation_words(words):
    to = "en"
    browser = webdriver.Chrome()
    for word in words:
        path = f"https://www.bing.com/translator?ref=TThis&text={word['original'].replace(' ', '%20')}&from=auto&to={to}"
        browser.get(path)
        time.sleep(5)  # 不确认多少秒，五秒比较保守，短了页面可能出不来
        translation = browser.find_element(By.ID, "tta_output_ta").get_attribute("value")
        word["translation"] = translation
        # TODO 执行更新平台
    browser.close()
    return words


def update_words(words):
    for word in words:
        if word["translation"] == '':
            continue
        url = f"https://paratranz.cn/api/projects/{project_id}/strings/{word['id']}"
        headers = {"Authorization": authorization, "Content-Type": "application/json", "Connection": "close"}
        data = json.dumps({"translation": word["translation"], "stage": 1, "uid": None})
        response = requests.put(url, headers=headers, data=data)
        # TODO 判断响应状态码，200则成功；429则请求过多，获取响应头Retry-After信息并等待相应时长重新执行
        print(f"已更新词条：{word['original']}", response)


if __name__ == '__main__':
    headers = {"Authorization": authorization, "Connection": "close"}
    for page in range(1, 800):
        url = f"https://paratranz.cn/api/projects/{project_id}/strings?stage=0&page={page}&pageSize=800"
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        data = response.json()
        if status_code == 200:
            words = translation_words(data["results"])
            update_words(words)
        if page == data["pageCount"]:
            break
