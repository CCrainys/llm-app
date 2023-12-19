from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)

from langchain.vectorstores import Milvus

connections.connect("default", host="localhost", port="19530")

pk = FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True)
text = FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2048)
vector = FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=768)

schema = CollectionSchema(
    fields=[pk, text, vector],
    description="arXiv dataset",
    index_params={
        "metric_type": "L2",
        "index_type": "GPU_IVF_PQ",
        "params": {"nlist": 128, "m": 4, "nbits": 8},
    },
)
collection_name = "TestLangchain"

def drop(collection_name):
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
    
    print(utility.list_collections())


def create(collection_name):
    if not utility.has_collection(collection_name):
        collection = Collection(name=collection_name, schema=schema)
        collection.flush()
    print(utility.list_collections())


def check(collection_name):
    collection = Collection(name=collection_name)
    # index_check = collection.index(index_name="_default_idx_104")
    # print(index_check.params)
    print(utility.list_indexes(collection_name))
    print(utility.list_collections())
    # 将所有数据flush到磁盘
    # collection.flush()
    index_params = {
        "index_type": "IVF_PQ",
        "params": {"nlist": 128, "m": 4, "nbits": 8},
        "metric_type": "L2",
    }
    # collection.create_index(field_name="vector", index_params=index_params)
    collection.load()
    print(collection.is_empty)
    print(collection.num_entities)

    res = collection.query(
        expr="text like 'The framework of lexicographical program%'",
        output_fields=["pk", "text", "vector"],
    )
    print(res[0]["pk"])
    print(res[0]["text"])
    print(len(res[0]["text"]))
    print(len(res[0]["vector"]))
    print(type(res[0]["vector"][0]))


if __name__ == "__main__":
    # drop(collection_name)
    # create(collection_name)
    check(collection_name)
