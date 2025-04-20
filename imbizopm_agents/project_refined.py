import gradio as gr
from langchain.prompts import PromptTemplate
from langchain.chat_models import init_chat_model

# Create a LangChain prompt template for refining the project idea
prompt_template = """
The user has given you a brief project idea. Based on this, you should try to understand the full scope of their project by breaking it down into smaller elements.
Ask follow-up questions if necessary to clarify the project idea. Keep asking until the user confirms that your understanding is correct.

User's project idea: {project_idea}
Refined understanding only (Do not include any other text): 
"""


def refine_project_idea(project_idea, model_name, api_key=None):
    # Instantiate the OpenAI LLM with the chosen model and optional API key
    llm = init_chat_model(model=model_name, api_key=api_key)
    # Initialize the prompt and chain dynamically
    prompt = PromptTemplate(input_variables=["project_idea"], template=prompt_template)
    llm_chain = prompt | llm
    # Generate a refined understanding based on the input
    refined_description = llm_chain.invoke(project_idea).content.strip()
    return refined_description


# Updated feedback prompt template to use the initial refinement output instead of the original project idea
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
4. Be specific and actionable

REFINED PROJECT DEFINITION:
"""


# Updated function to use only the initial refinement output and feedback for further refinement
def refine_project_idea_with_feedback(
    project_idea, refined_understanding, feedback, model_name, api_key=None
):
    if not refined_understanding or not feedback:
        raise ValueError("Both refined understanding and feedback must be provided")
    
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
        return final_refinement
    except Exception as e:
        return f"Error in refining with feedback: {str(e)}"


def interface_function(
    project_idea: str,
    model_name: str,
    api_key: str,
    feedback: str = None,
    output_text: str = None,
):
    if not project_idea or not project_idea.strip():
        return "Please provide a project idea."
    
    if not model_name or not model_name.strip():
        return "Please specify an AI model."
        
    # First-time project idea submission with no feedback
    if not feedback or not feedback.strip():
        try:
            return refine_project_idea(project_idea, model_name, api_key)
        except Exception as e:
            return f"Error processing your request: {str(e)}"
    
    # Refinement with feedback
    if not output_text or not output_text.strip():
        return "Missing previous refinement. Please submit your project idea first."
        
    try:
        return refine_project_idea_with_feedback(
            project_idea, output_text, feedback, model_name, api_key
        )
    except Exception as e:
        return f"Error processing your feedback: {str(e)}"


def get_interface():
    # Set up the Gradio interface using Blocks for more control
    with gr.Blocks() as iface:
        gr.Markdown("# Project Idea Refinement")
        gr.Markdown(
            "Enter your project idea along with your chosen AI model and API key (if required), and optionally provide feedback to further refine your vision."
        )

        with gr.Row():
            with gr.Column(scale=2):
                project_idea_input = gr.Textbox(
                    label="Project Idea",
                    placeholder="Enter your project idea...",
                    lines=5,
                )
                feedback_input = gr.Textbox(
                    label="Feedback (Optional)",
                    placeholder="Enter feedback for refinement...",
                    lines=3,
                )
            with gr.Column(scale=1):
                model_input = gr.Textbox(
                    label="AI Model",
                    placeholder="e.g., ollama:cogito:32b",
                    value="ollama:cogito:32b",
                )
                api_key_input = gr.Textbox(
                    label="API Key (Optional)",
                    placeholder="Enter API key",
                    type="password",
                )
                submit_button = gr.Button("Refine Idea")

        output_text = gr.Textbox(label="Refined Project Idea", lines=10)

        submit_button.click(
            fn=interface_function,
            inputs=[
                project_idea_input,
                model_input,
                api_key_input,
                feedback_input,
                output_text,
            ],
            outputs=[output_text],
        )

    # Launch the interface
    return iface


if __name__ == "__main__":
    iface = get_interface()
    iface.launch()
