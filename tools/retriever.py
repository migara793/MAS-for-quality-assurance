import logging
from typing import List, Any, Dict
from qdrant_client import QdrantClient
from qdrant_client.http import models
from google import genai
from google.genai import types
from app_utils.env import config

logger = logging.getLogger(__name__)

class ToolRetriever:
    def __init__(self):
        self.client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
        self.genai_client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.collection_name = "mcp_tools"
        self.vector_size = 3072  # gemini-embedding-001 dimension
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            recreate = False
            if exists:
                # Check current dimension
                collection_info = self.client.get_collection(self.collection_name)
                current_dim = collection_info.config.params.vectors.size
                if current_dim != self.vector_size:
                    logger.warning(f"Dimension mismatch: found {current_dim}, expected {self.vector_size}. Recreating collection.")
                    recreate = True

            if not exists or recreate:
                self.client.recreate_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=self.vector_size, distance=models.Distance.COSINE),
                )
                logger.info(f"Initialized Qdrant collection: {self.collection_name} (dim: {self.vector_size})")
        except Exception as e:
            logger.error(f"Error ensuring Qdrant collection: {e}")

    async def _get_embedding(self, text: str) -> List[float]:
        try:
            # Using gemini-embedding-001 which is 3072 dimensions
            response = self.genai_client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Embedding error with gemini-embedding-001: {e}. Trying fallback...")
            return [0.0] * self.vector_size

    async def index_tools(self, tools: List[Any]):
        points = []
        for i, tool in enumerate(tools):
            name = getattr(tool, 'name', f"tool_{i}")
            description = getattr(tool, 'description', "No description provided.")
            
            text_to_embed = f"Tool Name: {name}\nDescription: {description}"
            vector = await self._get_embedding(text_to_embed)
            
            if len(vector) != self.vector_size:
                 logger.error(f"Vector size mismatch for {name}: got {len(vector)}, expected {self.vector_size}")
                 continue

            points.append(models.PointStruct(
                id=i,
                vector=vector,
                payload={
                    "name": name,
                    "description": description,
                    "original_index": i
                }
            ))
        
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Indexed {len(points)} tools into Qdrant.")

    async def retrieve_tools(self, query: str, all_tools: List[Any], top_k: int = 7) -> List[Any]:
        if not query:
            return all_tools[:top_k]
            
        vector = await self._get_embedding(query)
        
        if len(vector) != self.vector_size:
            logger.error(f"Search vector size mismatch: got {len(vector)}, expected {self.vector_size}")
            return all_tools[:top_k]

        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=top_k
        )
        
        relevant_tool_names = [hit.payload["name"] for hit in search_result.points]
        logger.info(f"Retrieved {len(relevant_tool_names)} relevant tools for query: '{query[:50]}...'")
        
        filtered_tools = [t for t in all_tools if getattr(t, 'name', '') in relevant_tool_names]
        return filtered_tools

# Singleton instance
tool_retriever = ToolRetriever()
