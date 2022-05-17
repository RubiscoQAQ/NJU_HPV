import requests
import json
import time
import datetime
from retrying import retry

getTaskApi = "http://ndyy.nju.edu.cn/NewWeb/Ashx/API_Appointment.ashx?action=selectUserRWList&page=1&limit=15&params="
selectDateApi = "http://ndyy.nju.edu.cn/NewWeb/Ashx/API_Appointment.ashx?action=selectRWRq"
selectTimeApi = "http://ndyy.nju.edu.cn/NewWeb/Ashx/API_Appointment.ashx?action=selectRWSjd"
selectApi = "http://ndyy.nju.edu.cn/NewWeb/Ashx/API_Appointment.ashx?action=insertUserYyjl"


def readCookie():
    with open('cookie', 'r') as f:
        return f.read()


cookie = {"ASP.NET_SessionId": readCookie()}

Type = 901


# 302=疫苗 901=核酸

@retry()
def getTaskList(taskId):
    api = getTaskApi + str(taskId)
    res = requests.get(api, cookies=cookie).text
    if len(res) == 0:
        print('请更新cookies')
        return ['请更新cookies']
    res = json.loads(res)
    lst = []
    for task in res['data']:
        dic = []
        if '九价' in str(task['预约任务名称']) or task != 302:
            dic.append(task['预约任务开放时间'])
            dic.append(task['预约任务ID'])
            lst.append(dic)
    return lst


@retry()
def selectDate(taskList):
    api = selectDateApi
    dateLst = []
    for task in taskList:
        param = task + '^鼓楼'
        datas = {"params": param}
        res = json.loads(requests.post(api, data=datas, cookies=cookie).text)
        num = -1
        date = ''
        for element in res:
            # 自动选择人数最大的
            if element['可预约人数'] > num:
                date = element['日期']
                num = element['可预约人数']
        dateLst.append(date)
    return dateLst


@retry()
def selectTime(taskList, dateList):
    api = selectTimeApi
    paramList = []
    for i in range(0, len(taskList)):
        param = taskList[i] + "^鼓楼^" + dateList[i]
        datas = {"params": param}
        res = json.loads(requests.post(api, data=datas, cookies=cookie).text)
        num = -1
        time = ''
        for element in res:
            # 自动选择人数最大的
            if element['可预约人数'] > num:
                time = element['时间段']
                num = element['可预约人数']
        paramList.append(param + "^" + time)
    return paramList


@retry()
def tryInsert(paramList):
    api = selectApi
    for param in paramList:
        datas = {"params": param}
        res = requests.post(api, data=datas, cookies=cookie).text
        if res == '1':
            return "成功"
        return res


@retry()
def get_beijin_time():
    try:
        url = 'http://beijing-time.org/'
        request_result = requests.get(url=url)
        if request_result.status_code == 200:
            headers = request_result.headers
            net_date = headers.get("date")
            gmt_time = time.strptime(net_date[5:25], "%d %b %Y %H:%M:%S")
            bj_timestamp = int(time.mktime(gmt_time) + 8 * 60 * 60)
            return datetime.datetime.fromtimestamp(bj_timestamp)
    except Exception as exc:
        return datetime.datetime.now()


def startOnTime():
    taskList = []
    tasks = getTaskList(Type)
    if tasks[0] == '请更新cookies':
        return
    res = ' '
    while True:
        nowTime = get_beijin_time()
        print(nowTime)
        for task in tasks:
            d = datetime.datetime.strptime(task[0], '%Y/%m/%d %H:%M:%S')
            target = datetime.datetime.timestamp(d)
            now = datetime.datetime.timestamp(nowTime)
            if int(now) - int(target) > -10:
                tasks.remove(task)
                taskList.append(task[1])
        if len(taskList) > 0:
            res = tryInsert(selectTime(taskList, selectDate(taskList)))
        print(res)
        if res == '成功' or res == '您已预约该任务。' or res is None:
            break
