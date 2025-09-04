from flask import Flask, request, jsonify, render_template, session
import os
import json
import time
from agents import get_completion, extract_text_from_docx, topic_identification, common_topics, topic_identification_with_feedback

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session storage

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'docx'}

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Ensure the directory exists

OUTPUT_FOLDER = 'outputs'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Ensure the directory exists

def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')  # Render the homepage

# API information
@app.route('/save-azure-config', methods=['POST'])
def save_azure_config():
    """Save Azure configuration entered by the user."""
    data = request.json
    session['azure_endpoint'] = data.get('azure_endpoint')
    session['api_key'] = data.get('api_key')
    session['api_version'] = data.get('api_version')
    session['model'] = data.get('model')
    return jsonify({"message": "Azure configuration saved successfully!"})



# upload interview
@app.route('/upload-dialogue', methods=['POST'])
def upload_dialogue():
    """Handle dialogue file upload."""
    if 'dialogue' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['dialogue']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed types: .docx"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        file.save(filepath)
        return jsonify({"message": "File uploaded successfully", "file_path": filepath})
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

# display interview content   
@app.route('/get-file-content', methods=['GET'])
def get_file_content():
    """Fetch the content of the uploaded file."""
    file_path = request.args.get('file_path')
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        # Check the file extension and process accordingly
        if file_path.endswith('.docx'):
            content = extract_text_from_docx(file_path)  
        else:
            # Process plain text files
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": f"Error reading file: {str(e)}"}), 500

# topic identification (3 times running and keep common ones)
@app.route('/process-dialogue', methods=['POST'])
def process_dialogue():
    """Process uploaded dialogue and return dummy results."""
    data = request.json
    file_path = data.get('file_path')

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    try:
        azure_config = {
            "azure_endpoint": session.get('azure_endpoint'),
            "api_key": session.get('api_key'),
            "api_version": session.get('api_version'),
            "model": session.get('model')
        }

        dialogue = extract_text_from_docx(file_path)

        results_file = os.path.join(OUTPUT_FOLDER, "topic_identification_multiple_results.json")
        results = {} # store each running result

        # 3 time running
        for run in range(1, 4):  
            messages = topic_identification(dialogue)
            topics_response = get_completion(messages, azure_config)  
            results[f"run_{run}"] = topics_response
            time.sleep(1)

        # Save the 3-run results as a JSON file
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        messages = common_topics(results_file)
        common_response = get_completion(messages, azure_config) 

        return jsonify({"topics": common_response, "results_file": results_file})

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/regenerate', methods=['POST'])
def regenerate():
    """Regenerate results based on user feedback or generate a new response."""
    data = request.json
    file_path = data.get('file_path')
    feedback = data.get('feedback')
    previous_results = data.get('previous_results')

    try:
        azure_config = {
            "azure_endpoint": session.get('azure_endpoint'),
            "api_key": session.get('api_key'),
            "api_version": session.get('api_version'),
            "model": session.get('model')
        }

        dialogue = extract_text_from_docx(file_path)
        
        if feedback is None:  # Called from "Try Again"
            results_file = os.path.join(UPLOAD_FOLDER, "topic_identification_multiple_results.json")
            results = {}  # Store each run result

            for run in range(1, 4):
                messages = topic_identification(dialogue)
                topics_response = get_completion(messages, azure_config)
                results[f"run_{run}"] = topics_response
                time.sleep(1)

            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4)

            messages = common_topics(results_file)
            regenerated_response = get_completion(messages, azure_config)
  
        else:  # Called from "Regenerate with Feedback"
            messages = topic_identification_with_feedback(dialogue, feedback, previous_results)
            regenerated_response = get_completion(messages, azure_config)

        return jsonify({"regenerated_results": regenerated_response})
    
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/finalize-response', methods=['POST'])
def finalize_response():
    """Save the finalized response."""
    data = request.json
    final_response = data.get('final_response')

    try:
        with open(os.path.join(OUTPUT_FOLDER, "final_topic_identification.json"), "w") as f:
            json.dump(final_response, f, indent=4)
        return jsonify({"message": "Final response saved successfully!"})
    except Exception as e:
        return jsonify({"error": f"Failed to save final response: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)