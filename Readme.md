# 使用说明

> version：1.0
>
> Rubisco

## 脚本设置

脚本目前提供两个功能：预约核酸和预约九价疫苗。这是在Type中定义的。

```Python
Type = 901
# 302=疫苗 901=核酸
```

## 脚本逻辑

**系统整体使用失败重试，如果出现连接超时会自动重新尝试**

- 脚本会爬取当前栏目（901、302）下所有的可预约项目,然后获取他们的开始预约时间和任务ID。
- 获取北京时间，当北京时间距离开始时间小于10秒时，开始进行轮询，试图预约
- 在预约时间和地点时，地点默认选择鼓楼，时间选择当前可用人数最多的时间。
- 在生成完整的参数后，系统会自动提交预约请求。

## 脚本使用

**提前在ndyy上进行登陆**，即下图

![](Readme.assets/QQ%E6%88%AA%E5%9B%BE20220516172625.png)

在登陆后，尝试直接运行脚本。一些正常的提示信息如下

![](Readme.assets/QQ%E6%88%AA%E5%9B%BE20220516172758.png)

![QQ截图20220516172819](Readme.assets/QQ%E6%88%AA%E5%9B%BE20220516172819.png)

![QQ截图20220516172845](Readme.assets/QQ%E6%88%AA%E5%9B%BE20220516172845.png)

分别代表已经预约、成功预约和已经没有名额。

![](Readme.assets/QQ%E6%88%AA%E5%9B%BE20220516173127.png)

如果出现上图报错，请参照下面的教程

## 更新cookies

使用浏览器，在ndyy界面，按F12按键，进入控制台。

![](Readme.assets/QQ%E6%88%AA%E5%9B%BE20220516173324.png)

选择应用

![](Readme.assets/QQ%E6%88%AA%E5%9B%BE20220516173405.png)

选择cookies

![](Readme.assets/QQ%E6%88%AA%E5%9B%BE20220516173425.png)

将如图数值替换掉脚本中的数值

![](Readme.assets/QQ%E6%88%AA%E5%9B%BE20220516173446.png)

![](Readme.assets/QQ%E6%88%AA%E5%9B%BE20220516173616.png)

> version 2.0

# 新版本

新版本提供了新的处理方式，不再需要手动登陆。

## 设置

新版本的设置抽取到`设置`文件中，关键词有：自动、手动、核酸、疫苗。可以通过txt打开，修改实现变更设置。默认是自动登录、预约核酸

## 用户信息

用户信息保存在userMsg文件中，请在传播本文件前确保userMsg不包含自己的账号信息。系统在第一次打开时会要求输入密码，可以选择忽略掉这个配置文件。

**但是如果有需求，可以自行更改这个配置文件从而达到切换登陆用户的目的**

### cookie

新版本自动登录不再需要使用cookies，但是如果使用`手动登陆`，你需要将cookies的值放在这个文件中。

## 更新内容

- 将request替换为session，从而使得请求之间从独立的变成能够携带cookies信息的请求。

- 利用ddddocr库实现自动识别验证码

- 如果10次都不能正确识别，将弹出一个图片，要求用户手工识别（我还没有见过这种情况，因此也没有测试）



