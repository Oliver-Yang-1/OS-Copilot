import argparse
import json
import math
import re
import requests


class SubtitleDownload:
    def __init__(self, bvid: str, page, lang, cookie: str):
        self.bvid = bvid
        self.page = page
        self.lang = lang
        self.pagelist_api = "https://api.bilibili.com/x/player/pagelist"
        self.subtitle_api = "https://api.bilibili.com/x/player/v2"
        self.headers = {
            "authority": "api.bilibili.com",
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "origin": "https://www.bilibili.com",
            "referer": "https://www.bilibili.com/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "cookie": cookie,
        }

    def _get_player_list(self):
        response = requests.get(
            self.pagelist_api, params={"bvid": self.bvid}, headers=self.headers
        )
        cid_list = [x["cid"] for x in response.json()["data"]]
        return cid_list

    def _get_subtitle_list(self, cid: str):
        params = (
            ("bvid", self.bvid),
            ("cid", cid),
        )
        response = requests.get(self.subtitle_api, params=params, headers=self.headers)
        subtitles = response.json()["data"]["subtitle"]["subtitles"]
        if subtitles:
            n = 1
            print("当前字幕列表：")
            for x in subtitles:
                print(str(n) + "." + x["lan_doc"])
                n = n + 1
            if self.lang <= 0 or self.lang > n - 1:
                m = int(input("请输入下载的字幕序号："))
                while m <= 0 or m > n - 1:
                    m = int(input("选择字幕序号超出范围，请重新输入："))
            else:
                m = self.lang
            return ["https:" + subtitles[m - 1]["subtitle_url"]]
        else:
            print("获取字幕列表失败，当前没有可下载的字幕，或检查cookie是否正确")
            return None
        return []

    def _get_subtitle(self, cid: str):
        subtitles = self._get_subtitle_list(cid)
        if subtitles:
            return self._request_subtitle(subtitles[0])

    def _request_subtitle(self, url: str):
        response = requests.get(url)
        if response.status_code == 200:
            body = response.json()["body"]
            return body

    def _get_pagelist(self):
        response = requests.get(
            self.pagelist_api, params={"bvid": self.bvid}, headers=self.headers
        )
        print(response.json())
        pagelist = len(response.json()["data"])
        print(f"当前视频共有分集：{pagelist}")
        if self.page <= 0 or self.page > pagelist:
            page = int(input("请选择集数：")) - 1
            while page < 0 or page > pagelist:
                page = int(input("选择集数超出范围，请重新输入：")) - 1
        else:
            page = self.page - 1
        return page

    def download_subtitle(self):
        page = self._get_pagelist()
        print(self._get_player_list())
        subtitle_list = self._get_subtitle(self._get_player_list()[page])
        if subtitle_list:
            srt = ""
            for x in subtitle_list:
                content = ""
                # 获取纯文本内容
                content += x["content"] + "\n"
                # 获取srt格式内容
                startTime = x["from"]
                stopTime = x["to"]
                sid = x.get("sid", "unknown_sid")
                sid = x["sid"]
                srt += "{}\n".format(sid)
                hour = math.floor(startTime) // 3600
                minute = (math.floor(startTime) - hour * 3600) // 60
                sec = math.floor(startTime) - hour * 3600 - minute * 60
                minisec = int(math.modf(startTime)[0] * 1000)  # 处理开始时间
                srt += (
                    str(hour).zfill(2)
                    + ":"
                    + str(minute).zfill(2)
                    + ":"
                    + str(sec).zfill(2)
                    + ","
                    + str(minisec).zfill(3)
                )  # 将数字填充0并按照格式写入
                srt += " --> "
                hour = math.floor(stopTime) // 3600
                minute = (math.floor(stopTime) - hour * 3600) // 60
                sec = math.floor(stopTime) - hour * 3600 - minute * 60
                minisec = int(math.modf(stopTime)[0] * 1000)
                srt += (
                    str(hour).zfill(2)
                    + ":"
                    + str(minute).zfill(2)
                    + ":"
                    + str(sec).zfill(2)
                    + ","
                    + str(minisec).zfill(3)
                )
                srt += "\n" + x["content"] + "\n\n"  # 加入字幕文字

            print("字幕获取成功\n")

            # 保存字幕到文件
            with open("subtitle.srt", "w", encoding="utf-8") as file:
                file.write(srt)

            print("字幕已保存到subtitle.srt文件中。")
            return srt  # 可以选择返回srt格式字幕或纯文本字幕
        else:
            text = "该视频没有可供下载的字幕"
            return text


class SubtitleDownloadError(Exception):
    pass


def parse_bvid_from_url(url: str):
    """从Bilibili视频URL中解析出BVID"""
    pattern = r"BV(\w+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("无法从URL中解析出BVID")


def main():
    parser = argparse.ArgumentParser(description="Download subtitles from Bilibili")
    parser.add_argument("url", type=str, help="Bilibili video URL")
    parser.add_argument(
        "--cookie",
        type=str,
        required=True,
        help="User cookie for authentication, required to download subtitles",
    )
    parser.add_argument(
        "--lang", type=int, default=1, help="Language code for subtitles (default: 1)"
    )
    parser.add_argument(
        "--page", type=int, default=1, help="The page (集数) to download subtitles from"
    )

    args = parser.parse_args()

    try:
        # 解析命令行传递的参数
        bvid = parse_bvid_from_url(args.url)
        downloader = SubtitleDownload(bvid, args.page, args.lang, args.cookie)
        subtitles = downloader.download_subtitle()
        print(subtitles)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
