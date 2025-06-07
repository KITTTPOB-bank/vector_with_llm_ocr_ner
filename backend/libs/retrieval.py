import database.elastic as elastic 
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import cohere

load_dotenv()

async def keyword_search(query: str, index_name: str = "movie",  top_k: int = 3):
    es = await elastic.connect()  
    search_query = {
        "size": top_k,
        "query": {
            "match": {
                "content": {
                    "query": query,
                    "operator": "or"  
                }
            }
        }
    }
    resp = await es.search(index=index_name, body=search_query)
    hits = resp["hits"]["hits"]
    results = []
    for hit in hits:
        source = hit["_source"]
        results.append({
            "content": source.get("content"),
            "movie_imdb_link": source.get("movie_imdb_link"),
        })
    return results


async def vector_search(query: str, top_k: int = 5):
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")

    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=OPENAI_KEY)

    new_vector_store = FAISS.load_local(
        "faiss_index", embeddings, allow_dangerous_deserialization=True
    )

    raw_results = new_vector_store.similarity_search(
        query=query,
        k=top_k,
    )

    results = []
    for res in raw_results:
        results.append({
            "content": res.page_content,
            "movie_imdb_link": res.metadata.get('movie_imdb_link', None),
        })

    return results

async def rerank(docs : list , query: str , top_n: int = 4):
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    co = cohere.ClientV2(api_key=COHERE_API_KEY)
    response = co.rerank(
        model="rerank-v3.5",
        query=query,
        documents=docs,
        top_n=top_n,
    )

    return response


async def hybrid_search():


    return None