import re
import openai
import json
from duckduckgo_search import DDGS


def extract_query(text: str) -> str:
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches[0] if matches else text


def ask_llm(query, api_key = "95aa27ad-fe66-42f3-b745-b81217733190", model = "Meta-Llama-3.1-70B-Instruct", JSON = False):
    for i in range(5):
        SambaNova_Client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.sambanova.ai/v1",
            )

        response = SambaNova_Client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content": "You're a advance data analyst."},{"role":"user","content":query}],
            temperature =  0.1,
            top_p = 0.1,
            response_format={"type": "json_object"}
        )
        if not JSON:
            print(model)
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


SUMMRIZATION_PROMPT = """{data} \n Extract and Summerize all the informations related to "{query}", Withing 200 words in Bullet format."""

ANSWER_GENERATION_PROMPT = """Answer this query: {query}, based on the following context in Markdown Format. 
                            Context: {data}
                            You may use Your own knowledge if required, but do not mention about your own knowledge anywhere.
                            Generated answer must be within 800 words.
                            """

QUICK_SEARCH_PROMPT = """
                            Answer this question in this format:
                            {"status":str, "answer": str, "urls": list(str)}
                            YOU MUST PUT THE JSON ANSWER WITHIN TWO ```

                            if you can answer the question with the provided context, set status to 'success' else it will be as 'pending'
                            if you can't answer the question keep answer as empty.
                            if you are not able to answer with the provided context return a list of urls from the provided ones that you would like to visit for more data. return a list of upto 5 urls.
                            if you are able to answer from the provide context keep the urls empty.
                            NOTE: YOU MUSTREPLY WITH UPTO 5 URLS IF YOURE ASKED TO GENERATE ANY CODE IN THE QUESTION. DO NOT GENERATE ANY CODE EVEN IF YOU KNOW THE ANSWER.
                            Question: 
                        """

LENGTHY_SEARCH_PROMPT = """
                            Answer this question in this format:
                            {"status":"pending", "urls": list(str)}
                            YOU MUST PUT THE JSON ANSWER WITHIN TWO ```

                            Return a list of upto 5 urls from the provided ones that you would like to visit for more Context to answer the following question.
                            Question:

                        """

SHORT_ANSWER_FINE_TUNING_PROMPT = """
                            Question:
                            {query}
                            Answer:
                            {answer}

                            You have been Provided with a question and it's answer. Your job is to make the answer more Humanlike.
                            Please Generate the answer in Markdown Format in a Humanlike way.
                            NOTE: IF THERE IS ANY CODE INVOLVED THE ANSWER YOU MUST PUT THE CODE BETWEEN TWO ```
                            """

LINK_SUMMERIZATION_PROMPT = """
                            {data} \n Extract 5 image urls related to "{query}", in JSON format with "images" as the key and a list of url as value.
                            """

IMAGE_SUMMERIZATION_PROMPT = """
                            {data} \n Extract 5 links that can use used as references when generating a report on "{query}", in JSON format with "links" as the key and a list of url as value.
                            """

REPORT_GENERATION_PROMPT = """
                            {data}
                            You have been provided with a report and some images and links related to this question:
                            {question}

                            your job is to unify them and create a Final report that consists of all three of these in MARKDOWN format.

                            NOTE: PUT THE IMAGE URLS IN A WAY SO THAT THEY CAN BE DISPLAYED DIRETLY ON THE MARKDOWN.
                                  PUT THE REFERENCE AS YOU SEE FIT.
                                  MAKE THE REPORT LOOK AS HUMAN LIKE AS POSSIBLE.
                            """