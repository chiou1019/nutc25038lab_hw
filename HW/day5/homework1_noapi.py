from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

client = QdrantClient(url="http://localhost:6333")

# 建立 collection（先檢查）
if not client.collection_exists("test_collection"):
    client.create_collection(
        collection_name="test_collection",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    
    
texts = [
    "人工智慧是未來趨勢",
    "Python 是熱門程式語言",
    "機器學習是 AI 的一部分",
    "深度學習使用神經網路",
    "資料科學需要統計知識"
]



from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

embeddings = model.encode(texts)



from qdrant_client.models import PointStruct

points = []

for i, (text, vector) in enumerate(zip(texts, embeddings)):
    points.append(
        PointStruct(
            id=i,
            vector=vector.tolist(),
            payload={"text": text}
        )
    )

client.upsert(
    collection_name="test_collection",
    points=points
)


query = "AI 有什麼應用"
query_vector = model.encode([query])[0]

results = client.query_points(
    collection_name="test_collection",
    query=query_vector,
    limit=3
)

for point in results.points:
    print(f"ID: {point.id}")
    print(f"Score: {point.score}")
    print(f"Text: {point.payload['text']}")
    print("------")

