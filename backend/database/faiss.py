import pandas as pd
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
import asyncio
import os

async def embding_to_faiss():
    df = pd.read_csv(r"C:\vector_with_llm_ocr_ner\serch_movie\csv\Data for Test movie_dataset - AI Engineer.csv")

    cols_to_embed = ["movie_title", "director_name", "genres", "plot_keywords", "title_year", "content_rating"]
    df = df[cols_to_embed + ["movie_imdb_link"]].dropna(subset=cols_to_embed)

    embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")

    faiss_index = None

    for i, row in df.iterrows():
 
        text = " | ".join([str(row[col]) for col in cols_to_embed])

 
        doc = Document(
            page_content=text,
            metadata={
                "row_index": i,
                "movie_imdb_link": row["movie_imdb_link"]
            }
        )
 
        embedding = await embed_model.aembed_query(text)

    
        if faiss_index is None:
            faiss_index = FAISS.from_embeddings([(doc, embedding)], embed_model)
        else:
            faiss_index.add_embeddings([embedding], [doc])

 
    faiss_index.save_local("faiss_movie_index")

    return "✅ FAISS index saved to ./faiss_movie_index/"
 
