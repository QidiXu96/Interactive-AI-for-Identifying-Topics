# Interactive-AI-for-Identifying-Topics
An Innovative Method for Theme Identification in Healthcare Qualitative Studies Using AI-Human Collaboration

## Workflow
<img width="6648" height="5288" alt="study overview topic new (11)" src="https://github.com/user-attachments/assets/c95c8ec7-6725-4aa4-959b-b72b294037d6" />

The CoTI framework consists of two phases:<br>
	1.	**Preprocessing Phase**: The preprocessing phase was designed to develop refined clue and reasoning instructions using *Refiner*. This process began with the random selection of several interviews as training examples, which were submitted to the reasoning model to identify relevant topics. These AI-generated topics served as learning examples to iteratively refine the clue and reasoning instructions. The refinement process is iterative, consisting of four interconnected stages: clue instruction, reasoning instruction, evaluation, and optimization. Each stage built upon the previous one, ensuring a systematic progression toward high-quality clue and reasoning instructions.
<br>
	2.	**Inference Phase**: The inference phase aimed to apply the refined clue and reasoning instructions to identify topics for new interviews using *Thematizer*. This phase involved two key steps: topic identification, which involved identifying all applicable topics for each interview (individual-level), and topic merging, which clustered similar topics across all interviews into higher-level topics to develop a final codebook (group-level).
<br>

## No Installation
You can visualize the workflow directly by clicking on [topic_identification_covid19.ipynb](src/covid_topic_identification.ipynb)

## Installation 
The `web_based_app` folder contains the source code for a web-based application, including `.py` and `.html` files. Follow the steps below to run the application.
1. **Clone the Repository**
   ```bash
   git clone https://github.com/QidiXu96/Interactive-AI-Identifying_Topics.git
   cd Interactive-AI-Identifying_Topics/web_based_app
2. **Create Virtual Environment (option)**
   ```bash
   python3 -m venv topic_env
   source topic_env/bin/activate
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
4. **Run the Application**
   ```bash
   python3 app.py
5. **Access the Application**
   ```bash
   open http://127.0.0.1:5000
6. **Modify or Extend** <br>
   You can modify the app.py, agents.py and index.html files in the web_based_app folder to customize the application.

