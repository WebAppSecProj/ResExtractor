# Andromo Android Rev
作者：beizishaozi，如需转载请注明出处
## 目录
+ 简述
+ 应用特征描述
+ 资源数据提取
+ 结论

## 简述
Andromo框架只支持Android应用开发，不支持iOS应用。该框架支持在线开发，需创建账户。对于试用，只支持三次app创建并且每个app只能有效7天，并且不能自定义包名。在线开发网址：https://builder.andromo.com。通过该框架创建应用时，用户是通过添加不同的activity来创建页面、上传网页信息和创建URL链接。支持的Activity列表如下：
<div align=left><img src="./image/Andromo/Andromo_activities.png"/></div>
其中Custom Page是用于创建页面，创建的页面也是保存在assets目录下。<br>
HTML Archive是上传网页信息，它会保存在assets目录下。<br>
Website,About,RSS则是通过填入URL链接进行加载，URL链接保存在res/values/strings.xml文件中。但是About模块的URL都是通过浏览器打开，并不是由应用打开，因此这部分URL不再提取范围内。后续视情况可添加<br>
Photo gallery和PDF document则是上传照片和PDF文件。<br>
另外开发应用时，不支持对这些资源信息进行加密处理。
Andromo相关信息参考：http://www.andromo.com/。
<br><br>

## 应用特征描述
对基于该框架生成的应用进行逆向分析。考虑到该框架的支付方案是允许自定义包名，因此其主Activity上不存在独一无二的特征。但是在assets目录下存在一个文件consentform.html，该文件在应用开发时无法由开发人员修改、删除，因此将该文件作为基于Andromo框架开发的应用特征。<br>
同时考虑到该框架在实际使用时只有进行付费才能持续使用app，因此不确定，如果使用付费开发，consentform.html文件是不是就存在修改、删除等操作。从开发流程上来分析，没有发现任何相关说明。<br><br>

## 资源数据提取
正如“简述”部分所说，创建的页面和上传的页面信息都保存在assets目录下，而创建的URL链接则是保存在res/values/strings.xml文件中。因此，需要将这两部分信息提取出来，URL链接信息单独保存在extract_info.json文件中。<br><br>

## 结论
Andromo框架支持基于web的Android应用开发，但是该框架没有提供加密功能，因此定位到存储资源数据的目录直接解压缩进行提取即可，比较方便。