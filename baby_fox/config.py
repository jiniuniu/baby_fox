import os

HOME_ROOT = os.environ.get("HOME")
DATA_ROOT = os.path.join(HOME_ROOT, "data")
CODE_ROOT = os.path.join(HOME_ROOT, "code")

# 所有数据存储的根目录（包括模型、知识库文件、知识库索引、日志）
FILES_ROOT = os.path.join(DATA_ROOT, "local_files_repo")
INDEX_ROOT = os.path.join(DATA_ROOT, "index_repo")
MODEL_ROOT = os.path.join(DATA_ROOT, "imported_models")
LOG_ROOT = os.path.join(DATA_ROOT, "log")


# embedding
EMBEDDING_MODEL_PATH = os.path.join(MODEL_ROOT, "GanymedeNil_text2vec-large-chinese")


# 日志相关配置
APP_LOGGER_NAME = "baby_fox"
LOG_FILE_PATH = os.path.join(LOG_ROOT, f"{APP_LOGGER_NAME}.log")
