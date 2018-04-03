#!usr/bin/python2.7
# -*- coding=utf-8 -*-

import requests
import datetime
import json
import os
from enum import Enum
from requests.adapters import HTTPAdapter
import multiprocessing
from multiprocessing import Process
import ConfigParser
import math
import random


class Period(Enum):
    ALL = 0
    MIN1 = 1
    MIN5 = 2
    MIN15 = 3
    MIN30 = 4
    MIN60 = 5
    DAY = 6
    WEEK = 7
    MONTH = 8
    YEAR = 9


PERIOD_MAP = {0: Period.ALL, 1: Period.MIN1, 2: Period.MIN5, 3: Period.MIN15, 4: Period.MIN30, 5: Period.MIN60,
              6: Period.DAY, 7: Period.WEEK, 8: Period.MONTH, 9: Period.YEAR}
KLINE_TYPE = {Period.ALL: "ALL", Period.MIN1: "MIN1", Period.MIN5: "MIN5", Period.MIN15: "MIN15", Period.MIN30: "MIN30",
              Period.MIN60: "MIN60", Period.DAY: "DAY", Period.WEEK: "WEEK", Period.MONTH: "MONTH", Period.YEAR: "YEAR"}
LWORK_TYPE = {Period.MIN1: "m1", Period.MIN5: "m5", Period.MIN15: "m15", Period.MIN30: "m30",
              Period.MIN60: "h1", Period.DAY: "d1", Period.WEEK: "w1", Period.MONTH: "mn1"}
TIME_MINUTES_DELTA = {Period.MIN1: 1, Period.MIN5: 5, Period.MIN15: 15, Period.MIN30: 30, Period.MIN60: 60,
                      Period.DAY: 60 * 24, Period.WEEK: 60 * 24 * 7}


# date="20171201", delta=-1
# return "20171130"
def dayDelta(date, delta):
    if len(date) != 8:
        raise Exception("dayDelta date Error", date)
    timeFormat = "%Y%m%d"
    t = datetime.datetime.strptime(date, timeFormat)
    newDate = t + datetime.timedelta(days=delta)
    return newDate.strftime(timeFormat)


# date_time="201712010000", delta=-1
# return "201711302359"
def minDelta(date_time, delta):
    if len(date_time) != 12:
        print("minDelta date_time Error " + date_time)
        return ""
    timeFormat = "%Y%m%d%H%M"
    t = datetime.datetime.strptime(date_time, timeFormat)
    newDate_time = t + datetime.timedelta(minutes=delta)
    return newDate_time.strftime(timeFormat)


def getMaxDay(YYYYMM):
    if len(YYYYMM) != 6:
        print("getMaxDay input Error " + YYYYMM)
        return 0
    max_day = 31
    while True:
        try:
            datetime.datetime.strptime("%s%d" % (YYYYMM, max_day), "%Y%m%d")
            return max_day
        except:
            max_day -= 1
            if (max_day < 28):
                print("getMaxDay input Error " + YYYYMM)
                return 0


class Kline:
    ZERO_LIST = ["0", "0", "0", "0", "0", "0"]

    def __init__(self, type):
        self.open = "0.0"
        self.high = "0.0"
        self.low = "0.0"
        self.close = "0.0"
        self.preclose = "0.0"
        self.date = 0
        self.time = 0
        self.type = type
        self.trade_date = 0

    def load(self, one_json):
        self.open = str(one_json["open"])
        self.high = str(one_json["high"])
        self.low = str(one_json["low"])
        self.close = str(one_json["close"])
        self.utc_time = one_json["time"]
        # 转换为东八区时间
        if self.type not in [Period.WEEK, Period.MONTH]:
            utc8_time = minDelta(self.utc_time, 60 * 8)
            self.date = int(utc8_time[0:8])
            self.time = int(utc8_time[8:])
            # 8点之后交易日才是自然日
            if self.time <= 800:
                self.trade_date = int(dayDelta(str(self.date), -1))
            else:
                self.trade_date = self.date
            if self.type == Period.DAY:  # 日线时间填0
                self.time = 0
                self.trade_date = self.date
        else:  # 周线、月线自然日和交易日填同一个值，其中周线填周末的日期，月线填月末的日期
            self.date = int(self.utc_time[0:8])
            if self.type == Period.MONTH:  # Lwork的月K线time是201712000000，我们需要的是201712310000
                self.date += getMaxDay(str(self.date)[0:6])
            self.time = int(self.utc_time[8:])
            self.trade_date = self.date

    # 补线时使用
    def newLine(self, date, time, price):
        self.date = date
        self.time = time
        self.open = price
        self.high = price
        self.low = price
        self.close = price
        self.preclose = price
        self.utc8_time = "%d%04d" % (date, time)
        # 8点之后交易日才是自然日
        if self.time <= 800 and self.type != Period.DAY:
            self.trade_date = int(dayDelta(str(self.date), -1))
        else:
            self.trade_date = self.date

    # 检测开高低收价格里是否有为0的值
    def noZeroValue(self):
        if self.open == "0" or self.high == "0" or self.low == "0" or self.close == "0":
            return False
        return True

    def format(self):
        line = ",".join([str(self.date), str(self.trade_date), str(self.time), self.open, self.high, self.low,
                         self.close] + self.ZERO_LIST + [self.preclose])
        return line


