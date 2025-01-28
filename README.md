# Interactive-AI-for-Identifying-Topics
An Innovative Method for Theme Identification in Healthcare Qualitative Studies Using LLM and Human Collaboration

## Workflow
![Workflow (1)](https://github.com/user-attachments/assets/f318174b-3840-4a5f-883f-2fd506e6eb4b)

The IAITH framework consists of two phases:<br>
	1.	**Preprocessing Phase**: In this phase, the *Clue-LLM* generates context-based clues from a given dialogue (with human-identified topics) in the training set. The *Reasoning-LLM* then generates reasonings that link these clues to the identified topics. The *Evaluation-LLM* analyzes the clue-reasoning-topic pairs across the training set and provides common feedback, which is used by the *Optimization-LLM* to fine-tune the clue and reasoning instructions. These four LLM agents work together iteratively to refine the instructions.<br>
	2.	**Inference Phase**: In this phase, the *Topic-LLM* utilizes the finetuned clue and reasoning instructions to identify all applicable. This process is repeated multiple times to ensure the identification of consistent topics. Human involvement is actively encouraged during this phase to provide feedback. The identified topics are then processed by the *Merge-LLM*, which clusters them by merging semantically related or synonymous topics to generate the final consolidated topics.<br>

## Prompt Structure
### Prompt for *Clue-LLM* in the Preprocessing phase
```
System: You are a linguistic expert with extensive experience analyzing patient-doctor dialogues. These patients are diagnosed with heart failure. You are trying to understand patient's perception of the intensity of heart failure medications. Your task is to extract key clues (limit to 200 words) diectly from original dialogues supporting each given identified topic.<br>
Clues must:<br>
- Be direct quotes from the dialogue (no summarization or interpretation).<br>
- Be brief but contextually complete.<br>
- Highlight key phrases, contextual information, emotional tones, or symptoms related to the topic.<br>

User: List clues (i.e. key phrases, contextual information, semantic and emotional tones, temporal information, symptom descriptions) in the following patient-doctor dialogue that support each given identified topic.<br>
Dialogue: {dialogue}<br>
Topics: {human-identified topics}<br>
Clues:
```




