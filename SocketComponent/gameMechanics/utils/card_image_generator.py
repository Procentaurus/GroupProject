import os
import json
import time
import requests
from openai import OpenAI

# Initialize OpenAI client with your API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("API key for OpenAI is not set in the environment variables.")
client = OpenAI(api_key=openai_api_key)

# Path to the cards.json file
cards_file_path = 'gameMechanics/fixtures/cards.json'

# Folder to store images
output_folder = "static/card_images"
os.makedirs(output_folder, exist_ok=True)

# API limits
REQUESTS_PER_MINUTE = 5
REQUEST_DELAY = 60 / REQUESTS_PER_MINUTE

def generate_image_with_rate_limit(prompt, output_path):
    """Generate an image using OpenAI's DALL-E API with rate limiting."""
    try:
        # Generate the image using the updated API structure
        response = client.images.generate(
            model="dall-e-3",  # Use the latest DALL-E model
            prompt=prompt,
        )

        image_url = response.data[0].url

        # Download the image
        image_data = requests.get(image_url).content
        with open(output_path, "wb") as f:
            f.write(image_data)
        print(f"Image saved: {output_path}")
    except Exception as e:
        print(f"Error generating image for prompt '{prompt}': {e}")

def main():
    # Load data from the cards.json file
    with open(cards_file_path, "r", encoding="utf-8") as f:
        cards_data = json.load(f)

    # Track the number of requests made
    requests_made = 0

    # Iterate over the cards and generate images
    for card in cards_data:
        card_name = card["fields"]["name"]

        # Prepare the filename
        safe_name = card_name.replace(" ", "_").lower()
        output_path = os.path.join(output_folder, f"{safe_name}.png")

        # Skip if the file already exists to save API requests
        if os.path.exists(output_path):
            print(f"Image already exists for {card_name}, skipping...")
            continue

        # Prepare the prompt
        prompt = (
            f"School-themed illustration. Name: '{card_name}'. No text - only image. "
            f"Digital cartoonish style, colorful and visually appealing. Modern art style."
        )

        # Generate the image
        generate_image_with_rate_limit(prompt, output_path)
        
        # Increment the request counter
        requests_made += 1

        # Enforce rate limiting
        if requests_made % REQUESTS_PER_MINUTE == 0:
            print(f"Waiting {REQUEST_DELAY:.2f} seconds to respect rate limits...")
            time.sleep(REQUEST_DELAY)

if __name__ == "__main__":
    main()
