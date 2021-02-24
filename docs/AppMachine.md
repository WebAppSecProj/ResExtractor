# SeattleCloud Android Rev
如需转载请注明出处
## 目录
+ 简述
+ 应用特征描述
+ 资源数据提取
+ 结论

## 简述
AppMachine框架既支持生成Android应用，也支持生成iOS应用。其应用相关的资源文件也是支持加密存储。
其相关的主要功能是通过c#代码实现，然后通过mono引擎在移动设备上本地执行c#代码来完成应用的运行。
若要对其进行分析，需要利用mono引擎相关的代码去调用c#的代码。
因此对AppMachine相关的分析主要以静态分析为主，动态分析为辅。
然后因为iOS系统中不允许有模拟代码或解释代码，因此在iOS中dll文件中只有c#相关的方法，而没有其确切的代码。
这些代码会被编译为AOT代码并放到另一些文件中，使得对其进行逆向比较困难。
所以对于AppMachine的分析主要基于Android版本分析，不过同样因为AppMachine的代码是这种跨平台型设计，因此Android与iOS的实现都是相同的。

## 应用特征描述
### Android
该框架生成的Android应用在包名上不具有明显特征，但是其主Activity名为app.Main，且其在assets目录下包含一个resources.zip文件。

### iOS
该框架生成的iOS应用在包名上不具有明显的特征，因此也需要通过应用所包含的文件进行分析。
具体而言，该框架生成的ipa包下面会包含着一些名为Appmachine.*.arm64的文件，这些文件中就是保存着c#的AOT代码。

## 资源数据提取
AppMachine对应用独有的数据，包括资源数据都进行了整合压缩到一个resources.zip文件中。这个文件在iOS和Android中的位置不同。不过构造和加密方式都是相同的。
Android中的位置为assets目录下，iOS则是在应用的目录下与应用的可执行文件同层。

resources.zip主要包含一个或多个文件夹和两个分别名为app.dat,marker.dat的文件。
app.dat文件中主要包含着一些应用相关的信息，如在与服务器通信的应用id等，其中DrawingNo的标签为应用主要使用的resources.zip下面的哪个文件夹。

在这些文件夹下面主要饱含着一些名如CmsContent_*.dat，Webservice_*.dat，dd.dat的文件以及一个images的文件夹。
其中dd.dat是包含应用数据最主要的文件。这个文件中内容经过定制的TEA算法加密保护。不过现在版本所有的加密密钥都是确定的，因此可以直接使用确定的密钥进行解密后，通过对应的读取方法从这个文件里面读取出对应的一些相关的资源数据。

其中，加密密钥生成的伪代码如下：
```python
def generate_key_list(key_str):
	key_list = [0x0,0x0,0x0,0x0]
	num = 0
	for tmp_i in range(len(key_str)):
		tmp_char = key_str[tmp_i]
		if (((tmp_char.isalnum())|(tmp_char == "_")|(tmp_char == " "))&((tmp_char != " ")|((i<=0)|(key_str[tmp_i-1]!=" ")))):
			num3 = (num & 3)<<3
			num4 = 0xff << (num3 & 0x1f)
			num2 = ((key_list[(num & 0xff) >> 2]& num4)>>(num3 & 0x3f)) & 0xff
			num2 = (((num2 << 1)^(num2 >> 1 )) ^ bytes(tmp_char)) & 0xff
			tmp_num = key_list[(num & 0xff)>>2]
			key_list[(num & 0xff)>>2] = tmp_num & ((~num4)&0xff)
			num5 = ((num2 << (num3 & 0x1f))& num4)|(key[(num & 0xff) >>2])
			key_list[(num & 0xff)>>2] = num5
			num +=1
	return key_list
```

处理解密的为代码如下：
```python
num = 13 
num6 = 0x9e3779b9
index = 0
while index<data.length:
	num2 = data[index]
	num3 = data[index+1]
	num4 = 0xc6ef3720
	num5 = 0x20
	while(true):
		if(num5-- <= 0):
			data[index] = num2 ^ num
			data[index+1] = num3
			num = ((num + 0x1b)%0x7ae0)
			index +=2
			break
		num3 -= (((num2<<4) ^ (num2>>5))+num2) ^ (num4 + this._key[(num4>>11)&3])
		num4 -= num6
		num2 -= (((num3<<4) ^ (num3>>5))+num3) ^ (num4 + this._key[(num4 & 3)])
```

解密时会将加密文件每0x4000取一段出来进行解密，如果不足0x4000则取为能整除8的数（余数为1则进一位）。
然后0x4000个字节转为0x1000个int进行处理。
加密文件的头四个字节为文件长度。


## 结论
Appmachine利用C#实现了框架的主要代码，并且对其资源数据等进行了加密保护，通过对保存数据的文件进行解密就可以从中获取应用的相关资源数据。
