import openai
from docx import Document

# Step 1: Load text from the Word document
def load_document(file_path):
    doc = Document(file_path)
    content = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():  # Skip empty paragraphs
            content.append(paragraph.text.strip())
    return "\n".join(content)

# Step 2: Query OpenAI GPT
def query_openai(api_key, document_text, user_query):
    openai.api_key = api_key

    # Combine the document text and user's question
    prompt = f"""
    The following is information extracted from a document:
    {document_text}

    Based on this document, answer the following question:
    {user_query}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

# Step 3: Main function
if __name__ == "__main__":
    # Path to your Word document
    doc_path = "C:/Users/User/Desktop/code/cheatAI/beta/Ukraine.docx"
    
    # Your OpenAI API key
    api_key = "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"

    # Load the document
    document_text = load_document(doc_path)
    print("Document loaded successfully.")

    # Ask questions
    while True:
        user_query = input("\nEnter your question (or type 'exit' to quit): ")
        if user_query.lower() == 'exit':
            print("Exiting. Goodbye!")
            break
        
        # Get GPT's response
        response = query_openai(api_key, document_text, user_query)
        print("\nGPT Response:")
        print(response)
