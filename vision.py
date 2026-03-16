import requests
import base64

def answer_image_question(image_file, input_text):
    print("Sending image to Quilt-LLaVA server...")

    # Read and encode image as base64
    image_bytes = image_file.read()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    payload = {
        "question": input_text if input_text else "describe this image in detail",
        "image": image_b64
    }

    try:
        response = requests.post(
            "http://127.0.0.1:5001/quilt",
            json=payload,
            timeout=120
        )
        result = response.json()
        return result["response"]

    except requests.exceptions.ConnectionError:
        return "Error: Quilt-LLaVA server is not running. Please start quilt_server.py first."
    except requests.exceptions.Timeout:
        return "Error: Quilt-LLaVA server timed out. Please try again."