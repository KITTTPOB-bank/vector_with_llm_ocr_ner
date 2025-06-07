import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
from langchain_community.docstore.in_memory import InMemoryDocstore
from uuid import uuid4

import faiss

async def embding_to_faiss():
    df = pd.read_csv("database/Data for Test movie_dataset - AI Engineer.csv")
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")

    cols_to_embed = ["movie_title", "director_name", "genres", "plot_keywords", "title_year", "content_rating"]
    df[cols_to_embed] = df[cols_to_embed].fillna("")
    df = df[cols_to_embed + ["movie_imdb_link"]].dropna(subset=cols_to_embed) 

    embed_model = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=OPENAI_KEY)

    vector_store = FAISS(
        embedding_function=embed_model,
        index=faiss.IndexFlatL2(1536),
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )

    docs = []
    for i, row in df.iterrows():
        text = (
        f"Title: {row['movie_title']}. "
        f"Director: {row['director_name']}. "
        f"Genres: {row['genres'].replace('|', ', ')}. "
        f"Keywords: {row['plot_keywords'].replace('|', ', ')}. "
        f"Year: {row['title_year']}. "
        f"Rating: {row['content_rating']}."
        )        
        doc = Document(
            page_content=text,
            metadata={
                "row_index": i,
                "movie_imdb_link": row["movie_imdb_link"]
            }
        )
        
        docs.append(doc)
    
    uuids = [str(uuid4()) for _ in range(len(docs))]

    vector_store.add_documents(documents=docs, ids=uuids)

    vector_store.save_local("faiss_index")

    return "✅ FAISS index saved"


    