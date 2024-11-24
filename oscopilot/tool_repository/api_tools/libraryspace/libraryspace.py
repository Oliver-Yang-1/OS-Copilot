import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import re
from datetime import datetime
import pandas as pd
from fastapi import APIRouter, HTTPException,UploadFile,File,Form, Depends


def parse_library_space(url="https://lib.hku.hk/js/availabilityFull.div"):

    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # 发送GET请求
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        raw_html = response.content
        # 解码二进制数据
        if isinstance(raw_html, bytes):
            html_text = raw_html.decode('utf-8')
        else:
            html_text = raw_html
        
        # 提取时间
        time_match = re.search(r"<div id='Time'>(.*?)</DIV>", html_text)
        timestamp = datetime.strptime(time_match.group(1), '%Y %b %d %H:%M:%S') if time_match else None
        
        # 使用正则表达式提取所有计数
        pattern = r"<div id='(\w+)_Cnt([ABT])'>(.*?)</DIV>"
        matches = re.findall(pattern, html_text)
        
        # 组织数据
        counts = {}
        for location, count_type, value in matches:
            if location not in counts:
                counts[location] = {'A': 0, 'B': 0, 'T': 0}
            counts[location][count_type] = int(value)
        
        # 转换为DataFrame
        data = []
        for location, values in counts.items():
            data.append({
                'Location': location,
                'Available': values['A'],
                'Occupied': values['B'],
                'Total': values['T']
            })
        
        df = pd.DataFrame(data)
        
        # 添加位置说明
        location_map = {
            'DEN05DR': 'Dental Library Discussion Rooms',
            'EDU08DR': 'Education Library Discussion Rooms',
            'LAW02DR': 'Law Library Discussion Rooms',
            'LAW02ST': 'Law Library Study Space',
            'MAI01AV': 'Main Library (1/F) Audio-Visual',
            'MAI01MS': 'Main Library (1/F) Multimedia Space',
            'MAI01OS': 'Main Library (1/F) Open Space',
            'MAI01ST': 'Main Library (1/F) Study Space',
            'MAI023D': 'Main Library (2/F) 3D Printing',
            'MAI02PC': 'Main Library (2/F) PC Area',
            'MAI02VC': 'Main Library (2/F) Video Conferencing',
            'MAI02CC': 'Main Library (2/F) Collaborative Commons',
            'MAI02SE': 'Main Library (2/F) Special Equipment',
            'MAI02SR': 'Main Library (2/F) Study Room',
            'MAI04SR': 'Main Library (4/F) Study Room',
            'MAI04ST': 'Main Library (4/F) Study Space',
            'MAI03RC': 'Main Library (3/F) Research Commons',
            'MAI03VP': 'Main Library (3/F) Viewing Pod',
            'MAI03PC': 'Main Library (3/F) PC Area',
            'MAI03DR': 'Main Library (3/F) Discussion Room',
            'MAI03ST': 'Main Library (3/F) Study Space',
            'MAI03SU': 'Main Library (3/F) Study Unit',
            'MED00AV': 'Medical Library AV group ',
            'MED00DR': 'Medical Library Discussion Room',
            'MED00SR': 'Medical Library Study Room',
            'MUS11PC': 'Music Library PC Area',
            'MUS11DR': 'Music Library Discussion Room',
            'MUS11ST': 'Music Library Study Space'
        }
        
        # 添加位置说明列
        df['Description'] = df['Location'].map(location_map)
        
        # 重新排序列
        df = df[['Location', 'Description', 'Available', 'Occupied', 'Total']]
        
        # 添加时间戳
        df['Timestamp'] = timestamp
        # 只保留需要的列
        df = df[['Location', 'Description', 'Available', 'Occupied', 'Total']]
        
        # 转换为JSON格式
        json_data = df.to_dict('records')
        
        return json_data
        
    
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return None


def main():
    res=parse_library_space()
    print(res)
    



if __name__ == "__main__":
    main()

