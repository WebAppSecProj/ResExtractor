MIT App Inventor Android Rev
作者：beizishaozi，如需转载请注明出处
## 目录
+ 简述
+ 应用特征描述
+ 资源数据提取
+ 结论

## 简述
App Inventor是一个基于云的工具，开发人员可以通过浏览器开发Android应用，但不支持开发iOS应用。App Inventor介绍参考http://appinventor.mit.edu/about-us。App Inventor提供了众多组件可以进行app界面设计，多媒体设计等，具体参考下图左侧列表
<div align=left><img src="./image/AppInventor/appinventor_designer.png"/></div>
此外，App Inventor提供了blocks进行app程序编码，如下图所示
<div align=left><img src="./image/AppInventor/appinventor_blocks.png"/></div>
具体开发指导参考http://appinventor.mit.edu/explore/get-started。这种方式不需要直接进行java编码，由平台生成相关的java代码。
因此该框架提供了丰富的功能，并不局限于开发web应用。
<br><br>

## 应用特征描述
对使用该框架生成的应用进行反编译，其AndroidManifest.xml如下图所示
<div align=left><img src="./image/AppInventor/appinventor_manifest.png"/></div>
经分析，其application的名字是”com.google.appinventor.components.runtime.multidex.MultiDexApplication“，该名字是确定的，因此将名字作为应用特征即可。
<br><br>

## 资源数据提取
在使用该框架时，发现该框架提供webiewer组件，支持填入任意URL链接，并将其硬编码在程序代码中。同时，也支持上传文件到assets目录下本地保存，然后通过webviewer进行展示。这两部分信息是项目所关注的，正是需要提取的资源数据。对于资源数据信息，App Inventor框架都是直接明文存储的，因此对于URL链接，通过反编译apk文件从主Activity的smali代码中读取，对于资源文件信息则是从assets目录下直接提取即可，比较方便。<br><br>

## 结论
App Inventor框架支持基于web的Android应用功能开发，但是该框架没有提供加密功能，因此定位到存储资源数据的目录直接解压缩进行提取即可，比较方便。

