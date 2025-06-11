from dotenv import load_dotenv
import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
import os
from openai import OpenAI
from presets import preset_json, preset_url
import pandas as pd


def create_excel(scores_dict, filename="relevance_scores.xlsx"):
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(list(scores_dict.items()), columns=['Tag', 'Score'])
    # Write the DataFrame to an Excel file, overwriting if it already exists
    df.to_excel(filename, index=False)
    st.success(f"Excel file created/updated: {filename}")


# Load the variables from .env file
load_dotenv()

import sys
print(sys.executable)

client = OpenAI()

def get_relevance_scores_streaming(article_text, tags_json):
    try:
        prompt = f"Please return the JSON object with relevance scores from 0 to 1 for each of the following tags. Create a 1-1 correspondance with the tags given, and the ratings returned. Do not create news tags outside of these.:\n{tags_json}., based on their relevance to this article:\n{article_text}\n\n Then sort the Json based on relevance highest to lowest."

        stream = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},  # Enable JSON mode
            stream=True,
        )

        for chunk in stream:
            yield chunk.choices[0].delta.content or ""
    except Exception as e:
        yield f"An error occurred while querying OpenAI: {e}"


def scrape_article_content(url):
    try:
        # Send a request to the URL
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the content of the page
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the main content of the article
            # This part might need customization based on the structure of the webpage
            # Here, I'm assuming the main content is within <article> tags
            article = soup.find('article')
            if article:
                return article.get_text(strip=True)
            else:
                return "Article content could not be extracted. Please check the URL structure."
        else:
            return f"Failed to retrieve the webpage. Status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        return f"An error occurred: {e}"




def main():
    st.title("Web Article Relevance Scorer")

    # UI elements for input
    url = st.text_input("Enter the URL of the article", preset_url)
    json_input = st.text_area("Enter your tag structure in JSON format", preset_json)

    print(preset_json)

    if st.button("Score Relevance"):
        if url and json_input:
            article_text = scrape_article_content(url)
            response_placeholder = st.empty()  # Create a placeholder for streaming response

            # Initialize an empty string to accumulate the response
            response_text = ""

            # Stream the response and update the UI in real-time
            for response_chunk in get_relevance_scores_streaming(article_text, json_input):
                response_text += response_chunk  # Accumulate the response text
                response_placeholder.write(response_text)  # Update the placeholder with the accumulated text

            try:
                scores_dict = json.loads(response_text)
                create_excel(scores_dict)
            except json.JSONDecodeError:
                    st.error("Failed to parse JSON for Excel creation.")


if __name__ == "__main__":
    main()
