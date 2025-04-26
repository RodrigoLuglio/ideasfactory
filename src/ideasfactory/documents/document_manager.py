"""
Document management utilities for IdeasFactory.

This module provides utilities for creating, storing, and versioning documents.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

import git
import frontmatter

from ideasfactory.utils.error_handler import handle_errors, safe_execute, handle_async_errors

# Configure logging
logger = logging.getLogger(__name__)


class DocumentManager:
    """
    Manager for creating, storing, and versioning documents.
    """
    
    def __init__(self, base_dir: str = "output"):
        """
        Initialize the document manager.
        
        Args:
            base_dir: Base directory for storing documents
        """
        self.base_dir = base_dir
        self._ensure_directories()
        self._init_git_repo()

    def _ensure_directories(self, session_id=None):
        """
        Ensure all required directories exist.
        
        Args:
            session_id: Optional session ID to create session-specific directories
        """
        # Create the base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)
        
        if session_id:
            # Create session-specific directory
            session_dir = os.path.join(self.base_dir, f"session-{session_id}")
            os.makedirs(session_dir, exist_ok=True)
            
            # Create subdirectories for different document types within the session dir
            os.makedirs(os.path.join(session_dir, "project-vision"), exist_ok=True)
            os.makedirs(os.path.join(session_dir, "prd"), exist_ok=True)
            os.makedirs(os.path.join(session_dir, "research-report"), exist_ok=True)
            # Create subfolder for path reports
            os.makedirs(os.path.join(session_dir, "research-report", "path-reports"), exist_ok=True)
            os.makedirs(os.path.join(session_dir, "architecture"), exist_ok=True)
            os.makedirs(os.path.join(session_dir, "task-list"), exist_ok=True)
            os.makedirs(os.path.join(session_dir, "standards-patterns"), exist_ok=True)
            os.makedirs(os.path.join(session_dir, "epics-stories"), exist_ok=True)
            os.makedirs(os.path.join(session_dir, "stories"), exist_ok=True)
            os.makedirs(os.path.join(session_dir, "research-requirements"), exist_ok=True)
        else:
            # Create global subdirectories for different document types
            os.makedirs(os.path.join(self.base_dir, "project-vision"), exist_ok=True)
            os.makedirs(os.path.join(self.base_dir, "prd"), exist_ok=True)
            os.makedirs(os.path.join(self.base_dir, "research-report"), exist_ok=True)
            # Create subfolder for path reports
            os.makedirs(os.path.join(self.base_dir, "research-report", "path-reports"), exist_ok=True)
            os.makedirs(os.path.join(self.base_dir, "architecture"), exist_ok=True)
            os.makedirs(os.path.join(self.base_dir, "task-list"), exist_ok=True)
            os.makedirs(os.path.join(self.base_dir, "standards-patterns"), exist_ok=True)
            os.makedirs(os.path.join(self.base_dir, "epics-stories"), exist_ok=True)
            os.makedirs(os.path.join(self.base_dir, "stories"), exist_ok=True)
            os.makedirs(os.path.join(self.base_dir, "research-requirements"), exist_ok=True)
    
    def _init_git_repo(self):
        """Initialize a Git repository for version control."""
        try:
            # Initialize the repository if it doesn't exist
            if not os.path.exists(os.path.join(self.base_dir, ".git")):
                self.repo = git.Repo.init(self.base_dir)
                
                # Create a .gitignore file
                with open(os.path.join(self.base_dir, ".gitignore"), "w") as f:
                    f.write("# Python\n__pycache__/\n*.py[cod]\n*$py.class\n\n")
                
                # Add and commit the .gitignore file
                self.repo.git.add(".gitignore")
                self.repo.git.commit("-m", "Initial commit: Add .gitignore")
            else:
                # Open the existing repository
                self.repo = git.Repo(self.base_dir)
        except Exception as e:
            logger.error(f"Error initializing Git repository: {str(e)}")
            # Continue without Git support
            self.repo = None
    
    def _write_frontmatter(self, filepath: str, post: frontmatter.Post):
        """
        Write a frontmatter post to a file.
        
        Handles different versions of the frontmatter library.
        """
        try:
            # Try the newer API first
            with open(filepath, "w", encoding="utf-8") as f:
                frontmatter.dump(post, f)
        except TypeError:
            # If that fails, try the older API
            with open(filepath, "wb") as f:
                content = frontmatter.dumps(post)
                f.write(content.encode('utf-8'))
    
    def _read_frontmatter(self, filepath: str) -> frontmatter.Post:
        """
        Read a frontmatter post from a file.
        
        Handles different versions of the frontmatter library.
        """
        try:
            # Try the newer API first
            with open(filepath, "r", encoding="utf-8") as f:
                return frontmatter.load(f)
        except (UnicodeDecodeError, TypeError):
            # If that fails, try the older API
            with open(filepath, "rb") as f:
                return frontmatter.loads(f.read().decode('utf-8'))
    
    @handle_errors
    def create_document(
        self,
        content: str,
        document_type: str,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new document.
        
        Args:
            content: Content of the document
            document_type: Type of the document (e.g., "project-vision")
            title: Title of the document
            metadata: Additional metadata for the document
            
        Returns:
            Path to the created document
        """
        # Use standardized filenames based on document type
        filename_mapping = {
            "project-vision": "project-vision.md",
            "prd": "product-requirements-document.md",
            "research-report": "research-report.md",
            "architecture": "system-architecture.md",
            "task-list": "task-list.md",
            "standards-patterns": "standards-patterns.md",
            "epics-stories": "epics-stories.md",
            "research-requirements": "technical-research-requirements.md"
        }
        
        # Get standardized filename or create from title
        if document_type == "path-report":
            # For path reports, create a unique filename based on the title
            # This ensures different paths don't overwrite each other
            if metadata and "path_name" in metadata:
                # Use the path name from metadata if available
                safe_path_name = metadata["path_name"].replace(" ", "-").lower()
                filename = f"path-report-{safe_path_name}.md"
            else:
                # Fallback to sanitized title if path_name not provided
                sanitized_title = title.replace(" ", "-").lower()
                if title.startswith("Path Report: "):
                    # Remove the "Path Report: " prefix if present
                    sanitized_title = sanitized_title[12:]
                filename = f"path-report-{sanitized_title}.md"
        elif document_type in filename_mapping:
            filename = filename_mapping[document_type]
        else:
            # Fallback to title-based filename
            sanitized_title = title.replace(" ", "-").lower()
            filename = f"{sanitized_title}.md"
        
        # Check if we have a session_id in the metadata
        session_id = None
        if metadata and "session_id" in metadata:
            session_id = metadata["session_id"]
            
        # Also store the original title in the metadata for display purposes
        if metadata is None:
            metadata = {}
        metadata["display_title"] = title
            
        # Ensure directories exist for this session if applicable
        if session_id:
            self._ensure_directories(session_id)
            
        # Determine the directory based on the document type and session
        if document_type == "path-report":
            # Store path reports in a subdirectory of research-report
            if session_id:
                directory = os.path.join(self.base_dir, f"session-{session_id}", "research-report", "path-reports")
            else:
                directory = os.path.join(self.base_dir, "research-report", "path-reports")
        elif document_type in ["project-vision", "prd", "research-requirements", "research-report", "architecture",
                            "task-list", "standards-patterns", "epics-stories", "stories"]:
            if session_id:
                directory = os.path.join(self.base_dir, f"session-{session_id}", document_type)
            else:
                directory = os.path.join(self.base_dir, document_type)
        else:
            # Default to the base directory or session directory
            if session_id:
                directory = os.path.join(self.base_dir, f"session-{session_id}")
            else:
                directory = self.base_dir
        
        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Create the full path
        filepath = os.path.join(directory, filename)
        
        # Prepare metadata
        # Add standard metadata
        metadata.update({
            "title": title,
            "created_at": datetime.now().isoformat(),
            "document_type": document_type,
            "version": "1.0.0"
        })
        
        # Create a post with frontmatter
        post = frontmatter.Post(content=content, **metadata)
        
        # Write the document to file
        self._write_frontmatter(filepath, post)
        
        # Version control the document if Git is available
        if self.repo:
            try:
                # Use relative path to avoid issues with Git
                rel_path = os.path.relpath(filepath, self.base_dir)
                
                # Check if the file exists to avoid Git errors
                if os.path.exists(filepath):
                    self.repo.git.add(rel_path)
                    self.repo.git.commit("-m", f"Create {document_type}: {title}")
            except Exception as e:
                logger.error(f"Error committing document to Git: {str(e)}")
        
        return filepath
    
    @handle_errors
    def update_document(
        self,
        filepath: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        commit_message: Optional[str] = None
    ) -> bool:
        """
        Update an existing document.
        
        Args:
            filepath: Path to the document
            content: New content for the document
            metadata: New metadata for the document (None to keep existing)
            commit_message: Commit message for version control
            
        Returns:
            True if the update was successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(filepath):
                logger.error(f"Document not found at path: {filepath}")
                return False
                
            # Read the existing document
            try:
                post = self._read_frontmatter(filepath)
            except Exception as e:
                logger.error(f"Error reading document frontmatter: {str(e)}")
                # If we can't read the frontmatter, try to rewrite the file completely
                try:
                    # Create basic metadata as fallback
                    basic_metadata = {
                        "title": os.path.basename(filepath).replace(".md", ""),
                        "updated_at": datetime.now().isoformat(),
                        "version": "1.0.0"
                    }
                    # Update with provided metadata
                    if metadata:
                        basic_metadata.update(metadata)
                    
                    # Create a new post
                    post = frontmatter.Post(content=content, **basic_metadata)
                    
                    # Write to file
                    self._write_frontmatter(filepath, post)
                    logger.info(f"Document recreated after frontmatter read error: {filepath}")
                    return True
                except Exception as inner_e:
                    logger.error(f"Failed to recreate document: {str(inner_e)}")
                    return False
            
            # Update content
            post.content = content
            
            # Update metadata if provided
            if metadata:
                for key, value in metadata.items():
                    post[key] = value
            
            # Increment version
            if "version" in post:
                try:
                    major, minor, patch = post["version"].split(".")
                    post["version"] = f"{major}.{minor}.{int(patch) + 1}"
                except (ValueError, TypeError):
                    # If version parsing fails, just set a new version
                    post["version"] = "1.0.0"
            else:
                post["version"] = "1.0.0"
            
            # Add last modified timestamp
            post["updated_at"] = datetime.now().isoformat()
            
            # Write the updated document
            try:
                self._write_frontmatter(filepath, post)
            except Exception as write_e:
                logger.error(f"Error writing document: {str(write_e)}")
                # Fallback to direct file write if frontmatter fails
                try:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write("---\n")
                        for key, value in post.metadata.items():
                            f.write(f"{key}: {value}\n")
                        f.write("---\n\n")
                        f.write(content)
                    logger.info(f"Document updated using fallback method: {filepath}")
                    return True
                except Exception as fallback_e:
                    logger.error(f"Fallback write failed: {str(fallback_e)}")
                    return False
            
            # Version control the document if Git is available
            if self.repo:
                try:
                    # Use relative path to avoid issues with Git
                    rel_path = os.path.relpath(filepath, self.base_dir)
                    
                    # Check if the file exists to avoid Git errors
                    if os.path.exists(filepath):
                        self.repo.git.add(rel_path)
                        message = commit_message or f"Update: {os.path.basename(filepath)}"
                        self.repo.git.commit("-m", message)
                except Exception as e:
                    logger.error(f"Error committing document update to Git: {str(e)}")
                    # Continue without Git - document is still updated
            
            return True
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return False
    
    @handle_errors
    def get_document(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Get a document and its metadata.
        
        Args:
            filepath: Path to the document
            
        Returns:
            Dictionary with document content and metadata, or None if not found
        """
        try:
            # Read the document
            post = self._read_frontmatter(filepath)
            
            # Return as a dictionary
            result = dict(post)
            result["content"] = post.content
            return result
        except Exception as e:
            logger.error(f"Error reading document: {str(e)}")
            return None
    
    @handle_errors
    def list_documents(self, document_type: Optional[str] = None, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available documents.
        
        Args:
            document_type: Type of documents to list (None for all)
            session_id: Optional session ID to filter by session
            
        Returns:
            List of document information dictionaries
        """
        result = []
        
        try:
            # Check for session-specific directories
            session_directories = []
            if session_id:
                # Only search in the specific session directory
                session_path = os.path.join(self.base_dir, f"session-{session_id}")
                if os.path.exists(session_path):
                    if document_type:
                        doc_type_path = os.path.join(session_path, document_type)
                        if os.path.exists(doc_type_path):
                            session_directories.append(doc_type_path)
                    else:
                        # Add all document type directories in this session
                        for d in [
                            "project-vision", "research-report", "architecture",
                            "task-list", "standards-patterns", "epics-stories", "stories"
                        ]:
                            doc_type_path = os.path.join(session_path, d)
                            if os.path.exists(doc_type_path):
                                session_directories.append(doc_type_path)
            else:
                # Search in all session directories and global directories
                # First, check for session-specific directories
                for dir_entry in os.listdir(self.base_dir):
                    if dir_entry.startswith("session-") and os.path.isdir(os.path.join(self.base_dir, dir_entry)):
                        session_path = os.path.join(self.base_dir, dir_entry)
                        if document_type:
                            doc_type_path = os.path.join(session_path, document_type)
                            if os.path.exists(doc_type_path):
                                session_directories.append(doc_type_path)
                        else:
                            # Add all document type directories in this session
                            for d in [
                                "project-vision", "research-report", "architecture",
                                "task-list", "standards-patterns", "epics-stories", "stories", "path-report"
                            ]:
                                doc_type_path = os.path.join(session_path, d)
                                if os.path.exists(doc_type_path):
                                    session_directories.append(doc_type_path)
                                    
                                    # Also check for path-reports subdirectory in research-report
                                    if d == "research-report":
                                        path_reports_dir = os.path.join(doc_type_path, "path-reports")
                                        if os.path.exists(path_reports_dir):
                                            session_directories.append(path_reports_dir)
                
                # Also check global directories
                if document_type:
                    global_dir = os.path.join(self.base_dir, document_type)
                    if os.path.exists(global_dir):
                        session_directories.append(global_dir)
                else:
                    for d in [
                        "project-vision", "research-report", "architecture",
                        "task-list", "standards-patterns", "epics-stories", "stories", "path-report"
                    ]:
                        global_dir = os.path.join(self.base_dir, d)
                        if os.path.exists(global_dir):
                            session_directories.append(global_dir)
                            
                            # Also check for path-reports subdirectory in research-report
                            if d == "research-report":
                                path_reports_dir = os.path.join(global_dir, "path-reports")
                                if os.path.exists(path_reports_dir):
                                    session_directories.append(path_reports_dir)
            
            # Now collect documents from all identified directories
            for directory in session_directories:
                if os.path.exists(directory):
                    for filename in os.listdir(directory):
                        if filename.endswith(".md"):
                            filepath = os.path.join(directory, filename)
                            
                            # Read the document metadata
                            post = self._read_frontmatter(filepath)
                            
                            # Add to the result
                            document_info = dict(post)
                            document_info["filepath"] = filepath
                            document_info["filename"] = filename
                            
                            # Determine session ID from path
                            path_parts = os.path.normpath(filepath).split(os.sep)
                            for part in path_parts:
                                if part.startswith("session-"):
                                    document_info["session_id"] = part[8:]  # Remove "session-" prefix
                                    break
                            
                            result.append(document_info)
            
            return result
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return []
    
    @handle_errors
    def get_document_history(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Get the version history of a document.
        
        Args:
            filepath: Path to the document
            
        Returns:
            List of version information dictionaries
        """
        if not self.repo:
            return []
        
        try:
            # Get the relative path
            rel_path = os.path.relpath(filepath, self.base_dir)
            
            # Get the commit history for the file
            commits = list(self.repo.iter_commits(paths=rel_path))
            
            # Format the result
            history = []
            for commit in commits:
                history.append({
                    "commit_id": commit.hexsha,
                    "author": commit.author.name,
                    "email": commit.author.email,
                    "date": commit.committed_datetime.isoformat(),
                    "message": commit.message
                })
            
            return history
        except Exception as e:
            logger.error(f"Error getting document history: {str(e)}")
            return []
        
    
    @handle_async_errors
    async def get_latest_document_by_type(self, document_type: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest version of a document of a specific type for a session.
        
        Args:
            document_type: Type of document to retrieve (e.g., "project-vision")
            session_id: Session ID for the document
            
        Returns:
            Document content and metadata, or None if not found
        """
        try:
            # Construct the expected path directly based on our folder structure
            session_path = os.path.join(self.base_dir, f"session-{session_id}")
            doc_type_path = os.path.join(session_path, document_type)
            
            # Use our existing filename mapping
            filename_mapping = {
                "project-vision": "project-vision.md",
                "prd": "product-requirements-document.md",
                "research-report": "research-report.md",
                "architecture": "system-architecture.md",
                "task-list": "task-list.md",
                "standards-patterns": "standards-patterns.md",
                "epics-stories": "epics-stories.md",
                "research-requirements": "technical-research-requirements.md"
            }
            
            if document_type in filename_mapping:
                # Use the standardized filename
                filename = filename_mapping[document_type]
                filepath = os.path.join(doc_type_path, filename)
                
                if os.path.exists(filepath):
                    return self.get_document(filepath)
                else:
                    logger.error(f"Document not found at expected path: {filepath}")
                    return None
            else:
                # If it's not a standard document type, fallback to listing
                documents = self.list_documents(document_type=document_type, session_id=session_id)
                
                if documents:
                    # Sort by version (if available) to get the latest
                    sorted_docs = sorted(
                        documents,
                        key=lambda x: x.get("version", "0.0.0"),
                        reverse=True
                    )
                    return self.get_document(sorted_docs[0]["filepath"])
                else:
                    logger.error(f"No {document_type} documents found for session {session_id}")
                    return None
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            return None
            
    @handle_async_errors
    async def get_all_path_reports(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all path reports for a session.
        
        Args:
            session_id: Session ID to get path reports for
            
        Returns:
            List of path report documents with their content and metadata
        """
        try:
            # Construct the path to the path-reports directory
            path_reports_dir = os.path.join(self.base_dir, f"session-{session_id}", "research-report", "path-reports")
            
            # Check if the directory exists
            if not os.path.exists(path_reports_dir):
                logger.info(f"Path reports directory does not exist for session {session_id}")
                return []
                
            # Get all markdown files in the directory
            path_reports = []
            for filename in os.listdir(path_reports_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(path_reports_dir, filename)
                    document = self.get_document(filepath)
                    if document:
                        # Add the filepath to the document for reference
                        document["filepath"] = filepath
                        path_reports.append(document)
            
            # Sort by path name for consistent ordering
            return sorted(path_reports, key=lambda x: x.get("path_name", x.get("title", "")))
        
        except Exception as e:
            logger.error(f"Error retrieving path reports: {str(e)}")
            return []