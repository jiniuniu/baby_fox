import os
from typing import List, Union

from langchain.docstore.document import Document
from langchain.document_loaders import TextLoader, UnstructuredFileLoader
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from tqdm import tqdm

from baby_fox.config import INDEX_ROOT
from baby_fox.index.text_tools import ChineseTextSplitter
from baby_fox.logger import get_logger

log = get_logger(__name__)


def write_check_file(filepath, docs):
    folder_path = os.path.join(os.path.dirname(filepath), "tmp_files")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    fp = os.path.join(folder_path, "load_file.txt")
    with open(fp, "a+", encoding="utf-8") as fout:
        fout.write("filepath=%s,len=%s" % (filepath, len(docs)))
        fout.write("\n")
        for i in docs:
            fout.write(str(i))
            fout.write("\n")
        fout.close()


class IndexBuilder:
    sentence_size: int = 100
    index_root = INDEX_ROOT

    def __init__(self, embeddings: HuggingFaceEmbeddings) -> None:
        self.embeddings = embeddings

    def build_index(
        self, filepath: Union[str, List[str]], index_name: str
    ) -> List[str]:
        loaded_files = []
        failed_files = []
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                log.info(f"{filepath} 路径不存在")
                return
            elif os.path.isfile(filepath):
                file = os.path.split(filepath)[-1]
                try:
                    docs = self.load_file(filepath)
                    log.info(f"{file} 已成功加载")
                    loaded_files.append(filepath)
                except Exception as e:
                    log.error(e)
                    log.info(f"{file} 未能成功加载")
                    return
            elif os.path.isdir(filepath):
                docs = []
                for file in tqdm(os.listdir(filepath), desc="加载文件"):
                    fullfilepath = os.path.join(filepath, file)
                    try:
                        docs += self.load_file(fullfilepath)
                        loaded_files.append(fullfilepath)
                    except Exception as e:
                        log.error(e)
                        failed_files.append(file)

                if len(failed_files) > 0:
                    log.info("以下文件未能成功加载：")
                    for file in failed_files:
                        log.info(f"{file}\n")

        else:
            docs = []
            for file in filepath:
                try:
                    docs += self.load_file(file)
                    log.info(f"{file} 已成功加载")
                    loaded_files.append(file)
                except Exception as e:
                    log.error(e)
                    log.info(f"{file} 未能成功加载")

        if len(docs) > 0:
            log.info("文件加载完毕，正在生成向量库")
            index_path = os.path.join(self.index_root, index_name)
            if os.path.isdir(index_path):
                index = FAISS.load_local(index_path, self.embeddings)
                index.add_documents(docs)
            else:
                index = FAISS.from_documents(docs, self.embeddings)
            index.save_local(index_path)
            return loaded_files
        else:
            log.info("文件均未成功加载，请检查依赖包或替换为其他文件再次上传。")
            return loaded_files

    def load_file(self, filepath: str) -> List[Document]:
        if filepath.lower().endswith(".md"):
            loader = UnstructuredFileLoader(filepath, mode="elements")
            docs = loader.load()
        elif filepath.lower().endswith(".txt"):
            loader = TextLoader(filepath)
            text_splitter = ChineseTextSplitter(
                pdf=False, sentence_size=self.sentence_size
            )
            docs = loader.load_and_split(text_splitter)
        else:
            loader = UnstructuredFileLoader(filepath, mode="elements")
            text_splitter = ChineseTextSplitter(
                pdf=False, sentence_size=self.sentence_size
            )
            docs = loader.load_and_split(text_splitter=text_splitter)

        write_check_file(filepath, docs)
        return docs
