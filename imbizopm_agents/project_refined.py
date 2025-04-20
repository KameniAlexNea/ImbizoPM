import gradio as gr
from langchain.prompts import PromptTemplate
from langchain.chat_models import init_chat_model

# Create a LangChain prompt template for refining the project idea
prompt_template = """
The user has given you a brief project idea. Based on this, you should try to understand the full scope of their project by breaking it down into smaller elements.
Ask follow-up questions if necessary to clarify the project idea. Keep asking until the user confirms that your understanding is correct.

User's project idea: {project_idea}
Refined understanding: 
"""

def refine_project_idea(project_idea, model_name, api_key=None):
    # Instantiate the OpenAI LLM with the chosen model and optional API key
    llm = init_chat_model(model=model_name, api_key=api_key)
    # Initialize the prompt and chain dynamically
    prompt = PromptTemplate(input_variables=["project_idea"], template=prompt_template)
    llm_chain = prompt | llm
    # Generate a refined understanding based on the input
    refined_description = llm_chain.run(project_idea)
    return refined_description

def interface_function(project_idea, model_name, api_key):
    return refine_project_idea(project_idea, model_name, api_key)


def get_interface():
    # Set up the Gradio interface with configurable AI model & API key
    iface = gr.Interface(
        fn=interface_function,
        inputs=[
            gr.Textbox(label="Project Idea", placeholder="Enter your project idea...", lines=5),
            gr.Textbox(label="AI Model", placeholder="e.g., gpt-4", value="gpt-4"),
            gr.Textbox(label="API Key (Optional)", placeholder="Enter API key", type="password")
        ],
        outputs="text",
        title="Project Idea Refinement",
        description="Enter your project idea along with your chosen AI model and API key (if required) to refine your vision."
    )

    # Launch the interface
    return iface

if __name__ == "__main__":
    # Launch the Gradio interface
    iface = get_interface()
    iface.launch()
