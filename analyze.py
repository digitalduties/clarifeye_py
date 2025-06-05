from flask import Flask, request, render_template, jsonify
import ipywidgets as ipy
import base64
from openai import OpenAI
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

@app.route("/")
def index():
  return render_template("upload_image.html")

@app.route("/analyze_ingredients", methods=["POST"])
def analyze_ingredients():
    client = OpenAI()
    prompt = prompt = """
        You are an agent that scans through a list of ingredients in a food product. The list usually starts with 'Ingredients:'. 
        Your job is to parse this list into a clean JSON structure with the following fields:

        1. `ingredients`: an array of objects with:
        - `name`: string (ingredient name)
        - `description`: string (what it is)
        - `purpose`: string (optional; what it's used for)

        2. `product_profile`: an object with boolean fields:
        - `gluten_free`: true or false
        - `vegan`: true or false
        - `halal`: true or false

        3. `risk_flags`: an object with 3 fields, each an array:
        - `sketchy_stimulants`: array of ingredient names, or empty array if none
        - `potential_allergens`: array of ingredient names, or empty array if none
        - `illegal_additives`: array of ingredient names, or empty array if none

        STRICT RULES:
        - If the text does not contain an ingredients list (does not include 'Ingredients:' or similar), return this JSON instead:
        `{ "error": "No ingredient list detected." }`

        - Do NOT analyze or interpret text from non-ingredient sources like promotional copy, nutritional claims, social media posts, etc.

        - Do NOT infer or guess missing ingredients. Only use what's explicitly written in the text.

        - If fields like vegan/halal/gluten-free are unclear or ambiguous, set them to `false` by default.

        - Return only JSON. No explanation, intro, or extra text.
    """

    image_file = request.files["image"]

    try:
        b64_image = base64.b64encode(image_file.read()).decode("utf-8")
        response = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/png;base64,{b64_image}"},
                    ],
                }
            ],
        )
        return response.output[0].content[0].text, 200
    except Exception as e:
        print("❌ Error during analysis:", e)