"""
Base step class for workflow UI components.
"""

import gradio as gr

from ..base import BaseUI


class BaseWorkflowStep(BaseUI):
    """Base class for workflow steps."""

    def __init__(self):
        """Initialize the base workflow step."""
        super().__init__()

    def build_step(self, visible: bool = False) -> gr.Group:
        """
        Build the UI for this workflow step.

        Args:
            visible: Whether the step should be visible by default

        Returns:
            The Gradio Group containing this step's UI elements
        """
        raise NotImplementedError("Subclasses must implement build_step method")

    def register_event_handlers(self) -> None:
        """Register event handlers for this step's UI elements."""
