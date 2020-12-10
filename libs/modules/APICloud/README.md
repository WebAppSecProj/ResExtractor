The underline works. 
So use 
```
git submodule add https://github.com/WebAppSecProj/uzmap-resource-extractor.git ./libs/modules/APICloud/uzmap_resource_extractor
```
to add submodule instead of 
```
git submodule add https://github.com/WebAppSecProj/uzmap-resource-extractor.git ./libs/modules/APICloud/uzmap-resource-extractor
```
or there will be an import error.