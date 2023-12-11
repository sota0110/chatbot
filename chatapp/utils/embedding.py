from openai import OpenAI
import pandas as pd
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from chromadb.config import Settings
from ..models import Article
from ..config.openai_key import free_secret_key

class Embedding:
    def __init__(self):
        self.client = OpenAI(api_key = free_secret_key)
        self.embedding_model = "text-embedding-ada-002"
        self.batch_size = 1000
    
    def get_embedding(self):
        data = Article.objects.all().values_list()
        titles = [item[1] for item in data]
        items = [item[2] for item in data]
        embeddings = []
        for batch_start in range(0, len(items), self.batch_size):
            batch_end = batch_start + self.batch_size
            batch = items[batch_start:batch_end]
            response = self.client.embeddings.create(model=self.embedding_model, input=batch).data
            for i, be in enumerate(response):
                assert i == be.index
            batch_embeddings = [e.embedding for e in response]
            embeddings.extend(batch_embeddings)

        df = pd.DataFrame({"title": titles, "embedding": embeddings})
        return df

    def create_chroma_client(self):
        persist_directory = 'chroma_persistence'
        chroma_client = chromadb.PersistentClient(path=persist_directory)
        return chroma_client

    def create_chroma_collection(self):
        chroma_client = self.create_chroma_client()
        embedding_function = OpenAIEmbeddingFunction(api_key=free_secret_key, model_name=self.embedding_model)
        collection = chroma_client.create_collection(name='stevie_collection', embedding_function=embedding_function)
        return collection

    def add_to_chroma_collection(self):
        df_embedding = self.get_embedding()
        chroma_client = self.create_chroma_client()
        self.stevie_collection = self.create_chroma_collection()
        self.stevie_collection.add(
            ids = df_embedding.index.astype(str).tolist(),
            documents = df_embedding['title'].tolist(),
            embeddings = df_embedding['embedding'].tolist(),
        )
        chroma_client.persist()

    def query_collection(
        query: str,
        collection: chromadb.api.models.Collection.Collection, 
        max_results: int = 100)-> tuple[list[str], list[float]]:
        results = collection.query(query_texts=query, n_results=max_results, include=['documents', 'distances'])
        strings = results['documents'][0]
        relatednesses = [1 - x for x in results['distances'][0]]
        return strings, relatednesses

    def add_query(self):
        self.strings, self.relatednesses = self.query_collection(
            collection=self.stevie_collection,
            query="ホームページ制作の仕事はありますか？",
            max_results=3,
        )

    def display_results(self):
        for string, relatedness in zip(self.strings, self.relatednesses):
            print(f"{relatedness=:.3f}")
            print(string)

    def main(self):
        self.add_to_chroma_collection()
        self.add_query()
        self.display_results()
