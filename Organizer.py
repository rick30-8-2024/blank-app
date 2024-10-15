import requests
import asyncio
import random
from search_agent import Research_Tool
from utils import ask_llm
from utils import fetch_images
from utils import fetch_videos
from utils import SUMMRIZATION_PROMPT, ANSWER_GENERATION_PROMPT
from utils import split_corpus
class Organizer:
    def __init__(self):
        self.researcher = Research_Tool()
        self.session = requests.session()
        self.keys = ['a83c8583-a310-44e1-ac82-75787a5d8dd5', 'fc966f2d-11a4-4b5c-87f6-c9e0d19869b0', 'bb909ed0-6f67-4131-be88-c731e1602659', 'f3269905-5dc2-4e3c-9181-6a155e019b85', 'ba327648-f98c-4f89-bbb2-6f82f9f53d0d', '348e3e5c-68ef-4bfd-94ff-a8da9112de21', 'fb0722f1-572e-41f0-aef7-bc70cb3b097e', '451dc795-c196-4a63-be92-54617da8da45', '50a9ab67-fb0e-49d6-b67f-16b5a7e777e2', '849d8319-fbf7-42b8-a1f8-68ec5d5bc69d']
        self.all_Images = []


    def get_filtered_urls(self, query):
        print(query)
        urls = self.researcher.search(query, random.randint(10,15))
        print(urls)
        self.all_urls = [i['url'] for i in urls]
        urls = ask_llm(query= f"{urls} \nreturn me 5 url that is most reliable for this query: '{query}'", json_schema='{"response":list(str)}',model='Meta-Llama-3.1-70B-Instruct')
        filtered_urls = [i for i in urls['response'] if "wikipedia.org/wiki/" in i] if "wikipedia.org/wiki/" in str(urls) else urls['response']
        print(filtered_urls)
        return filtered_urls

    async def summerize(self, data, model='Meta-Llama-3.1-8B-Instruct', bullet=True, show = False):
        text, query, key = data
        if show:
            print(data)
        
        prompt = SUMMRIZATION_PROMPT.format(text, query)
        
        if not bullet:
            prompt = ANSWER_GENERATION_PROMPT.format(query, text)

        data = await asyncio.to_thread(ask_llm, query=prompt, model=model , JSON=False, api_key=key)
        if "[status: failed]" in data:
            return ""
        print("-"*150,'\n',data,'\n',"-"*150)
        return data

    async def Processor(self, url, query):
        json_response = self.researcher.scrape_page(url)
        full_text = json_response['structured_data']['full_text']
        self.all_Images.extend([i['src'] for i in json_response['structured_data']['images']])
        chunked_text = split_corpus(full_text)
        
        for i in range(5):
            print(len(chunked_text))
            text_chunk_list = [(chunked_text[m], query, self.keys[m%10]) for m in range(len(chunked_text))]
            tasks = [self.summerize(chunk, show=True) for chunk in text_chunk_list]
            results = await asyncio.gather(*tasks)
            chunked_text = split_corpus("\n\n".join(results))
            if len(chunked_text) == 1:
                return "\n\n".join(results)

    async def search(self, query):
        filtered_urls = self.get_filtered_urls(query)
        tasks = [self.Processor(url, query) for url in filtered_urls]
        list_of_chunks = await asyncio.gather(*tasks)
        # print(len(final_data_list))
        # print(final_data_list)
        # final_data_list = "\n\n".join(final_data_list)
        # final_data = await self.summerize((final_data_list, query, random.choice(self.keys)), bullet=False)
        return final_data_list



#Extract the most important information from the following paragraph and summarize it in bullet points. Focus on the main ideas, key findings, and crucial details. Omit unnecessary words and phrases, and prioritize concise language.