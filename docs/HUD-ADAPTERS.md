# 只读 HUD 适配记录

目标与ELF指纹、RVA和16字节可执行前缀在`native/profiles.json`。该清单用`profile_extract.py`从另外提供的精确哈希原版ELF中提取；仓库不打包原版二进制或私有存档。

## Phigros 4.0.1 / 157

已核对IL2CPP元数据中的ScoreControl.Update：RVA `0x1d87a54`，`void(self, MethodInfo*)`。原函数执行后读取计数：perfect/good/bad/miss分别位于对象`0x58/0x5c/0x60/0x64`。`_noteCodes`为`0x88`的List，count位于List的`0x18`，仅读取总量供显示。任一计数越界则拒绝该帧。新对象或已判总量回退重置观察历史；中途接入保留实际累计计数并标记曲线缺失开头。没有调用Perfect/Good/Miss等判定方法。

## Phira 0.8.2 / 39

已核对AArch64原始函数：JudgeInner.commit `0xdb6b78`，inner在x0、判定在w1、误差double在d0；Judge.reset `0xdc9108`；Judge.update `0xdc9288`，四个指针参数。观察器将原调用及全部原参数原样转交，随后只更新自身计数。仅在update线程局部上下文内接收匹配inner身份的commit。`judge+0x58`仅用于指针相等比较，不读取或写入受保护JudgeInner内容，不绕过完整性检查。资源时间`resource+0x9e0`仅用于时间倒退重开识别，原始值不变。不读取受保护累计计数，因此中途接入无法补全前段；显示“仅统计本段判定”。总音符数不读取，保持未知，不臆造总量。

## 隔离和限额

LSPosed Native Hook接口依据[官方文档](https://github.com/LSPosed/LSPosed/wiki/Native-Hook)。只有一个只读JNI快照接口。所有游戏调用之外的计数、互斥锁、曲线和状态均属于本模块自己的内存；锁不会跨越原函数调用。单局最多20000个观察点，JNI每次最多514点，HUD每100ms读取一次。无统计写盘、网络请求、输入注入、时序目标或成绩设置接口。

仅处理确切版本、架构及ELF，安装前验证全部函数所在可执行段与前缀；失败撤回本模块已安装的观察入口。不会撤回其他模块入口。主机测试只能验证转交和统计逻辑，无法证明框架的原生挂接、实际Android对象生命周期与设备性能；这些仍需真机验收。
