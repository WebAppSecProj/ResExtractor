# Apps Geyser Android Rev
作者：beizishaozi，如需转载请注明出处
## 目录
+ 简述
+ 应用特征描述
+ 资源数据提取
+ 结论

## 简述
Apps Geyser框架只支持Android应用开发，不支持iOS应用。该框架支持在线开发，需创建账户，不限制开发应用数量。在线开发网址：https://appsgeyser.com/create/start/。 该框架支持两种模式来开发应用，一种是商业模式，一种是个人模式，不同模式支持的app是不同的。对于商业模式，支持app类型如下表所示
<div align=left><img src="./image/AppsGeyser/appsgeyser_busniss.png"/></div>
Businiss Website、Affliate Refferal Link和RSS都是通过添加URL链接即可。<br>
Page和HTML Code则是编写HTML页面，保存在应用assets目录下。<br>
其他两个则是要求与具体应用链接相关，YouTube要求填入YouTube的API key；Facebook Page则要求填入Facebook域名的URL链接。<br>
个人模式支持的app形式更多，如下图所示
<div align=left><img src="./image/AppsGeyser/appsgeyser_individual.png"/></div>
经测试，提供的app创建功能包括填入URL链接方式、编写HTML网页和上传网页资源压缩包（要求根目录下包括index.html页面）这三种方式。
具体信息参考在线开发网址即可。<br><br>

## 应用特征描述
对基于该框架生成的应用进行逆向分析。发现其主Activity的名字是确定的，即“com.appsgeyser.multiTabApp.MainNavigationActivity”。因此，将该主Activity名字作为基于Apps Geyser框架开发的应用特征。<br><br>


## 资源数据提取
Apps Geyser框架不支持对资源数据进行加密，因此相对来说提取工作比较方便。
正如“简述”部分所说，编写的HTML页面和上传的网页资源压缩包都保存在assets目录下，而应用起始页URL链接则是保存在res/raw/configuration.xml文件中，如下图所示。
<div align=left><img src="./image/AppsGeyser/appsgeyser_startpage.png"/></div>
同时对于只填入URL链接的方式，则将该URL链接作为应用起始页URL链接，只需要从文件res/raw/configuration.xml中读取即可。<br><br>

## 结论
Apps Geyser框架支持基于web的Android应用开发，但是该框架没有提供加密功能，因此定位到存储资源数据的目录直接解压缩进行提取即可。