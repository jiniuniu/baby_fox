import os

import requests


class TestCase:
    uri = "http://localhost:27777"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path1 = os.path.join(current_dir, "baby_fox/sample_data/company_info_fuge.txt")
    file_path2 = os.path.join(current_dir, "baby_fox/sample_data/product_info_fuge.txt")

    def test_upload(self):
        files = [
            ("files", open(self.file_path1, "rb")),
            ("files", open(self.file_path2, "rb")),
        ]
        data = {"knowledge_name": "fuge_tech2"}
        r = requests.post(f"{self.uri}/local_knowledge/upload", files=files, data=data)
        print(r.json())
        for f in files:
            f[1].close()

    def test_list_files(self):
        data = {"knowledge_name": "fuge_tech"}
        r = requests.get(f"{self.uri}/local_knowledge/list_files", params=data)
        print(r.json())

    def test_chat(self):
        data = {"query": "睡眠不好常见的问题有哪些"}
        r = requests.post(f"{self.uri}/chat", data=data)
        print(r.json())

    def test_chat_with_knowledge(self):
        data = {"question": "复歌科技的团队文化是什么", "knowledge_name": "fuge_tech"}
        r = requests.post(f"{self.uri}/local_knowledge/chat", json=data)
        print(r.json())

    def test_delete_files(self):
        data = {"knowledge_name": "fuge_tech2"}
        r = requests.post(f"{self.uri}/local_knowledge/delete", params=data)
        print(r.json())


if __name__ == "__main__":
    test_case = TestCase()
    # test_case.test_upload()
    # test_case.test_list_files()
    # test_case.test_chat()
    # test_case.test_chat_with_knowledge()
    # test_case.test_delete_files()
