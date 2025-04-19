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
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        # Create the base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Create subdirectories for different document types
        os.makedirs(os.path.join(self.base_dir, "project-vision"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "research-report"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "architecture"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "task-list"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "standards-patterns"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "epics-stories"), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, "stories"), exist_ok=True)
    
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
        # Create a filename from the title
        sanitized_title = title.replace(" ", "-").lower()
        filename = f"{sanitized_title}.md"
        
        # Determine the directory based on the document type
        if document_type in ["project-vision", "research-report", "architecture",
                            "task-list", "standards-patterns", "epics-stories"]:
            directory = os.path.join(self.base_dir, document_type)
        else:
            # Default to the base directory
            directory = self.base_dir
        
        # Create the full path
        filepath = os.path.join(directory, filename)
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
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
                self.repo.git.add(filepath)
                self.repo.git.commit("-m", f"Create {document_type}: {title}")
            except Exception as e:
                logger.error(f"Error committing document to Git: {str(e)}")
        
        return filepath
    
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
            # Read the existing document
            post = self._read_frontmatter(filepath)
            
            # Update content
            post.content = content
            
            # Update metadata if provided
            if metadata:
                for key, value in metadata.items():
                    post[key] = value
            
            # Increment version
            if "version" in post:
                major, minor, patch = post["version"].split(".")
                post["version"] = f"{major}.{minor}.{int(patch) + 1}"
            
            # Add last modified timestamp
            post["updated_at"] = datetime.now().isoformat()
            
            # Write the updated document
            self._write_frontmatter(filepath, post)
            
            # Version control the document if Git is available
            if self.repo:
                try:
                    self.repo.git.add(filepath)
                    message = commit_message or f"Update: {os.path.basename(filepath)}"
                    self.repo.git.commit("-m", message)
                except Exception as e:
                    logger.error(f"Error committing document update to Git: {str(e)}")
            
            return True
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return False
    
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
    
    def list_documents(self, document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available documents.
        
        Args:
            document_type: Type of documents to list (None for all)
            
        Returns:
            List of document information dictionaries
        """
        result = []
        
        try:
            # Determine which directories to search
            if document_type:
                directories = [os.path.join(self.base_dir, document_type)]
            else:
                directories = [
                    os.path.join(self.base_dir, d) for d in [
                        "project-vision", "research-report", "architecture",
                        "task-list", "standards-patterns", "epics-stories", "stories"
                    ]
                ]
            
            # Collect documents from each directory
            for directory in directories:
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
                            result.append(document_info)
            
            return result
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return []
    
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