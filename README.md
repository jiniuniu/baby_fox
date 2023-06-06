# Baby_fox

## 简介
基于企业私有数据构建专属知识库问答聊天工具，兼容 [langchain](https://github.com/hwchase17/langchain) 支持的所有大语言模型。

## 开发流程 (WIP)

### 1. 本地开发
本地开发流程

```shell
# 下载代码仓库
$ git clone https://github.com/jiniuniu/baby_fox.git

# 进入项目
$ cd baby_fox

# 安装依赖
$ pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 安装 spacy 的中文包
$ python -m spacy download zh_core_web_sm -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 启动服务
$ python api.py
```
服务启动之后打开 `localhost:27777`, 即可使用fastapi的doc的ui对每个API进行测试。


### 2. 推理服务部署（待测试）

1. 本地跑通后，将 `IS_LOCAL` 设成 `FALSE`，执行下面的命令把代码上传到网盘
    ```shell
    # 首先参照 https://min.io/download下载并安装mc客户端，并进行如下配置：(需要 AKSK 鉴权信息)
    $ mc alias set ark <some lanrui url> <AK> <SK> --api S3v4

    $ mc ls <网盘挂载路径>
    $ mc cp --recursive <本项目路径> <网盘挂载路径>
    ```
2. 创建推理服务，选择 3090 24G 显卡的机器，
    - 选择 pytorch 公有镜像（official-1.12.1-cuda11.6-cudnn8-devel）
    - 端口 27777
    - 挂载网盘，填写挂载路径对应的是 [baby_fox/config.py](baby_fox/config.py) 的 `HOME_ROOT`。
    - 启动脚本
        ```shell
        cd <挂载路径>/baby_fox
        # 安装依赖
        pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

        # 安装spacy中文包
        python -m spacy download zh_core_web_sm -i https://pypi.tuna.tsinghua.edu.cn/simple/

        python3 api.py
        ```
    - 模型位置选择从网盘导入并设置挂载路径
    - 高级配置中，不勾选挂载只读






