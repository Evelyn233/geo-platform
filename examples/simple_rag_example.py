#!/usr/bin/env python
"""
Simple RAG example using RAG-Anything without complex LightRAG processing
"""

import os
import asyncio
import logging
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add project root directory to Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from raganything import RAGAnything, RAGConfig
from raganything.config import ContextConfig
from lightrag.utils import logger

# Gemini imports
import google.generativeai as genai

# Hugging Face imports
from transformers import AutoTokenizer, AutoModel
import torch
import requests
import json

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=False)


async def gemini_complete_if_cache(
    model: str,
    prompt: str,
    system_prompt: str = None,
    history_messages: List[Dict[str, str]] = None,
    messages: List[Dict[str, Any]] = None,
    api_key: str = None,
    **kwargs,
) -> str:
    """Gemini completion function with caching"""
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("Google API key is required for Gemini")
    
    genai.configure(api_key=api_key)
    
    # Use Gemini Pro for text generation
    model_name = "gemini-1.5-pro"
    
    try:
        model = genai.GenerativeModel(model_name)
        
        # Prepare the full prompt
        full_prompt = ""
        if system_prompt:
            full_prompt += f"System: {system_prompt}\n\n"
        if history_messages:
            for msg in history_messages:
                full_prompt += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"
        if prompt:
            full_prompt += f"User: {prompt}\n"
        
        # Generate response
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        raise


async def gemini_embed(texts: List[str], api_key: str = None) -> List[List[float]]:
    """Gemini embedding function"""
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("Google API key is required for Gemini embeddings")
    
    # Configure Gemini with the API key
    genai.configure(api_key=api_key)
    
    try:
        embeddings = []
        for text in texts:
            # Use the correct Gemini embedding API
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            # Handle both object and dict responses
            if hasattr(result, 'embedding'):
                embeddings.append(result.embedding)
            elif isinstance(result, dict) and 'embedding' in result:
                embeddings.append(result['embedding'])
            else:
                # Try to access the embedding value directly
                embeddings.append(result)
        
        return embeddings
        
    except Exception as e:
        logger.error(f"Error calling Gemini embedding API: {e}")
        raise


