import streamlit as st
import time
from search_agent import Research_Tool
import random
from utils import QUICK_SEARCH_PROMPT, LENGTHY_SEARCH_PROMPT
from Organizer import Organizer
import asyncio

search_engine = Research_Tool()
organizer = Organizer()



async def main():
    st.set_page_config(layout="centered", page_title="AI-Researcher")
    st.session_state.SearchEngineStatus = False
    st.session_state.Decision = False
    st.session_state.crawl_status = False
    st.session_state.ready_for_extraction = False
    st.session_state.answer = False

    

    if "search_query" not in st.session_state:
        st.session_state.search_query = ""

    # LANDING PAGE
    st.header("AI-Researcher")

    #Search Bar
    st.session_state.search_query = st.text_input("", placeholder="Search Query Here...", key="top_search")


    # Search button, toogle button
    Search, toogle, value, _ = st.columns([0.1,0.1,5,20])
    with Search:
        if st.button("Search", type="primary"):
            if st.session_state.SearchEngineStatus:
                st.session_state.SearchEngineStatus = False
                st.session_state.Decision = False
                st.session_state.crawl_status = False
                st.session_state.ready_for_extraction = False
                st.session_state.answer = False

            with st.spinner('Searching The Internet...'):
                #Searching The Internet
                web_search_results = search_engine.search(st.session_state.search_query, random.randint(10, 15))
                st.session_state.SearchEngineStatus = True
    
    #Updating Internet Data
    if st.session_state.SearchEngineStatus:
        with st.expander("Data from the internet"):
            st.json(web_search_results)
            #Quick Search
            if st.session_state.Searching_mode == "quick_search":
                with st.spinner('Deciding If Answer can be Constructed or Need more data...'):
                    temp_ans = organizer.get_filtered_urls(all_urls=web_search_results, prompt=QUICK_SEARCH_PROMPT, query= st.session_state.search_query)
                    st.session_state.Decision = True
                    
            #Research Mode
            if st.session_state.Searching_mode == "research":
                with st.spinner('Filtering Important urls to CRAWL...'):
                    temp_ans = organizer.get_filtered_urls(all_urls=web_search_results, prompt=LENGTHY_SEARCH_PROMPT, query= st.session_state.search_query)
                    st.session_state.Decision = True
                    

    #Updating Quick Search Data
    if st.session_state.Decision == True:
        if not isinstance(temp_ans, str):
            # Meaning it's a list of urls
            if len(temp_ans) == 1:
                with st.expander("Decided To Crawl This Wikipedia for more context."):
                    st.json({"Filtered_Urls":temp_ans})
                    st.session_state.crawl_status = True
            else:
                with st.expander("Decided To Crawl These sites for more context."):
                    st.json({"Filtered_Urls":temp_ans})
                    st.session_state.crawl_status = True
            
        else:
            #Meaning It's the answer
            with st.spinner('Structuring The Answer...'):
                st.session_state.answer = organizer.fine_tune_ans(query = st.session_state.search_query, answer = temp_ans)
                # st.markdown()

    if st.session_state.crawl_status == True:
        with st.spinner('Crawling and Collecting Data...'):
            crawl_results = await organizer.process_url(temp_ans)
            with st.expander("Crawling completed and Data Collected..."):
                st.json(crawl_results)
                st.session_state.ready_for_extraction = True


    if st.session_state.ready_for_extraction == True:
        with st.spinner('Summerizing and Generating Report (This may take upto 2 mins)...'):
            processed_data = await organizer.multi_text_processor(st.session_state.search_query)
            st.session_state.answer = processed_data
            # st.markdown(processed_data)
                
    if st.session_state.answer:
        st.markdown(st.session_state.answer)








    with toogle:
        status = st.checkbox("Research Mode (Takes 35sec - 2mins)")
        if status:
            st.session_state.Searching_mode = "research"
        if not status:
            st.session_state.Searching_mode = "quick_search"


    















if __name__ == "__main__":
    asyncio.run(main())