# code="USDJPY", type=1, start_date="20171201", end_date="20171204"
class ShortKlineDownload(object):
    '''分钟、日、周、月K线下载类'''
    BARS = 199
    TITLE = "date,trade_date,time,open,high,low,close,volume," \
            "turnover,average,position,settlement,turnover_ratio,prev_close\n"

    def __init__(self, code, type, start_date, end_date, auth_dict):
        self.auth_dict = auth_dict
        self.start_date = start_date + "0000"
        now = datetime.datetime.now()
        # lwork请求历史数据时若时间大于当前时间无返回
        if int(end_date) > int(now.strftime("%Y%m%d")):
            self.end_date = now.strftime("%Y%m%d") + "0000"
        else:
            self.end_date = end_date + "0000"
        if int(self.start_date) > int(self.end_date):
            print("start_date Error " + start_date)
            raise Exception("Invalid start_date", start_date)
        self.kline_type = type
        self.code = code
        # run之后按时间反序存储Kline对象
        self.kline_list = []
        self.req_session = requests.Session()
        self.req_session.mount("https://", HTTPAdapter(max_retries=16))

    # 进行K线下载处理
    def run(self):
        content = self.__requestKline(self.end_date, self.kline_type, self.code)
        ignoreFirst = False
        try:
            oldest_time, ignoreFirst = self.__contentParse(content, ignoreFirst, self.end_date)
            if (self.kline_type not in [Period.WEEK, Period.MONTH, Period.YEAR] and self.kline_list[0].utc_time != self.end_date):
                json_dict = {}
                json_dict["open"] = self.kline_list[0].close
                json_dict["high"] = self.kline_list[0].close
                json_dict["low"] = self.kline_list[0].close
                json_dict["close"] = self.kline_list[0].close
                json_dict["time"] = self.end_date
                line = Kline(self.kline_type)
                line.load(json_dict)
                self.kline_list.insert(0, line)
            while (len(oldest_time) > 0 and int(oldest_time) > int(self.start_date)):
                content = self.__requestKline(oldest_time, self.kline_type, self.code)
                oldest_time, ignoreFirst = self.__contentParse(content, ignoreFirst, oldest_time)
                if len(self.kline_list) > 5000:
                    self.write2File()
                    self.kline_list = []
        except Exception, Argument:
            print (Argument)

    # 写入文件
    def write2File(self):
        if len(self.kline_list) == 0:
            return
        self.__fillPreClose()
        # ./LWORK/MIN1  存放下载下来的K线的目录
        dir_path = os.path.sep.join([".", "LWORK", KLINE_TYPE[self.kline_type]])
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # USDJPY.min1.csv
        csv_file_name = ".".join([self.code, KLINE_TYPE[self.kline_type].lower(), "csv"])
        file_path = dir_path + os.path.sep + csv_file_name
        writeTitle = False
        if not os.path.exists(file_path):
            writeTitle = True
        f = open(file_path, "a")
        if writeTitle:
            f.write(self.TITLE)
        # 周线，月线无需补线
        if self.kline_type in [Period.WEEK, Period.MONTH, Period.YEAR]:
            for item in self.kline_list:
                _continue = self.__myselfWrite(f, item)
                if _continue == False:
                    break
        else:
            _continue = self.__myselfWrite(f, self.kline_list[0])
            if _continue:
                expect_date, expect_time = self.__expectTime(self.kline_list[0])
                try:
                    for item in self.kline_list[1:]:
                        close = item.close
                        # 下一根K线的时间不是预期的时间，则使用上一根K线的close去补线
                        while expect_date != item.date or expect_time != item.time:
                            line = Kline(self.kline_type)
                            line.newLine(expect_date, expect_time, close)
                            _continue = self.__myselfWrite(f, line)
                            if _continue == False:
                                f.close()
                                return
                            expect_date, expect_time = self.__expectTime(line)
                        _continue = self.__myselfWrite(f, item)
                        if _continue == False:
                            f.close()
                            return
                        expect_date, expect_time = self.__expectTime(item)
                except IndexError:
                    pass
        f.close()

    def __requestKline(self, end_time, type, symbol):
        url = "https://feed.api.lwork.com/v1/history/bar"
        payload = {"bars": self.BARS,
                   "symbol": symbol,
                   "period": LWORK_TYPE[type],
                   "type": "2",  # mid价格
                   "endtime": end_time}
        headers = {"x-api-tenantId": self.auth_dict["tenantId"],
                   "x-api-token": self.auth_dict["token"]}
        try:
            r = self.req_session.get(url, params=payload, headers=headers)
        except requests.exceptions.SSLError:
            print("Error " + r.url)
            return ""
        else:
            # print(r.url)
            return r.text

    # 返回最久远那根K线的时间(UTC)，解析出来的K线放入self.kline_list
    def __contentParse(self, text, ignore_first, end_time):
        json_info = json.loads(text)
        if json_info["msg"] != "ok":
            raise Exception("__contentParse Error", text + self.code)
        # 最久远那根K线的时间
        oldestTime = ""
        for item in json_info["data"]:
            # 跳过第一根K线，循环调用时endtime那根K线会重复
            if ignore_first:
                ignore_first = False
                continue
            line = Kline(self.kline_type)
            line.load(item)
            oldestTime = line.utc_time
            self.kline_list.append(line)
        # 返回的K线数量小于请求的数量 -> 已经没有更早的K线  (对于分钟K线，可能会有这种情况，需要将请求end_time往前推)
        if len(json_info["data"]) < self.BARS:
            '''当查询m1的bar且没有数据返回时，表示近期没有可用的bar，可往前推8小时再查询'''
            if self.kline_type == Period.MIN1:
                # 实测直接往前推一天就能接着查到了
                if len(oldestTime) == 0:
                    oldestTime = end_time
                YYYYMMDDHHMM = dayDelta(oldestTime[0:8], -1) + "0000"
                return YYYYMMDDHHMM, False
            else:
                return "", False
        else:
            return oldestTime, True

    # 用前一根K线的close生成下一根K线的preclose
    def __fillPreClose(self):
        for i in range(0, len(self.kline_list)):
            try:
                self.kline_list[i].preclose = self.kline_list[i + 1].close
            except IndexError:  # 最早一根K线的preclose用open来填充
                self.kline_list[i].preclose = self.kline_list[i].open

    # 返回理论上下一根K线的date和time
    def __expectTime(self, kline_obj):
        YYYYHHMMhhmm = str(kline_obj.date) + "%04d" % kline_obj.time
        expect_time = minDelta(YYYYHHMMhhmm, -TIME_MINUTES_DELTA[kline_obj.type])
        date = int(expect_time[0:8])
        time = int(expect_time[8:])
        return date, time

    # 判断这根K线的时间是否在下载范围内  长周期K线一次请求199根，可能范围就超了
    def __isNeedWrite(self, kline):
        start_time = 0
        kline_time = 0
        if self.kline_type not in [Period.MONTH, Period.YEAR]:
            start_time = int(self.start_date[0:8])  # YYYYMMDD
            kline_time = int(str(kline.trade_date)[0:8])
        elif self.kline_type == Period.MONTH:  # YYYYMM
            start_time = int(self.start_date[0:6])
            kline_time = int(str(kline.trade_date)[0:6])
        elif self.kline_type == Period.YEAR:  # YYYY
            start_time = int(self.start_date[0:4])
            kline_time = int(str(kline.trade_date)[0:4])
        else:
            raise Exception("Invalid kline_type", self.kline_type)
        # K线的时间已经早于需要下载的时间段
        if kline_time < start_time:
            return False
        return True

    def __myselfWrite(self, f, kline):
        if self.__isNeedWrite(kline):
            if kline.noZeroValue():
                f.write(kline.format() + "\n")
            return True
        return False


