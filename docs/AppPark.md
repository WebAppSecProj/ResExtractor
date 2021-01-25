AppPark Android Rev
作者：beizishaozi，如需转载请注明出处
## 目录
+ 简述
+ 应用特征描述
+ 资源数据提取
+ 结论

## 简述
AppPark提供在线制作、一键生成应用的功能。它分四步生存应用，如下图所示
<div align=left><img src="./image/AppPark/apppark_gen.png"/></div>
第一步提供了很多模板，但是很多模板都是VIP收费的
<div align=left><img src="./image/AppPark/apppark_theme.png"/></div>
第二步和第三步则是对模板内的页面进行编辑，它提供了很多控件，但大部分控件都是vip专用
<div align=left><img src="./image/AppPark/apppark_widget.png"/></div>
开发人员根据应用需要进行编辑即可。
为了分析AppPark框架，选择网站上提供的案例进行逆向分析。

## 应用特征描述
通过对案例app进行逆向分析，发现这些包名都是以“cn.apppark.”为前缀，其他无明显特征。
<div align=left><img src="./image/AppPark/apppark_package.png"/></div>

## 资源数据提取
通过对案例app进行逆向分析，发现有些应用会将图片和json文件保存在目录assets/initFiles中，有些应用则不保存任意信息在本地。除此之外，还有很多资源信息通过http请求从AppPark运营管理平台（https://cms.apppark.cn）获取，通过指定不同的参数可以获取各种信息，包括图片、网页等。这样的http请求包括https://cms.apppark.cn/v2.0/push.ws, https://cms.apppark.cn/v2.0/InfoRelease.ws, https://cms.apppark.cn/v2.0/info.ws, https://cms.apppark.cn/v2.0/cms.ws, https://cms.apppark.cn/v2.0/takeAwayProduct.ws等，同时配合不同的参赛值，可获取不同的资源信息。具体可以通过hook应用类中cn.apppark.vertify.network.request.WebServiceRequest中方法Ksoap2ForString(String arg1, String arg2, String arg3, String arg4, String arg5, boolean arg6),参数包括了访问的url链接以及请求参数，返回值则是响应包。在实际提取时，对于从AppPark运营管理平台获取的资源信息不在提取范围之内，只提取本地资源信息。

## 结论
应用大部分资源都是保存在AppPark运营管理平台，需要通过访问这个平台获取，而且每个资源几乎都需要访问，类似于将资源文件信息都保存在远程服务器上，要获取这些资源，需要构建很多不同的URL链接才可以，较为复杂，因此只提取应用本地保存的资源。