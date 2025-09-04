from AzureUtils import get_completion, read_docx
import time
import json
import os

def topic_identification_prompt(dialogue, optimized_clue, optimized_reasoning):
    prompt = (
        "Your task is to identify ALL applicable topics for the given interview."
        "Each topic should be concise, meaningful, and specific. Avoid combining distinct ideas or using vague terms.\n\n"
        "There may be multiple topics, so ensure you capture each distinct one.\n\n"
        f"Step 1 Extract CLUES: {optimized_clue}\n\n"
        f"Step 2 Generate REASONING: {optimized_reasoning}\n\n"
        "Step 3 Identify TOPICS: Based on the dialogue, clues, and reasoning, identify all applicable topics.\n\n"

        "### IMPORTANT REQUIREMENTS FOR IDENTIFIED TOPICS ###\n\n"
        "- **Clarity:** Use precise and specific language, avoiding vague or ambiguous terms such as 'perception' or 'impact' without emotional context.\n\n"
        "- **Single Concept:** Ensure each topic represents one distinct idea, avoiding the merging of separate concepts.\n\n"
        "- **Relevance and Specificity:** Make topics meaningful, actionable, and directly related to the context of the dialogue.\n\n"
        "- **Self-Explanatory:** Each topic should be understandable on its own, without needing to read the clues or reasoning. The topic itself should help readers grasp the content meaningfully.\n\n"

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
            "content": """
            ### Background ###
            The COVID-19 pandemic severely tested global health systems, leading to rapid operational adaptations like surge capacity expansion and widespread telemedicine adoption, while exposing critical vulnerabilities in supply chains. 
            Healthcare workforces faced immense mental health burdens and ethical dilemmas regarding resource allocation and duty to treat. Policy responses varied, with governance structures and political leadership significantly influencing effectiveness, often highlighting pre-existing weaknesses in public health infrastructure and exacerbating health inequities. The crisis underscored the urgent need for sustained investment in preparedness, data-driven decision-making, and universal health coverage to build more resilient and equitable systems for future challenges.
            
            You are a qualitative research expert with extensive experience analyzing interviews.
            These interviews were conducted with health workers, policymakers, key informants, and patients between Oct-Dec 2020 to examining the health system response to COVID-19 in Sierra Leone.
            The research aims to explore how the pandemic affected service delivery, health workers, patient access to services, leadership, and governance. Additionally, the research examines to what extent the legacy of the 2013–2016 Ebola outbreak influenced the COVID-19 response and public perception.

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

def process_multiple_dialogues_n(dialogue_file_paths, optimized_clue, optimized_reasoning, output_dir, n):
    # multipe run for each interview
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  

    summary = {}

    for dialogue_file_path in dialogue_file_paths:
        dialogue_name = os.path.splitext(os.path.basename(dialogue_file_path))[0]
        output_file_path = os.path.join(output_dir, f"{dialogue_name}_results.json")

        results = {}

        try:
            dialogue = read_docx(dialogue_file_path)

            for run in range(1, n+1):  
                messages = topic_identification_prompt(dialogue, optimized_clue, optimized_reasoning)
                response = get_completion(messages)  
                res = response.choices[0].message.content.strip()
                results[f"run_{run}"] = res

                time.sleep(1)
    
        except Exception as e:
            print(f"Error processing {dialogue_file_path}: {e}")
            results["error"] = str(e)

        with open(output_file_path, "w", encoding='utf-8') as json_file:
            json.dump(results, json_file, indent=4)

        summary[dialogue_file_path] = output_file_path

    return summary

def aggregate_topics(json_file_path):
    try:
        with open(json_file_path, "r") as file:
            outputs = json.load(file)
    except Exception as e:
        print(f"Error reading file {json_file_path}: {e}")
        return None

    prompt = (
        "You are analyzing topic identification outputs from multiple analyses of the same interview.\n\n"
        "### Your Goal ###\n\n"
        "Aggregate all topics found across multiple outputs. If a topic appears in multiple outputs:\n"
        "- Merge all its associated clues (without modification).\n"
        "- Concisely summarize the reasoning.\n"
        "- Choose the best topic name from the outputs.\n\n"
        "For unique topics (appearing only once):\n"
        "- Keep them as they are.\n\n"
        
        "### Instructions ###\n"
        "For each topic:\n"
        "1. Select the best topic name.\n"
        "2. Aggregate all associated clues (without modification).\n"
        "3. Summarize the reasoning concisely.\n\n"

        "### Output Format ###\n"
        "Provide your results in the following format for EACH topic:\n\n"
        "Topic: [Insert best topic name]\n\n"
        "Clues (max 200 words): [Insert aggregated clues]\n\n"
        "Reasoning (max 150 words): [Insert summarized reasoning]\n\n"
    )

    for idx, content in enumerate(outputs.values(), start=1): 
        prompt += f"Output {idx}:\n{content}\n\n"
    
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant analyzing topic identification outputs to aggregate results effectively."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    return messages

def process_aggregate_topics(summary, aggregate_results_dir):
    os.makedirs(aggregate_results_dir, exist_ok=True)

    aggregate_results_summary = {}

    for dialogue_file_path, json_file_path in summary.items():
        try:
            dialogue_name = os.path.splitext(os.path.basename(dialogue_file_path))[0]
            aggregate_file_path = os.path.join(aggregate_results_dir, f"{dialogue_name}_aggregate.json")

            messages = aggregate_topics(json_file_path)
            response = get_completion(messages)  
            aggregate = response.choices[0].message.content.strip()

            with open(aggregate_file_path, "w", encoding='utf-8') as file:
                json.dump({"aggregate_topics": aggregate}, file, indent=4)

            aggregate_results_summary[dialogue_file_path] = aggregate_file_path

        except Exception as e:
            print(f"Error consolidating topics for {dialogue_file_path}: {e}")

    return  aggregate_results_summary

def remove_double_asterisks(data):
    """
    Recursively remove '**' from all keys and values in a dictionary or list.
    """
    if isinstance(data, dict):
        return {key.replace('**', ''): remove_double_asterisks(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [remove_double_asterisks(item) for item in data]
    elif isinstance(data, str):
        return data.replace('**', '')
    else:
        return data
    
def remove_triple_hash(data):
    """
    Recursively remove '###' from all keys and values in a dictionary or list.
    """
    if isinstance(data, dict):
        return {key.replace('### ', ''): remove_triple_hash(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [remove_triple_hash(item) for item in data]
    elif isinstance(data, str):
        return data.replace('### ', '')
    else:
        return data
    
def process_multiple_json_files(file_paths):
    for file_path in file_paths:
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)

            # Clean the JSON data
            cleaned_data = remove_double_asterisks(json_data)
            cleaned_data = remove_triple_hash(cleaned_data)

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(cleaned_data, file, indent=4)

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

def merge_json_files(file_paths, output_file_path):
    merged_data = {}

    for file_path in file_paths:
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)

            file_name = os.path.splitext(os.path.basename(file_path))[0]
            merged_data[file_name] = json_data

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    output_dir = os.path.dirname(output_file_path)
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(merged_data, file, indent=4)
    except Exception as e:
        print(f"Error saving merged JSON file: {e}")

def save_entire_json_as_expanded_text(input_json_path, output_text_path):
    """
    Load the JSON file and produce a text file that expands any literal
    '\\n' into actual newlines, printing nested dictionaries/lists in
    a more human-readable way.
    """
    with open(input_json_path, 'r', encoding='utf-8') as infile:
        data = json.load(infile)

    # Recursively replace literal "\n" with real newlines in strings
    def expand_newlines(obj):
        if isinstance(obj, dict):
            return {k: expand_newlines(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [expand_newlines(item) for item in obj]
        elif isinstance(obj, str):
            # If the JSON had "...\n..." as an escaped newline, by the time
            # we do json.load(), it should already be a real newline in Python.
            # But if the original file literally contained "\\n", this will fix it:
            return obj.replace('\\n', '\n')
        else:
            return obj

    data = expand_newlines(data)

    # Convert the data to a custom multi-line text format
    def dict_to_str(d, indent=0):
        lines = []
        for k, v in d.items():
            if isinstance(v, dict):
                lines.append(" " * indent + f"{k}:")
                lines.append(dict_to_str(v, indent + 4))
            elif isinstance(v, list):
                lines.append(" " * indent + f"{k}:")
                lines.append(list_to_str(v, indent + 4))
            else:
                # For strings or other scalars, indent them
                text_val = str(v).replace('\n', '\n' + ' ' * (indent + 4))
                lines.append(" " * indent + f"{k}: {text_val}")
        return "\n".join(lines)

    def list_to_str(lst, indent=0):
        lines = []
        for item in lst:
            if isinstance(item, dict):
                lines.append(" " * indent + "-")
                lines.append(dict_to_str(item, indent + 4))
            elif isinstance(item, list):
                lines.append(" " * indent + "-")
                lines.append(list_to_str(item, indent + 4))
            else:
                # For strings or other scalars, indent them
                text_val = str(item).replace('\n', '\n' + ' ' * (indent + 4))
                lines.append(" " * indent + f"- {text_val}")
        return "\n".join(lines)

    if isinstance(data, dict):
        final_text = dict_to_str(data)
    elif isinstance(data, list):
        final_text = list_to_str(data)
    else:
        # If it's just a scalar, just convert it
        final_text = str(data)

    # Write the custom-formatted text to a file
    with open(output_text_path, 'w', encoding='utf-8') as outfile:
        outfile.write(final_text)

def codebook(json_file):
    import json

    with open(json_file, "r", encoding="utf-8") as f:
        content = json.load(f)

    json_text = json.dumps(content, indent=2, ensure_ascii=False)

    prompt = (
        "Below is a JSON file containing multiple identified topics with extracted clues and generated reasoning.\n\n"
        "**Your task is to create a robust and conceptually sound codebook.** This is a crucial step in thematic analysis for organizing and synthesizing qualitative data.\n\n"
        "### 🧩 Instructions for Codebook Formation:\n"
        "1. **Group original topics into broader, higher-level codes** based on a **single, clearly identifiable shared key concept**.\n"
        "2. **Each original topic must belong to exactly one higher-level code**. Avoid overlap or duplication.\n"
        "3. **Do not merge topics solely based on vague thematic similarity**. Merging must be grounded in a specific, shared concept.\n"
        "4. **Higher-level codes must be mutually exclusive**, covering distinct conceptual territories.\n"
        "5. If an original topic does not share a strong conceptual basis with any others, treat it as its own higher-level code.\n\n"
        "### 🔽 Input JSON:\n"
        f"{json_text}\n\n"
    )

    system_instruction = (
        "You are a qualitative research expert assisting in developing a thematic codebook from structured interview results. \n\n"
        "Each entry consists of:\n"
        "- **Topic**: a theme identified in one interview.\n"
        "- **Clues**: direct quotes from the dialogue.\n"
        "- **Reasoning**: why this topic is relevant or meaningful.\n\n"
        "Your task:\n"
        "- Review all topic-clue-reasoning triples.\n"
        "- Merge them into distinct, high-quality codes.\n\n"
        "Each code in the codebook should include:\n"
        "- `code_name`: The name of the higher-level concept\n"
        "- `description`: A short explanation of what this code captures and why the grouped topics fit\n"
        "- `original_topics`: The list of topics it covers\n"
        "- `representative_clues`: A few relevant supporting quotes\n\n"
        "Only merge topics when there is a strong conceptual overlap. Be precise and avoid redundancy."
    )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt}
    ]

    return messages
