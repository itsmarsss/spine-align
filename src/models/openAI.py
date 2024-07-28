import openai
import base64
import os
import cv2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

system_prompt = """Analyse this photo and determine whether the person has good or bad posture in JSON format, an approximate depth map has as well as the photo have been provided, be a bit lenient:
             {
                "posture": "good" or "bad",
                "confidence": 0 to 100 (always 2 significant figures)
             }"""

def resize_image(img, target_size=512):
    # Get the original dimensions
    original_height, original_width = img.shape[:2]
    
    # Determine the scaling factor based on the longest side
    if original_width > original_height:
        scale_factor = target_size / original_width
    else:
        scale_factor = target_size / original_height
        
    # Calculate the new dimensions
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    
    # Resize the image
    resized_image = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return resized_image

def query_gpt(img_raw, img_depth):
    # Convert the images to base64 encoding
    img_raw = resize_image(img_raw)
    img_depth = resize_image(img_depth)
    
    _, buffer = cv2.imencode('.png', img_raw)
    encoded_image_raw = base64.b64encode(buffer).decode('utf-8')

    _, buffer = cv2.imencode('.png', img_depth)
    encoded_image_depth = base64.b64encode(buffer).decode('utf-8')

    # Send the image to the ChatGPT-4 API
    chat_completion = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image_raw}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{encoded_image_depth}"
                        }
                    }
                ]
            }
        ], 
        temperature=0,
        max_tokens=100,
        top_p=0,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={ "type": "json_object" },
    )

    # Extract and print the response
    response = chat_completion.choices[0].message.content
    print(response)
    return response