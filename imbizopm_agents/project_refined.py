import time

import gradio as gr
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate

# Create a LangChain prompt template for refining the project idea
prompt_template = """
The user has given you a brief project idea. Based on this, you should try to understand the full scope of their project by breaking it down into smaller elements.
Ask follow-up questions if necessary to clarify the project idea. Keep asking until the user confirms that your understanding is correct.

User's project idea: {project_idea}
Refined understanding only (Do not include any other text): 
"""

# Updated feedback prompt template with clearer instructions
prompt_template_feedback = """
You are an expert project consultant helping to refine a project idea through iterations.

ORIGINAL PROJECT IDEA:
{project_idea}

CURRENT UNDERSTANDING:
{refined_understanding}

USER FEEDBACK:
{feedback}

Based on the original idea and the user's feedback, provide an improved and comprehensive project definition that addresses the feedback while maintaining alignment with the original vision.

Your response should:
1. Integrate the feedback meaningfully 
2. Clarify any ambiguities
3. Identify the project's scope, goals, and potential implementation steps
4. Ask specific follow-up questions about unclear points
5. Be specific and actionable with clear next steps
6. Organize the response with clear sections for: Project Overview, Goals, Implementation Steps, and Open Questions

REFINED PROJECT DEFINITION:
"""

# Dictionary of available models with descriptions
AVAILABLE_MODELS = {
    "ollama:cogito:32b": "Cogito 32B - Good for creative projects",
    "ollama:llama2:13b": "Llama2 13B - Balanced performance",
    "ollama:mistral:7b": "Mistral 7B - Fast and efficient",
    "gpt-3.5-turbo": "GPT-3.5 Turbo - Requires OpenAI API key",
    "gpt-4": "GPT-4 - Advanced capabilities, requires OpenAI API key",
    "custom": "Custom model - Enter a model name manually",
}


def refine_project_idea(project_idea, model_name, api_key=None):
    # Instantiate the LLM with the chosen model and optional API key
    try:
        llm = init_chat_model(model=model_name, api_key=api_key)
        # Initialize the prompt and chain dynamically
        prompt = PromptTemplate(
            input_variables=["project_idea"], template=prompt_template
        )
        llm_chain = prompt | llm
        # Generate a refined understanding based on the input
        refined_description = llm_chain.invoke(project_idea).content.strip()
        return refined_description, None
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg.lower():
            return None, "API key error: Please provide a valid API key for this model."
        elif "connection" in error_msg.lower():
            return (
                None,
                f"Connection error: Could not connect to the model service. Is Ollama running? Error: {error_msg}",
            )
        else:
            return None, f"Error: {error_msg}"


def refine_project_idea_with_feedback(
    project_idea, refined_understanding, feedback, model_name, api_key=None
):
    if not refined_understanding or not feedback:
        return None, "Both refined understanding and feedback must be provided"

    try:
        llm = init_chat_model(model=model_name, api_key=api_key)
        prompt = PromptTemplate(
            input_variables=["project_idea", "refined_understanding", "feedback"],
            template=prompt_template_feedback,
        )
        llm_chain = prompt | llm
        final_refinement = llm_chain.invoke(
            dict(
                project_idea=project_idea,
                refined_understanding=refined_understanding,
                feedback=feedback,
            )
        ).content.strip()
        return final_refinement, None
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg.lower():
            return None, "API key error: Please provide a valid API key for this model."
        elif "connection" in error_msg.lower():
            return (
                None,
                f"Connection error: Could not connect to the model service. Is Ollama running? Error: {error_msg}",
            )
        else:
            return None, f"Error in refining with feedback: {error_msg}"


