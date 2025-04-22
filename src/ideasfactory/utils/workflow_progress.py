import asyncio

# Create a helper for updating progress
async def update_progress(screen, selector: str, status_text: str, progress_value: int):
    """
    Update a progress indicator on a screen.
    
    Args:
        screen: Screen instance
        selector: CSS selector for the progress bar
        status_text: Status text to show
        progress_value: Progress value (0-100)
    """
    # Update status text if a status widget is available
    status_widgets = screen.query(f"{selector}_status")
    if status_widgets:
        status_widgets[0].update(status_text)
    
    # Update progress bar if available
    progress_widgets = screen.query(f"{selector}_progress")
    if progress_widgets:
        progress_widgets[0].update(progress=progress_value)
    
    # Force a UI refresh
    screen.refresh()
    
    # Small pause to allow UI to update
    await asyncio.sleep(0.1)