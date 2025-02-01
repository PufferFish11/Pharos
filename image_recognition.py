import base64
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_VISION_MODEL

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=OPENAI_API_KEY)

class BlindAssistant:
    def __init__(self):
        # Pre-input system prompt specifying the assistant's role and responsibilities
        self.conversation_history = [
            {
                "role": "system",
                "content": (
                    """You are a friendly and highly capable assistant dedicated to helping visually impaired users navigate and understand their surroundings. 
                    Remember, the user cannot see, so provide detailed, clear, and accessible descriptions of images and answer their queries with concise, practical guidance. 
                    When an image is provided, assume it represents their current environment and analyze it carefully to point out landmarks, obstacles, or facilities that may assist in safe navigation. 
                    Always be patient, empathetic, and precise in your responses. 
                    Maintain context throughout the conversation to offer consistent, multi-turn dialogue support."""
                )
            }
        ]

    def encode_image(self, image_path):
        """
        Read the image file and return its Base64 encoded string.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def send_message(self, text=None, image_path=None):
        """
        Send a message to OpenAI that may include text and/or an image.
        - text: The user's textual message (optional)
        - image_path: Path to an image file (optional)
        
        Constructs the message, calls the OpenAI API, and appends the result to the conversation history
        to maintain multi-turn dialogue context.
        """
        # Construct message content as a list to allow multiple parts (text and image)
        message_parts = []
        if text:
            message_parts.append({
                "type": "text",
                "text": text
            })
        if image_path:
            base64_image = self.encode_image(image_path)
            message_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })
        if not message_parts:
            print("Error: You must provide text or image input.")
            return None

        # Append the user's message to the conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message_parts
        })

        try:
            # Call the OpenAI API with the full conversation history to maintain multi-turn context
            response = client.chat.completions.create(
                model=OPENAI_VISION_MODEL,
                messages=self.conversation_history,
            )
            assistant_reply = response.choices[0].message.content.strip()

            # Append the assistant's reply to the conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_reply
            })
            return assistant_reply
        except Exception as e:
            print("Error while calling API: ", e)
            return None

def main():
    assistant = BlindAssistant()
    
    print("Welcome to the Blind Assistant")
    print("You can send a text message directly, or upload an image by starting your input with 'img:'")
    print("For example: img:my_image.jpg")
    print("Enter 'quit' to exit.")
    
    while True:
        user_input = input("Please enter your message: ").strip()
        if user_input.lower() == "quit":
            break

        # If the input starts with "img:", treat it as an image input and prompt for an optional text description
        if user_input.startswith("img:"):
            image_path = user_input[4:].strip()
            text = input("Your question: ").strip()
            reply = assistant.send_message(text=text if text else None, image_path=image_path)
        else:
            # Text-only input
            reply = assistant.send_message(text=user_input)
        
        if reply:
            print("Reply:", reply)
        else:
            print("No reply, please try again.")

if __name__ == "__main__":
    main()
