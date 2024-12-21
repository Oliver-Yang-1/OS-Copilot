import argparse
import yt_dlp
from collections import Counter


class YouTubeDownloader:
    def __init__(self, url: str):
        self.url = url
        self.ydl_opts_video = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",  # 确保视频和音频为 MP4 格式
            "merge_output_format": "mp4",  # 合并后的文件格式为 MP4
            "outtmpl": "%(title)s.%(ext)s",  # 视频文件命名：以视频标题命名
        }
        self.ydl_opts_subtitle = {
            "writesubtitles": True,  # 下载手动上传的字幕
            "writeautomaticsub": True,  # 下载自动生成的字幕
            "subtitleslangs": ["en", "zh-Hans"],  # 优先下载英文和简体中文字幕
            "skip_download": True,  # 只下载字幕，不下载视频
            "outtmpl": "%(title)s.%(ext)s",  # 字幕文件命名：以视频标题命名
        }
        self.subtitle_file = None  # 字幕文件路径
        self.video_title = None  # 视频标题

    def download_video(self):
        """下载视频"""
        print(f"开始下载视频：{self.url}")
        with yt_dlp.YoutubeDL(self.ydl_opts_video) as ydl:
            info_dict = ydl.extract_info(self.url, download=True)
            self.video_title = info_dict.get("title", "video")
        print(f"✅ 视频下载完成：{self.video_title}.mp4")

    def download_subtitle(self):
        """下载字幕"""
        print(f"开始下载 {self.url} 的字幕...")
        with yt_dlp.YoutubeDL(self.ydl_opts_subtitle) as ydl:
            info_dict = ydl.extract_info(self.url, download=True)
            self.video_title = info_dict.get("title", "video")
            subtitles = info_dict.get("requested_subtitles")

            if not subtitles:
                print("❌ 此视频没有可用字幕。")
                return None

            # 获取字幕文件路径
            self.subtitle_file = (
                f"{self.video_title}.en.vtt"
                if "en" in subtitles
                else f"{self.video_title}.zh-Hans.vtt"
            )
            print(f"✅ 字幕下载完成，文件名为：{self.subtitle_file}")
            return self.subtitle_file

    def convert_vtt_to_srt(self):
        """将 VTT 格式字幕转换为 SRT 格式"""
        if not self.subtitle_file or not self.subtitle_file.endswith(".vtt"):
            print("❌ 未找到 VTT 字幕，无法进行转换。")
            return None

        srt_file = self.subtitle_file.replace(".vtt", ".srt")

        try:
            with open(self.subtitle_file, "r", encoding="utf-8") as vtt_file, open(
                srt_file, "w", encoding="utf-8"
            ) as srt_output:
                lines = vtt_file.readlines()
                counter = 1
                for line in lines:
                    # 跳过无意义的行
                    if line.strip() == "" or line.startswith("WEBVTT"):
                        continue
                    if "-->" in line:
                        srt_output.write(f"{counter}\n")
                        counter += 1
                    srt_output.write(line)

            print(f"✅ 字幕已成功转换为 SRT 格式，文件名为：{srt_file}")
            self.subtitle_file = srt_file  # 更新为 SRT 文件路径
            return srt_file
        except Exception as e:
            print(f"❌ 字幕转换失败：{e}")
            return None

    def summarize_subtitle(self):
        """生成字幕摘要"""
        if not self.subtitle_file or not self.subtitle_file.endswith(".srt"):
            print("❌ 未找到 SRT 字幕，无法生成摘要。")
            return None

        try:
            with open(self.subtitle_file, "r", encoding="utf-8") as srt_file:
                content = srt_file.readlines()

            # 提取字幕内容
            subtitle_lines = [
                line.strip()
                for line in content
                if not line.strip().isdigit() and "-->" not in line
            ]
            full_text = " ".join(subtitle_lines)

            # 简单关键词统计
            words = full_text.split()
            word_counts = Counter(words)
            most_common = word_counts.most_common(10)

            # 打印关键词
            print("\n🔑 字幕关键词统计：")
            for word, count in most_common:
                print(f"{word}: {count} 次")

            # 简单生成摘要
            summary = self._simple_summary(subtitle_lines)
            print("\n📝 字幕摘要：")
            print(summary)

            return summary
        except Exception as e:
            print(f"❌ 生成字幕摘要失败：{e}")
            return None

    @staticmethod
    def _simple_summary(lines):
        """简单的字幕内容摘要方法"""
        if len(lines) <= 10:
            return " ".join(lines)  # 如果字幕行数少于 10 行，直接返回全文
        else:
            return (
                " ".join(lines[:5]) + " ... " + " ".join(lines[-5:])
            )  # 返回开头和结尾部分


def main():
    parser = argparse.ArgumentParser(description="下载 YouTube 视频及字幕")
    parser.add_argument("url", type=str, help="YouTube 视频 URL")
    parser.add_argument("--video", action="store_true", help="下载视频")
    parser.add_argument("--subtitle", action="store_true", help="下载字幕")
    args = parser.parse_args()

    # 初始化下载器
    downloader = YouTubeDownloader(args.url)

    # 下载视频
    if args.video:
        downloader.download_video()

    # 下载字幕
    if args.subtitle:
        subtitle_file = downloader.download_subtitle()
        # if subtitle_file:
        #     # 转换字幕为 SRT 格式
        #     downloader.convert_vtt_to_srt()


if __name__ == "__main__":
    main()
