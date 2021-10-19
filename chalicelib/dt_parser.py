import re
import calendar
# import jieba
# import jieba.posseg as pseg
import datetime
from dateutil.relativedelta import relativedelta
from opencc import OpenCC

cc = OpenCC('tw2s')

# jieba.add_word("小时", tag='t')
# jieba.add_word("分钟", tag='t')
#
#
# def cut_text(s):
#     sp = cc.convert(s)
#     words = pseg.cut(sp)
#     a = ''
#     for word, flag in words:
#         # print('%s %s' % (word, flag))
#         if flag in ['x', 'm', 't', 'f']:
#             a += word
#     # print(a)
#     return a

num_dic = {
    '零': '0',
    '一': '1',
    '二': '2',
    '两': '2',
    '三': '3',
    '四': '4',
    '五': '5',
    '六': '6',
    '七': '7',
    '八': '8',
    '九': '9'
}

unit_dic = {
    '十': 10,
    '百': 100,
    '千': 1000
}


def parse_year(time_str, dt_obj):
    # ---------- if year is implied ---------- #
    implied_words = {
        "明年": 1,
        "后年": 2
    }

    for implied_word in implied_words.keys():
        if implied_word in time_str:
            dt_obj = dt_obj + relativedelta(years=implied_words[implied_word])
            return dt_obj

    # ---------- if year is explicit ---------- #
    match_obj = re.search(r'([0-9零一二两三四五六七八九十]+年)', time_str)
    if match_obj:
        chinese_year = match_obj[0][:-1]
        number_year = ""
        for chinese_char in chinese_year:
            if chinese_char in num_dic:
                number_year += num_dic[chinese_char]
            else:
                number_year += chinese_char
        dt_obj = dt_obj + relativedelta(year=int(number_year))
        return dt_obj

    return dt_obj


def parse_month(time_str, dt_obj):

    # ---------- if month is implied ---------- #
    implied_words = {
        "下个月": 1
    }

    for implied_word in implied_words.keys():
        if implied_word in time_str:
            dt_obj = dt_obj + relativedelta(months=implied_words[implied_word])
            return dt_obj

    # ---------- if year is explicit ---------- #
    num_dic["十"] = "10"
    num_dic["十一"] = "11"
    num_dic["十二"] = "12"

    match_obj = re.search(r'([0-9一二三四五六七八九十]+月)', time_str)

    if match_obj:
        chinese_month = match_obj[0][:-1]
        if chinese_month.isdigit():
            dt_obj = dt_obj + relativedelta(month=int(chinese_month))
        else:
            number_month = num_dic[chinese_month]
            dt_obj = dt_obj + relativedelta(month=int(number_month))

        num_dic.pop("十")
        num_dic.pop("十一")
        num_dic.pop("十二")

        return dt_obj

    return dt_obj


def parse_date(time_str, dt_obj):

    # ---------- if day is implied ---------- #
    implied_words = {
        "明天": 1,
        "后天": 2,
        "大后天": 3
    }

    for implied_word in implied_words.keys():
        if implied_word in time_str:
            dt_obj = dt_obj + relativedelta(days=implied_words[implied_word])
            return dt_obj


    match_obj = re.search(r'([0-9一二两三四五六七八九十百千]+天后)', time_str)
    if match_obj:
        chinese_day = match_obj[0][:-2]
        if chinese_day.isdigit():
            number_day = int(chinese_day)
        else:
            number_day = 0
            for chinese_char in chinese_day:
                if chinese_char in num_dic:
                    number_day += int(num_dic[chinese_char])
                elif chinese_char in unit_dic:
                    if number_day == 0:
                        number_day = 1
                    number_day = number_day * unit_dic[chinese_char]
                else:
                    number_day += int(chinese_char)
        dt_obj = dt_obj + relativedelta(days=number_day)
        return dt_obj

    # ---------- if day is explicit ---------- #
    match_obj = re.search(r'([0-9零一二两三四五六七八九十]+[日号])', time_str)
    if match_obj:
        chinese_day = match_obj[0][:-1]
        if chinese_day.isdigit():
            number_day = int(chinese_day)
        else:
            number_day = 0
            for chinese_char in chinese_day:
                if chinese_char in num_dic:
                    number_day += int(num_dic[chinese_char])
                elif chinese_char in unit_dic:
                    if number_day == 0:
                        number_day = 1
                    number_day = number_day * unit_dic[chinese_char]
                else:
                    number_day += int(chinese_char)
        dt_obj = dt_obj + relativedelta(day=number_day)
        return dt_obj

    return dt_obj


