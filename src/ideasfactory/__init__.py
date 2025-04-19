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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ideasfactory.log"),
        logging.StreamHandler()
    ]
)

# Define version
__version__ = "0.1.0"


def main():
    """Run the IdeasFactory application."""
    app = IdeasFactoryApp()
    app.run()


if __name__ == "__main__":
    main()