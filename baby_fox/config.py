import os

# 本地开发，路径不一样
IS_LOCAL = True

# 挂载路径
if not IS_LOCAL:
    DATA_ROOT = "/home/models/"
else:
    DATA_ROOT = os.path.join(os.getenv("HOME"), "data")

MODEL_ROOT = os.path.join(DATA_ROOT, "imported_models")

# 日志的存储路径
LOG_ROOT = os.path.join(DATA_ROOT, "log")
APP_LOGGER_NAME = "baby_fox"
LOG_FILE_PATH = os.path.join(LOG_ROOT, f"{APP_LOGGER_NAME}.log")


# 知识库相关配置
# 文件上传api的根目录
FILES_ROOT = os.path.join(DATA_ROOT, "local_files_repo")
# 上传的文件构建索引存储根目录
INDEX_ROOT = os.path.join(DATA_ROOT, "index_repo")
# embedding 模型文件存储目录
EMBEDDING_MODEL_PATH = os.path.join(MODEL_ROOT, "GanymedeNil_text2vec-large-chinese")
# 默认知识库目录
DEFAULT_KNOWLEDGE_NAME = "marketing_knowledge_demo"


# 如果本地部署chatGLM-6B，对应的路径
CHATGLM_6B_MODEL_PATH = os.path.join(MODEL_ROOT, "chatglm-6b")
CHATGLM_6B_API_ENDPOINT = os.getenv("CHATGLM_6B_API_ENDPOINT")