async def huggingface_complete_if_cache(
    model: str,
    prompt: str,
    system_prompt: str = None,
    history_messages: List[Dict[str, str]] = None,
    messages: List[Dict[str, Any]] = None,
    api_key: str = None,
    **kwargs,
) -> str:
    """Hugging Face completion function using free models"""
    try:
        # Prepare the full prompt
        full_prompt = ""
        if system_prompt:
            full_prompt += f"System: {system_prompt}\n\n"
        if history_messages:
            for msg in history_messages:
                full_prompt += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"
        if prompt:
            full_prompt += f"User: {prompt}\n"
        
        # Use Hugging Face Inference API (free tier)
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        
        response = requests.post(
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
            headers=headers,
            json={"inputs": full_prompt, "max_length": 100}
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            return str(result)
        else:
            raise Exception(f"Hugging Face API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error calling Hugging Face API: {e}")
        raise


async def huggingface_embed(texts: List[str], api_key: str = None) -> List[List[float]]:
    """Hugging Face embedding function using free models"""
    try:
        # Use a simple sentence transformer model
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Load model and tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        
        embeddings = []
        for text in texts:
            # Tokenize and get embeddings
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = model(**inputs)
                # Use mean pooling
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy().tolist()
                embeddings.append(embedding)
        
        return embeddings
        
    except Exception as e:
        logger.error(f"Error calling Hugging Face embedding: {e}")
        raise


async def simple_rag_example(
    file_path: str,
    output_dir: str,
    api_key: str,
    model_type: str = "gemini",
):
    """
    Simple RAG example that avoids complex LightRAG processing
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure RAG
        config = RAGConfig(
            working_dir="./simple_rag_storage",
            parser="mineru",
            parse_method="auto",
            multimodal_processing={
                "image": False,
                "table": False,
                "equation": False,
            },
            max_concurrent_files=1,
            context_config=ContextConfig(
                context_window=1,
                context_mode="page",
                max_context_tokens=2000,
                include_headers=True,
                include_captions=True,
                filter_content_types=["text"],
            ),
        )
        
        # Define LLM model function based on model type
        if model_type == "gemini":
            def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
                return gemini_complete_if_cache(
                    "gemini-1.5-pro",
                    prompt,
                    system_prompt=system_prompt,
                    history_messages=history_messages,
                    api_key=api_key,
                    **kwargs,
                )
        else:  # huggingface
            def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
                return huggingface_complete_if_cache(
                    "microsoft/DialoGPT-medium",
                    prompt,
                    system_prompt=system_prompt,
                    history_messages=history_messages,
                    api_key=api_key,
                    **kwargs,
                )
        
        # Define embedding function based on model type
        if model_type == "gemini":
            from lightrag.utils import EmbeddingFunc
            embedding_func = EmbeddingFunc(
                embedding_dim=768,
                max_token_size=8192,
                func=lambda texts: gemini_embed(texts, api_key=api_key),
            )
        else:  # huggingface
            from lightrag.utils import EmbeddingFunc
            embedding_func = EmbeddingFunc(
                embedding_dim=384,
                max_token_size=8192,
                func=lambda texts: huggingface_embed(texts, api_key=api_key),
            )
        
        # Simple vision model function
        def vision_model_func(prompt, system_prompt=None, history_messages=[], image_data=None, messages=None, **kwargs):
            return llm_model_func(prompt, system_prompt, history_messages, **kwargs)
        
        # Initialize RAGAnything with minimal settings
        rag = RAGAnything(
            config=config,
            llm_model_func=llm_model_func,
            vision_model_func=vision_model_func,
            embedding_func=embedding_func,
        )
        
        # Process document
        logger.info(f"Processing document: {file_path}")
        await rag.process_document_complete(
            file_path=file_path, 
            output_dir=output_dir, 
            parse_method="auto"
        )
        
        # Simple query
        logger.info("\nQuerying processed document:")
        query = "What is the main content of the document?"
        logger.info(f"Query: {query}")
        
        try:
            result = await rag.aquery(query, mode="hybrid")
            logger.info(f"Answer: {result}")
        except Exception as e:
            logger.error(f"Query failed: {e}")
            # Try simple text processing instead
            logger.info("Trying simple text processing...")
            
            # Get the parsed content directly
            from raganything.parser import get_parser
            parser = get_parser("mineru")
            content_list = await parser.parse(file_path, method="auto")
            
            # Simple text extraction
            text_content = ""
            for content in content_list:
                if hasattr(content, 'text') and content.text:
                    text_content += content.text + "\n"
            
            logger.info(f"Extracted text content: {text_content[:500]}...")
            
            # Simple query using LLM directly
            simple_prompt = f"Based on this document content:\n\n{text_content}\n\nQuestion: {query}\n\nAnswer:"
            answer = await llm_model_func(simple_prompt)
            logger.info(f"Simple answer: {answer}")
        
    except Exception as e:
        logger.error(f"Error in simple RAG example: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


def main():
    """Main function to run the simple example"""
    parser = argparse.ArgumentParser(description="Simple RAG Example")
    parser.add_argument("file_path", help="Path to the document to process")
    parser.add_argument(
        "--output", "-o", default="./output", help="Output directory path"
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("GOOGLE_API_KEY"),
        help="API key for the selected model",
    )
    parser.add_argument(
        "--model-type",
        choices=["gemini", "huggingface"],
        default="gemini",
        help="Type of model to use (gemini or huggingface)",
    )

    args = parser.parse_args()

    # Check if API key is provided
    if not args.api_key:
        logger.error("Error: API key is required")
        return

    # Create output directory if specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)

    # Run simple RAG example
    asyncio.run(
        simple_rag_example(
            args.file_path,
            args.output,
            args.api_key,
            args.model_type,
        )
    )


if __name__ == "__main__":
    print("Simple RAG Example")
    print("=" * 30)
    print("Processing document with simplified RAG pipeline")
    print("=" * 30)

    main()

