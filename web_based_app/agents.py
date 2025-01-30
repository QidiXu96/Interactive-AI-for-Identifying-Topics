from docx import Document
from openai import AzureOpenAI

def get_completion(messages, azure_config):
    """ GET completion from openai api"""
    client = AzureOpenAI(
         azure_endpoint = azure_config['azure_endpoint'], 
         api_key = azure_config['api_key'],  
         api_version = azure_config['api_version']
         )
    
    response = client.chat.completions.create(
        model = azure_config['model'], 
        messages = messages,
        max_tokens = 6000,
        temperature = 0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    try:
        return response.choices[0].message.content.strip()
    except (KeyError, IndexError) as e:
        raise ValueError(f"Error parsing Azure API response: {e}")

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def topic_identification(dialogue):
    """Original Topic identification"""

    prompt = (
        "Your task is to identify ALL applicable topics for the given dialogue."
        "Topics should be about patient's perception of the intensity of heart failure medications."
        "Each topic should be concise, meaningful, and specific. Avoid combining distinct ideas or using vague terms.\n\n"
        "There may be multiple topics, so ensure you capture each distinct one.\n\n"
        "Step 1 Extract CLUES: Extract concise and contextually relevant clues from the patient-doctor dialogue that reflect the patient's experiences and emotions, particularly focusing on aspects related to medication adherence and quality of life. Aim to capture precise quotes that highlight specific themes, such as emotional effects of side effects or logistical barriers to treatment. Additionally, incorporate targeted follow-up questions like 'How have the side effects affected your daily life?' or 'What difficulties do you face in accessing your medications?' to elicit deeper insights into the patient's feelings and thoughts. Ensure the clues are clear, relevant, and free from redundancy, providing a comprehensive understanding of the patient's situation.\n\n"
        "Step 2 Generate REASONING: Utilize the extracted clues to construct a coherent narrative that connects to the identified topics, emphasizing the implications of the patient's experiences on medication adherence and overall health management. Organize the reasoning into distinct sections, each addressing specific themes such as emotional impacts, logistical challenges, and patient agency. Clearly articulate the connections between the clues and the topics, ensuring that each link is logical and well-supported. Illustrate the emotional and psychological impacts with specific examples from the clues, focusing on how these experiences affect the patient's treatment outcomes, including financial burdens and the patient-doctor relationship dynamics. Maintain clarity and avoid repetition throughout the reasoning.\n\n"
        "Step 3 Identify TOPICS: Based on the dialogue, clues, and reasoning, identify all applicable topics.\n\n"
        
        "### IMPORTANT REQUIREMENTS FOR IDENTIFIED TOPICS ###\n\n"
        "- **Clarity:** Use precise and specific language, avoiding vague or ambiguous terms such as 'perception' or 'impact' without emotional context.\n\n"
        "- **Emotional Context:** Clearly indicate the nature of any perceptions, emotions, or reactions (e.g., positive, negative) as they appear in the dialogue.\n\n"
        "- **Single Concept:** Ensure each topic represents one distinct idea, avoiding the merging of separate concepts.\n\n"
        "- **Relevance and Specificity:** Make topics meaningful, actionable, and directly related to the context of the dialogue.\n\n"
        
        "### Examples ###\n\n"
        "Good Topics:\n\n"
        "- **Burden from the number of medications** (highlights the number of medications taken as a significant burden)\n\n"
        "- **Problem in logistics** (reports issues related to obtaining medications)\n\n"
        "- **Impact from patient-doctor relationship** (discusses how the interaction between patient and doctor/healthcare system influences)\n\n"
        "- **Adverse drug effects** (report the patient's experience of side effects from medications)\n\n"
        "Bad Topics:\n\n"
        "- **Medication management support** (vague and unclear. It does not specify whether the patient received support, lacked support, or faced issues related to medication management.)\n\n"
        "- **Perceived medication burden** (vague and unclear. It does not provide sufficient information about whether or not the patient experienced a medication number burden)\n\n"
        "- **Emotional impact of medication side effects** (combines two distinct concepts into one)\n\n"
        "- **Medication adherence and management** (vague and unclear, combines two distinct concepts into one)\n\n"
        "Make sure each identified topic follows good topic examples and avoids bad topic examples.\n\n"
        
        "### Output Format ###\n\n"
        "For EACH identified topic, provide the following EXACTLY:\n\n"
        "Identify topic: [Insert topic here]\n\n"
        "Clues (max 200 words): [Insert clues here]\n\n"
        "Reasoning (max 150 words): [Insert reasoning here]\n\n"
        f"Dialogue: {dialogue}\n\n"
    )
    
    messages = [
        {
            "role": "system",
            "content": """You are a medical expert tasked with identifying topics of patient-doctor dialogues.
            These patients are diagnosed with heart failure. You are trying to understand patient's perception of the intensity of heart failure medications.
            
            Your task:
            - Identify **all applicable topics** for the given dialogue (there may be more than one).
            - For each identified topic, provide clues and reasoning to explain the connection.
            
            Clues must:
            - Be direct quotes from the dialogue (no summarization or interpretation).
            - Be brief but contextually complete.
            - Highlight key phrases, contextual information, emotional tones, or symptoms related to the topic.

            Reasoning must:
            - Links the clues directly to the topic.
            - Explains the logical connection between the clues and topic.
            - Avoids adding external context or information not present in the clues.
            """
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    return messages

def topic_identification_with_feedback(dialogue, feedback=None, previous_results=None):
    """Topic identification with feedback resolution and selective topic modification"""

    prompt = (
        "Below is the original dialogue, the previous results, and specific feedback. "
        "Your goal is to revise the previous results according to the feedback while referring back to the original dialogue for context. "
        "Ensure that only the topics mentioned in the feedback are modified, while other topics remain unchanged.\n\n"
        f"### Original Dialogue:\n{dialogue}\n\n"
        f"### Previous Results (JSON Format):\n{previous_results}\n\n"
        f"### Feedback:\n{feedback}\n\n"
        "### Revised Results:\n\n"
        "Provide the updated JSON with the revisions based on the feedback while preserving all other information from the original results."
        "- Identify topic: [Insert topic here]\n"
        "- Clues (max 200 words): [Insert clues here]\n"
        "- Reasoning (max 150 words): [Insert reasoning here]\n"    
    )
    
    messages = [
        {
            "role": "system",
            "content": """You are an expert assistant tasked with refining analytical results based on feedback.  
            
            ### Revision Guidelines:
            1. Reanalyze the original dialogue for topics mentioned in the feedback.
            2. Revise the clues and reasoning for these topics to align with the feedback, ensuring consistency and accuracy.
            3. Preserve all other topics, clues, and reasoning from the previous results without modification.
            4. Maintain the original JSON structure in your revised output.
            5. Ensure that the reasoning is logically derived from the clues and aligns with the feedback.
            """
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    return messages