def parse_weekday(time_str, dt_obj):

    # ---------- if weekday is implied ---------- #
    # implied_words = {
    #
    # }
    #
    # for implied_word in implied_words.keys():
    #     if implied_word in time_str:
    #         dt_obj + relativedelta(days=implied_words[implied_word])
    #         return dt_obj

    # ---------- if weekday is explicit ---------- #

    week_day_dic = {
        "1": calendar.MONDAY,
        "2": calendar.TUESDAY,
        "3": calendar.WEDNESDAY,
        "4": calendar.THURSDAY,
        "5": calendar.FRIDAY,
        "6": calendar.SATURDAY,
        "7": calendar.SUNDAY,
        "一": calendar.MONDAY,
        "二": calendar.TUESDAY,
        "三": calendar.WEDNESDAY,
        "四": calendar.THURSDAY,
        "五": calendar.FRIDAY,
        "六": calendar.SATURDAY,
        "天": calendar.SUNDAY,
        "日": calendar.SUNDAY
    }

    match_obj = re.search(r'((?:星期|礼拜|週)[1-7一二三四五六天日])', time_str)
    if match_obj:
        print(match_obj[0])
        chinese_weekday = match_obj[0][-1]
        number_weekday = week_day_dic[chinese_weekday]
        new_dt_obj = dt_obj + relativedelta(weekday=number_weekday)
        if new_dt_obj == dt_obj:
            new_dt_obj = dt_obj + relativedelta(days=1, weekday=number_weekday)
        return new_dt_obj

    return dt_obj


def parse_hour(time_str, dt_obj):

    # ---------- if hour is implied ---------- #
    implied_words = {
        "早上": 9,
        "中午": 12,
        "下午": 15,
        "晚上": 20,
        "今晚": 20,
        "傍晚": 18,
        "半夜": 0
    }

    match_obj = re.search(r'([0-9一二两三四五六七八九十百千]+小时后)', time_str)
    if match_obj:
        chinese_hour = match_obj[0][:-3]
        if chinese_hour.isdigit():
            number_hour = int(chinese_hour)
        else:
            number_hour = 0
            for chinese_char in chinese_hour:
                if chinese_char in num_dic:
                    number_hour += int(num_dic[chinese_char])
                elif chinese_char in unit_dic:
                    if number_hour == 0:
                        number_hour = 1
                    number_hour = number_hour * unit_dic[chinese_char]
                else:
                    number_hour += int(chinese_char)
        dt_obj = dt_obj + relativedelta(hours=number_hour)
        return dt_obj

    # ---------- if hour is explicit ---------- #
    match_obj = re.search(r'([0-9一二两三四五六七八九十]+[点时])', time_str)
    if match_obj:
        chinese_hour = match_obj[0][:-1]
        if chinese_hour.isdigit():
            number_hour = int(chinese_hour)
        else:
            number_hour = 0
            for chinese_char in chinese_hour:
                if chinese_char in num_dic:
                    number_hour += int(num_dic[chinese_char])
                elif chinese_char in unit_dic:
                    if number_hour == 0:
                        number_hour = 1
                    number_hour = number_hour * unit_dic[chinese_char]
                else:
                    number_hour += int(chinese_char)

        if '点半' in time_str:
            dt_obj = dt_obj + relativedelta(minute=30)

        if '晚上' in time_str or '下午' in time_str:
            dt_obj = dt_obj + relativedelta(hour=number_hour+12)
            return dt_obj

        dt_obj = dt_obj + relativedelta(hour=number_hour)
        return dt_obj

    for implied_word in implied_words.keys():
        if implied_word in time_str:
            dt_obj = dt_obj + relativedelta(hour=implied_words[implied_word])
            return dt_obj

    if '后' in time_str and '后天' not in time_str:
        return dt_obj

    dt_obj = dt_obj + relativedelta(hour=8)

    return dt_obj


