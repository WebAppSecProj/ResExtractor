# SeattleCloud Android Rev
作者：beizishaozi，如需转载请注明出处
## 目录
+ 简述
+ 应用特征描述
+ 资源数据提取
+ 结论

## 简述
Seattle Cloud支持iPhone,iPad,Android,Kindle平台的应用开发，开发步骤简单明了。
<div align=left><img src="./image/SeattleCloud/seattlecloud_developstep.png"/></div>
一共有四步。第一步是选择模板，Seattle Cloud提供了几十个模板
<div align=left><img src="./image/SeattleCloud/seattlecloud_muban.png"/></div>
选定模板之后，第二步就是进行编辑和配置
<div align=left><img src="./image/SeattleCloud/seattlecloud_pages.png"/></div>
这里提供了多个APP PAGES，从截图来看，PAGE TYPE共有29*8个，有些PAGE是支持可以本地编辑网页资源文件也可以填入URL链接。
最后两步就是生成和发布应用，生成应用是需要收费的，但是该框架提供了一个安卓应用，能提供预览功能，可以参考。<br><br>

## 应用特征描述
通过关键词搜索，在virustotal和google play上发现了若干使用了该框架进行开发的应用。通过对这些应用进行反编译分析，这些应用的主Activity名字是确定的，固定为“com.seattleclouds.AppStarterActivity”。因此将该名字作为应用特征进行检索。另外，需要说明的是，对这些应用反编译之后的代码结构以及资源文件进行对比，是相对很类似的，才将其确定为这些应用是使用了框架开发，并根据关键词确定框架为Seattle Cloud。<br><br>

## 资源数据提取
该框架虽然不支持免费生成应用，但是对应用编辑的内容支持下载。下载之后是一个压缩包，其中包括了测试开发时配置的资源文件以及其他一些文件。其中有一个app.xml文件，它罗列出了资源文件信息和配置信息等内容，测试开发时的网页资源文件都可以从app.xml文件中获取，包括添加的URL链接，只是添加的URL链接也是保存在一个HTML文件中。如下图所示
<div align=left><img src="./image/SeattleCloud/seattlecloud_url.png"/></div>
图中标红部分为添加的url链接。
<br>
此外，对于这些信息没有进行任何加密处理，可以直接根据app.xml进行提取即可。
<div align=left><img src="./image/SeattleCloud/seattlecloud_appxml.png"/></div>
途中标红区域即为第二步中所有配置的PAGE信息，按照顺序依次提取即可，这些PAGE页面和app.xml均保存在assets/Main目录中。<br><br>

## 结论
Seattle Cloud框架支持模块化的Android和iOS应用开发，并且该框架也没有提供加密功能，因此为了提取网页资源信息，只需要从assets/Main目录中提取即可。