# lean_work无年K线，需要从月K线合成
class YearShortKlineDownload(ShortKlineDownload):
    '''年K线下载类'''

    def __init__(self, code, start_date, end_date, auth_dict):
        super(YearShortKlineDownload, self).__init__(code, Period.MONTH, start_date, end_date, auth_dict)
        # 起始日期修改为那一年的1月1日
        self.start_date = self.start_date[0:4] + "01010000"
        start_year = int(self.start_date[0:4])
        end_year = int(self.end_date[0:4])
        self.year_list = []
        # 解析出需要获取哪几年的年K线
        for i in range(start_year, end_year + 1):
            self.year_list.append(i)

    def run(self):
        super(YearShortKlineDownload, self).run()
        same_year_kline = {}
        for item in self.kline_list:
            year = item.date / 10000
            if year in self.year_list:
                try:
                    same_year_kline[year].append(item)
                except:
                    same_year_kline[year] = []
                    same_year_kline[year].append(item)
        self.kline_list = []
        # kline list是反序的
        for key in same_year_kline.keys():
            open = same_year_kline[key][-1].open  # 年open取第一根月K线的open
            close = same_year_kline[key][0].close  # 年close取最后一个月K线的close
            high = 0.0
            low = float("inf")
            for line in same_year_kline[key]:
                if float(line.high) > high:
                    high = float(line.high)
                if float(line.low) != 0.0 and float(line.low) < low:
                    low = float(line.low)
            year_kline = Kline(Period.YEAR)
            year_kline.open = open
            year_kline.high = str(high)
            year_kline.low = str(low)
            year_kline.close = close
            year_kline.date = int("%d1231" % key)
            year_kline.trade_date = year_kline.date
            year_kline.time = 0
            self.kline_list.append(year_kline)
        self.kline_list.reverse()

    def write2File(self):
        self.kline_type = Period.YEAR
        super(YearShortKlineDownload, self).write2File()


