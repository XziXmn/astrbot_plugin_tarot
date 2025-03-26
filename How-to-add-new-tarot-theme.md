## 如何添加新的塔罗牌主题资源？

`v0.4.0` 新增东方塔罗牌主题资源！且支持用户添加主题！

1. 该功能对**图片后缀无要求**

2. 如果你有完整的塔罗牌资源，请根据[资源说明](./README.md#资源说明)与 `./resource/BilibiliTarot` 的目录结构将塔罗牌分类并**建立对应目录**，并**重命名**塔罗牌图片文件：

   ```python
   ["MajorArcana", "Cups", "Pentacles", "Sowrds", "Wands"]
   ```

3. 如果塔罗牌资源不完整也没关系，但请确保**每个子类资源完整**。例如，我有新的塔罗牌主题 `NameOfNewTheme`，但仅有大阿卡纳22张，及圣杯15张，则建立如下 `NameOfNewTheme` 子目录：

   ```
   MyTarotResource
   ├ BilibiliTarot
   │ └ ……
   ├ TouhouTarot
   │ └ ……
   └ NameOfNewTheme
     ├ Cups
     │ ├ 圣杯-01.png
     │ ├ 圣杯-02.png
     │ ├ ……
     │ └ 圣杯王后.png
     └ MajorArcana
       ├ 0-愚者.png
       ├ 01-魔术师.png
       ├ ……
       └ 21-世界.png
   ```

   将其放入 `Resource` 目录下即可。
   
   Enjoy!🥳
