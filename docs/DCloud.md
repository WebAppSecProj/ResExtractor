# Dcloud
如需转载请注明出处
+ 简述
+ 应用特征描述
+ 资源数据提取
+ 结论

## 简述
uni-app(即DCloud)是一个使用 Vue.js 开发所有前端应用的框架，开发者编写一套代码，可发布到iOS、Android、Web（响应式）、以及各种小程序（微信/支付宝/百度/头条/QQ/钉钉/淘宝）、快应用等多个平台。

<br>
<br>

## 应用特征描述

### Android
DCloud开发的Android应用的主要特征为其主Activity的名字为固定"io.dcloud.PandoraEntry"。

### iOS
DCloud开发的iOS应用的主要特征为其Bundle Identifier以io.dcloud开头

## 资源数据提取
### Android
DCloud开发的Android应用的资源文件在assets/apps/{appid}/www/目录下，其中appid需要通过读取assets/data/dcloud_control.xml中获取。

应用的入口页面则可以通过读取资源文件中的manifest.json中的launch_path即可获得


### iOS
iOS相关的资源文件则是在应用目录下的Pandora/apps/{appid}/www目录下，其中appid需要通过应用目录下的control.xml进行读取。

应用的入口页面可以通过读取资源文件中的manifest.json中的launch_path即可获得.

## 结论
DCloud的本地资源未经过加密，因此直接进行提取即可。