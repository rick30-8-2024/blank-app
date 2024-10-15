import re
import openai
import json
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from groq import Groq

def extract_query(text: str) -> str:
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0] if matches else text


def ask_llm(query, api_key = "95aa27ad-fe66-42f3-b745-b81217733190", json_schema = None, model = "Meta-Llama-3.1-70B-Instruct", JSON = True):
    for i in range(5):
        SambaNova_Client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.sambanova.ai/v1",
            )
        if not JSON:
            prompt = query
        else:
            prompt = f"""Answer the following question in the JSON format{json_schema}
                        YOU MUST PUT THE JSON ANSWER WITHIN TWO ```
                         Question:
                         {query}"""

        response = SambaNova_Client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content": "You're a advance data analyst."},{"role":"user","content":prompt}],
            temperature =  0.1,
            top_p = 0.1,
            response_format={"type": "json_object"}
        )
        if not JSON:
            return extract_query(response.choices[0].message.content)
        try:
            data = json.loads(extract_query(response.choices[0].message.content))
            return data
        except Exception as e:
            print(e)
            print(response.choices[0].message.content)




def fetch_images(query, no_of_results):
    results = DDGS().images(
        keywords=query,
        region="wt-wt",
        safesearch="off",
        size=None,
        color="Monochrome",
        type_image=None,
        layout=None,
        license_image=None,
        max_results=no_of_results,
    )
    return results

def fetch_videos(query, no_of_results):
    results = DDGS().videos(
        keywords=query,
        region="wt-wt",
        safesearch="off",
        timelimit="w",
        resolution="high",
        duration="medium",
        max_results=no_of_results,
    )
    return results

def split_corpus(corpus, max_words=4000):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!|\n)\s+', corpus.strip())
    current_list = []
    word_count = 0
    all_splits = []
    for sentence in sentences:
        words_in_sentence = sentence.split()
        sentence_word_count = len(words_in_sentence)
        if word_count + sentence_word_count <= max_words:
            current_list.append(sentence)
            word_count += sentence_word_count
        else:
            all_splits.append(current_list)
            current_list = [sentence]
            word_count = sentence_word_count
    if current_list:
        all_splits.append(current_list)

    return [" ".join(i) for i in all_splits]


SUMMRIZATION_PROMPT = """{} \n Extract the most important information from the following paragraph and summarize it in bullet points focusing on the query: "{}". 
                        Focus on the main ideas, key findings, and crucial details. Omit unnecessary words and phrases, and prioritize concise language. 
                        If you receive any captcha verification and there is no data regarding th query. return "[status: failed]" without any apology or explanation. 
                        Do not try to fix this using your own knowledge, use only the context provided to construct the answer. 
                        """

ANSWER_GENERATION_PROMPT = """Answer this query: {}, based on the following context in Markdown Format. 
                            Context: {}
                            You may use Your own knowledge if required, but do not mention about your own knowledge anywhere.
                            """