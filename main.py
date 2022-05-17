import appWithSession
import app



if __name__ == '__main__':
    Type = 901
    # 302=疫苗 901=核酸
    Mode = 1
    # 0=自动登陆，1=手动登陆
    with open('设置','r',encoding='utf-8') as f:
        content = f.read()
        if '手动' in content:
            Mode = 1
        else:
            Mode = 0
        if '核酸' in content:
            Type = 901
        else:
            Type = 302
    app.Type = Type
    appWithSession.Type = Type
    if Mode==0:
        appWithSession.tryLogin()
    else:
        print('请注意，一般而言，手动登陆意味着要设置cookie，请仔细阅读readme')
        input('按任意键继续')
        app.startOnTime()
    input('任务完成,按任意键继续')