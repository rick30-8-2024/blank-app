import requests
import asyncio
import random
from search_agent import Research_Tool
from utils import ask_llm
from utils import fetch_images
from utils import fetch_videos
from utils import SUMMRIZATION_PROMPT, ANSWER_GENERATION_PROMPT, DYNAMIC_SEARCH_PROMPT
from utils import split_corpus
import json



class Organizer:
    def __init__(self):
        self.researcher = Research_Tool()
        self.session = requests.session()
        self.keys = ['a83c8583-a310-44e1-ac82-75787a5d8dd5', 'fc966f2d-11a4-4b5c-87f6-c9e0d19869b0', 'bb909ed0-6f67-4131-be88-c731e1602659', 'f3269905-5dc2-4e3c-9181-6a155e019b85', 'ba327648-f98c-4f89-bbb2-6f82f9f53d0d', '348e3e5c-68ef-4bfd-94ff-a8da9112de21', 'fb0722f1-572e-41f0-aef7-bc70cb3b097e', '451dc795-c196-4a63-be92-54617da8da45', '50a9ab67-fb0e-49d6-b67f-16b5a7e777e2', '849d8319-fbf7-42b8-a1f8-68ec5d5bc69d']
        self.all_Images = []
        self.all_links = []


    def get_filtered_urls(self, query):
        print(query)
        urls = self.researcher.search(query, random.randint(10, 15))
        print(urls)
        
        # Get the URLs in a list
        self.all_urls = [i['url'] for i in urls]
        
        # Pass the URLs to the LLM for further filtering
        urls = ask_llm(query=str(urls) + DYNAMIC_SEARCH_PROMPT + query, JSON=True, model='Meta-Llama-3.1-70B-Instruct')
        print(urls, type(urls))
        try:
            if urls.get('status') == 'pending':
                print("whole response: ", urls)
                print("Just urls", urls.get('urls'))
                
                # Check if the response has 'urls' and filter accordingly
                if urls.get('urls'):
                    filtered_urls = [i for i in urls['urls'] if "wikipedia.org/wiki/" in i] \
                                    if "wikipedia.org/wiki/" in str(urls) else urls['urls']
                    print(filtered_urls)
                    return filtered_urls if filtered_urls else []  # Return empty list if no URLs
                else:
                    return []  # Return empty list if no 'urls' key is present
            else:
                print("url_answer", urls.get('answer'))
                return urls.get('answer') or []  # Return empty list if 'answer' is None
        except Exception as e:
            print("Exception occurred:", str(e))
            print("except", urls)
            return [] 


    async def summerize(self, data, prompt, model='Meta-Llama-3.1-8B-Instruct', show = False):
        text, query, key = data
        print("COUNT HERE")
        if show:
            print(data)
        
        prompt = prompt.format(data = text, query = query)

        data = await asyncio.to_thread(ask_llm, query=prompt, model=model , JSON=False, api_key=key)
        if "[status: failed]" in data:
            return ""
        print("-"*150,'\n',data,'\n',"-"*150)
        return data

    async def Processor(self, url):
        json_response = self.researcher.scrape_page(url)
        full_text = json_response['structured_data']['full_text']
        self.all_Images.extend(json_response['structured_data']['images'])
        self.all_links.extend(json_response['structured_data']['links'])
        return full_text
    
    async def process_text_corpus(self, text_corpus, query):
        chunked_text = split_corpus(text_corpus)
        
        while len(chunked_text) > 1:  
            print("Here We Go Again")
            text_chunk_list = [(chunk, query, self.keys[m % len(self.keys)]) for m, chunk in enumerate(chunked_text)]
            tasks = [self.summerize(chunk, prompt=SUMMRIZATION_PROMPT) for chunk in text_chunk_list]
            results = await asyncio.gather(*tasks)
            
            text_corpus = "\n\n".join(results)
            print(len(text_corpus))  
            chunked_text = split_corpus(text_corpus) 
            print(len(chunked_text)) 
        
        text_corpus = await self.summerize(data = (text_corpus, query, random.choice(self.keys)), prompt =  ANSWER_GENERATION_PROMPT, model = 'Meta-Llama-3.1-70B-Instruct')

        return text_corpus  


    async def search(self, query):
        filtered_urls = self.get_filtered_urls(query)
        if not isinstance(filtered_urls, str):
            tasks = [self.Processor(url) for url in filtered_urls]
            list_of_chunks = await asyncio.gather(*tasks)
            alltext = "\n\n".join(list_of_chunks)
            summery = await self.process_text_corpus(alltext, query)
            summery = summery.strip('\n').strip(" ")
            print(self.all_Images)
            print(self.all_links)
            print(self.all_urls)
            # print(len(final_data_list))
            # print(final_data_list)
            # final_data_list = "\n\n".join(final_data_list)
            # final_data = await self.summerize((final_data_list, query, random.choice(self.keys)), bullet=False)
            return summery
        else:
            return filtered_urls



#Extract the most important information from the following paragraph and summarize it in bullet points. Focus on the main ideas, key findings, and crucial details. Omit unnecessary words and phrases, and prioritize concise language.