## Prompt Structure
### Prompt for *initial topic discovery* in the Preprocessing phase
```
System message: 
### Background ###
Heart failure patients' perception of medication intensity is a complex experience influenced by factors beyond dosage, including side effects, treatment burden, psychological impact, quality of life, and cost. This perception is shaped by patient characteristics such as age, disease severity, comorbidities, gender, and socioeconomic status. Understanding these perceptions, along with patients' beliefs about their medications, is crucial for improving adherence and tailoring treatment strategies to enhance their quality of life. Ultimately, a patient-centered approach that involves effective communication and shared decision-making is essential in managing heart failure medication regimens.

You are a qualitative research expert tasked with identifying topics of patient-doctor dialogues. These patients are diagnosed with heart failure. You are trying to understand patient's perception of the intensity of heart failure medications.

Your task:
- Identify important topics for the given dialogue (there may be more than one).
- For each identified topic, provide clues and reasoning to explain the connection.
            
Clues must:
- Be direct quotes from the dialogue (no summarization or interpretation).
- Be brief but contextually complete.
- Highlight key phrases, contextual information, emotional tones, or symptoms related to the topic.
Reasoning must:
- Links the clues directly to the topic.
- Explains the logical connection between the clues and topic.
- Avoids adding external context or information not present in the clues.
           
User message: 
Your task is to identify important topics for the given interview.
Each topic should be concise, meaningful, and specific. Avoid combining distinct ideas or using vague terms.
Step 1 Extract CLUES.
Step 2 Generate REASONING.
Step 3 Identify TOPICS: Based on the dialogue, clues, and reasoning, identify all applicable topics.

### Output Format ###
For EACH identified topic, provide the following EXACTLY:
Identify topic: [Insert topic here]
Clues (max 200 words): [Insert clues here]
Reasoning (max 150 words): [Insert reasoning here]

Dialogue: {dialogue}
```
### Prompt for *Clue-LLM* in the Preprocessing phase
```
System message: 
You are a qualitative research expert with extensive experience analyzing patient-doctor dialogues. These patients are diagnosed with heart failure. You are trying to understand patient's perception of the intensity of heart failure medications. Your task is to extract key clues (limit to 200 words) directly from original dialogues supporting each given identified topic.

Clues must:
- Be direct quotes from the dialogue (no summarization/interpretation/explanation).
- Be brief but contextually complete.
- Highlight key phrases, contextual information, emotional tones, or symptoms related to the topic.
          
User message: 
List clues (i.e. key phrases, contextual information, semantic and emotional tones, temporal information, symptom descriptions) in the following patient-doctor dialogue that support each given identified topic.
Dialogue: {dialogue}
Topics: {topics}
### Output Format EXACTLY following ###        
Topic: clues
```
### Prompt for *Reasoning-LLM* in the Preprocessing phase
```
System message: 
You are a qualitative research expert tasked with analyzing patient-doctor dialogues. These patients are diagnosed with heart failure. You are trying to understand patient's perception of the intensity of heart failure medications. Your goal is to provide a clear and concise reasoning process (limit to 150 words) based on provided clues to explain each corresponding identified topic.

Ensure your reasoning:
- Links the clues directly to the topic.
- Explains the logical connection between the clues and topic.
- Avoids adding external context or information not present in the clues.

User message: 
Based on the given clues, generate the reasoning process that supports the identified topics.
Clues: {clues}
Topics: {topics}
### Output Format EXACTLY following ###
Topic: reasoning
```
### Prompt for *Evaluation-LLM* in the Preprocessing phase
```
System message: 
You are an evaluation expert tasked with analyzing a BATCH of patient-doctor dialogue clue-reasoning-topic pairs. These patients are diagnosed with heart failure, and the focus is on understanding their perception of the intensity of heart failure medications. 
Your tasks are as follows:            
1. Evaluate each Clues-Reasoning-Topic pair for Clue Quality and Reasoning Quality.
2. Provide feedback on both the relevance and completeness of the clues, and the logical coherence of the reasoning.            
3. Identify common issues across all pairs in clue and reasoning generation.
4. Suggest improvements to the clue and reasoning prompts based on recurring patterns of errors.

User message: 
Clues-Reasoning-Topic Pair {i + 1} 
**Clues:** {clues}
**Reasoning:** {reasoning}
**Topics:** {topics}

### Evaluation Task ###
For the above Clues-Reasoning-Topic pair:
1. **Clue Quality:** Evaluate the clues based on the following:
- How relevant and accurate are the clues in supporting the topic(s)?
- Are the clues complete (include all key information) and free of irrelevant details?
2. **Reasoning Quality:** Assess the reasoning based on the following:
- Does the reasoning logically connect the clues to the topic(s)?
- Are there any gaps or missing logic in the reasoning process?
- Is the reasoning concise and free of unnecessary content?

### Aggregate Feedback Task ###
Based on your evaluation of all the Clues-Reasoning-Topic pairs, provide in the following format EXACTLY following:
### Aggregate Feedback Task ###
**Common Issues:**
- **Clue Generation:** Identify recurring problems in the generated clues (e.g., missing context, irrelevant clues).        
- **Reasoning Generation:** Highlight frequent issues in reasoning (e.g., logical gaps, weak connections between clues and topics).
**Suggestions for Improvement:**
- **Clue Prompt:** Propose specific improvements to the clue generation prompt.
- **Reasoning Prompt:** Recommend actionable enhancements to the reasoning generation prompt.
```
### Prompt for *Optimization-LLM* in the Preprocessing phase
```
System message: 
You are part of an optimization system that improves text. You will be asked to creatively and critically improve the clue prompt and reasoning prompt (instructions).  You will receive some feedback, and use the feedback to improve both clue and reasoning prompts simultaneously. The feedback may be noisy, identify what is important and what is correct. Pay attention to the role description of the clue and reasoning prompts (instructions), and the context in which it is used. 
           
User message: 
You are tasked with improving two prompts based on provided feedback.

### Task Description ###
Given the following feedback, improve both the **Clue Prompt** and the **Reasoning Prompt** simultaneously to address the issues and suggestions provided:
1. The **Clue Prompt** should:
- Guide the user/system to extract relevant, precise, and contextually complete clues directly from the dialogue.
- Ensure the clues are accurate quotes, avoid irrelevant or incomplete clues, and incorporate missing elements identified in the feedback.
 - Focus on ensuring clarity and usability of the prompt.
2. The **Reasoning Prompt** should:
- Guide the user/system to logically and effectively connect the clues to the identified topics.\n"
- Ensure the reasoning structure is clear, addresses logical gaps, and builds a strong link between the clues and topics.\n"
- Incorporate improvements to reasoning clarity and structure as per the feedback.

### DO NOT VIOLATE THE FOLLOWING SYSTEM RULES ###
These are foundational instructions that must NEVER be contradicted or weakened.
[CLUE RULES]
Be direct quotes from the dialogue (no summarization/interpretation/explanation).
Quotes must be brief but contextually complete.
[REASONING RULES]
Use only the provided clues.
Do not introduce external information or assumptions.

### Provided Inputs ###
**Feedback:**{feedback}
**Current Clue Prompt:**{clue_prompt}
**Current Reasoning Prompt:**{reasoning_prompt}

### Output Instructions ###
You MUST provide your improved prompts formatted as follows:
- For the clue prompt: <IMPROVED_CLUE_PROMPT> your improved clue prompt text </IMPROVED_CLUE_PROMPT>
- For the reasoning prompt: <IMPROVED_REASONING_PROMPT> your improved reasoning prompt text </IMPROVED_REASONING_PROMPT>
The text provided between these tags will directly replace the current prompts, so ensure your improvements are complete, clear, and directly address the feedback provided.
```
### Prompt for *Thematizer* in the Inference phase
```
System message: 
### Background ###
Heart failure patients' perception of medication intensity is a complex experience influenced by factors beyond dosage, including side effects, treatment burden, psychological impact, quality of life, and cost. This perception is shaped by patient characteristics such as age, disease severity, comorbidities, gender, and socioeconomic status. Understanding these perceptions, along with patients' beliefs about their medications, is crucial for improving adherence and tailoring treatment strategies to enhance their quality of life. Ultimately, a patient-centered approach that involves effective communication and shared decision-making is essential in managing heart failure medication regimens.
            
You are a qualitative research expert tasked with identifying topics of patient-doctor dialogues. These patients are diagnosed with heart failure. You are trying to understand patient's perception of the intensity of heart failure medications.
            
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

User message: 
Your task is to identify ALL applicable topics for the given dialogue.  Topics should be about patient's perception of the intensity of heart failure medications. Each topic should be concise, meaningful, and specific. Avoid combining distinct ideas or using vague terms.        
There may be multiple topics, so ensure you capture each distinct one.

Step 1 Extract CLUES: {optimized_clue_prompt}
Step 2 Generate REASONING: {optimized_reasoning_prompt}
Step 3 Identify TOPICS: Based on the dialogue, clues, and reasoning, identify all applicable topics.

### IMPORTANT REQUIREMENTS FOR IDENTIFIED TOPICS ###        
- **Clarity:** Use precise and specific language, avoiding vague or ambiguous terms such as 'perception' or 'impact' without emotional context.
- **Emotional Context:** Clearly indicate the nature of any perceptions, emotions, or reactions (e.g., positive, negative) as they appear in the dialogue.
- **Single Concept:** Ensure each topic represents one distinct idea, avoiding the merging of separate concepts.
- **Relevance and Specificity:** Make topics meaningful, actionable, and directly related to the context of the dialogue.
- **Self-Explanatory:** Each topic should be understandable on its own, without needing to read the clues or reasoning. The topic itself should help readers grasp the content meaningfully.

### Output Format ###
For EACH identified topic, provide the following EXACTLY:
Identify topic: [Insert topic here]
Clues (max 200 words): [Insert clues here]
Reasoning (max 150 words): [Insert reasoning here]
Dialogue: {dialogue}
```
### Prompt for *Codebook-LLM* in the Inference phase
```
System message: 
You are a qualitative research expert assisting in developing a thematic codebook from structured interview results.
Each entry consists of:
- **Topic**: a theme identified in one interview.
- **Clues**: direct quotes from the dialogue.
- **Reasoning**: why this topic is relevant or meaningful.

Your task:
- Review all topic-clue-reasoning triples.
- Merge them into distinct, high-quality codes.
Each code in the codebook should include:
- `code_name`: The name of the higher-level concept
- `description`: A short explanation of what this code captures and why the grouped topics fit
- `original_topics`: The list of topics it covers
- `representative_clues`: A few relevant supporting quotes
Only merge topics when there is a strong conceptual overlap. Be precise and avoid redundancy.

User message: 
Below is a JSON file containing multiple patients’ identified topics with extracted clues and generated reasoning.
**Your task is to create a robust and conceptually sound codebook.** This is a crucial step in thematic analysis for organizing and synthesizing qualitative data.

### Instructions for Codebook Formation ### 
1. **Group original topics into broader, higher-level codes** based on a **single, clearly identifiable shared key concept**.
2. **Each original topic must belong to exactly one higher-level code**. Avoid overlap or duplication.
3. **Do not merge topics solely based on vague thematic similarity**. Merging must be grounded in a specific, shared concept.
4. **Higher-level codes must be mutually exclusive**, covering distinct conceptual territories.
5. If an original topic does not share a strong conceptual basis with any others, treat it as its own higher-level code.

### Examples of Incorrect Merging ###
- 'Low financial burden from medications' merged with 'Patient’s lack of knowledge about heart failure medications'.
→ Incorrect: One relates to financial impact, the other to knowledge.
- Overlapping code labels like 'Patient Knowledge and Perception' vs. 'Patient Understanding of Medications'.
→ Too similar—should be unified under a single label (e.g., 'Patient Comprehension of Medications').

### Examples of Correct Merging ### 
- 'Low financial burden' + 'High financial burden' → 'Financial Impact of Medications' (shared key concept: **Financial Impact**).
- 'Mistrust doctor' + 'Trust doctor' → 'Patient-Doctor Relationship' (shared key concept: **Relational Trust**).
### Input JSON: {original json file}  
```





