from typing import Optional

from ideasfactory.utils.session_manager import SessionManager
from ideasfactory.documents.document_manager import DocumentManager

async def load_document_content(session_id: str, document_type: str) -> Optional[str]:
    """
    Load document content from the session or document manager.
    
    Args:
        session_id: Session ID
        document_type: Type of document to load
        
    Returns:
        Document content or None if not found
    """
    # Get document path from session manager
    session_manager = SessionManager()
    document_path = session_manager.get_document(session_id, document_type)
    
    if document_path:
        # Load from specific path
        doc_manager = DocumentManager()
        document = doc_manager.get_document(document_path)
        if document and "content" in document:
            return document["content"]
    
    # Fallback to loading by type
    doc_manager = DocumentManager()
    document = await doc_manager.get_latest_document_by_type(document_type, session_id)
    if document and "content" in document:
        # Store path for future reference
        if "filepath" in document:
            session_manager.add_document(session_id, document_type, document["filepath"])
        return document["content"]
    
    return None