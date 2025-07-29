**Vector-**

A deep research tool based on OpenAI's gpt-4o. 

Coded primarily in python. Utilises two layers of LLMS. Layer 1 conducts prompt optimization and analysis to produce search queries. 
These search queries are used to scrape the internet for sources, which are downloaded and placed in a vector store (on average, 30 sources per prompt).
A RAG system then answers the original prompt, including citations from several of the sources downloaded.
