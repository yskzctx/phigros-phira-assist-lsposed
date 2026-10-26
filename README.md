# Phigros / Phira 纯辅助 LSPosed 模块

一个独立仓库，两个独立APK：**Phigros辅助**与**Phira辅助**。Malody仅作为皮肤制作思路的参考，不是本项目的适配目标。本项目不继承原实验模块的代码历史、二进制或游玩修改能力。

**当前0.1.0为基础候选，尚未经过手机/真实LSPosed运行验收。** 已完成编译、主机测试、源码/DEX能力核对和签名检查。不能把这些检查写成游戏内已实测可用。

## 下载与安装

[0.1.0候选发行页](https://github.com/yskzctx/phigros-phira-assist-lsposed/releases/tag/v0.1.0-pre.1)

|模块|安装包|唯一作用域|参考Activity版本|
|---|---|---|---|
|Phigros辅助|[Phigros APK](https://github.com/yskzctx/phigros-phira-assist-lsposed/releases/download/v0.1.0-pre.1/Phigros-Assist-LSPosed-v0.1.0-TEST.apk)|`com.PigeonGames.Phigros`|4.0.1（157），UnityPlayerActivity|
|Phira辅助|[Phira APK](https://github.com/yskzctx/phigros-phira-assist-lsposed/releases/download/v0.1.0-pre.1/Phira-Assist-LSPosed-v0.1.0-TEST.apk)|`org.flos.phira`|0.8.2（39），MainActivity|

两个新模块的包名分别为`org.rhythmlab.assist.phigros`与`org.rhythmlab.assist.phira`，与其他实验模块不同。只安装需要的一份即可。皮肤工作台可从模块桌面入口独立打开；游戏内窗口辅助需要支持传统Xposed API的LSPosed。启用模块、核对只勾选对应宿主，再冷启动游戏；**长按音量上键打开辅助面板**。普通按键继续交给原窗口处理；触发长按前系统音量可能已变化。面板不会自动弹出或注入游戏触摸。

## 当前实际实现

- **窗口亮度**：仅设置当前Activity窗口，不改系统亮度；暂停/离开时恢复捕获的窗口设置。
- **前台常亮**：仅在目标Activity前台应用，离开时恢复原常亮标志。
- **界面回调采样**：手动启动/停止，显示Android Choreographer回调的平均间隔与P95。**这不是Unity或游戏渲染FPS，更不是音符时序分析。**
- **皮肤资源工作台**：用Android文件选择器授权ZIP；复制到模块自己的私有目录，限额检查、路径/重名/CRC与体积检查、基础Phira八图布局/PNG尺寸/长条图集核对；图片预览、音效试听、只读元数据、原字节导出和删除检查副本。原始文件不覆盖。
- **实际使用免责声明**：模块首页长期显示；每次进程冷启动首次打开辅助面板时要求阅读，面板也可再次查看。

## 两个游戏分别适配

|范围|Phigros|Phira|
|---|---|---|
|窗口辅助|独立宿主入口|独立宿主入口|
|皮肤工作台|用于检查/预览准备资源|为原生资源包管理补充检查、预览和导出|
|游戏内皮肤应用|**本版未接入，不会显示“已应用”**|本版不改写原版皮肤配置；导出后通过原版皮肤功能手动导入|
|引擎渲染、完整特效/音效/线色适配|待逐项核对|以原版资源包实际支持为准，检查器不模拟完整渲染|

不将“能列出包内图片”称为“已完成游戏内换肤”，不承诺Malody皮肤能直接用于这两个游戏。研究记录见[皮肤制作参考](docs/SKIN-RESEARCH.md)，后续范围见[路线与边界](docs/ROADMAP.md)。

## 不提供的能力

不提供自动游玩、自动输入、判定干预、目标分数/准确率/误差、结算或历史成绩修改、RKS修改、解锁/货币修改；不读取或迁移游戏存档，不碰登录和上传结果，不绕过购买、账号、服务器、完整性或反作弊检查。原版游戏的网络行为保持原样。

当前安装包只有本项目Java类、清单与作用域资源；没有原生库、游戏引擎、原游戏素材或旧实验模块类。自动检查入口见[audit.py](audit.py)。能力核对只能说明当前代码和构建包含什么，不能代替设备兼容验收。

## 构建与测试

需要JDK17+、Python3.11+、Android SDK platform36/build-tools36.0.0、[Xposed API82编译依赖](https://api.xposed.info/de/robv/android/xposed/api/82/api-82.jar)。Xposed API只参与编译，不打包。无Gradle/NDK/Rust或网络运行依赖。

```text
python test.py --out <仓库外测试目录>
python build.py --sdk <SDK目录> --xposed-api <api-82.jar> --keystore <仓库外签名库> --password-file <仓库外密码文件> --alias <签名别名> --out <仓库外输出目录>
python audit.py --out <同一输出目录>
```

APK和测试产物放仓库外。私钥、密码、游戏存档和用户皮肤不要提交。代码采用MIT许可；资源权利仍归各自作者。[使用说明与免责声明](DISCLAIMER.md)不替代合法授权，也不是免责保证。