def parse_minute(time_str, dt_obj):

    # ---------- if minute is implied ---------- #
    # implied_words = {
    #
    # }
    #
    # for implied_word in implied_words.keys():
    #     if implied_word in time_str:
    #         dt_obj = dt_obj + relativedelta(minutes=implied_words[implied_word])


    match_obj = re.search(r'([0-9一二两三四五六七八九十百千]+分钟后)', time_str)
    if match_obj:
        chinese_minute = match_obj[0][:-3]
        if chinese_minute.isdigit():
            number_minute = int(chinese_minute)
        else:
            number_minute = 0
            for chinese_char in chinese_minute:
                if chinese_char in num_dic:
                    number_minute += int(num_dic[chinese_char])
                elif chinese_char in unit_dic:
                    if number_minute == 0:
                        number_minute = 1
                    number_minute = number_minute * unit_dic[chinese_char]
                else:
                    number_minute += int(chinese_char)
        dt_obj = dt_obj + relativedelta(minutes=number_minute)
        return dt_obj

    # ---------- if minute is explicit ---------- #
    match_obj = re.search(r'([0-9零一二两三四五六七八九十]+[分])', time_str)
    if match_obj:
        chinese_minute = match_obj[0][:-1]
        if chinese_minute.isdigit():
            number_minute = int(chinese_minute)
        else:
            number_minute = 0
            for chinese_char in chinese_minute:
                if chinese_char in num_dic:
                    number_minute += int(num_dic[chinese_char])
                elif chinese_char in unit_dic:
                    if number_minute == 0:
                        number_minute = 1
                    number_minute = number_minute * unit_dic[chinese_char]
                else:
                    number_minute += int(chinese_char)
        dt_obj = dt_obj + relativedelta(minute=number_minute)
        return dt_obj

    match_obj = re.search(r'(早上|下午|晚上)?([0-9零一二两三四五六七八九十]+)?[点]([0-9零一二两三四五六七八九十]+)?[分]', time_str)
    if match_obj:
        chinese_minute = match_obj[0][:-1]
        if chinese_minute.isdigit():
            number_minute = int(chinese_minute)
        else:
            number_minute = 0
            for chinese_char in chinese_minute:
                if chinese_char in num_dic:
                    number_minute += int(num_dic[chinese_char])
                elif chinese_char in unit_dic:
                    if number_minute == 0:
                        number_minute = 1
                    number_minute = number_minute * unit_dic[chinese_char]
                else:
                    number_minute += int(chinese_char)
        dt_obj = dt_obj + relativedelta(minute=number_minute)

        return dt_obj



    if '后' in time_str and '后天' not in time_str:
        return dt_obj

    if '点半' in time_str:
        return dt_obj

    dt_obj = dt_obj + relativedelta(minute=0)

    return dt_obj


def print_dt(dt_obj):
    temp = dt_obj.strftime("%Y %b %d %a %H %M")
    print(temp)


def dt_convert(s):
    s = cc.convert(s)
    print("inside dt_convert")
    dt = datetime.datetime.utcnow()
    dt = dt + relativedelta(hours=8)
    # s = cc.convert(s)

    print("before parse:" + dt.strftime("%Y%m%d%H%M"))

    dt = parse_year(s, dt)
    dt = parse_month(s, dt)
    dt = parse_date(s, dt)
    dt = parse_weekday(s, dt)
    dt = parse_hour(s, dt)
    dt = parse_minute(s, dt)

    print("after parse:" + dt.strftime("%Y%m%d%H%M"))

    dt = dt - relativedelta(hours=8)
    # print_dt(dt)
    # temp = dt.astimezone(tz.gettz('UTC'))
    # print_dt(temp)
    #
    # print(temp.strftime("%Y%m%d%H%M"))
    return dt.strftime("%Y%m%d%H%M")

# print(dt_convert(cc.convert("3點半叫我")))