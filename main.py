import json
import time

import requests
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

project_id = 9158  # 云平台项目ID
authorization = ""  # 云平台Token


def translation_words(words):
    to = "en"
    browser = webdriver.Chrome()
    for word in words:
        path = f"https://www.bing.com/translator?ref=TThis&text={word['original'].replace(' ', '%20')}&from=auto&to={to}"
        if len(path) >= 513:
            print(f"词条过长，跳过词条：{path}")
            continue
        browser.get(path)
        for i in range(1, 200):
            try:
                element = browser.find_element(By.ID, "tta_output_ta")
            except NoSuchElementException:
                if i == 199:
                    print(f"跳过词条：{word['original']}")
                    break
                print(f"第{i}次抛出异常，长度：{len(path)}")
                time.sleep(1)
                continue
            else:
                translation = element.get_attribute("value")
                for j in range(1, 200):
                    if translation == " ...":
                        time.sleep(1)
                        translation = browser.find_element(By.ID, "tta_output_ta").get_attribute("value")
                        continue
                    break
                word["translation"] = translation
                update_word(word)
                break
    browser.close()
    return words


def update_word(word):
    if word["translation"] == '':
        return
    url = f"https://paratranz.cn/api/projects/{project_id}/strings/{word['id']}"
    headers = {"Authorization": authorization, "Content-Type": "application/json", "Connection": "close"}
    data = json.dumps({"translation": word["translation"], "stage": 1, "uid": None})
    response = requests.put(url, headers=headers, data=data)
    # TODO 判断响应状态码，200则成功；429则请求过多，获取响应头Retry-After信息并等待相应时长重新执行
    print(f"已更新词条：{word['original']}", response)


def update_words(words):
    for word in words:
        update_word(word)


if __name__ == '__main__':
    headers = {"Authorization": authorization, "Connection": "close"}
    for page in range(1, 800):
        url = f"https://paratranz.cn/api/projects/{project_id}/strings?stage=0&page={page}&pageSize=800"
        response = requests.get(url, headers=headers)
        status_code = response.status_code
        data = response.json()
        if status_code == 200:
            words = translation_words(data["results"])
        if page == data["pageCount"]:
            break