class KlineDownLoad(object):
    '''按交易日下载K线，范围[start_date, end_date)  左闭右开'''

    def __init__(self, code, type, start_date, end_date, auth_dict):
        self.start_date = start_date
        self.end_date = end_date
        self.code = code
        self.type = type
        self.auth_dict = auth_dict
        if type == Period.YEAR:
            self.download = YearShortKlineDownload(code, start_date, end_date, self.auth_dict)
        elif type != Period.ALL:
            self.download = ShortKlineDownload(code, type, start_date, end_date, self.auth_dict)

    def autoRun(self):
        if self.type == Period.ALL:
            for type in [Period.MIN1, Period.MIN5, Period.MIN15, Period.MIN30,
                         Period.MIN60, Period.DAY, Period.WEEK, Period.MONTH]:
                self.download = ShortKlineDownload(self.code, type, self.start_date, self.end_date, self.auth_dict)
                self.__run()
            self.download = YearShortKlineDownload(self.code, self.start_date, self.end_date, self.auth_dict)
            self.__run()
        else:
            self.__run()

    def __run(self):
        self.download.run()
        self.download.write2File()


class DownloadProcess(Process):
    def __init__(self, code_list, type, start_date, end_date, auth_dict):
        super(DownloadProcess, self).__init__()
        self.kline_download = []
        for code in code_list:
            self.kline_download.append(KlineDownLoad(code, type, start_date, end_date, auth_dict))

    def run(self):
        for item in self.kline_download:
            print("##start download[%s]" % item.code)
            item.autoRun()
            print("@@[%s]download over" % item.code)


def chunks(arr, m):
    n = int(math.ceil(len(arr) / float(m)))
    return [arr[i:i + n] for i in range(0, len(arr), n)]


def main():
    if os.path.exists("LWORK"):
        print("exist LWORK dir")
        return
    auth_dict = {}
    cp = ConfigParser.SafeConfigParser()
    with open("kline.conf", "r") as f:
        cp.readfp(f)
    all_code_str = cp.get("symbol", "code")
    thread_num = cp.get("thread", "thread_num")
    if int(thread_num) < 1:
        thread_num = 1
    kline_type = PERIOD_MAP[int(cp.get("conf", "kline_type"))]
    start_date = cp.get("conf", "start_date")
    end_date = cp.get("conf", "end_date")
    auth_dict["tenantId"] = cp.get("auth", "tenantId")
    auth_dict["token"] = cp.get("auth", "token")
    if len(auth_dict["tenantId"]) == 0 or len(auth_dict["token"]) == 0:
        raise Exception("auth NULL")
    all_code = all_code_str.split(";")
    code_count = len(all_code)
    if code_count == 0:
        raise Exception("symbol NULL")
    random.shuffle(all_code)
    code_list_arr = chunks(all_code, thread_num)
    thr = []
    for i in range(0, len(code_list_arr)):
        thr.append(DownloadProcess(code_list_arr[i], kline_type, start_date, end_date, auth_dict))
    for item in thr:
        item.start()
    for item in thr:
        item.join()
    print("All Done")


if __name__ == '__main__':
    main()
