import database.elastic as elastic 
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import cohere
from langchain_chroma import Chroma

load_dotenv()

async def rerank_cohere(docs : list , query: str , top_n: int = 4):
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    co = cohere.ClientV2(api_key=COHERE_API_KEY)
    response = co.rerank(
        model="rerank-v3.5",
        query=query,
        documents=docs,
        top_n=top_n,
    )

    return response.results


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
 
    vector_store = Chroma(
        collection_name="movies",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db",
    )

    raw_results = vector_store.similarity_search(
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
 
async def hybrid_search(query: str):
    try:
        keyword_docs = await keyword_search(query)
    except Exception as e:
        keyword_docs = []

    try:
        vector_docs = await vector_search(query)
    except Exception as e:
        vector_docs = []

    combined = vector_docs + keyword_docs

    seen_links = set()
    unique_docs = []
 
    for item in combined:
        link = item.get("movie_imdb_link")
        if link not in seen_links:
            seen_links.add(link)
            unique_docs.append(item)
    try:
        docs = [item["content"] for item in unique_docs]
        rerank : list[dict] = await rerank_cohere(docs , query)

    except Exception as e:
        docs = []
    final_results = []
    for item in rerank:
 
        idx = item.index
        doc = unique_docs[idx]
 
        final_results.append({
            "content": doc["content"],
            "movie_imdb_link": doc.get("movie_imdb_link"),
            "relevance_score": item.relevance_score
        })
 
    return final_results
