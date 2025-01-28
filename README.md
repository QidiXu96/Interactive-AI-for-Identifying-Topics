# Interactive-AI-for-Identifying-Topics
An Innovative Method for Theme Identification in Healthcare Qualitative Studies Using LLM and Human Collaboration

## Workflow
![Workflow (1)](https://github.com/user-attachments/assets/6e661e89-542d-4ef1-ac88-8a207b4e04b6)

The IAITH framework consists of two phases:
	1.	**Preprocessing Phase**: In this phase, the *Clue-LLM* generates context-based clues from a given dialogue (with human-identified topics) in the training set. The *Reasoning-LLM* then generates reasonings that link these clues to the identified topics. The *Evaluation-LLM* analyzes the clue-reasoning-topic pairs across the training set and provides common feedback, which is used by the *Optimization-LLM* to fine-tune the clue and reasoning instructions. These four LLM agents work together iteratively to refine the instructions.
	2.	**Inference Phase**: In this phase, the *Topic-LLM* utilizes the finetuned clue and reasoning instructions to identify all applicable, consistent topics for new dialogues. Humans can provide feedback throughout this process. The identified topics are then processed by the *Merge-LLM*, which clusters them by merging semantically related or synonymous topics to generate the final consolidated topics.

