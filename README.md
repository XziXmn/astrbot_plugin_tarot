<div align="center">

# Tarot

_🔮 赛博塔罗牌 🔮_

</div>

## 序

_“许多傻瓜对千奇百怪的迷信说法深信不疑：象牙、护身符、黑猫、打翻的盐罐、驱邪、占卜、符咒、毒眼、塔罗牌、星象、水晶球、咖啡渣、手相、预兆、预言还有星座。”——《人类愚蠢辞典》_

## 关于

一个基于 AstrBot 框架的塔罗牌占卜插件，支持多牌阵和单张牌占卜，并通过 AI 生成详细解析。

## 版本

🧰 [v0.4.0](https://github.com/XziXmn/astrbot_plugin_tarot)

⚠ 适配 AstrBot >= v4.5.7（保留 v3.4.39+ 旧版接口回退）

👉 [如何添加新的塔罗牌主题资源？](./How-to-add-new-tarot-theme.md)欢迎贡献！🙏

## 安装

### 方式一：通过 AstrBot WebUI 安装（推荐）

1. 打开 AstrBot 管理面板，进入「插件市场 / 安装插件」。
2. 选择「从 GitHub 仓库地址安装」，填入：
   ```
   https://github.com/XziXmn/astrbot_plugin_tarot
   ```
3. 点击安装，等待插件下载并自动安装依赖。
4. 安装完成后，在「AstrBot 插件」页面找到「赛博塔罗牌」，点击「重载插件」。

### 方式二：手动安装

1. 将本仓库克隆或下载到 AstrBot 的 `data/plugins/` 目录下，目录名保持为 `astrbot_plugin_tarot`：
   ```bash
   cd AstrBot/data/plugins
   git clone https://github.com/XziXmn/astrbot_plugin_tarot.git
   ```
2. 重启 AstrBot，插件会自动加载。

### 资源准备

本插件仅包含初始资源 `resources/TouhouTarot`（东方主题，仅大阿卡纳）。如需完整占卜体验，请下载扩展资源并放入对应目录：

[塔罗资源下载](https://www.123912.com/s/UQZ8Vv-uOLav?) 提取码:omBT

资源路径在插件配置项 `resource_path` 中修改，默认为 `./resources`。

## 命令

1. [占卜] 随机选取牌阵进行占卜并提供 AI 解析，可根据用户输入（如“占卜 情感”）模糊匹配或通过 AI 选择合适的牌阵（如“圣三角牌阵”），随机抽取对应数量的塔罗牌，并生成带颜表情的 AI 解析。

2. [塔罗牌] 抽取一张塔罗牌，提供简短回应和 AI 解析，适合快速占卜。；

3. [薇拉 / 玫瑰小姐 / 玫瑰姐姐 / 薇拉姐姐 / 占卜师] 唤出薇拉姐姐，进入持续引导对话，聊完后进行专属占卜。

4. [开启转发 / 关闭转发] 切换群聊转发模式。

## 资源说明

1. 韦特塔罗(Waite Tarot)包括22张大阿卡纳(Major Arcana)牌与权杖(Wands)、星币(Pentacles)、圣杯(Cups)、宝剑(Swords)各系14张的小阿卡纳(Minor Arcana)共56张牌组成，其中国王、皇后、骑士、侍从也称为宫廷牌(Court Cards)；

   - BilibiliTarot：B站幻星集主题塔罗牌
   - TouhouTarot：东方主题塔罗牌，仅包含大阿卡纳

   ⚠ 资源中额外四张王牌(Ace)不在体系中，因此不会在占卜时用到，因为小阿卡纳中各系均有Ace牌，但可以自行收藏。

2. `tarot.json`中对牌阵，抽牌张数、是否有切牌、各牌正逆位解读进行说明。`cards` 字段下对所有塔罗牌做了正逆位含义与资源路径的说明；

3. 根据牌阵的不同有不同的塔罗牌解读，同时也与问卜者的问题、占卜者的解读等因素相关，因此不存在所谓的解读方式正确与否。`cards` 字段下的正逆位含义参考以下以及其他网络资源：

   - 《棱镜/耀光塔罗牌中文翻译》，中华塔罗会馆(CNTAROT)，版权原因恕不提供
   - [AlerHugu3s/PluginVoodoo](https://github.com/AlerHugu3s/PluginVoodoo/blob/master/data/PluginVoodoo/TarotData/Tarots.json)
   - [塔罗.中国](https://tarotchina.net/)
   - [塔罗牌](http://www.taluo.org/)
   - [灵匣](https://www.lnka.cn/)

   🤔 也可以说是原作者MinatoAquaCrews的解读版本

## 本插件改自

1. [真寻bot插件库/tarot](https://github.com/AkashiCoin/nonebot_plugins_zhenxun_bot)

2. [haha114514/tarot_hoshino](https://github.com/haha114514/tarot_hoshino)

3.  [hMinatoAquaCrews/nonebot_plugin_tarot](https://github.com/MinatoAquaCrews/nonebot_plugin_tarot)
