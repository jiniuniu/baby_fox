# Baby_fox

## 简介
基于企业私有数据构建专属知识库问答聊天工具，兼容 [langchain](https://github.com/hwchase17/langchain) 支持的所有大语言模型。

## 部署 (working in progress)

### 初始化安装环境

```shell
# 确认 Python 3.8 及以上版本
$ python --version
Python 3.11.0

# 如果低于这个版本，可使用conda安装环境
$ conda create -p /your_path/env_name python=3.11

# 激活环境
$ source activate /your_path/env_name
$ pip3 install --upgrade pip

# 拉取仓库
$ git clone https://github.com/jiniuniu/baby_fox.git


# 进入目录
$ cd baby_fox

 # 用清华的pip镜像源地址安装依赖
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

```

### 设置参数

打开文件 [baby_fox/config.py](baby_fox/config.py) 检查更改文件路径设置。

1. 在挂载的网盘上创建对应的文件夹
2. embedding: 下载 [GanymedeNil/text2vec-large-chinese](https://huggingface.co/GanymedeNil/text2vec-large-chinese/tree/main) 模型并存储在 `config.py` 对应的路径中。

## Docker 部署
