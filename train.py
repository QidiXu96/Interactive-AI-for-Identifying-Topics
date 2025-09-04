import json
import os
import glob
import codecs
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from utils import extract_text_from_docx, qwen_response_train, strip_thinking_content, remove_word_count_footer

def clue_prompt(dialogue, topics, clue_instruction):
    """
    clue_LLM:
    input: (dialogue, topic)
    output: (clue)
    """
    prompt = (
        f"{clue_instruction}\n\n"
        f"Dialogue:\n{dialogue}\n\n"
        f"Topics:\n{topics}\n\n"
        "### Output Format EXACTLY following ###\n\n"
        "Topic: clues\n\n"
    )
    
    messages = [
        {
            "role": "system",
            "content": """
            You are a qualitative research expert with extensive experience analyzing interviews. 
            These interviews were conducted with health workers, policymakers, key informants, and patients between Oct-Dec 2020 to examining the health system response to COVID-19 in Sierra Leone.
            The research aims to explore how the pandemic affected service delivery, health workers, patient access to services, leadership, and governance. Additionally, the research examines to what extent the legacy of the 2013–2016 Ebola outbreak influenced the COVID-19 response and public perception.
            Your task is to extract key clues (limit to 200 words) diectly from original dialogues supporting each given identified topic.

            Clues must:
            - Be direct quotes from the dialogue (no summarization/interpretation/explanation).
            - Be brief but contextually complete.
            - Highlight key phrases, contextual information, emotional tones, or symptoms related to the topic.
            """
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    return messages

def reasoning_prompt(clues, topics, reasoning_instruction):
    """
    reasoning_LLM:
    input: (clue, topic)
    output: (reasoning)
    """
    prompt = (
        f"{reasoning_instruction}\n\n"
        f"Clues:\n{clues}\n\n"
        f"Topics:\n{topics}\n\n"
         "### Output Format EXACTLY following ###\n\n"
        "Topic: reasoning\n\n"
        )
    
    messages = [
        {
            "role": "system",
            "content": """
            You are a qualitative research expert with extensive experience analyzing interviews.
            These interviews were conducted with health workers, policymakers, key informants, and patients between Oct-Dec 2020 to examining the health system response to COVID-19 in Sierra Leone.
            The research aims to explore how the pandemic affected service delivery, health workers, patient access to services, leadership, and governance. Additionally, the research examines to what extent the legacy of the 2013–2016 Ebola outbreak influenced the COVID-19 response and public perception.
            Your goal is to provide a clear and concise reasoning process (limit to 150 words) based on provided clues to explain each corresponding identified topic.

            Ensure your reasoning:
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

def evaluation_prompt_batch(json_file_paths):
    prompt = ""

    for i, file_path in enumerate(json_file_paths):
        with open(file_path, "r") as file:
            data = json.load(file)
            clues = data.get("clues", "N/A")
            reasoning = data.get("reasoning", "N/A")
            topics = data.get("topics", "N/A")
        
        # Append each dialogue's evaluation content to the prompt
        prompt += (
            f"### Clues-Reasoning-Topic Pairs ###\n\n"
            f"**Clues:** {clues}\n\n"
            f"**Reasoning:** {reasoning}\n\n"
            f"**Topics:** {topics}\n\n"
            "### Evaluation Task ###\n"
            "For the above Clues-Reasoning-Topic pair:\n"
            "1. **Clue Quality:** Evaluate the clues based on the following:\n"
            "   - How relevant and accurate are the clues in supporting the topic(s)?\n"
            "   - Are the clues complete (include all key information) and free of irrelevant details?\n\n"
            "2. **Reasoning Quality:** Assess the reasoning based on the following:\n"
            "   - Does the reasoning logically connect the clues to the topic(s)?\n"
            "   - Are there any gaps or missing logic in the reasoning process?\n"
            "   - Is the reasoning concise and free of unnecessary content?\n\n"
        )
    
    # Add the aggregate feedback section
    prompt += (
        "Based on your evaluation of all the Clues-Reasoning-Topic pairs, provide in the following format EXACTLY following:\n\n"
        "### Aggregate Feedback Task ###\n"
        "**Common Issues:**\n"
        "- **Clue Generation:** Identify recurring problems in the generated clues (e.g., missing context, irrelevant clues).\n"
        "- **Reasoning Generation:** Highlight frequent issues in reasoning (e.g., logical gaps, weak connections between clues and topics).\n\n"
        "**Suggestions for Improvement:**\n"
        "- **Clue Prompt:** Propose specific improvements to the clue generation prompt.\n"
        "- **Reasoning Prompt:** Recommend actionable enhancements to the reasoning generation prompt.\n\n"
    )
    
    messages = [
        {
            "role": "system",
            "content": """
            You are an evaluation expert tasked with analyzing a BATCH of clue-reasoning-topic pairs.
            These interviews were conducted with health workers, policymakers, key informants, and patients between Oct-Dec 2020 to examining the health system response to COVID-19 in Sierra Leone.
            The research aims to explore how the pandemic affected service delivery, health workers, patient access to services, leadership, and governance. Additionally, the research examines to what extent the legacy of the 2013–2016 Ebola outbreak influenced the COVID-19 response and public perception.

            Your tasks are as follows:\n
            1. Evaluate each Clues-Reasoning-Topic pair for Clue Quality and Reasoning Quality.\n
            2. Provide feedback on both the relevance and completeness of the clues, and the logical coherence of the reasoning.\n
            3. Identify common issues across all pairs in clue and reasoning generation.\n
            4. Suggest improvements to the clue and reasoning prompts based on recurring patterns of errors.
            """
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    return messages

def optimization_prompt(clue_prompt, reasoning_prompt, feedback):
    do_not_violate_block = (
        "### DO NOT VIOLATE THE FOLLOWING SYSTEM RULES ###\n\n"
        "These are foundational instructions that must NEVER be contradicted or weakened.\n\n"
        "[CLUE RULES]\n"
        "Be direct quotes from the dialogue (no summarization/interpretation/explanation).\n"
        "Quotes must be brief but contextually complete.\n\n"
        "[REASONING RULES]\n"
        "Use only the provided clues.\n"
        "Do not introduce external information or assumptions.\n\n"
    )
    prompt = (
        "You are tasked with improving two prompts based on provided feedback.\n\n"
        "### Task Description ###\n"
        "Given the following feedback, improve both the **Clue Prompt** and the **Reasoning Prompt** simultaneously to address the issues and suggestions provided:\n\n"
        "1. The **Clue Prompt** should:\n"
        "   - Guide the user/system to extract relevant, precise, and contextually complete clues directly from the dialogue.\n"
        "   - Ensure the clues are accurate quotes, avoid irrelevant or incomplete clues, and incorporate missing elements identified in the feedback.\n"
        "   - Focus on ensuring clarity and usability of the prompt.\n\n"
        "2. The **Reasoning Prompt** should:\n"
        "   - Guide the user/system to logically and effectively connect the clues to the identified topics.\n"
        "   - Ensure the reasoning structure is clear, addresses logical gaps, and builds a strong link between the clues and topics.\n"
        "   - Incorporate improvements to reasoning clarity and structure as per the feedback.\n\n"
        f"{do_not_violate_block}\n\n"
        "### Provided Inputs ###\n"
        f"**Feedback:**\n{feedback}\n\n"
        f"**Current Clue Prompt:**\n{clue_prompt}\n\n"
        f"**Current Reasoning Prompt:**\n{reasoning_prompt}\n\n"
        "### Output Instructions ###\n"
        "You MUST provide your improved prompts formatted as follows:\n"
        "- For the clue prompt: `<IMPROVED_CLUE_PROMPT> your improved clue prompt text </IMPROVED_CLUE_PROMPT>`\n"
        "- For the reasoning prompt: `<IMPROVED_REASONING_PROMPT> your improved reasoning prompt text </IMPROVED_REASONING_PROMPT>`\n\n"
        "The text provided between these tags will directly replace the current prompts, so ensure your improvements are complete, clear, and directly address the feedback provided.\n\n"
    )

    messages = [
        {
            "role": "system",
            "content": """
            You are part of an optimization system that improves text. You will be asked to creatively and critically improve the clue prompt and reasoning prompt (instructions). 
            You will receive some feedback, and use the feedback to improve both clue and reasoning prompts simultaneously. The feedback may be noisy, identify what is important and what is correct. 
            Pay attention to the role description of the clue and reasoning prompts (instructions), and the context in which it is used. 
            """
    
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    return messages

def complete_workflow(model, tokenizer, docx_file_paths, topics_list, clue_instruction, reasoning_instruction, json_output_dir, iteration):
    json_file_paths = []

    for i, file_path in enumerate(docx_file_paths):
        try:
            # Step 1: Extract dialogue from `.docx`
            dialogue = extract_text_from_docx(file_path)

            # Get the corresponding topics
            topics = topics_list[i]

            # Step 2: Generate clues using `clue_prompt`
            clue_messages = clue_prompt(dialogue, topics, clue_instruction)
            clue_response = qwen_response_train(model, tokenizer, clue_messages)
            clues = remove_word_count_footer(strip_thinking_content(clue_response))
        
            # Step 3: Generate reasoning using `reasoning_prompt`
            reasoning_messages = reasoning_prompt(clues, topics, reasoning_instruction)
            reasoning_response = qwen_response_train(model, tokenizer, reasoning_messages)
            reasoning = remove_word_count_footer(strip_thinking_content(reasoning_response))

            # Save intermediate results to JSON
            json_file_path = f"{json_output_dir}/{file_path.split('/')[-1].replace('.docx', f'_iteration_{iteration + 1}.json')}"
            json_file_paths.append(json_file_path)
            with open(json_file_path, "w") as json_file:
                json.dump({
                    "dialogue": file_path,
                    "clues": clues,
                    "reasoning": reasoning,
                    "topics": topics
                }, json_file, indent=4)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Step 4: Evaluate batches using `evaluation_prompt_batch`
    evaluation_messages = evaluation_prompt_batch(json_file_paths)
    evaluation_response = qwen_response_train(model, tokenizer, evaluation_messages)
    evaluation = strip_thinking_content(evaluation_response)

    aggregate_feedback_marker = "### Aggregate Feedback Task ###"
    agg_feedback = ""
    if aggregate_feedback_marker in evaluation:
        agg_feedback = evaluation.split(aggregate_feedback_marker, 1)[1]   
    
    # Step 5: Optimize prompts using `optimization_prompt`
    optimized_messages = optimization_prompt(clue_instruction, reasoning_instruction, agg_feedback)
    optimization_response = qwen_response_train(model, tokenizer, optimized_messages)
    optimization = strip_thinking_content(optimization_response)
    optimized_clue_prompt = optimization.split("<IMPROVED_CLUE_PROMPT>")[1].split("</IMPROVED_CLUE_PROMPT>")[0].strip()
    optimized_reasoning_prompt = optimization.split("<IMPROVED_REASONING_PROMPT>")[1].split("</IMPROVED_REASONING_PROMPT>")[0].strip()

    # Output the results for this iteration
    return {
        "feedback": agg_feedback,
        "optimized_clue_prompt": optimized_clue_prompt,
        "optimized_reasoning_prompt": optimized_reasoning_prompt
    }

def iterative_workflow(
    model, tokenizer, docx_file_paths, topics_list, initial_clue_instruction, initial_reasoning_instruction, json_output_dir, num_iterations
):
    clue_instruction = initial_clue_instruction
    reasoning_instruction = initial_reasoning_instruction
    final_results = {}

    for iteration in range(num_iterations):
        print(f"Running iteration {iteration}/{num_iterations}...")
        iteration_json_output_dir = f"{json_output_dir}/iteration_{iteration}"
        os.makedirs(iteration_json_output_dir, exist_ok=True)

        # Save current prompts
        previous_clue_prompt = clue_instruction
        previous_reasoning_prompt = reasoning_instruction
        
        # Step 1: Run the complete workflow for this iteration
        results = complete_workflow(model, tokenizer, docx_file_paths, topics_list, clue_instruction, reasoning_instruction, iteration_json_output_dir, iteration)

        # Update the prompts for the next iteration
        clue_instruction = results["optimized_clue_prompt"]
        reasoning_instruction = results["optimized_reasoning_prompt"]

        final_results[f"Iteration {iteration}"] = {
            "previous_clue_prompt": previous_clue_prompt,
            "previous_reasoning_prompt": previous_reasoning_prompt,
            "feedback": results["feedback"],
            "obtained_improved_clue_prompt": clue_instruction,
            "obtained_improved_reasoning_prompt": reasoning_instruction
        }

        print(f"\nIteration {iteration} Feedback:")
        print(results["feedback"])
        print(f"\nOptimized Clue Prompt (Iteration {iteration}):")
        print(clue_instruction)
        print(f"\nOptimized Reasoning Prompt (Iteration {iteration}):")
        print(reasoning_instruction)

    return {
        "final_results": final_results
    }

# evaluation
def get_shot_folders(base_path):
    """Retrieve all available shot folders dynamically."""
    return sorted(glob.glob(os.path.join(base_path, "*_shots")))

def get_iteration_folders(shot_folder):
    """Retrieve all available iteration folders inside a given shot folder."""
    return sorted(glob.glob(os.path.join(shot_folder, "iteration_*")))

def get_clues(json_file):
    """Read a JSON file, fix all Unicode symbols, and return decoded content."""
    with codecs.open(json_file, "r", encoding="utf-8") as file:
        raw_data = file.read()  # Read raw content
        decoded_data = json.loads(raw_data)  # Properly decode JSON
    
    # Extract and clean 'clues'
    clues = decoded_data.get("clues", "")
    
    return clues  # Return cleaned clues

def process_iteration(iteration_folder):
    """Process a single iteration folder (may have more than one json file) and return extracted data."""
    json_files = [f for f in glob.glob(os.path.join(iteration_folder, "*.json")) if "iteration" in os.path.basename(f)]

    all_clues = []  # Store clues from all JSON files in this shot folder

    for json_file in json_files:
        clues = get_clues(json_file)
        all_clues.append(clues)

    return " ".join(all_clues)  # Concatenate all extracted clues

def get_all_iterations_for_shot(base_path, shot_number):
    """Retrieve dataset for all iterations of a specific few-shot setting."""
    shot_folder = os.path.join(base_path, f"{shot_number}_shots")
    
    # Ensure the shot folder exists
    if not os.path.exists(shot_folder):
        print(f"Error: Shot folder '{shot_folder}' does not exist.")
        return None

    # Get all iteration folders inside this shot
    iteration_folders = get_iteration_folders(shot_folder)

    data_list = []
    for iteration_folder in iteration_folders:
        iteration_number = os.path.basename(iteration_folder).split("_")[-1]  # Extract {j} from "iteration_{j}"
        model_extracted = process_iteration(iteration_folder)

        data_list.append({
            "shot_number": shot_number,
            "iteration_number": iteration_number,
            "model_extracted": model_extracted,
            "human_annotated": ""  # Leave blank for manual input
        })

    return pd.DataFrame(data_list)  # Return DataFrame containing all iterations

def get_all_few_shots(base_path):
    """Retrieve datasets for all few-shot settings, including all iterations."""
    shot_folders = get_shot_folders(base_path)
    
    few_shot_datasets = {}
    for shot_folder in shot_folders:
        shot_number = os.path.basename(shot_folder).split("_")[0]  # Extract {i} from "{i}_shots"
        few_shot_datasets[shot_number] = get_all_iterations_for_shot(base_path, shot_number)

    return few_shot_datasets  # Dictionary with shot_number as key and DataFrame as value

# Function to compute Jaccard similarity at the token level
def compute_jaccard(model_text, human_text):
    model_tokens = set(word_tokenize(model_text.lower()))  # Tokenize and normalize case
    human_tokens = set(word_tokenize(human_text.lower()))  # Tokenize and normalize case

    intersection = model_tokens.intersection(human_tokens)
    union = model_tokens.union(human_tokens)

    return len(intersection) / len(union) if union else 0  # Avoid division by zero