def get_interface():
    with gr.Blocks() as iface:
        # State variables
        project_state = gr.State("")
        refined_state = gr.State("")
        history_state = gr.State([])

        # Header
        gr.Markdown("# 🔍 Project Idea Refinement")
        gr.Markdown(
            """Enter your project idea and get AI assistance to refine and clarify it. 
            You can provide feedback to further improve the refinement.
            
            > **Tip**: Be specific about your project goals, target audience, and any technical constraints.
            """
        )

        with gr.Tabs():
            with gr.TabItem("Refine Project"):
                with gr.Row():
                    with gr.Column(scale=2):
                        project_idea_input = gr.Textbox(
                            label="Project Idea",
                            placeholder="Example: I want to build a mobile app that helps people track their fitness goals...",
                            lines=5,
                        )
                        feedback_input = gr.Textbox(
                            label="Feedback (Optional)",
                            placeholder="Provide feedback on the refinement or answer any questions...",
                            lines=3,
                            visible=True,
                        )

                        with gr.Row():
                            clear_btn = gr.Button("Clear", variant="secondary")
                            submit_button = gr.Button("Refine Idea", variant="primary")

                    with gr.Column(scale=1):
                        with gr.Group():
                            gr.Markdown("### Model Settings")
                            model_dropdown = gr.Dropdown(
                                choices=list(AVAILABLE_MODELS.keys()),
                                value="ollama:cogito:32b",
                                label="Select AI Model",
                            )
                            custom_model_input = gr.Textbox(
                                label="Custom Model Name",
                                placeholder="Enter custom model name",
                                visible=False,
                            )
                            model_info = gr.Markdown("")
                            api_key_input = gr.Textbox(
                                label="API Key (if required)",
                                placeholder="Enter API key",
                                type="password",
                            )

                with gr.Row():
                    with gr.Row():
                        output_status = gr.Markdown("### Ready")
                    output_text = gr.Textbox(
                        label="Refined Project Idea",
                        lines=10,
                        placeholder="Refinement will appear here...",
                    )

            with gr.TabItem("Refinement History"):
                history_container = gr.HTML("No refinement history yet.")

        # Logic to show/hide custom model input
        def update_model_visibility(model_name):
            is_custom = model_name == "custom"
            model_desc = AVAILABLE_MODELS.get(model_name, "")
            return {
                custom_model_input: gr.update(visible=is_custom),
                model_info: gr.update(
                    value=f"**Model Info**: {model_desc}" if not is_custom else ""
                ),
            }

        model_dropdown.change(
            fn=update_model_visibility,
            inputs=[model_dropdown],
            outputs=[custom_model_input, model_info],
        )

        # Process function for refinement
        def process_refinement(
            project_idea,
            feedback,
            model_selection,
            custom_model,
            api_key,
            project_state,
            refined_state,
            history_state,
        ):
            # Update status to indicate processing
            yield {
                output_status: gr.update(value="### ⏳ Processing..."),
                submit_button: gr.update(interactive=False),
            }

            # Determine which model to use
            model_name = (
                custom_model if model_selection == "custom" else model_selection
            )

            # Store project idea if new
            if not project_state or project_state != project_idea:
                project_state = project_idea

            # First-time submission or new project idea
            if not feedback or not refined_state:
                result, error = refine_project_idea(project_idea, model_name, api_key)

                if error:
                    yield {
                        output_status: gr.update(value=f"### ❌ Error: {error}"),
                        output_text: gr.update(value=""),
                        submit_button: gr.update(interactive=True),
                    }
                    return project_state, refined_state, history_state

                refined_state = result
                # Add to history
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                history_entry = {
                    "timestamp": timestamp,
                    "project": project_idea,
                    "refinement": result,
                    "feedback": None,
                }
                history_state = [history_entry] + history_state

                # Update the history display
                history_html = generate_history_html(history_state)

                yield {
                    output_status: gr.update(
                        value="### ✅ Initial Refinement Complete"
                    ),
                    output_text: gr.update(value=result),
                    history_container: gr.update(value=history_html),
                    submit_button: gr.update(interactive=True),
                }

            # Refinement with feedback
            else:
                if not refined_state:
                    yield {
                        output_status: gr.update(
                            value="### ❌ Error: Missing previous refinement"
                        ),
                        submit_button: gr.update(interactive=True),
                    }
                    return project_state, refined_state, history_state

                result, error = refine_project_idea_with_feedback(
                    project_state, refined_state, feedback, model_name, api_key
                )

                if error:
                    yield {
                        output_status: gr.update(value=f"### ❌ Error: {error}"),
                        submit_button: gr.update(interactive=True),
                    }
                    return project_state, refined_state, history_state

                refined_state = result
                # Add to history
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                history_entry = {
                    "timestamp": timestamp,
                    "project": project_state,
                    "refinement": result,
                    "feedback": feedback,
                }
                history_state = [history_entry] + history_state

                # Update the history display
                history_html = generate_history_html(history_state)

                yield {
                    output_status: gr.update(
                        value="### ✅ Refinement Updated with Feedback"
                    ),
                    output_text: gr.update(value=result),
                    history_container: gr.update(value=history_html),
                    submit_button: gr.update(interactive=True),
                }

            return project_state, refined_state, history_state

        def generate_history_html(history):
            if not history:
                return "No refinement history yet."

            html = "<div style='max-height: 600px; overflow-y: auto;'>"
            for i, entry in enumerate(history):
                html += f"<div style='margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;'>"
                html += (
                    f"<h4>Refinement #{len(history) - i} - {entry['timestamp']}</h4>"
                )
                html += f"<p><strong>Project Idea:</strong><br>{entry['project']}</p>"
                if entry["feedback"]:
                    html += f"<p><strong>Feedback:</strong><br>{entry['feedback']}</p>"
                html += f"<p><strong>Refinement:</strong><br>{entry['refinement']}</p>"
                html += "</div>"
            html += "</div>"
            return html

        def clear_fields():
            return {
                project_idea_input: gr.update(value=""),
                feedback_input: gr.update(value=""),
                output_text: gr.update(value=""),
                output_status: gr.update(value="### Ready"),
            }

        # Connect the interface elements
        submit_button.click(
            fn=process_refinement,
            inputs=[
                project_idea_input,
                feedback_input,
                model_dropdown,
                custom_model_input,
                api_key_input,
                project_state,
                refined_state,
                history_state,
            ],
            outputs=[
                output_status,
                output_text,
                history_container,
                submit_button,
                project_state,
                refined_state,
                history_state,
            ],
        )

        clear_btn.click(
            fn=clear_fields,
            inputs=[],
            outputs=[project_idea_input, feedback_input, output_text, output_status],
        )

    return iface


if __name__ == "__main__":
    demo = get_interface()
    demo.launch()
