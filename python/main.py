import json
import pprint
import time
import requests
import re
from utils import get_logger, except_output, init_logging

init_logging(log_path="log.txt")

logger = get_logger()

# github的token
github_token = ""
# 项目的api的url
repo_url = "https://api.github.com/repos/fslongjin/This-project-has-N-stars"
regex_pattern = re.compile(r'This-repo-has-(\d+)?-stars')
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "token " + github_token
}


def get_stars():
    """
    获取项目有多少个star
    :return: 项目名称和star数量
    """
    r = requests.get(repo_url, headers=headers)
    r = r.json()
    res = {
        "repo_name": r['full_name'],
        "stars": int(r['watchers']),
    }
    logger.info("Successfully get stars: current stars:{}, current repo name:{}".format(r['watchers'], r['full_name']))
    return res


def update_project_name(data):
    """
    更新项目名称
    :return: None
    """
    current_stars = regex_pattern.findall(data['repo_name'])[0]
    # print(current_stars)
    # print(current_stars.group())
    # current_stars = current_stars.group()
    if int(current_stars) != data['stars']:
        # update
        new_name = "This-repo-has-{}-stars".format(data['stars'])
        new_data = {
            "name": new_name,
            "description": "这个仓库有{}个star，不信你试试".format(data['stars'])
        }
        logger.info("Try to update repo, new Name:{}".format(new_name))
        r = requests.patch(repo_url, headers=headers, data=json.dumps(new_data))
        if r.status_code == 200:
            logger.info("Update successfully, new Name:{}".format(new_name))
        else:
            logger.error("Update failed, response is :\n {}".format(r.text))


@except_output(logger)
def main_loop():
    update_project_name(get_stars())


if __name__ == '__main__':

    while True:
        main_loop()
        time.sleep(3)

