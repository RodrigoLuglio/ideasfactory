"""
IdeasFactory - Agile AI Driven Documentation for Complex Projects Development using AI Agents.

This package provides a tool that helps mature ideas from brainstorming to complete
implementation plans with detailed documentation.
"""

import os
import sys
import logging
from typing import Optional, List

from ideasfactory.ui.app import IdeasFactoryApp

def setup_logging():
    """Set up consistent logging across the application."""
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("ideasfactory.log"),
            logging.StreamHandler()
        ]
    )
    
    # Set specific levels for modules
    logging.getLogger("ideasfactory.agents").setLevel(logging.DEBUG)
    logging.getLogger("ideasfactory.documents").setLevel(logging.DEBUG)
    logging.getLogger("ideasfactory.ui").setLevel(logging.INFO)
    logging.getLogger("ideasfactory.utils").setLevel(logging.DEBUG)
    logging.getLogger("ideasfactory.tools").setLevel(logging.INFO)

# Define version
__version__ = "0.1.0"


def main():
    """Run the IdeasFactory application."""
    # Set up logging
    setup_logging()
    logging.info("Starting IdeasFactory application...")
    logging.info(f"IdeasFactory version: {__version__}")
    logging.info("Python version: %s", sys.version)
    logging.info("OS: %s", os.name)
    logging.info("Platform: %s", sys.platform)
    logging.info("Architecture: %s", os.uname().machine if hasattr(os, 'uname') else "Unknown")
    logging.info("Environment variables: %s", os.environ)
    logging.info("Command line arguments: %s", sys.argv)
    logging.info("Current working directory: %s", os.getcwd())
    logging.info("Python path: %s", sys.path)
    
    app = IdeasFactoryApp()
    app.run()


if __name__ == "__main__":
    main()