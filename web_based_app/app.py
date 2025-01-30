from flask import Flask, request, jsonify, render_template, session
import os
import json
from agents import extract_text_from_docx, topic_identification, topic_identification_with_feedback, get_completion

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session storage

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the directory exists

@app.route('/')
def index():
    return render_template('index.html')  # Render the homepage

@app.route('/save-azure-config', methods=['POST'])
def save_azure_config():
    """Save Azure configuration entered by the user."""
    data = request.json
    session['azure_endpoint'] = data.get('azure_endpoint')
    session['api_key'] = data.get('api_key')
    session['api_version'] = data.get('api_version')
    session['model'] = data.get('model')
    return jsonify({"message": "Azure configuration saved successfully!"})

@app.route('/upload-dialogue', methods=['POST'])
def upload_dialogue():
    """Handle dialogue file upload."""
    if 'dialogue' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['dialogue']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    try:
        file.save(filepath)
        return jsonify({"message": "File uploaded successfully", "file_path": filepath})
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
    
@app.route('/get-file-content', methods=['GET'])
def get_file_content():
    """Fetch the content of the uploaded file."""
    file_path = request.args.get('file_path')
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        # Check the file extension and process accordingly
        if file_path.endswith('.docx'):
            content = extract_text_from_docx(file_path)  # Assuming extract_text_from_docx is a helper function for .docx files
        else:
            # Process plain text files
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": f"Error reading file: {str(e)}"}), 500

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
        messages = topic_identification(dialogue)
        topics_response = get_completion(messages, azure_config)

        return jsonify({"topics": topics_response})

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
            messages = topic_identification(dialogue)
        else:  # Called from "Regenerate with Feedback"
            messages = topic_identification_with_feedback(dialogue, feedback, previous_results)
        
        regenerated_response = get_completion(messages, azure_config)
        return jsonify({"regenerated_results": regenerated_response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/finalize-response', methods=['POST'])
def finalize_response():
    """Save the finalized response."""
    data = request.json
    final_response = data.get('final_response')

    # For testing, simulate saving the response
    try:
        with open(os.path.join(UPLOAD_FOLDER, "final_response.json"), "w") as f:
            json.dump(final_response, f, indent=4)
        return jsonify({"message": "Final response saved successfully!"})
    except Exception as e:
        return jsonify({"error": f"Failed to save final response: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)