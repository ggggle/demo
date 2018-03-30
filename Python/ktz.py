#!/usr/bin/env python3

from xml.dom.minidom import parse, Node
import xml.dom.minidom
import sys, os
import datetime
import time
import threading
import shutil

g_cfg = {}
g_cfg['CCFX'] = {}
g_cfg['XSGE'] = {}
g_cfg['XDCE'] = {}
g_cfg['XZCE'] = {}
mktId2mktName = {'0x0303': 'CCFX', '0x0304': 'XSGE', '0x0305': 'XDCE', '0x0306': 'XZCE'}
tradeMkt2hsMkt = {'CFFEX': 'CCFX', 'SH': 'XSGE', 'DL': 'XDCE', 'ZZ': 'XZCE'}
hsMkt2tradeName = {'CCFX': 'CFFEX', 'XSGE': 'SH', 'XDCE': 'DL', 'XZCE': 'ZZ'}
# mkt_name=['CCFX','XSGE','XDCE','XZCE']

min_field_index = {'trade_date': 0, 'forward_date': 1, 'forward_time': 2, 'backward_date': 3, 'backward_time': 4,
                   'open': 5, 'high': 6, 'low': 7, 'close': 8, 'volume': 9, 'turnover': 10, 'average': 11,
                   'position': 12, 'settlement': 13, 'turnover_ratio': 14}

month_day_leapyear = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
month_day_normalyear = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

data = {}


# data['CCFX']={}
# data['XSGE']={}
# data['XDCE']={}
# data['XZCE']={}

# rade_section_str=

# [0900,1130] [1330-1500]


# step 1

# step

# step

# step 生成向前归向后归K线
class kLineThred(threading.Thread):
    def __init__(self, mkt, input_path, trade_path, output_path):
        threading.Thread.__init__(self)
        self.mkt = mkt
        self.input_path = input_path
        self.trade_path = trade_path
        self.output_path = output_path

    def run(self):
        print("start " + self.mkt)
        full_kline_check(self.input_path, self.trade_path, self.output_path, self.mkt)
        print("exit " + self.mkt)


# input:一个交易日的完整K线
# output:各类分钟K线
def detect_temp_close(infile):
    pass


def detect_night_trade(infile):
    file_HD = open(infile)
    try:
        longstr = file_HD.read()
    finally:
        file_HD.close()
    print(longstr)

'''因为交易日是通过反推得到的，因此最后一天如果有夜市的话就无法获取到正确的交易日，所以舍去最后一天的夜'''
def cut_last_day(input_path,output_path):
    for mkt in os.listdir(input_path):
        if mkt not in ['DL','SH']:
            pass
        for file_name in os.listdir('/'.join([input_path,mkt,'1Min'])):
            if file_name not in ['a9000.csv']:
                pass
            if not os.path.exists('/'.join([output_path,mkt,'1Min'])):
                os.makedirs('/'.join([output_path,mkt,'1Min']))
            file = open('/'.join([input_path,mkt,'1Min',file_name]))
            file_read = file.read()
            content = file_read.split('\n')
            temp = content[-1].split(',')
            #print(temp, len(temp))
            if len(temp) == 1:
                continue
            flag = temp[2]
            new_file = open('/'.join([output_path, mkt, '1Min', file_name]), 'w')
            if int(flag) < 1800:
                new_file.write(file_read)
                new_file.close()
                file.close()
                continue
            for i in range(0,len(content)):
                tmp = content[i].split(',')
                if int(tmp[1]+tmp[2]) < int(temp[1]+'1800'):
                    new_file.write(content[i]+'\n')
                else:
                    break
            new_file.close()
            file.close()


def detect(mkt_path_list, enum):
    if 1 == enum:  # 检测小休市
        for mkt_path in mkt_path_list:
            for ktype in os.listdir(mkt_path):
                if ktype in ['1Min']:
                    detect_temp_close(infile)
    if 2 == enum:
        for mkt_path in mkt_path_list:
            for ktype in os.listdir(mkt_path):
                if ktype in ['1Min']:
                    detect_night_trade(infile)
    pass


# 1分钟线落地时间点序列
def calc_oneday_minute_kline(one_trade_day, step, time_slot, backward=False):
    pass


def calc_minute_kline(trade_day_dict, step, forward=True):
    for trade_day in trade_date_list:
        kline_list = sorted(tradeday_dict[tradeday], key=lambda kline: int(kline.split(',')[2]))
        if trade_time_section[0] != len(kline_list):
            if forward:
                temp = fill_blank(kline_list, forward_version, forward)
            else:
                temp = fill_blank(kline_list, backward_version, forward)
        new_kline_list = calc_minute_kline(temp, 60, time_slot)

    pass


