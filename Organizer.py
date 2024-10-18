import requests
import asyncio
import random
from search_agent import Research_Tool
from utils import ask_llm
from utils import fetch_videos
from utils import SUMMRIZATION_PROMPT, ANSWER_GENERATION_PROMPT, LINK_SUMMERIZATION_PROMPT
from utils import split_corpus
from utils import REPORT_GENERATION_PROMPT, SHORT_ANSWER_FINE_TUNING_PROMPT, IMAGE_SUMMERIZATION_PROMPT
from utils import is_article, is_image_url



class Organizer:
    def __init__(self):
        self.researcher = Research_Tool()
        self.session = requests.session()
        self.keys = ['a83c8583-a310-44e1-ac82-75787a5d8dd5', 'fc966f2d-11a4-4b5c-87f6-c9e0d19869b0', 'bb909ed0-6f67-4131-be88-c731e1602659', 'f3269905-5dc2-4e3c-9181-6a155e019b85', 'ba327648-f98c-4f89-bbb2-6f82f9f53d0d', '348e3e5c-68ef-4bfd-94ff-a8da9112de21', 'fb0722f1-572e-41f0-aef7-bc70cb3b097e', '451dc795-c196-4a63-be92-54617da8da45', '50a9ab67-fb0e-49d6-b67f-16b5a7e777e2', '849d8319-fbf7-42b8-a1f8-68ec5d5bc69d']
        self.all_Images = []
        self.all_links = []
        self.full_text = []

    def get_filtered_urls(self, all_urls, prompt, query = None):
        # print(query)
        # all_urls = self.researcher.search(query, random.randint(10, 15))
        # print(all_urls)
        self.all_urls = [i['url'] for i in all_urls]
        
        urls = ask_llm(query=str(all_urls) + prompt + query, JSON=True, model='Meta-Llama-3.1-70B-Instruct')
        print(urls)
        try:
            if urls.get('status') == 'pending':
                if urls.get('urls'):
                    filtered_urls = [i for i in urls['urls'] if "wikipedia.org/wiki/" in i] \
                                    if "wikipedia.org/wiki/" in str(urls) else urls['urls']
                    # print("filtered_urls: ",filtered_urls)
                    return filtered_urls if filtered_urls else []  
                else:
                    return []  
            elif urls.get('status') == 'code':
                ans = ask_llm(query = query, model = 'Meta-Llama-3.1-405B-Instruct')
                return ans
            else:
                # print("url_answer", urls.get('answer'))
                return urls.get('answer') or []  
        except Exception as e:
            print("Exception occurred:", str(e))
            print("except", urls)
            return [] 


    async def summerize(self, data, prompt, model='Meta-Llama-3.1-8B-Instruct', show = False):
        text, query, key = data
        # if show:
        #     print(data)
        
        prompt = prompt.format(data = text, query = query)

        data = await asyncio.to_thread(ask_llm, query=prompt, model=model , JSON=False, api_key=key)
        if "[status: failed]" in data:
            return ""
        # print("-"*150,'\n',data,'\n',"-"*150)
        return data

    async def Processor(self, url):
        json_response = self.researcher.scrape_page(url)
        self.full_text.append(json_response['structured_data']['full_text'])
        self.all_Images.extend(json_response['structured_data']['images'])
        self.all_links.extend(json_response['structured_data']['links'])
        return json_response
    
    async def process_text_corpus(self, text_corpus, query, prompt, model = "Meta-Llama-3.1-8B-Instruct"):
        print(text_corpus)
        chunked_text = split_corpus(text_corpus)
        
        while len(chunked_text) > 1:  
            # print("Here We Go Again")
            text_chunk_list = [(chunk, query, self.keys[m % len(self.keys)]) for m, chunk in enumerate(chunked_text)]
            tasks = [self.summerize(chunk, prompt=prompt, model = model) for chunk in text_chunk_list]
            results = await asyncio.gather(*tasks)
            
            text_corpus = "\n\n".join(results)
            # print(len(text_corpus))  
            chunked_text = split_corpus(text_corpus) 
            # print(len(chunked_text)) 
        
        text_corpus = await self.summerize(data = (text_corpus, query, random.choice(self.keys)), prompt =  ANSWER_GENERATION_PROMPT, model = 'Meta-Llama-3.1-70B-Instruct')
        if 'image' in query:
            print("image_output: ",text_corpus)
        if 'link' in query:
            print("link_output: ",text_corpus)
        else:
            print("text_output: ", text_corpus)
        return text_corpus  
    
    async def mass_check(self, list_of_data, function):
        if function == 'image':
            tasks = [is_image_url(i) for i in list_of_data]

        if function == 'link':
            tasks = [is_article(i) for i in list_of_data]

        filtered_data = await asyncio.gather(*tasks)
        return [i for i in filtered_data if i != None]

    async def process_url(self, filtered_urls):
        tasks = [self.Processor(url) for url in filtered_urls]
        list_of_json = await asyncio.gather(*tasks)
        # print("all Images",self.all_Images)
        self.all_Images = await self.mass_check([
                                i for i in self.all_Images
                                if (
                                    any(ext in i['src'] for ext in [".png", ".jpg", ".webp", ".jpeg"])  # Check for allowed extensions
                                    and "svg" not in i['src']  # Exclude SVG images
                                    and not i['src'].startswith("data")  # Exclude inline base64 images
                                    and (i['src'].startswith("https://") or i['src'].startswith("//"))
                                )
                            ], 'image')
        self.all_links = await self.mass_check([i for i in self.all_links if i['text'] != '' and i['href'].startswith("https://")], 'link')
        # print("all Images",self.all_Images)
        # print("all links", self.all_links)
        return {"Crawl Results": list_of_json}

    async def multi_text_processor(self, query):
        # print(self.all_Images)
        # print(self.all_links)
        tasks = [self.process_text_corpus(text_corpus= " ".join(self.full_text), query = query, prompt = SUMMRIZATION_PROMPT, model='Meta-Llama-3.1-8B-Instruct'),
                 self.process_text_corpus(text_corpus=str(self.all_Images), query = query, prompt=IMAGE_SUMMERIZATION_PROMPT, model = "Meta-Llama-3.1-70B-Instruct"),
                 self.process_text_corpus(text_corpus=str(self.all_links), query = query, prompt=LINK_SUMMERIZATION_PROMPT, model = "Meta-Llama-3.1-70B-Instruct")
                ]

        text_image_links = await asyncio.gather(*tasks)
        # print(text_image_links)
        final_report = ask_llm(query= REPORT_GENERATION_PROMPT.format(data = str(text_image_links), question = query), model="Meta-Llama-3.1-70B-Instruct")
        # print(final_report)
        return final_report

    def fine_tune_ans(self, query, answer):
        data = ask_llm(query= SHORT_ANSWER_FINE_TUNING_PROMPT.format(query = query, answer = answer), model="Meta-Llama-3.1-70B-Instruct")
        print(data)
        return data
    













    async def search(self, filtered_urls, query):
        tasks = [self.Processor(url) for url in filtered_urls]
        list_of_chunks = await asyncio.gather(*tasks)
        alltext = "\n\n".join(list_of_chunks)

        summery = await self.process_text_corpus(alltext, query, prompt=SUMMRIZATION_PROMPT)
        summery = summery.strip('\n').strip(" ")
        print(self.all_Images)
        print(self.all_links)
        print(self.all_urls)
        # print(len(final_data_list))
        # print(final_data_list)
        # final_data_list = "\n\n".join(final_data_list)
        # final_data = await self.summerize((final_data_list, query, random.choice(self.keys)), bullet=False)
        return summery


    
