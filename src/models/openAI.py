import openai
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def upload_picture_and_text(picture_path, text):
    # Read the image file and encode it to base64
    with open(picture_path, 'rb') as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    # Create the prompt with the text and the base64 encoded image
    prompt = f"Text: {text}\nImage (base64): {image_base64}"

    # Make the API request
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # Return the response text
    return response.choices[0].text.strip()

if __name__ == "__main__":
    picture_path = input("Enter the path to the picture: ")
    text = input("Enter the descriptive text: ")
    response = upload_picture_and_text(picture_path, text)
    print(response)
