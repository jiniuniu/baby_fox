import requests

uri = "http://localhost:27777"

file_path1 = (
    "/Users/nianji/code/side_work/baby_fox/baby_fox/sample_data/company_info_fuge.txt"
)

file_path2 = (
    "/Users/nianji/code/side_work/baby_fox/baby_fox/sample_data/product_info_fuge.txt"
)


files = [("files", open(file_path1, "rb")), ("files", open(file_path2, "rb"))]

data = {"knowledge_name": "fuge_tech"}

r = requests.post(f"{uri}/local_doc_qa/upload", files=files, data=data)
print(r.json())
