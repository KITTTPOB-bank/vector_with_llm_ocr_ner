from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
import pandas as pd
import os
from uuid import uuid4

async def embedding_to_chroma():
    df = pd.read_csv("database/Data for Test movie_dataset - AI Engineer.csv")
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")

    cols_to_embed = ["movie_title", "director_name", "genres", "plot_keywords", "title_year", "content_rating"]
    df[cols_to_embed] = df[cols_to_embed].fillna("")
    df = df[cols_to_embed + ["movie_imdb_link"]].dropna(subset=cols_to_embed)

    embed_model = OpenAIEmbeddings(model="text-embedding-ada-002", api_key=OPENAI_KEY)
    vector_store = Chroma(
        collection_name="movies",
        embedding_function=embed_model,
        persist_directory="./chroma_langchain_db",  
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

    vector_store.add_documents(documents=docs,  ids=uuids)

    return "✅ Chroma index saved"
