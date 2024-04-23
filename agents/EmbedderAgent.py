from abc import ABC
from .core import Agent 
from vertexai.language_models import TextEmbeddingModel



class EmbedderAgent(Agent, ABC): 
    """ 
    This Agent generates embeddings 
    """ 

    agentType: str = "EmbedderAgent"

    def __init__(self, mode, embeddings_model='textembedding-gecko@002'): 
        if mode == 'vertex': 
            self.mode = mode 
            self.model = TextEmbeddingModel.from_pretrained(embeddings_model)

        elif mode == 'lang-vertex': 
            self.mode = mode 
            from langchain.embeddings import VertexAIEmbeddings
            self.model = VertexAIEmbeddings() 

        else: raise ValueError('EmbedderAgent mode must be either vertex or lang-vertex')



    def create(self, question): 
        """Text embedding with a Large Language Model."""

        if self.mode == 'vertex': 
            if isinstance(question, str): 
                embeddings = self.model.get_embeddings([question])
                for embedding in embeddings:
                    vector = embedding.values
                return vector
            
            elif isinstance(question, list):  
                vector = list() 
                for q in question: 
                    embeddings = self.model.get_embeddings([q])

                    for embedding in embeddings:
                        vector.append(embedding.values) 
                return vector
            
            else: raise ValueError('Input must be either str or list')

        elif self.mode == 'lang-vertex': 
            vector = self.embeddings_service.embed_documents(question)
            return vector           