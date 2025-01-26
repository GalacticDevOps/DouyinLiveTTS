#!/usr/bin/python
# coding:utf-8

# @FileName:    main.py
# @Time:        2024/1/2 22:27
# @Author:      bubu
# @Project:     douyinLiveWebFetcher

from liveMan import DouyinLiveWebFetcher

if __name__ == '__main__':
    # live_id = input("请输入直播间ID号: ")
    # live_id = "26756119119"
    DouyinLiveWebFetcher().start_gui()
