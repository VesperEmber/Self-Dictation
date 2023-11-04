<h1 align="center">
  <br>
  Self-Dictation
  <br>
</h1>

<h3 align="center">
A dictation tool developed for myself.
</h3>

***

#### TLHX：反正程序只是为了给我自己用的，以下 README.md 的内容纯属为了仪式感写一写。

***

## 快速上手

一款智能单词听写工具。整个流程大概是：

1. 你需要能科学上网(you know what I mean)
2. 注册个 [Microsoft Azure](https://azure.microsoft.com/en-us)，然后在上面部署个 TTS 项目，拿到你的 api key 以及项目部署的
   region，最后把它们写到 **speech_config.json** 文件的对应位置 (
   放心，仅背单词的话每月额度是够的，不用花什么钱。让我们再次感谢微软，阿门)
3. 如果第二步正确配置完成，那现在应该就能享受到 Microsoft Azure 的高质量语音服务了，否则就只能用 pyttsx3 作为替代来读单词了。Azure
   可支持多种语言，目前我写的程序里限制为 5 种，分别是 english, chinese, german, japanese, french。如果只有 pyttsx3 的话就只能使用
   chinese 或者 english
4. 手动导入要考的词汇及其含义到单词本 (毕竟我做是听写软件，不是词典，单词及其含义还是要你自己导的)
5. 划分得到最总要考的子单词本范围，设置听写模式，抽词数量等，然后开始听写 (开冲)

**Note**: 单词的发音会在 import 导入单词的时候就被下载到本地，上述配置失败了就没法获取它的高质量发音了。不过单词本身以及含义都会正常导入词典，
使用 pyttsx3 的辣鸡读音替代一下也不是不能用。本地已经存着音源的单词不会受到影响，程序会直接播放本地的音源 (妙啊)

***

## 开发动机

本项目是我花了大约一周(妈的，累死了)
时间，仅为自己开发的智能听写单词工具，用于解决我背完单词之后，难以找到朋友帮我频繁听写的痛点(妈的，太痛了)<br>

我个人背单词的方法大致是先在生活中或是做题时，遇到不会的单词就直接查它的发音以及含义，然后抄一遍记在单词本上，连查带写一个词大约用一分钟，
这也同时是背的过程了。在最后我会需要别人帮我听写一遍：对方念单词的发音，我在本上写出单词的拼写以及全部的含义(
真的好用，你还不试试？)<br>

我一直认为背完单词后听写、尤其是频繁听写是很有必要的，这个过程可以加深印象，强化记忆，省的背完了忘然后忘了再背。若不是这么个操作，我也不可能俩半月考到北大来(
我牛逼吧)

## 痛点分析

在以上过程的痛点需求大致就可以理解为：<br>

1. 足够方便的操作：程序操作起来不能浪费太多时间，以至于现场找朋友帮忙听写都来得及找到了(这太艹了)
2. 足够标准的发音：以免听不出来，或是带坏自己的听力口语，乃至影响阅读水平(确信.jpg)
3. 足够智能的抽词：不拘泥于完全随机抽词，最好能哪个词难考哪个，哪个容易忘考哪个(请猛攻我的弱点！)
4. 足够聪明的阅卷：应当允许同义词也算含义，不应要求用户写含义必须严格字符串匹配(不然就太蠢了)

基于此，目前为止我实现的部分功能核心概括起来大概就是：<br>

* 动态维护单词本：增删改查那是必须的
* 不同模式智能抽词：除了简单随机抽词之外，还有个考虑不同权重(考察次数、难易度、正确率、遗忘曲线)的智能抽词
* 多语言标准语音听写：调的 Microsoft Azure API，感谢微软，阿门
* 语义相似度检测判卷：上 huggingface
  随便找了俩预训练模型，分别是 [MiniLM](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
  和 [sbert](https://huggingface.co/uer/sbert-base-chinese-nli)，感谢 huggingface，阿门

## 使用方法

run 就完事了，我觉得我新手引导做的不错：

* 英语认识吧？(你都来背单词了，程序一共就那么几个词，你还不给它查了背了，是不是得反省一下？)
* help 会吧？

遇事不决，不知道指令咋用，敲 help 就完事了。一个 help 解决不了的，那你可以 help help

### 程序打包

可以直接使用我放出的 release 版本 (理论上我应该会发布的，我要是懒了就当我没说)<br>
不然直接本地 run 也行，要是非要打包可执行文件出来，那可以使用 pyinstaller 执行以下命令:<br>
> <code>pyinstaller --copy-metadata tqdm --copy-metadata regex --copy-metadata requests --copy-metadata packaging
> --copy-metadata filelock --copy-metadata numpy --copy-metadata huggingface-hub --copy-metadata safetensors
> --copy-metadata pyyaml --copy-metadata torch --collect-data torch --collect-data tqdm --collect-data regex
> --collect-data requests --collect-data packaging --collect-data filelock --collect-data numpy --collect-data
> huggingface-hub --collect-data safetensors --collect-data pyyaml --copy-metadata tokenizers --collect-data tokenizers
> --add-binary=";." -i icon.ico main.py</code><br>

最后这个<code>--add-binary=";."</code>可以重复多次，里面把 Microsoft Azure 打包需要的各种 .dll 加进去

**Note:** 打包完之后得到的 .exe 文件别忘了拿到项目文件夹根目录去，否则没法通过相对路径找到 **speech_config.json** 等文件
***

## 未来展望

莫得未来了，一周从零写个这么个玩意强度有点大了，耽误科研又耽误生活，不过好在以后可以用这玩意给我自己背单词听写了，也算是没白写<br>

以后用的多或许可以开发个图形界面，再加点别的功能啥的