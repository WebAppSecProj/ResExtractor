# APICloud iOS Rev

---
作者：pshad0w，如需转载请注明出处

## 简述
由于在使用APICloud框架生成iOS应用时，开发者可以选择对打包的资源进行加密，这导致我们无法直接获取明文的资源，所以我们对整个框架做了逆向分析，还原了资源的解密过程
<div align=center><img src="./image/APICloud/apicloud-1.jpg"/></div>

以下内容以`朝阳到家`应用为例，该应用可以从`App Store`下载

<!--more-->

### 1. 定位解密函数
首先dump应用并解压ipa包，得到应用的主二进制文件`UZApp`。丢到ida64进行分析，发现应用在启动时需要加载资源文件，并在加载时对资源文件进行解密。尝试使用字符串的方式定位解密函数。尝试搜索关键字`encrypt`，得到如下结果
<div align=center><img src="./image/APICloud/apicloud-2.jpg"/></div>

由函数类名猜测解密方法在`UZWidget`或者`UZAES`中，挑选第一个方法跟进，发现解密处理在`fileDataInWidget:`方法中
<div align=center><img src="./image/APICloud/apicloud-3.jpg"/></div><br>
<div align=center><img src="./image/APICloud/apicloud-4.jpg"/></div><br>
<div align=center><img src="./image/APICloud/apicloud-5.jpg"/></div>

发现实际处理逻辑并没有显示地址，直接挂调试器，用lldb启动应用，拿到ASLR偏移`0x004e64000`
<div align=center><img src="./image/APICloud/apicloud-6.jpg"/></div>

接着下断在上面`blr x8`转跳的地方，让程序继续运行，拿到`x8`的值`0x00104e9978c`
<div align=center><img src="./image/APICloud/apicloud-7.jpg"/></div><br>
<div align=center><img src="./image/APICloud/apicloud-8.jpg"/></div>

计算方法的真实地址`addr = 0x00104e9978c - ASLR = 0x00104e9978c - 0x004e64000`，并在ida中转跳到该地址，发现使用的是rc4算法。
<div align=center><img src="./image/APICloud/apicloud-9.jpg"/></div><br>
<div align=center><img src="./image/APICloud/apicloud-10.jpg"/></div>

这里对rc4算法xref一下，发现有2个调用路径
<div align=center><img src="./image/APICloud/apicloud-11.jpg"/></div>

接下来需要确定该算法解密的文件是否是我们需要的资源文件。通过objc name的xref回溯，随便选择一个方法跟进，通过动态调试拿到文件路径
<div align=center><img src="./image/APICloud/apicloud-12.jpg"/></div><br>
<div align=center><img src="./image/APICloud/apicloud-13.jpg"/></div>

到此可以确认了，该应用使用了rc4算法加密。接下来就需要逆向算法，看看使用的是不是标准的rc4算法以及如何获取key
### 2. 解密分析
- __re_RC4
<div align=center><img src="./image/APICloud/apicloud-14.jpg"/></div>
初步看一下，代码功能为s盒初始化，填充key，下个断验证下
<div align=center><img src="./image/APICloud/apicloud-15.jpg"/></div><br>
<div align=center><img src="./image/APICloud/apicloud-16.jpg"/></div>

因为`key=ce1f1ef32f62ff6d7606`，可以看到栈帧里已经被key填满了，证明猜测无误。s盒里经过key的计算已经被填充满，用以进行下面`__RC4`的计算
- __RC4
<div align=center><img src="./image/APICloud/apicloud-17.jpg"/></div>
看上去也是比较正常的rc4算法，接下来就开始写解密算法

### 3. 解密实现
这里有两种方式：
- 找一个现成的rc4算法改一改
- 照抄
我比较懒，所以就直接照抄算法。但是要注意，ida的F5结果有时候会有错，抄的时候最好是抄汇编实现。解密效果如下：
<div align=center><img src="./image/APICloud/apicloud-18.jpg"/></div>
搞定，再换个文件试试
<div align=center><img src="./image/APICloud/apicloud-19.jpg"/></div>

### 结论
实测下来，该框架使用了多个key来解密不同的文件，大部分的网页资源都可以用同一个key来解密。但所有的资源解密都是共用一套rc4算法，所以对于不同文件，传递不同的key解密即可。分析到此结束。
