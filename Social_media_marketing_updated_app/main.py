from flask import Flask, render_template, request, Response, send_file
import openai
import pdfkit

app = Flask(__name__)

# Set your OpenAI API key here
openai.api_key = "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"

# Define a dictionary to map routes to task descriptions
task_descriptions = {
    "/plan": """You will be provided with a description of a product that the company has, and your task is to create a social media marketing plan with step-by-step points to enhance user understanding.
    - Create attractive social media contents based on the marketing plan for the social media marketing.
    - Create a marketing schedule for publishing contents as a calendar for the social media marketing.
    - Create an attractive caption for the social media posters when the user creates posters based on contents provided.
    - Suggest hashtag keywords for the social media posters.
    
    Output example:
    - Plan: 'output of the plan created by the system'
    - Contents: 'output of the contents created by the system'
    - Schedules: 'output of the schedules created by the system'
    - Captions: 'output of the captions created by the system'
    - Hashtags: 'output of the hashtags created by the system'
    """,
    "/analytics": "You will be provided with a description of the performance that the marketing plan gives, and your task is to analyze performance and replan with the corrections for the social media marketing."
}

# Define functions for different routes
@app.route("/plan", methods=["GET", "POST"])
def plan():
    task_route = "/plan"
    return handle_task(task_route)

@app.route("/analytics", methods=["GET", "POST"])
def analytics():
    task_route = "/analytics"
    return handle_task(task_route)

# Function to generate a PDF from conversation HTML
def generate_pdf(conversation_html):
    try:
        pdfkit.from_string(conversation_html, 'conversation.pdf')
        return 'conversation.pdf'
    except Exception as e:
        return str(e)

# Route to download the PDF
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    conversation = request.form['conversation']

    # Generate a PDF from the conversation HTML content
    pdf_filename = generate_pdf(conversation)

    # Send the PDF as a downloadable file
    try:
        return send_file(pdf_filename, as_attachment=True)
    except Exception as e:
        return str(e)

# Common function to handle tasks
def handle_task(task_route):
    task_description = task_descriptions.get(task_route, "")
    conversation = []  # Initialize an empty list to store the conversation history

    if request.method == "POST":
        message = request.form["message"]

        # Add user's message to the conversation
        conversation.append({"role": "user", "content": f"Person: {message}"})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": task_description},
                *conversation  # Include the entire conversation history
            ],
            max_tokens=900  # Adjust as needed
        )

        # Add AI's reply to the conversation
        reply = response.choices[0].message["content"].replace('\n', '<br><br>')
        conversation.append({"role": "assistant", "content": reply})

        # Combine conversation into a single HTML string
        conversation_html = "".join([message["content"] for message in conversation])

        return render_template("index.html", conversation=conversation, task_description=task_description, task_route=task_route, conversation_html=conversation_html)

    return render_template("index.html", conversation=conversation, task_description=task_description, task_route=task_route)

if __name__ == '__main__':
    app.run(debug=True)
