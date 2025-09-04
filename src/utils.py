from docx import Document
import re

def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX file.
    """
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def qwen_response(model, tokenizer, system_prompt, user_prompt, max_new_tokens=132768, print_prompt=False):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    if print_prompt:
        print("\n====== Final Prompt Sent to Model ======\n")
        print(text)
        print("\n========================================\n")

    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=max_new_tokens
    )

    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

def qwen_response_train(model, tokenizer, messages, max_new_tokens=132768, print_prompt=False):
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    if print_prompt:
        print("\n====== Final Prompt Sent to Model ======\n")
        print(text)
        print("\n========================================\n")

    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=max_new_tokens
    )

    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

def strip_thinking_content(response_text):
    marker = "</think>"
    index = response_text.find(marker)

    if index != -1:
        return response_text[index + len(marker):].strip()
    else:
        return response_text.strip()  # no marker found; return full response

def remove_word_count_footer(text):
    """
    Remove any trailing '(Word count: ...)' or similar summary note.
    """
    return re.sub(r'\n*\(Word count: \d+\)\s*$', '', text.strip())
