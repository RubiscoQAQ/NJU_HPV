import requests
import json
import time
import datetime
import app
from retrying import retry
from PIL import Image
from io import BytesIO
import ddddocr


getTaskApi = "http://ndyy.nju.edu.cn/NewWeb/Ashx/API_Appointment.ashx?action=selectUserRWList&page=1&limit=15&params="
selectDateApi = "http://ndyy.nju.edu.cn/NewWeb/Ashx/API_Appointment.ashx?action=selectRWRq"
selectTimeApi = "http://ndyy.nju.edu.cn/NewWeb/Ashx/API_Appointment.ashx?action=selectRWSjd"
selectApi = "http://ndyy.nju.edu.cn/NewWeb/Ashx/API_Appointment.ashx?action=insertUserYyjl"
home = "http://ndyy.nju.edu.cn/NewWeb/"
loginApi = "http://ndyy.nju.edu.cn/NewWeb/Ashx/API_Login.ashx?action=login"
picApi = "http://ndyy.nju.edu.cn/NewWeb/Ashx/Captcha.ashx?w=80&h=36"
requests = requests.session()
Type = 302
# 302=疫苗 901=核酸

@retry()
def getTaskList(taskId):
    api = getTaskApi+str(taskId)
    res = requests.get(api).text
    if len(res)==0:
        print('请更新cookies')
        print('尝试登录...')
        tryLogin()
        return ['请更新cookies']
    res = json.loads(res)
    lst = []
    for task in res['data']:
        dic = []
        d = datetime.datetime.strptime(task['预约任务开放时间'], '%Y/%m/%d %H:%M:%S').date()
        today = datetime.datetime.today().date()
        if ('九价' in str(task['预约任务名称']) and today == d) or taskId != 302:
            dic.append(task['预约任务开放时间'])
            dic.append(task['预约任务ID'])
            lst.append(dic)
    return lst

@retry()
def selectDate(task):
    api = selectDateApi
    dateLst = []
    taskList = []
    for i in task:
        taskList.append(i['taskNum'])
    for task in taskList:
        param = task+'^鼓楼'
        datas = {"params":param}
        res = json.loads(requests.post(api,data=datas).text)
        num = -1
        date = ''
        for element in res:
            #自动选择人数最大的
            if element['可预约人数']>num:
                date = element['日期']
                num = element['可预约人数']
        dateLst.append(date)
    return dateLst

@retry()
def selectTime(task,dateList):
    api = selectTimeApi
    paramList = []
    taskList = []
    for i in task:
        taskList.append(i['taskNum'])
    for i in range(0,len(taskList)):
        param = taskList[i]+"^鼓楼^"+dateList[i]
        datas = {"params": param}
        res = json.loads(requests.post(api, data=datas).text)
        num = -1
        time = ''
        for element in res:
            # 自动选择人数最大的
            if element['可预约人数'] > num:
                time = element['时间段']
                num = element['可预约人数']
        paramList.append(param+"^"+time)
    return paramList

@retry()
def tryInsert(paramList):
    api = selectApi
    resList = []
    for param in paramList:
        datas = {"params": param}
        res = requests.post(api,data=datas).text
        print('任务:'+str(param))
        print(str(res))
        if res != '1' and res != '您已预约该任务。':
            resList.append(param.split('^')[0])

    return resList

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
    while len(tasks)==0:
        print(datetime.datetime.now())
        print('请等待任务放出')
        tasks = getTaskList(Type)
    if tasks[0] == '请更新cookies':
        return
    res = ' '
    while True:
        nowTime = get_beijin_time()
        print(nowTime)
        taskId = 1
        for task in tasks:
            d = datetime.datetime.strptime(task[0], '%Y/%m/%d %H:%M:%S')
            target = datetime.datetime.timestamp(d)
            now = datetime.datetime.timestamp(nowTime)
            if int(now)-int(target)>-5:
                print('开始预约任务'+str(taskId)+':代码-'+str(task[1]))
                taskId += 1
                tasks.remove(task)
                dic = {'taskNum': task[1], 'maxTime': 10}
                taskList.append(dic)
            else:
                print('任务'+str(taskId)+'等待开始')
                taskId += 1
        if len(taskList)>0:
            paramList = selectTime(taskList,selectDate(taskList))
            res = tryInsert(paramList)
            if res == []:
                print('任务完成')
                break
            for i in res:
                for j in taskList:
                    if j['taskNum']==i:
                        j['maxTime']-=1
                        if j['maxTime']==0:
                            taskList.remove(j)
            if taskList == []:
                print('所有任务都已经尝试')
                break


def tryLogin():
    times = 0
    while True:
        try:
            initCookies()
            picMsg = requests.get(picApi)
            byte = BytesIO(picMsg.content)
            pic = ''
            if times > 10:
                print("请输入验证码:")
                image = Image.open(byte)
                image.show()
                pic = input()
            else:
                print("自动识别验证码...")
                ocr = ddddocr.DdddOcr()
                pic = ocr.classification(byte.getvalue())


            datas = {"params":readUser()+"^"+pic}
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            }
            res = requests.post(loginApi,data=datas,headers=headers)
            if res.status_code==500:
                changeCookies()
                res = requests.post(loginApi, data=datas, headers=headers)
                if res.status_code == 500:
                    print("请手动登陆并设置cookies,登录后，输入<确认>继续")
                    temp = input()
                    if '确认' in temp:
                        app.startOnTime()
                    break
            elif '验证码' in res.text:
                times+=1
            elif '密码' in res.text:
                print('密码错误')
                print('请输入账号:', end='')
                uid = input()
                print('请输入密码:', end='')
                pwd = input()
                setUser(uid, pwd)
            else:
                print("登录成功")
                times = 0
                startOnTime()
                break
        except Exception:
            print("请手动登陆并设置cookies")

def readUser():
    with open('userMsg','r') as f:
        content = f.read()
        if len(content)==0:
            print('首次使用请输入账号:',end='')
            uid = input()
            print('请输入密码:', end='')
            pwd = input()
            setUser(uid,pwd)
            return uid+"^"+pwd
        return content

def setUser(uid, pwd):
    with open('userMsg', 'w') as f:
        content = uid+"^"+pwd
        f.write(content)


def changeCookies():
    session = requests.get(home).cookies.get("ASP.NET_SessionId")


def initCookies():
    session = requests.get(home).cookies.get("ASP.NET_SessionId")
