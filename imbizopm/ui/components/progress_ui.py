"""
Progress indicator UI components for ImbizoPM.
"""

import time
from typing import Dict, List, Optional, Union

import gradio as gr


def create_status_box() -> gr.StatusTracker:
    """Create a status box for tracking long-running operations."""
    return gr.StatusTracker()


def update_status(
    tracker: gr.StatusTracker, 
    message: str, 
    progress: Optional[float] = None
) -> None:
    """
    Update status box with message and progress.
    
    Args:
        tracker: The status tracker component
        message: Status message to display
        progress: Optional progress value (0.0-1.0)
    """
    if progress is not None:
        tracker.update(message, progress=progress)
    else:
        tracker.update(message)


def create_progress_slider() -> gr.Slider:
    """Create a progress slider UI component."""
    return gr.Slider(
        minimum=0, 
        maximum=100, 
        value=0, 
        step=1, 
        label="Progress",
        interactive=False,
        visible=False
    )
