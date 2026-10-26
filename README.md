# Phigros / Phira 纯辅助 LSPosed 模块

一个独立仓库，两个独立APK：**Phigros辅助**与**Phira辅助**。Malody仅作为皮肤制作思路的参考，不是本项目的适配目标。本项目不继承原实验模块的代码历史、二进制或游玩修改能力。

**当前0.2.0为实时HUD候选，尚未经过手机/真实LSPosed运行验收。** 已完成编译、主机测试、源码/DEX能力核对和签名检查。不能把这些检查写成游戏内已实测可用。

## 下载与安装

[0.2.0 HUD候选发行页](https://github.com/yskzctx/phigros-phira-assist-lsposed/releases/tag/v0.2.0-pre.1)

|模块|安装包|唯一作用域|参考Activity版本|
|---|---|---|---|
|Phigros辅助|[Phigros APK](https://github.com/yskzctx/phigros-phira-assist-lsposed/releases/download/v0.2.0-pre.1/Phigros-Assist-LSPosed-v0.2.0-HUD-TEST.apk)|`com.PigeonGames.Phigros`|4.0.1（157），UnityPlayerActivity|
|Phira辅助|[Phira APK](https://github.com/yskzctx/phigros-phira-assist-lsposed/releases/download/v0.2.0-pre.1/Phira-Assist-LSPosed-v0.2.0-HUD-TEST.apk)|`org.flos.phira`|0.8.2（39），MainActivity|

两个新模块的包名分别为`org.rhythmlab.assist.phigros`与`org.rhythmlab.assist.phira`，与其他实验模块不同。只安装需要的一份即可。皮肤工作台可从模块桌面入口独立打开；游戏内窗口辅助需要支持传统Xposed API的LSPosed。启用模块、核对只勾选对应宿主，再冷启动游戏；**长按音量上键打开辅助面板**。普通按键继续交给原窗口处理；触发长按前系统音量可能已变化。面板不会自动弹出或注入游戏触摸。

## 当前实际实现

- **只读实时HUD**：漏击Miss、击中Perfect＋Good、独立Bad计数、P/G/Bad/Miss明细，以及已判定音符ACC和真实累计ACC曲线。长按音量上键打开面板后手动启用；四角位置、70%—130%大小及40%—100%底板不透明度可调。HUD不接收触摸，离开游戏窗口时移除。
- **窗口亮度**：仅设置当前Activity窗口，不改系统亮度；暂停/离开时恢复捕获的窗口设置。
- **前台常亮**：仅在目标Activity前台应用，离开时恢复原常亮标志。
- **界面回调采样**：手动启动/停止，显示Android Choreographer回调的平均间隔与P95。**这不是Unity或游戏渲染FPS，更不是音符时序分析。**
- **皮肤资源工作台**：用Android文件选择器授权ZIP；复制到模块自己的私有目录，限额检查、路径/重名/CRC与体积检查、基础Phira八图布局/PNG尺寸/长条图集核对；图片预览、音效试听、只读元数据、原字节导出和删除检查副本。原始文件不覆盖。
- **实际使用免责声明**：模块首页长期显示；每次进程冷启动首次打开辅助面板时要求阅读，面板也可再次查看。

## HUD数据口径与适配限制

ACC = (Perfect + 0.65 × Good) / 已判定音符数 × 100%，Bad与Miss计0；尚无判定时显示“—”。这是当前已判音符的累计准确率，既不是目标准确率，也不是按整张谱面总音符计算的完成度；它不改写游戏分数。曲线横轴为已判定音符数，纵轴标注实际区间。按桶保留极值和首尾点，最多514个显示点，内存保存最多20000个观察点。中途接入、曲线缺少开头或数据暂未更新均明确标注；没有连接时不生成假数据。

只读适配范围为**arm64-v8a的Phigros4.0.1（157）和Phira0.8.2（39）的已核对原生库**，完整ELF的SHA-256见[native/profiles.json](native/profiles.json)。版本号相同但ELF不同也不会强行挂接。先校验版本、架构和ELF哈希，再由LSPosed原生接口接入，并逐项核对可执行段及函数前缀。不匹配或接口不可用时仅报告状态，基础窗口辅助仍可使用。

Phigros在原版ScoreControl.Update执行后读取P/G/Bad/Miss计数；Phira只旁观原版判定提交并原样转交所有参数，**不读取或改写受保护的判定结构**，因此中途挂接只统计本段。重开和换谱会重置观察历史。原生接入参考[LSPosed官方Native Hook说明](https://github.com/LSPosed/LSPosed/wiki/Native-Hook)。

具体验证范围与手机待验项目见[0.2.0安装说明](docs/INSTALL-0.2.0.md)。

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

当前安装包只含本项目Java类、清单、作用域资源与独立的只读`libassist_observer.so`。没有游戏引擎、原游戏素材或旧实验模块类。唯一JNI数据接口是读取观察器自己的快照，没有配置判定或修改游戏数据的入口。自动检查入口见[audit.py](audit.py)。能力核对只能说明当前代码和构建包含什么，不能代替设备兼容验收。

## 构建与测试

需要JDK17+、Python3.11+、Android SDK platform36/build-tools36.0.0、[Xposed API82编译依赖](https://api.xposed.info/de/robv/android/xposed/api/82/api-82.jar)。Xposed API只参与编译，不打包。还需Android NDK26.3和用于主机测试的GCC。无Gradle/Rust或网络运行依赖。

```text
python test.py --out <仓库外测试目录>
python build.py --sdk <SDK目录> --ndk <NDK目录> --xposed-api <api-82.jar> --keystore <仓库外签名库> --password-file <仓库外密码文件> --alias <签名别名> --out <仓库外输出目录>
python audit.py --out <同一输出目录>
```

APK和测试产物放仓库外。私钥、密码、游戏存档和用户皮肤不要提交。代码采用MIT许可；资源权利仍归各自作者。[使用说明与免责声明](DISCLAIMER.md)不替代合法授权，也不是免责保证。
