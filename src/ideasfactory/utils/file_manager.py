"""
File management utilities for IdeasFactory.

This module provides utilities for loading documents and managing files.
"""

import os
import logging
from typing import Optional, Dict, Any, List

from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.documents.document_manager import DocumentManager
from ideasfactory.utils.error_handler import handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)

@handle_async_errors
async def load_document_content(session_id: str, document_type: str) -> Optional[str]:
    """
    Load document content from the session or document manager.
    
    This is the centralized method for document content retrieval across the application.
    
    Args:
        session_id: Session ID
        document_type: Type of document to load
        
    Returns:
        Document content or None if not found
    """
    # Get document path from session manager (single source of truth)
    session_manager = SessionManager()
    document_path = session_manager.get_document(session_id, document_type)
    
    try:
        if document_path:
            # Load from specific path
            doc_manager = DocumentManager()
            document = doc_manager.get_document(document_path)
            if document and "content" in document:
                content_length = len(document["content"]) if document["content"] else 0
                logger.info(f"Document {document_type} loaded from path: {document_path} with {content_length} chars")
                if content_length == 0:
                    logger.warning(f"Document {document_type} has zero length content")
                return document["content"]
            else:
                logger.warning(f"Problem with document {document_type}: exists={document is not None}, has_content={'content' in document if document else False}")
        
        # Fallback to loading by type
        logger.info(f"No document path in session, trying to find document by type: {document_type}")
        doc_manager = DocumentManager()
        document = await doc_manager.get_latest_document_by_type(document_type, session_id)
        if document and "content" in document:
            # Store path for future reference
            if "filepath" in document:
                session_manager.add_document(session_id, document_type, document["filepath"])
                logger.info(f"Document path added to session: {document['filepath']}")
            return document["content"]
        
        logger.warning(f"Document {document_type} not found for session {session_id}")
        return None
    except Exception as e:
        logger.error(f"Error loading document content: {str(e)}")
        return None

# Additional helper functions related to file management can be added here