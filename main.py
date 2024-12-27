#!/usr/bin/python
# coding:utf-8

from liveMan import DouyinLiveWebFetcher

if __name__ == '__main__':
    live_id = input("请输入直播间ID号: ")
    # live_id = "565075835478"
    DouyinLiveWebFetcher(live_id).start()