def dateShift(date, n):
    dateC = datetime.datetime(int(date) // 10000, (int(date) // 100) % 100, int(date) % 100, 0, 0, 0)
    timestamp = time.mktime(dateC.timetuple())
    timestamp += 60 * 60 * 24 * n
    time_array = time.localtime(timestamp)
    date_str = time.strftime("%Y%m%d", time_array)
    return int(date_str)


def append_new_kline(slot, trade_date, current_date, pre_close, pre_position, is_forward):
    field = []
    field.append(trade_date)
    if is_forward:
        date_str = current_date
        time_str = slot
        '''hh=time_str[-len(time_str):-2]
        mm=time_str[-2:]
        dateC=datetime.datetime(int(date_str)//10000,(int(date_str)//100)%100,int(date_str)%100,int(hh),int(mm),0)

        timestamp=time.mktime(dateC.timetuple())
        timestamp+=60
        time_array= time.localtime(timestamp)
        date_str = time.strftime("%Y%m%d",time_array)
        time_str =time.strftime("%H%M",time_array)'''
        field.append(date_str)
        field.append(time_str)
        field.append('')
        field.append('')

    else:
        print("append_new_kline backward is not ready")
        date_str = current_date
        time_str = slot
        '''hh=time_str[-len(time_str):-2]
        mm=time_str[-2:]
        dateC=datetime.datetime(int(date_str)//10000,(int(date_str)//100)%100,int(date_str)%100,int(hh),int(mm),0)

        timestamp=time.mktime(dateC.timetuple())
        timestamp-=60
        time_array= time.localtime(timestamp)
        date_str = time.strftime("%Y%m%d",time_array)
        time_str =time.strftime("%H%M",time_array)'''
        field[3] = date_str
        field[4] = time_str

    field.append(pre_close)
    field.append(pre_close)
    field.append(pre_close)
    field.append(pre_close)

    field.append('0')  # volume
    field.append('0')  # turnover
    field.append('0')  # average
    field.append(pre_position)  # position
    field.append('0')  # settlement
    field.append('0')  # turnover_ratio
    # field.append('fill in blank')#turnover_ratio

    return ','.join(field)


def make_slot(kline_list):
    slot_dict = {}
    for kline in kline_list:
        if len(kline) == 0:
            break
        slot_dict[kline.split(',')[2]] = kline
    return slot_dict


def fill_empty_slot(slot_dict, slot_list, trade_date, current_date, pre_close, pre_position, is_forward):
    iret_list = []
    if trade_date in ['20141229']:
        pass

    for slot in slot_list:
        kline = slot_dict.get(slot, "Empty")
        if 'Empty' == kline:
            kline = append_new_kline(slot, trade_date, current_date, pre_close, pre_position, is_forward)
            slot_dict[slot] = kline
        pre_close = kline.split(',')[min_field_index['close']]
        pre_position = kline.split(',')[min_field_index['position']]
        iret_list.append(kline)
    if len(iret_list) != len(slot_list):
        print("exception detected")
    # if trade_date in ['20141229']:
    #    print (len(iret_list))
    #    print (iret_list)

    return iret_list


def night_kline_selector(kline_list):
    night_kline = []
    day_kline = []
    for kline in kline_list:
        time = kline.split(',')[2]
        if 800 < int(time) and int(time) < 1700:
            day_kline.append(kline)
        else:
            night_kline.append(kline)
    return [night_kline, day_kline]


def slot_sort(kline):
    date_str = kline.split(',')[1]
    time_str = kline.split(',')[2]
    hh = time_str[-len(time_str):-2]
    mm = time_str[-2:]
    dateC = datetime.datetime(int(date_str) // 10000, (int(date_str) // 100) % 100, int(date_str) % 100, int(hh),
                              int(mm), 0)
    timestamp = time.mktime(dateC.timetuple())
    return timestamp


def fill_blank_day_tradeday(code_info, kline_list, last_kline, slot_list, mkt_cfg, is_forward):
    # print (kline_list)
    trade_day = kline_list[0].split(',')[min_field_index['trade_date']]
    pre_close = last_kline.split(',')[min_field_index['close']]
    pre_position = last_kline.split(',')[min_field_index['position']]

    slot_dict = make_slot(kline_list)
    new_kline_list = fill_empty_slot(slot_dict, slot_list, trade_day, trade_day, pre_close, pre_position, is_forward)
    # print(new_kline_list)
    return new_kline_list


def fill_blank_night_tradeday(code_info, kline_list, last_kline, slot_list, mkt_cfg, is_forward):
    # print (kline_list)
    last_tradeday = last_kline.split(',')[min_field_index['trade_date']]
    trade_date = kline_list[0].split(',')[min_field_index['trade_date']]
    pre_close = last_kline.split(',')[min_field_index['close']]
    pre_position = last_kline.split(',')[min_field_index['position']]

    if trade_date in ['20141229']:
        pass
    if trade_date in ['20160215']:
        pass
    if trade_date in ['20160504']:
        pass

    # print (next_day)
    [night_kline, day_kline] = night_kline_selector(kline_list)
    night_kline = sorted(night_kline, key=lambda kline: slot_sort(kline))
    day_kline = sorted(day_kline, key=lambda kline: slot_sort(kline))

    [start_date, end_date, trade_time_section] = get_trade_time_section(code_info[1].upper(), trade_date, mkt_cfg)
    [f2b, b2f, forward_slot_night, backward_slot_night] = forward_backward_map(trade_time_section[2][0:1], 60)
    [f2b, b2f, forward_slot_day, backward_slot_day] = forward_backward_map(
        trade_time_section[2][1:len(trade_time_section[2])], 60)

    # night_trade_flag=True
    # 计算下一个自然日是不是国假日
    # print (str(next_day))
    next_day = dateShift(last_tradeday, 1)
    if next_day in mkt_cfg['restday']:
        # print (trade_date)

        slot_dict = make_slot(day_kline)
        day_kline = fill_empty_slot(slot_dict, forward_slot_day, trade_date, trade_date, pre_close, pre_position,
                                    is_forward)
    else:
        # pass
        slot_dict = make_slot(night_kline)
        night_kline = fill_empty_slot(slot_dict, forward_slot_night, trade_date, last_tradeday, pre_close, pre_position,
                                      is_forward)  #
        # if trade_date in ['20141229']:
        #    print (night_kline)
        pre_close = night_kline[-1].split(',')[min_field_index['close']]
        slot_dict = make_slot(day_kline)
        day_kline = fill_empty_slot(slot_dict, forward_slot_day, trade_date, trade_date, pre_close, pre_position,
                                    is_forward)

    # 更新last_kline

    # fill_blank_day_tradeday(code_info,day_kline,last_kline,slot_list,mkt_cfg,is_forward)

    night_kline.extend(day_kline)
    return night_kline

'''修改第一条线'''
def change_trade_day(input_path,output_path):
    for mkt in os.listdir(input_path):
        if mkt not in ['DL','SH']:
            pass
        for file_name in os.listdir('/'.join([input_path,mkt,'1Min'])):
            file = open('/'.join([input_path,mkt,'1Min',file_name]))
            content = file.read().split('\n')
            if not os.path.exists('/'.join([output_path,mkt,'1Min'])):
                os.makedirs('/'.join([output_path,mkt,'1Min']))
            new_file = open('/'.join([output_path,mkt,'1Min',file_name]),'w')
            temp = content[0].split(',')
            new_first_line = ','.join([temp[1],content[0][9:]])
            new_file.write(new_first_line+'\n')
            for i in range(1,len(content)):
                if i == (len(content)-1):
                    new_file.write(content[i])
                else:
                    new_file.write(content[i]+'\n')
            file.close()
            new_file.close()

def fill_blank(code_info, outfile, trade_day_dict, mkt_cfg, is_forward=True):
    code = os.path.basename(outfile)
    code = code.split('.')[0]
    # log_hd=open(outfile,"w")
    # log_hd.write(code+"\n")
    title = "trade_date,forward_date,forward_time,backward_date,backward_time,open,high,low,close,volume,turnover,average,position,settlement,turnover_ratio\n"
    '''if is_forward:
        title="trade_date,forward_date,forward_time,open,high,low,close,volume,turnover,average,position,settlement,turnover_ratio\n"
    else:
        title="trade_date,backward_date,backward_time,open,high,low,close,volume,turnover,average,position,settlement,turnover_ratio\n"
        '''
    outfile_hd = open(outfile, "w")
    outfile_hd.write(title)
    trade_day_list = sorted(list(trade_day_dict.keys()), key=lambda k: int(k))

    [start_date, end_date, trade_time_section] = get_trade_time_section(code, trade_day_list[0], mkt_cfg)
    [f2b, b2f, forward_version, backward_version] = forward_backward_map(trade_time_section[2], 60)
    # 第一天被扔掉
    # pre_tradyday=sorted(trade_day_dict[trade_day_list[0]],key=lambda kline:int(kline.split(',')[2]) )#按顺序
    last_kline = trade_day_dict[trade_day_list[0]][-1]
    # print (pre_tradyday)
    buffer = []
    for trade_day in trade_day_list[1:len(trade_day_list)]:
        # kline_list=sorted(trade_day_dict[trade_day],key=lambda kline:int(kline.split(',')[2]) )
        kline_list = trade_day_dict[trade_day]

        if int(trade_day) < int(start_date) or int(end_date) < int(trade_day):
            [start_date, end_date, trade_time_section] = get_trade_time_section(code, trade_day, mkt_cfg)
            [f2b, b2f, forward_version, backward_version] = forward_backward_map(trade_time_section[2], 60)

        if len(kline_list) < int(trade_time_section[0]):
            # log_hd.write (' '.join([str(trade_day),trade_time_section[0],str(len(kline_list))])+'\n')
            # continue
            if trade_time_section[1]:
                # print ("night trade")
                if is_forward:
                    kline_list = fill_blank_night_tradeday(code_info, kline_list, last_kline, forward_version, mkt_cfg,
                                                           is_forward)
                else:
                    kline_list = fill_blank_night_tradeday(code_info, kline_list, last_kline, backward_version, mkt_cfg,
                                                           is_forward)
            else:
                # print ("day trade")
                if is_forward:
                    kline_list = fill_blank_day_tradeday(code_info, kline_list, last_kline, forward_version, mkt_cfg,
                                                         is_forward)
                else:
                    kline_list = fill_blank_day_tradeday(code_info, kline_list, last_kline, backward_version, mkt_cfg,
                                                         is_forward)
        last_kline = kline_list[-1]
        buffer.extend(kline_list)

    outfile_hd.write('\n'.join(buffer))
    outfile_hd.close()
    # log_hd.close()
    pass


def dayOfWeek(date):
    y = int(date) // 10000
    m = int(date) // 100 % 100
    d = int(date) % 100
    if (m == 1 or m == 2):
        m += 12
        y -= 1
    w = (d + 1 + 2 * m + 3 * (m + 1) // 5 + y + y // 4 - y // 100 + y // 400) % 7;
    return w;

    year = int(date) // 10000
    # date=date-(year)*10000
    month = (date // 100) % 100
    day = date % 100
    if (month <= 2):
        month += 12
        --year
    yh = year // 100
    yl = year % 100
    w = (yl + (yl // 4) + (yh // 4) - (2 * yh) + (26 * (month + 1) // 10) + day - 1) % 7
    if (w < 0):
        w += 7
    return w


# Date_Time_Format=0 默认不变
# Date_Time_Format=1 20160510 0930
'''start 2016/05/03    stop 2016/06/28   返回这个期间的交易日列表  值的属性为字符串'''


def calc_month_tradeday(start, stop, market):
    restday_path = './restday'
    trade_time_section_info = "trader.xml"
    loadRestday(restday_path, g_cfg)
    load_trade_info(trade_time_section_info, g_cfg)
    start_year, start_month, start_day = start.split('/')
    stop_year, stop_month, stop_day = stop.split('/')
    trade_day = []
    for year in range(int(start_year), int(stop_year) + 1):
        month_day = []
        month_1 = 1
        month_2 = 12
        if year % 4 == 0:
            month_day = month_day_leapyear
        else:
            month_day = month_day_normalyear
        if year == int(start_year):
            month_1 = start_month
        if year == int(stop_year):
            month_2 = stop_month
        for month in range(int(month_1), int(month_2) + 1):
            day_1 = 1
            day_2 = month_day[month - 1]
            if year == int(start_year) and month == int(start_month):
                day_1 = start_day
            if year == int(stop_year) and month == int(stop_month):
                day_2 = stop_day
            for day in range(int(day_1), int(day_2) + 1):
                this_day_return = ''.join([str(year), '/', '0' * (2 - len(str(month))) + str(month), '/',
                                           '0' * (2 - len(str(day))) + str(day)])
                this_day = ''.join(
                    [str(year), '0' * (2 - len(str(month))) + str(month), '0' * (2 - len(str(day))) + str(day)])
                try:
                    g_cfg[market]['restday'].index(int(this_day))
                except:
                    flag = dayOfWeek(this_day)
                    if flag != 0 and flag != 6:
                        trade_day.append(this_day_return)
    return trade_day


def calc_date_diff(date1, date2):
    date1 = time.strptime(date1, "%Y%m%d")
    date2 = time.strptime(date2, "%Y%m%d")
    date1 = datetime.datetime(date1[0], date1[1], date1[2])
    date2 = datetime.datetime(date2[0], date2[1], date2[2])
    return (date2 - date1).days


'''返回date加上days
date_add("20151231",3)'''


def date_add(date, days):
    date = datetime.datetime.strptime(date, "%Y/%m/%d").date()
    date = date + datetime.timedelta(days=days)
    date = datetime.datetime.strftime(date, "%Y-%m-%d")
    split = date.split('-')
    return '/'.join([split[0], split[1], split[2]])


'''输入一个日期，返回离这个日期最近的下一个交易日'''


def get_next_tradeday(date, mkt):
    trade_date_list = calc_month_tradeday(date, date_add(str(date), 10), tradeMkt2hsMkt[mkt])
    date_split = date.split('/')
    date = date_split[0] + date_split[1] + date_split[2]
    for item in trade_date_list:
        if int(date) < int(item):
            return str(item)


'''有些代码在某些交易日没有产生数据，通过这个函数可以在这些交易日补上一条10点10分的K线'''


def fill_everyday(input_path, output_path):
    for mkt in os.listdir(input_path):
        for type in os.listdir('/'.join([input_path, mkt])):
            if type not in ['1Min']:
                continue
            for file_name in os.listdir('/'.join([input_path, mkt, type])):
                content = open('/'.join([input_path, mkt, type, file_name])).read().split('\n')
                start_date = '2013/01/01'
                end_date = content[-2].split(' ')[0]
                tradeday_list = calc_month_tradeday(start_date, end_date, mkt)
                new_list = []
                days = 0
                temp = ''
                last_day = ''
                for item in content[0:-1]:

                    if int(item.split(' ')[0].split('/')[0] + item.split(' ')[0].split('/')[1] +
                                   item.split(' ')[0].split('/')[2]) < int(
                                            start_date.split('/')[0] + start_date.split('/')[1] + start_date.split('/')[
                                2]):
                        new_list.append(item)
                        continue
                    now_day = item.split(' ')[0]
                    if last_day == '':
                        last_day = now_day
                    if now_day != last_day:
                        try:
                            if (now_day.split('/')[0] + now_day.split('/')[1] + now_day.split('/')[2]) != tradeday_list[
                                days]:
                                new_list.append(tradeday_list[days] + ' ' + temp.split(' ')[1])
                        except:
                            print('1')
                        days += 1
                        continue
                    new_list.append(item)
                    temp = item
                    last_day = temp.split(' ')[0]
                if not os.path.exists('/'.join([output_path, mkt, type])):
                    os.makedirs('/'.join([output_path, mkt, type]))
                new_file = open('/'.join([output_path, mkt, type, file_name]), 'w')
                for item in new_list:
                    new_file.write(item + '\n')
                new_file.close()
                doto


def calc_file_tradeday(infile, Date_Time_Format, mkt):
    min1_file_name = infile

    min1_file = open(min1_file_name, "r")
    try:
        min1_lines = min1_file.read().split('\n')
    finally:
        min1_file.close()
    iret_list = []
    trade_date = 0
    start_date = min1_lines[0].split(' ')[0]
    stop_date = min1_lines[-2].split(' ')[0]
    # trade_date_list = calc_month_tradeday(start_date,stop_date,tradeMkt2hsMkt[mkt])
    # trade_date_list.reverse()
    temp = ''
    num = -1
    kline_ano = ''
    today_has_day_trad = True
    date_ano = ''
    for line in min1_lines[::-1]:
        if len(line) == 0:
            continue
        date_template = "2016/05/10"
        date_time_template = "2016/05/10 14:59"
        date = line.split(' ')[0]
        data = line[len(date_time_template) + 1:]
        trade_time = line.split(' ')[1].split(',')[0]
        '''
        if (''.join(date.split('/'))!=temp):
            if today_has_day_trad==False:
                kline_ano = ','.join(date_ano) + ',' + data
                iret_list.append(kline_ano)
                today_has_day_trad = True
            num+=1
            if int(''.join(trade_time.split(':')))>2000:
                date_ano = [''.join(date.split('/')), ''.join(date.split('/')), '1000']
                today_has_day_trad = False
        try:
            while(trade_date_list[num]!=''.join(date.split('/'))):
                kline = ','.join([trade_date_list[num],trade_date_list[num],'1000',data])
                iret_list.append(kline)
                num+=1
        except IndexError:
            print(infile,temp)
        '''
        if 1 == Date_Time_Format:
            tmp = date.split('/')
            date = ''.join(tmp)
            tmp = trade_time.split(':')
            trade_time = ''.join(tmp)
        # print (date,trade_time,data,sep=',')
        if trade_date == 0:
            trade_date = date
        week_index = dayOfWeek(''.join(date.split('/')))  # 计算是周几
        '''小于17:00才会变更存储的trade_date为当前自然日
        但是如果某个自然日没有白天的数据，就不会进入这里，导致交易日错误'''
        if int(''.join(trade_time.split(':'))) < 1700:
            if 0 != week_index and 6 != week_index:
                trade_date = ''.join(date.split('/'))
                # today_has_day_trad = True
        # date_diff = calc_date_diff(date,trade_date)
        '''差值大于3  说明可能有一天白天没有交易数据  取此自然日下一个交易日作为这笔数据的交易日
        if date_diff>3:
            print('date_diff is '+str(date_diff))
            print('infile is'+str(infile))
            trade_date = get_next_tradeday(date='/'.join([date[0:4],date[4:6],date[6:8]]),mkt=mkt)
            print('tadedate is '+trade_date)
        '''
        tmp = [trade_date, date, trade_time, data]
        kline = ','.join(tmp)
        iret_list.append(kline)
        temp = date
    iret_list.reverse()
    return iret_list


def calc_tradeday(input_path, output_path):
    for mkt in os.listdir(input_path):
        if mkt not in ['DL','SH']:
            pass
        for ktype in os.listdir('/'.join([input_path, mkt])):
            if ktype in ['1Day']:
                continue
            for file_name in os.listdir('/'.join([input_path, mkt, ktype])):
                '''需要相应的注释掉calc_file_tradeday里的那个while循环
                这些代码有零点之后的夜市  需要注释掉while循环
                除此之外的代码都没有零点后的夜市    无需注释掉while循环'''
                # if file_name in ['sn000.csv','sn888.csv','ni000.csv','ni888.csv','cu000.csv','cu888.csv',
                #                     'al000.csv','al888.csv','zn000.csv','zn888.csv','au000.csv','au888.csv',
                #                     'pb000.csv','pb888.csv','ag000.csv','ag888.csv']:
                #    continue
                flag = file_name.split('.')[0][-3:]
                if not os.path.exists('/'.join([output_path, mkt, ktype])):
                    os.makedirs('/'.join([output_path, mkt, ktype]))
                tradeday_list = calc_file_tradeday('/'.join([input_path, mkt, ktype, file_name]), 1, mkt)
                outfile_HD = open('/'.join([output_path, mkt, ktype, file_name]), "w")
                outfile_HD.write('\n'.join(tradeday_list))
                outfile_HD.close()
                # break


def group_by_tradeday(kline_list):
    tradedate_dict = {}
    last_tradedate = 0
    for kline in kline_list:
        if len(kline) == 0:
            break
        tradedate = kline.split(',')[0]
        if last_tradedate == tradedate:
            tradedate_dict[last_tradedate].append(kline)
        else:
            tradedate_dict[tradedate] = []
            tradedate_dict[tradedate].append(kline)
            last_tradedate = tradedate
    return tradedate_dict


def static_file_tradeday(file_path):
    file_HD = open(file_path, "r")
    try:
        all_kline = file_HD.read().split('\n')
    finally:
        file_HD.close()
    tradeday_dict = group_by_tradeday(all_kline)
    tradeday_list = sorted(list(tradeday_dict.keys()), key=lambda t: int(t))

    static_list = []
    total = 0
    for tradeday in tradeday_list:
        # print (tradeday, "line Num:",len(tradeday_dict[tradeday]))
        if len(tradeday_dict[tradeday]) <= 100:
            total += 1
        static_list.append(','.join(["tradeday:" + tradeday, "kline num:" + str(len(tradeday_dict[tradeday]))]))
    if total > 100:
        print(file_path, total, str(100 * total / len(tradeday_list))[0:5] + "%")
    return static_list


def static_tradeday_kline(input_path, output_path):
    for mkt in os.listdir(input_path):
        for ktype in os.listdir('/'.join([input_path, mkt])):
            if ktype in ['1Day']:
                continue
            for file_name in os.listdir('/'.join([input_path, mkt, ktype])):
                tradeday_kline_static = static_file_tradeday('/'.join([input_path, mkt, ktype, file_name]))
                if not os.path.exists('/'.join([output_path, mkt, ktype])):
                    os.makedirs('/'.join([output_path, mkt, ktype]))
                outfile_HD = open('/'.join([output_path, mkt, ktype, file_name]), "w")
                outfile_HD.write('\n'.join(tradeday_kline_static))
                outfile_HD.close()


def load_trade_info(config_file, config):
    xmldoc = xml.dom.minidom.parse(config_file)
    root = xmldoc.documentElement
    child_node = root.firstChild
    mkt_list = root.getElementsByTagName('MARKET')
    for mkt_cfg in mkt_list:
        mkt = (mkt_cfg.getElementsByTagName('Name')[0]).childNodes[0].nodeValue.strip()
        # print (mkt)
        mkt_config = config[mkt]
        mkt_config['market_trade_section'] = {}
        trade_section = mkt_config['market_trade_section']
        tradeSections = mkt_cfg.getElementsByTagName('tradeTimeSection')[0]
        tradeSection_list = tradeSections.getElementsByTagName('tradeSection')
        for tradeSection in tradeSection_list:
            TradeTime_list = tradeSection.getElementsByTagName('TradeTime')
            secId = tradeSection.getAttribute('id')
            num = tradeSection.getAttribute('num')
            section_list = []
            night_flag = False
            # print (secId,num)
            for tradeTime in TradeTime_list:
                open_var = tradeTime.getAttribute('open')
                close = tradeTime.getAttribute('close')
                if len(tradeTime.getAttribute('flag')) != 0:
                    night_flag = True
                section_list.append((open_var, close))
                # print (open_var,close)
            trade_section[secId] = (num, night_flag, section_list)

        mkt_config['code_trade_section'] = {}
        trade_section = mkt_config['code_trade_section']
        Securities = mkt_cfg.getElementsByTagName('Securities')[0]
        Security_list = Securities.getElementsByTagName('Security')
        for Security in Security_list:
            code = Security.getAttribute('name')
            # print (code)
            section_list = []
            trade_section[code] = section_list
            SectionId_list = Security.getElementsByTagName('tradeSectionId')
            for SectionId in SectionId_list:
                secId = SectionId.childNodes[0].nodeValue.strip()
                Start = SectionId.getAttribute('Start')
                End = SectionId.getAttribute('End')
                section_list.append((secId, Start, End))
                # print (secId,Start,End)
    pass


def getNextStartTime(segment_length, last_remain, segment, forward=False):
    ret_var = []
    ret_var.append([])
    length = segment_length - last_remain
    y_s = int(segment[0][0:4])
    m_s = int(segment[0][4:6])
    d_s = int(segment[0][6:8])
    hh_s = int(segment[0][8:10])
    mm_s = int(segment[0][10:12])
    dateC = datetime.datetime(y_s, m_s, d_s, hh_s, mm_s, 0)
    timestamp_start = time.mktime(dateC.timetuple())

    y_e = int(segment[1][0:4])
    m_e = int(segment[1][4:6])
    d_e = int(segment[1][6:8])
    hh_e = int(segment[1][8:10])
    mm_e = int(segment[1][10:12])
    dateC = datetime.datetime(y_e, m_e, d_e, hh_e, mm_e, 0)
    timestamp_end = time.mktime(dateC.timetuple())

    timestamp = timestamp_start

    if forward:
        while (timestamp + length) < timestamp_end:
            timestamp += length
            time_array = time.localtime(timestamp)
            time_var = time.strftime("%H%M", time_array)
            ret_var[0].append(time_var)
            length = segment_length
    else:
        while (timestamp + length) <= timestamp_end:
            timestamp += length
            time_array = time.localtime(timestamp)
            time_var = time.strftime("%H%M", time_array)
            ret_var[0].append(time_var)
            length = segment_length
    ret_var.append(timestamp_end - timestamp)
    return ret_var


def get_groud_time(trade_section_list, secend_per_segment, forward=False):
    trade_section = trade_section_list
    ground_time = []
    remain = 0
    if forward:  # 开拓者
        ground_time.append(trade_section[0][0])
        for segment in trade_section:
            start_time = int(segment[0])
            end_time = int(segment[1])
            seg_start = "20000101" + segment[0]
            seg_end = "20000101" + segment[1]
            if start_time > end_time:
                seg_end = "20000102" + segment[1]
            two_point = []
            two_point.append(seg_start)
            two_point.append(seg_end)

            result = getNextStartTime(secend_per_segment, remain, two_point, True)
            ground_time.extend(result[0])
            remain = result[1]

    else:  # hundsun
        for segment in trade_section:
            start_time = int(segment[0])
            end_time = int(segment[1])
            seg_start = "20000101" + segment[0]
            seg_end = "20000101" + segment[1]
            if start_time > end_time:
                seg_end = "20000102" + segment[1]
            two_point = []
            two_point.append(seg_start)
            two_point.append(seg_end)

            result = getNextStartTime(secend_per_segment, remain, two_point)
            ground_time.extend(result[0])
            remain = result[1]
        if int(remain) != 0:
            ground_time.append(trade_section[len(trade_section) - 1][1])

    return ground_time


def forward_backward_map(trade_section, secend_per_segment):
    backward_version = []  # 恒生
    forward_version = []
    b2f = {}
    f2b = {}
    time2index = {}

    backward_version = get_groud_time(trade_section, secend_per_segment)
    forward_version = get_groud_time(trade_section, secend_per_segment, True)

    # print (forward_version)
    index = 0
    for time_section in backward_version:
        # print (time_section)
        b2f[time_section] = forward_version[index]
        f2b[forward_version[index]] = time_section
        # print (f2b[forward_version[index]],b2f[time_section])
        index += 1
    return [f2b, b2f, forward_version, backward_version]


def get_trade_time_section(code, date, mkt_cfg):
    trade_section_list = []
    trade_section = []
    try:
        trade_section_list = mkt_cfg['code_trade_section'][code.upper()]
    except:
        try:
            trade_section_list = mkt_cfg['code_trade_section'][(code[0:2]+'000').upper()]
        except:
            try:
                trade_section_list = mkt_cfg['code_trade_section'][(code[0] + '000').upper()]
            except:
                trade_section_list = mkt_cfg['code_trade_section'][(code[0] + '9000').upper()]
    for (trade_section_id, start_date, end_date) in trade_section_list:
        if int(start_date) <= int(date) and int(date) <= int(end_date):
            trade_section = [start_date, end_date, mkt_cfg['market_trade_section'][trade_section_id]]
            break
    return trade_section


def calcRestday(rest_day_list, year):
    tmp = []
    for holiday in rest_day_list:
        if len(holiday) == 9:
            [start, end] = holiday.split("-")
            start = int(year) * 10000 + int(start)
            end = int(year) * 10000 + int(end)
        else:
            start = int(year) * 10000 + int(holiday)
            end = start
        dateC = datetime.datetime(start // 10000, (start // 100) % 100, start % 100, 0, 0, 0)
        timestamp = time.mktime(dateC.timetuple())
        while 1:
            time_array = time.localtime(timestamp)
            date = time.strftime("%Y%m%d", time_array)
            if int(date) <= end:
                tmp.append(int(date))
            else:
                break
            timestamp += 60 * 60 * 24
            # print (start,end)
            # print (tmp)
    return tmp


def loadRestday(config_file_path, config):
    xmlfiles = os.listdir(config_file_path)
    config['CCFX']["restday"] = []
    config['XSGE']["restday"] = []
    config['XDCE']["restday"] = []
    config['XZCE']["restday"] = []
    for file_name in xmlfiles:
        xml_file = config_file_path + '/' + file_name
        tmp = file_name.split('.')
        year = tmp[1]
        xmldoc = xml.dom.minidom.parse(xml_file)
        root = xmldoc.documentElement
        restday_list = root.getElementsByTagName('exch')
        for restday in restday_list:
            '''if restday.getAttribute('type')=='0x0303':
                print (restday.childNodes[0].data)
            if restday.getAttribute('type')=='0x0304':
                print (restday.childNodes[0].data)
            if restday.getAttribute('type')=='0x0305':
                print (restday.childNodes[0].data)
            if restday.getAttribute('type')=='0x0306':
                print (restday.childNodes[0].data)'''
            if (restday.getAttribute('type') != '0x0303' and
                        restday.getAttribute('type') != '0x0304' and
                        restday.getAttribute('type') != '0x0305' and
                        restday.getAttribute('type') != '0x0306'):
                continue
            # print (restday.getAttribute('type'))
            # print (restday.childNodes[0].data)
            mkt_cfg = config[mktId2mktName[restday.getAttribute('type')]]
            rest_day_list = calcRestday(restday.childNodes[0].data.split(","), year)
            mkt_cfg["restday"].extend(rest_day_list)
            # print ('stop')
    return


def load_data(infile):
    file_hd = open(infile)
    try:
        bigstr = file_hd.read()
    finally:
        file_hd.close()
    return bigstr


# return cleaning kline   返回没有title的kline
def load_kline_data(infile, withTitle=True):
    iret_list = []
    temp_list = load_data(infile).split('\n')
    start_pos = 1
    if not withTitle:
        start_pos = 0
    for kline in temp_list[start_pos:]:  # 如果有title，则跳过title
        if len(kline) == 0:
            continue
        iret_list.append(kline)
    return iret_list


# 交易日内k线按先后顺序排列,必须是干净的k线
def load_trade_data(kline_list, check=False):
    tradedates = {}
    last_tradedate = 0
    for line in kline_list:
        if len(line) == 0:
            continue
        fields = line.split(",")
        tradedate = int(fields[min_field_index['trade_date']])
        date = int(fields[1])
        trade_time = int(fields[2])
        #print(date, tradedate, trade_time, sep=":")
        if last_tradedate == tradedate:
            tradedates[last_tradedate].append(line)
        else:

            if check and int(last_tradedate) and len(tradedates[last_tradedate]) % 5 != 0:
                print(len(tradedates[last_tradedate]))
                return [False, last_tradedate]
            tradedates[tradedate] = []
            tradedates[tradedate].append(line)
            last_tradedate = tradedate
    return [True, tradedates]


def load_mkt_kline_data(input_path):
    mkt_data = []
    # data[tradeMkt2hsMkt[mkt_folder]]=mkt_data
    for ktype_folder in os.listdir(input_path):
        if ktype_folder in ['1Day']:
            continue
        for file_name in os.listdir('/'.join([input_path, ktype_folder])):
            # if file_name not in ['B9000.min1.csv']:
            # continue
            mkt_data.append((file_name, load_kline_data('/'.join([input_path, ktype_folder, file_name]))))
            # print (file_name)
    return mkt_data


def convertKLineFormat(inputKline, ktype='1Min'):
    # date,trade_date,time,open,high,low,close,volume,turnover,average,position,settlement,turnover_ratio
    if ktype == '1Min':
        [trade_date, date, time, open_str, high, low, close_str, volume, position] = inputKline.split(',')
        turnover = '0'
        average = '0'
        settlement = '0'
        turnover_ratio = '0'
        temp = [trade_date, date, time, '', '', open_str, high, low, close_str, volume, turnover, average, position,
                settlement, turnover_ratio]
        return temp
    else:
        [trade_date, open_str, high, low, close_str, volume, position] = inputKline.split(',')
        trade_date = ''.join(trade_date.split('/'))
        turnover = '0'
        average = '0'
        settlement = '0'
        turnover_ratio = '0'
        temp = [trade_date, trade_date, '0', trade_date, '0', open_str, high, low, close_str, volume, turnover, average,
                position, settlement, turnover_ratio]
        return temp


def convert2HSFormatFile(infile, outfile, ktype='1Min'):
    # print (infile,outfile)
    new_kline_list = []
    kline_data_list = load_kline_data(infile, False)
    for kline in kline_data_list:
        # print (kline)
        new_kline = convertKLineFormat(kline, ktype)
        new_kline_list.append(','.join(new_kline))
    return new_kline_list


def convert2HSFormat(input_path, output_path, kLineType='1Min'):
    title = "trade_date,forward_date,forward_time,backward_date,backward_time,open,high,low,close,volume,turnover,average,position,settlement,turnover_ratio\n"
    typeName = ''
    if kLineType == '1Min':
        typeName = 'min1'
    else:
        typeName = 'day'

    for mkt in os.listdir(input_path):
        if mkt not in ['DL','SH']:
            pass
        for ktype in os.listdir('/'.join([input_path, mkt])):
            if ktype != kLineType:
                continue
            for file_name in os.listdir('/'.join([input_path, mkt, ktype])):
                print(file_name)
                if not os.path.exists('/'.join([output_path, mkt, ktype])):
                    os.makedirs('/'.join([output_path, mkt, ktype]))
                kline_list = convert2HSFormatFile('/'.join([input_path, mkt, ktype, file_name]),
                                                  '/'.join([output_path, mkt, ktype, file_name]), kLineType)

                code = file_name.split('.')[0]
                file_name = code.upper() + '.' + typeName + ".csv"
                print(file_name)

                outfile_HD = open('/'.join([output_path, mkt, ktype, file_name]), "w")
                outfile_HD.write(title)
                outfile_HD.write('\n'.join(kline_list))
                outfile_HD.close()
                # break
    pass


def klineforword2backward(kline):
    field = kline.split(',')
    f_date = field[min_field_index['forward_date']]
    f_time = field[min_field_index['forward_time']]

    hh = f_time[-len(f_time):-2]
    mm = f_time[-2:]
    dateC = datetime.datetime(int(f_date) // 10000, (int(f_date) // 100) % 100, int(f_date) % 100, int(hh), int(mm), 0)

    timestamp = time.mktime(dateC.timetuple())
    timestamp += 60
    time_array = time.localtime(timestamp)
    b_date = time.strftime("%Y%m%d", time_array)
    b_time = time.strftime("%H%M", time_array)

    field[min_field_index['backward_date']] = b_date
    field[min_field_index['backward_time']] = b_time
    return ','.join(field)


def fileforword2backward(input_file):
    infile_hd = open(input_file)
    try:
        big_str = infile_hd.read()
    finally:
        infile_hd.close()
    kline_list = big_str.split('\n')
    output_kline_list = []
    for kline in kline_list[1:len(kline_list)]:
        newkline = klineforword2backward(kline)
        # print (newkline)
        output_kline_list.append(newkline)
    return output_kline_list


def forword2backward(input_path, output_path):
    # for mkt_name in ['CCFX','XSGE','XDCE','XZCE']:
    title = "trade_date,forward_date,forward_time,backward_date,backward_time,open,high,low,close,volume,turnover,average,position,settlement,turnover_ratio\n"
    for mkt in os.listdir(input_path):
        for ktype in os.listdir('/'.join([input_path, mkt])):
            if ktype in ['1Day']:
                continue
            for file_name in os.listdir('/'.join([input_path, mkt, ktype])):

                if not os.path.exists('/'.join([output_path, mkt, ktype])):
                    os.makedirs('/'.join([output_path, mkt, ktype]))
                kline_list = fileforword2backward('/'.join([input_path, mkt, ktype, file_name]))
                code = file_name.split('.')[0]
                file_name = code.upper() + '.min1.csv'
                print(file_name)
                outfile_HD = open('/'.join([output_path, mkt, ktype, file_name]), "w")
                outfile_HD.write(title)
                outfile_HD.write('\n'.join(kline_list))
                outfile_HD.close()


def calc_segment_kline(segment):
    # if ktype in ['1Min']:
    field = segment[0].split(',')
    field[min_field_index['trade_date']] = segment[-1].split(',')[min_field_index['trade_date']]
    field[min_field_index['forward_date']]
    field[min_field_index['forward_time']]

    field[min_field_index['open']]
    open_inited = False
    if int(field[min_field_index['volume']]) != 0:
        open_inited = True

    high_loger = int(round(float(field[min_field_index['high']]) * 10000, 0))
    low_loger = int(round(float(field[min_field_index['low']]) * 10000, 0))
    volume_sum = int(field[min_field_index['volume']])
    turnover_sum = float(field[min_field_index['turnover']])
    i_line = segment[0].split(',')

    for kline in segment[1:len(segment)]:
        if len(kline) == 0:
            continue
        i_line = kline.split(',')

        if int(i_line[min_field_index['volume']]) == 0:
            continue

        high = int(round(float(i_line[min_field_index['high']]) * 10000, 0))
        low = int(round(float(i_line[min_field_index['low']]) * 10000, 0))

        if not open_inited:
            field[min_field_index['open']] = i_line[min_field_index['open']]
            field[min_field_index['low']] = i_line[min_field_index['low']]
            low_loger = int(round(float(i_line[min_field_index['low']]) * 10000, 0))
            high_loger = int(round(float(i_line[min_field_index['high']]) * 10000, 0))
            field[min_field_index['high']] = i_line[min_field_index['high']]
            open_inited = True

        if low_loger > low:
            low_loger = low
            field[min_field_index['low']] = i_line[min_field_index['low']]

        if high_loger < high:
            high_loger = high
            field[min_field_index['high']] = i_line[min_field_index['high']]
        volume = int(i_line[min_field_index['volume']])
        volume_sum += volume
        turnover = float(i_line[min_field_index['turnover']])
        turnover_sum += turnover

    field[min_field_index['backward_date']] = i_line[min_field_index['backward_date']]
    field[min_field_index['backward_time']] = i_line[min_field_index['backward_time']]
    field[min_field_index['close']] = i_line[min_field_index['close']]
    field[min_field_index['volume']] = str(volume_sum)
    field[min_field_index['turnover']] = str(turnover_sum)

    field[min_field_index['average']] = i_line[min_field_index['average']]
    field[min_field_index['position']] = i_line[min_field_index['position']]
    field[min_field_index['settlement']] = i_line[min_field_index['settlement']]
    field[min_field_index['turnover_ratio']] = i_line[min_field_index['turnover_ratio']]

    field[min_field_index['open']] = '%.4f' % (float(field[min_field_index['open']]))
    field[min_field_index['high']] = '%.4f' % (float(field[min_field_index['high']]))
    field[min_field_index['low']] = '%.4f' % (float(field[min_field_index['low']]))
    field[min_field_index['close']] = '%.4f' % (float(field[min_field_index['close']]))
    field[min_field_index['turnover']] = '%.4f' % (float(field[min_field_index['turnover']]))
    field[min_field_index['average']] = '%.4f' % (float(field[min_field_index['average']]))
    field[min_field_index['settlement']] = '%.4f' % (float(field[min_field_index['settlement']]))
    field[min_field_index['turnover_ratio']] = '%.5f' % (float(field[min_field_index['turnover_ratio']]))

    return field


def calc_n_minute_kline(kline_list, n):
    n_kline_list = []
    segment = []
    count = 0
    for kline in kline_list:
        count += 1
        segment.append(kline)
        count = count % n
        if count == 0:
            # print ("segment break")
            n_kline_list.append(','.join(calc_segment_kline(segment)))
            segment.clear()
    if count != 0:
        n_kline_list.append(','.join(calc_segment_kline(segment)))
    return n_kline_list


def calc_5min_kline(mkt, code, ktype, trade_date_dict, output_path, title):
    foot_step = int(ktype[3 - len(ktype):])
    # print (ktype,foot_step)
    new_kline_list = []
    trade_date_list = sorted(list(trade_date_dict.keys()), key=lambda l: l)
    for trade_date in trade_date_list:
        oneday_kline_list = trade_date_dict[trade_date]
        new_kline_list.extend(calc_n_minute_kline(oneday_kline_list, foot_step))
    # if not os.path.exists(output_path):
    #    os.makedirs(output_path)
    file_name = '.'.join([code, ktype, 'csv'])
    outfile = '/'.join([output_path, file_name])
    # print (outfile)
    outfile_HD = open(outfile, "w")
    outfile_HD.write(title)
    outfile_HD.write('\n'.join(new_kline_list[::-1]))
    outfile_HD.close()


def calc_minute_kline(input_path, output_path):
    title = "trade_date,forward_date,forward_time,backward_date,backward_time,open,high,low,close,volume,turnover,average,position,settlement,turnover_ratio\n"
    for mkt in os.listdir(input_path):
        # if mkt not in ['SH']:
        #    continue
        for ktype in os.listdir('/'.join([input_path, mkt])):
            if ktype in ['1Day']:
                continue
            for file_name in os.listdir('/'.join([input_path, mkt, ktype])):
                # if file_name not in ['m9888.csv']:
                #    continue
                # print (file_name)
                # if not os.path.exists('/'.join([output_path,mkt,ktype])):
                #    os.makedirs('/'.join([output_path,mkt,ktype]))

                # inputfile_HD=open('/'.join([input_path,mkt,ktype,file_name]),"r")
                # big_str=inputfile_HD.read()
                # inputfile_HD.close()
                # kline_list=big_str.split('\n')
                # kline_list=kline_list[1:len(kline_list)]
                code = file_name.split('.')[0].upper()
                kline_list = load_kline_data('/'.join([input_path, mkt, ktype, file_name]))
                iret_list = load_trade_data(kline_list, True)

                if iret_list[0] == False:
                    print(mkt, code, iret_list[1])
                    continue

                trade_date_dict = iret_list[1]

                outfile_path = '/'.join([output_path, mkt, 'MIN5'])
                print(outfile_path + '/' + code + '.min5.csv')
                if not os.path.exists(outfile_path):
                    os.makedirs(outfile_path)
                iRet = calc_5min_kline(mkt, code, 'min5', trade_date_dict, outfile_path, title)
                if iRet == False:
                    continue

                outfile_path = '/'.join([output_path, mkt, 'MIN15'])
                print(outfile_path + '/' + code + '.min15.csv')
                if not os.path.exists(outfile_path):
                    os.makedirs(outfile_path)
                iRet = calc_5min_kline(mkt, code, 'min15', trade_date_dict, outfile_path, title)
                if iRet == False:
                    continue

                outfile_path = '/'.join([output_path, mkt, 'MIN30'])
                print(outfile_path + '/' + code + '.min30.csv')
                if not os.path.exists(outfile_path):
                    os.makedirs(outfile_path)
                iRet = calc_5min_kline(mkt, code, 'min30', trade_date_dict, outfile_path, title)
                if iRet == False:
                    continue

                outfile_path = '/'.join([output_path, mkt, 'MIN60'])
                print(outfile_path + '/' + code + '.min60.csv')
                if not os.path.exists(outfile_path):
                    os.makedirs(outfile_path)
                calc_5min_kline(mkt, code, 'min60', trade_date_dict, outfile_path, title)

                pass


def firstDateInSegment(date, ktype):
    # week
    y = int(date) // 10000
    m = (int(date) // 100) % 100
    d = int(date) % 100
    if ktype == 'WEEK':
        index = dayOfWeek(date)
        first_date = dateShift(date, (1 - index))
    elif ktype == 'MONTH':
        first_date = y * 10000 + m * 100 + 1
    elif ktype == 'YEAR':
        first_date = y * 10000 + 101
    return first_date


def calcDayKline(input_path, output_path, kLineType):
    title = "trade_date,forward_date,forward_time,backward_date,backward_time,open,high,low,close,volume,turnover,average,position,settlement,turnover_ratio\n"
    for mkt in os.listdir(input_path):
        for ktype in os.listdir('/'.join([input_path, mkt])):
            if ktype in ['1Min']:
                continue
            for file_name in os.listdir('/'.join([input_path, mkt, ktype])):
                code = file_name.split('.')[0].upper()
                # print (mkt,code)
                inputfile_HD = open('/'.join([input_path, mkt, ktype, file_name]), "r")
                big_str = inputfile_HD.read()
                inputfile_HD.close()
                kline_list = big_str.split('\n')
                kline_list = kline_list[1:len(kline_list)]
                index_dict = {}
                kline_dick = {}
                n_kline_list = []
                for kline in kline_list:
                    field = kline.split(',')
                    trade_date = field[min_field_index['trade_date']]
                    kline_dick[trade_date] = kline
                    index_date = firstDateInSegment(trade_date, kLineType.upper())
                    value = index_dict.get(index_date, 'Empty')
                    if value == 'Empty':
                        index_dict[index_date] = []
                    index_dict[index_date].append(trade_date)
                    pass

                index_list = sorted(list(index_dict.keys()), key=lambda d: d, reverse=True)
                for index_date in index_list:
                    index_dict[index_date].sort()  # 一个周期内内k线按时间顺序排序
                    segment = []
                    for date in index_dict[index_date]:
                        segment.append(kline_dick[date])
                    kline = calc_segment_kline(segment)
                    n_kline_list.append(','.join(kline))
                file_name = code.upper() + '.' + kLineType + '.csv'
                outfile_path = '/'.join([output_path, mkt, kLineType.upper()])
                if not os.path.exists(outfile_path):
                    os.makedirs(outfile_path)
                outfile = outfile_path + '/' + file_name
                print(outfile)
                outfile_HD = open(outfile, "w")
                outfile_HD.write(title)
                outfile_HD.write('\n'.join(n_kline_list))
                outfile_HD.close()

def change_zz_filename(input_path):
    for type in os.listdir(input_path):
        for file_name in os.listdir('/'.join([input_path,type])):
            flag = file_name.split('.')[0][-3:]
            if flag == '000' or flag == '888':
                continue
            new_name = file_name[0:2]+file_name[3:]
            os.rename('/'.join([input_path,type,file_name]),'/'.join([input_path,type,new_name]))


'''修改K线中的值为正确的值'''
def full_kline_check(out_kline_path, tradeday_path, new_kline_path, mkt):
    for type in os.listdir('/'.join([out_kline_path, mkt])):
        for out_kline_name in os.listdir('/'.join([out_kline_path, mkt, type])):
            new_kline_all = ''
            new_kline_all += 'trade_date,forward_date,forward_time,backward_date,backward_time,open,high,low,close,volume,turnover,average,position,settlement,turnover_ratio\n'
            tradeday_name = out_kline_name.split('.')[0] + '.csv'
            print('/'.join([out_kline_path, out_kline_name]))
            file_kline_content = open('/'.join([out_kline_path, mkt, type, out_kline_name])).read().split('\n')
            tradeday_file = open('/'.join([tradeday_path, mkt, type, tradeday_name]))
            tradeday_content = tradeday_file.read().split('\n')
            num = 1
            for i in range(0, len(tradeday_content)):
                # for line in tradeday_file:
                line1_split = tradeday_content[i].split(',')
                tradeday1_date = line1_split[0] + line1_split[1] + line1_split[2]
                tradeday1_date = int(tradeday1_date)
                try:
                    line2_split = tradeday_content[i + 1].split(',')
                    tradeday2_date = int(line2_split[0] + line2_split[1] + line2_split[2])
                except:
                    tradeday2_date = tradeday1_date
                '''原K线的时间和tradeday里的时间相同，即tradeday里已经有这条K线'''
                if (int(file_kline_content[num].split(',')[0] +
                            file_kline_content[num].split(',')[1] +
                            file_kline_content[num].split(',')[2]) == tradeday1_date):
                    new_kline = ','.join([file_kline_content[num].split(',')[0], file_kline_content[num].split(',')[1],
                                          file_kline_content[num].split(',')[2], ',', line1_split[3], line1_split[4],
                                          line1_split[5], line1_split[6], line1_split[7], '0,0',
                                          line1_split[8].split('\n')[0], '0,0'])
                    new_kline_all += (new_kline + '\n')
                    num += 1
                try:
                    '''原K线中的时间在tradeday两条K线时间点中间，用tradeday里上一条的数据来补线'''
                    while (int(file_kline_content[num].split(',')[0] +
                                   file_kline_content[num].split(',')[1] +
                                   file_kline_content[num].split(',')[2]) < tradeday2_date
                           and int(file_kline_content[num].split(',')[0] +
                                       file_kline_content[num].split(',')[1] +
                                       file_kline_content[num].split(',')[2]) > tradeday1_date
                           or tradeday1_date == tradeday2_date):  # 两时间点相等，说明到最后一条了
                        new_kline = ','.join(
                            [file_kline_content[num].split(',')[0], file_kline_content[num].split(',')[1],
                             file_kline_content[num].split(',')[2], ',', line1_split[3], line1_split[4],
                             line1_split[5], line1_split[6], line1_split[7], '0,0', line1_split[8].split('\n')[0],
                             '0,0'])
                        new_kline += '\n'
                        new_kline_all += new_kline
                        num += 1
                except:
                    continue
            if not os.path.exists('/'.join([new_kline_path, mkt, type])):
                os.makedirs('/'.join([new_kline_path, mkt, type]))
            new_kline_file = open('/'.join([new_kline_path, mkt, type, out_kline_name]), 'w')
            new_kline_file.write(new_kline_all.rstrip('\n'))
            new_kline_file.close()


def postProcess(input_path, output_path, ktype_forder):
    # ktype_forder='DAY'

    for mkt in os.listdir(input_path):
        # if mkt not in ['SH']:
        #    continue
        for ktype in os.listdir('/'.join([input_path, mkt])):
            # if ktype not in ['1Day']:
            #    continue
            for file_name in os.listdir('/'.join([input_path, mkt, ktype])):
                infile = '/'.join([input_path, mkt, ktype, file_name])
                infile_hd = open(infile, 'r')
                kline = infile_hd.read().split('\n')
                infile_hd.close()
                title = kline[0]
                kline = kline[1:][::-1]
                outfile = '/'.join([output_path, mkt, ktype_forder, file_name])
                outfile_hd = open(outfile, 'w')
                outfile_hd.write(title + '\n')
                outfile_hd.write('\n'.join(kline))
                outfile_hd.close()
                print(infile)
    pass


def intiTradedateList(config):
    config['CCFX']["tradeday"] = []
    config['XSGE']["tradeday"] = []
    config['XDCE']["tradeday"] = []
    config['XZCE']["tradeday"] = []

    pass


def check_blank_trade(input_path):
    pass


step = 7

if 0 == step:
    detect(0)

'''将2016/6/20 9:31:00转换为 20160620,20160620,0931 计算交易日 统一精度，保留小数点后1位'''
input_path = "D:/lasthisdata"
output_path = "D:/OOOUT/tradeday"
if 1 == step:
    calc_tradeday(input_path, output_path)

input_path = "D:/OOOUT/tradeday"
output_path = "D:/OOOUT/static"
if 2 == step:
    static_tradeday_kline(input_path, output_path)
    check_blank_trade(input_path)

# 转换格式
input_path = "D:/OOOUT/2newtradeday"
output_path = "D:/OOOUT/HS_format"
if 3 == step:
    convert2HSFormat(input_path, output_path)

# 手工补全交易时间的信息
#到此即可************************************************************************
# 补齐数据
restday_path = './restday'
trade_time_section_info = "hs_trade_section.xml"
input_path = "D:/OOOUT/HS_format"
output_path = "D:/OOOUT/full_kline"
if 4 == step:
    loadRestday(restday_path, g_cfg)
    load_trade_info(trade_time_section_info, g_cfg)
    for mkt_name in ['XSGE', 'CCFX', 'XDCE', 'XZCE']:
        # if mkt_name not in ['XDCE']:
        # continue
        data_list = load_mkt_kline_data('/'.join([input_path, hsMkt2tradeName[mkt_name]]))
        for (file_name, kline_list) in data_list:
            # print(file_data)
            # kline_list=file_data.split('\n')
            # tradeday_dict=load_trade_data(kline_data)
            iret_list = load_trade_data(kline_list)
            if iret_list[0] == False:
                print(mkt_name, iret_list[1])
                continue
            trade_date_dict = iret_list[1]  # 历史未补齐的数据字典
            file_path = '/'.join([output_path, hsMkt2tradeName[mkt_name], '1Min', file_name])
            path = os.path.dirname(file_path)
            if not os.path.exists(path):
                os.makedirs(path)
            kline_trade_time_type = ''
            try:
                kline_trade_time_type = file_name.split('.')[0]
                #print(g_cfg[mkt_name]['code_trade_section'][file_name.split('.')[0].upper()])
            except KeyError:
                kline_trade_time_type = file_name.split('.')[0][0:2]+'000'

            fill_blank([mkt_name, kline_trade_time_type], file_path, trade_date_dict, g_cfg[mkt_name])
            # break
#不用做
out_kline_path = "D:/OOOUT/full_kline"
tradeday_path = "D:/OOOUT/2newtradeday"
new_kline_path = "D:/OOOUT/full_kline_new"
if 5 == step:
    full_kline_check(out_kline_path,tradeday_path,new_kline_path,"SH")

# 前后归
input_path = "D:/OOOUT/full_kline_new"
output_path = "D:/OOOUT/f2b"
if 6 == step:
    forword2backward(input_path, output_path)
pass

# 合成分钟线
input_path = "D:/code/F2B"
output_path = "D:/code/finally"
if 7 == step:
    calc_minute_kline(input_path, output_path)
pass

# 日级k线格式转换
input_path = "D:/22222/"
output_path = "D:/OOOUT/HS_format"
if 8 == step:
    convert2HSFormat(input_path, output_path, '1Day')
    pass

# 合成周月年线
input_path = "D:/OOOUT/HS_format"
output_path = "D:/OOOUT/finally"
if 9 == step:
    calcDayKline(input_path, output_path, 'week')
    calcDayKline(input_path, output_path, 'month')
    calcDayKline(input_path, output_path, 'year')
    pass

#
input_path = 'D:/OOOUT/HS_format'
output_path = 'D:/OOOUT/finally'
if 10 == step:
    input_path='D:/OOOUT/f2b'
    postProcess(input_path, output_path, 'DAY')
    postProcess(input_path,output_path,'MIN1')


# print(calc_month_tradeday('2015/12/58','2015/12/28','XDCE'))
# print(date_add('20121231',2))
# print(get_next_tradeday("2015/02/17","SH"))
#fill_everyday('E:/hisdata','E:/his')
# print(calc_month_tradeday('2012/9/1','2012/10/16','XSGE'))

def fill_one(in_path, out_path):
    for mkt in os.listdir(in_path):
        if mkt not in ['SH','DL']:
            pass
        for type in os.listdir('/'.join([in_path, mkt])):
            if type in ['1Day']:
                continue
            for name in os.listdir('/'.join([in_path, mkt, type])):
                if name not in ['AG1609.csv']:
                    pass
                file = open('/'.join([in_path, mkt, type, name]))
                content = file.read().split('\n')
                file.close()
                line1_time = content[0].split()[0]

                linelast_time = content[-2].split()[0]
                #linelast_time = '2016/09/30'
                #if linelast_time == '2016/09/13':   #最后一天如果有夜市需要修改一下日期，让程序把夜市的值copy过去
                    #linelast_time = '2016/08/15'
                print(line1_time, linelast_time, name)
                tradeday_list = calc_month_tradeday(line1_time, linelast_time, tradeMkt2hsMkt[mkt])
                new_content = ''
                i = 0
                for day in tradeday_list:
                    if day == '2015/11/09':
                        pass
                    insert_flag = False
                    if transferdate(day) < transferdate(content[i].split()[0]):
                        #new_content += (day + ' 10:00' + content[i - 1].split()[1][5:] + '\n')
                        temp_split = content[i - 1].split()[1].split(',')
                        new_content += (
                        day + ','.join([' 10:00', temp_split[4], temp_split[4], temp_split[4], temp_split[4], '0',
                                       temp_split[6]]) + '\n')
                        continue

                    if int(content[i].split()[1][0:2]) > 18 and insert_flag==False:
                        if i == 0:
                            pass
                        else:
                            #new_content += (day + ' 10:00' + content[i - 1].split()[1][5:] + '\n')
                            temp_split = content[i-1].split()[1].split(',')
                            new_content += (day + ','.join([' 10:00',temp_split[4],temp_split[4],temp_split[4],temp_split[4],'0',temp_split[6]])+'\n')
                            insert_flag = True

                    try:
                        last_day = ''
                        if content[i].split()[0] == '2015/09/19':
                            pass
                        while transferdate(day) >= transferdate(content[i].split()[0]):
                            if last_day!=content[i].split()[0] and int(content[i].split()[1].split(',')[0][0:2])>18 and transferdate(day) == transferdate(content[i].split()[0]) and insert_flag == False:
                                new_content += (day+','.join([' 10:00',content[i-1].split()[1].split(',')[4],content[i-1].split()[1].split(',')[4],content[i-1].split()[1].split(',')[4],content[i-1].split()[1].split(',')[4],'0',content[i-1].split()[1].split(',')[6]])+'\n')
                            new_content += content[i] + '\n'
                            last_day = content[i].split()[0]
                            i += 1
                        if transferdate(content[i-1].split()[0])!=transferdate(day):
                            new_content += (day+','.join([' 10:00',content[i-1].split()[1].split(',')[4],content[i-1].split()[1].split(',')[4],content[i-1].split()[1].split(',')[4],content[i-1].split()[1].split(',')[4],'0',content[i-1].split()[1].split(',')[6]])+'\n')
                    except:
                        print(name + ' done')
                if not os.path.exists('/'.join([out_path, mkt, type])):
                    os.makedirs('/'.join([out_path, mkt, type]))
                file = open('/'.join([out_path, mkt, type, name]), 'w')
                file.write(new_content)
                file.close()


def transferdate(date):
    date = date.split('/')
    date = date[0] + date[1] + date[2]
    return int(date)


#fill_one('D:/22222','D:/lasthisdata')


#change_trade_day('D:/OOOUT/tradeday','D:/OOOUT/newtradeday')

#cut_last_day('D:/OOOUT/newtradeday','D:/OOOUT/2newtradeday')

#change_zz_filename('D:/OOOUT/finally/ZZ')


