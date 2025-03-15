"""
Utility functions for streaming LLM outputs to Gradio interfaces.
"""

import itertools
import time
from typing import Callable, Dict, Generator, List, Optional, Union

import gradio as gr


def stream_with_progress(
    text_generator: Generator[str, None, None], 
    update_interval: float = 0.1
) -> Generator[str, None, None]:
    """
    Stream text with progress indicator.
    
    Args:
        text_generator: Generator yielding text chunks
        update_interval: Time between progress updates
    
    Yields:
        Text chunks with progress indicator
    """
    accumulated_text = ""
    start_time = time.time()
    dots = itertools.cycle([".", "..", "..."])
    last_update = start_time
    
    # Start with progress indicator
    yield "Generating"
    
    for chunk in text_generator:
        accumulated_text += chunk
        current_time = time.time()
        
        # Update progress indicator every update_interval seconds
        if current_time - last_update > update_interval:
            yield f"{accumulated_text} {next(dots)}"
            last_update = current_time
    
    # Return final text without progress indicator
    yield accumulated_text


def gradio_streaming_generator(
    generator_fn: Callable, 
    *args, 
    **kwargs
) -> Callable:
    """
    Wrapper for generator functions to make them compatible with Gradio streaming.
    
    Args:
        generator_fn: Function that returns a generator
        *args, **kwargs: Arguments to pass to generator_fn
        
    Returns:
        Function suitable for Gradio's streaming interface
    """
    def wrapped_generator():
        return stream_with_progress(generator_fn(*args, **kwargs))
    
    return wrapped_generator
