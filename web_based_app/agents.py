import json
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
    """ Read docx file"""
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)



def topic_identification(dialogue):
    """ Topic identification without human feedback (prompts from 2-shots at iteration 1)"""
    prompt = (
        "Your task is to identify ALL applicable topics for the given dialogue. "
        "Topics should be about patient's perception of the intensity of heart failure medications. "
        "Each topic should be concise, meaningful, and specific. Avoid combining distinct ideas or using vague terms.\n\n"
        "There may be multiple topics, so ensure you capture each distinct one.\n\n"
        f"Step 1 Extract CLUES: Identify and extract relevant clues from the patient-doctor dialogue that illuminate the emotional, physical, and practical impacts of medication on the patient's daily life. Ensure that these clues are precise quotes or paraphrases that capture the broader implications of the patient's situation, focusing specifically on the perception of medication intensity. Include contextual details or examples that illustrate the patient's experiences and feelings regarding their medication regimen. Avoid irrelevant or incomplete clues that do not directly relate to the medication's effects.\n\n"
        f"Step 2 Generate REASONING: Using the selected clues, construct a clear and logical reasoning process that explicitly connects the emotional and financial burdens faced by the patient to their potential impact on medication adherence and overall health outcomes. Highlight how these identified issues relate to the patient's experience and summarize the implications of these burdens to reinforce the relevance of the clues to the identified topics. Ensure that the reasoning flows cohesively and addresses any logical gaps, making the connections more evident.\n\n"
        "Step 3 Identify TOPICS: Based on the dialogue, clues, and reasoning, identify all applicable topics.\n\n"

        "### IMPORTANT REQUIREMENTS FOR IDENTIFIED TOPICS ###\n\n"
        "- **Clarity:** Use precise and specific language, avoiding vague or ambiguous terms such as 'perception' or 'impact' without emotional context.\n\n"
        "- **Emotional Context:** Clearly indicate the nature of any perceptions, emotions, or reactions (e.g., positive, negative) as they appear in the dialogue.\n\n"
        "- **Single Concept:** Ensure each topic represents one distinct idea, avoiding the merging of separate concepts.\n\n"
        "- **Relevance and Specificity:** Make topics meaningful, actionable, and directly related to the context of the dialogue.\n\n"
        "- **Self-Explanatory:** Each topic should be understandable on its own, without needing to read the clues or reasoning. The topic itself should help readers grasp the content meaningfully.\n\n"
        
        "### Examples ###\n\n"
        "Good Topics:\n\n"
        "- **Burden from the cost of the medications** (highlights the cost of medications taken as a significant burden)\n\n"
        "- **Impact from patient-doctor relationship** (discusses how the interaction between patient and doctor/healthcare system influences)\n\n"
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
            "content": """You are a qualitative research expert tasked with identifying topics of patient-doctor dialogues.
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



def common_topics(json_file_path):
    try:
        with open(json_file_path, "r") as file:
            outputs = json.load(file)
    except Exception as e:
        print(f"Error reading file {json_file_path}: {e}")
        return None

    prompt = (
        "You are analyzing topic identification outputs from multiple analyses of the same patient-doctor dialogue.\n\n"
        "### Your Goal ###\n\n"
        "Identify common topics across multiple outputs that appear in at least two outputs. For a topic to be considered common, it must:\n"
        "- Have similar meaning.\n"
        "- Be supported by similar extracted clues.\n"
        "- Have similar reasoning.\n\n"
        "**Important:**\n"
        "- Do NOT identify common topics within a single output.\n"
        "- Only compare across multiple outputs.\n\n"
        
        "### Instructions ###\n"
        "For each common topic:\n"
        "1. Select the best topic name from the outputs that represents the common topic.\n"
        "2. Aggregate all associated clues (without modification).\n"
        "3. Summarize the reasoning concisely.\n\n"

        "### Examples ###\n\n"
        "Good Topics:\n\n"
        "- **Burden from the cost of the medications** (highlights the cost of medications taken as a significant burden)\n\n"
        "- **Impact from patient-doctor relationship** (discusses how the interaction between patient and doctor/healthcare system influences)\n\n"
        "Bad Topics:\n\n"
        "- **Medication management support** (vague and unclear. It does not specify whether the patient received support, lacked support, or faced issues related to medication management.)\n\n"
        "- **Perceived medication burden** (vague and unclear. It does not provide sufficient information about whether or not the patient experienced a medication number burden)\n\n"
        "- **Emotional impact of medication side effects** (combines two distinct concepts into one)\n\n"
        "- **Medication adherence and management** (vague and unclear, combines two distinct concepts into one)\n\n"
        "Make sure each identified topic follows good topic examples and avoids bad topic examples.\n\n"

        "### Output Format ###\n"
        "Provide your results in the following format for EACH common topic:\n\n"
        "Topic: [Insert best topic name]\n\n"
        "Clues (max 200 words): [Insert aggregated clues]\n\n"
        "Reasoning (max 150 words): [Insert summarized reasoning]\n\n"
        "If no common topics are found, respond with:\n"
        "'No common topics found.'\n\n"
    )

    for idx, content in enumerate(outputs.values(), start=1): 
        prompt += f"Output {idx}:\n{content}\n\n"
    
    messages = [
        {
            "role": "system",
            "content": "You are an advanced AI designed to analyze outputs from topic identification tasks. Your job is to identify and process common topics based on meaning, clues, and reasoning across multiple outputs."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    return messages





def topic_identification_with_feedback(dialogue, feedback=None, previous_results=None):
    """Topic identification consider human feedback (human should mention which topic-clues-reasoning that they want to modify)"""

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