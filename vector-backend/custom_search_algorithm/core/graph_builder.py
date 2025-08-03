# graph_builder.py
import networkx as nx
from ..embedding import embed_text
from sentence_transformers.util import cos_sim

def build_graph(parsed_pages, query):
    graph = nx.Graph()
    query_vec = embed_text(query)

    for url, data in parsed_pages.items():
        page_vec = embed_text(data["text"])
        score = cos_sim(query_vec, page_vec).item()

        graph.add_node(url, title=data["title"], score=score,
                       text=data["text"], entities=data["entities"],
                       embedding=page_vec)

    for u in graph.nodes:
        for v in graph.nodes:
            if u == v: continue
            sim = cos_sim(graph.nodes[u]['embedding'], graph.nodes[v]['embedding']).item()
            if sim > 0.4:
                graph.add_edge(u, v, weight=sim)

    return graph