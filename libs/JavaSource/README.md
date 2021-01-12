# ResDecode.jar

```text
Extract WebApp Resource with java code.
```

```text
File Path : ./libs/bin/ResDecode.jar
Main Class: com.ResDecode.Main

Invoke Export Method: 
    jpype.startJVM(jvmPath, '-ea', '-Djava.class.path={0}'.format(Config.Config["decrypt_jar"]), convertStrings=False)
    jclass = jpype.JClass("com.ResDecode.Main")()
    jclass.[Export Method]()
```

Modules in ResDecode.jar </br>

|#|Module|Export Method|
|----|:----:|:----:|
|1|BuFan|get_appUrl|
|2|AppYet|DeAppYet|
