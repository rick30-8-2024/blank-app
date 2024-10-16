# import streamlit as st

# def main():
#     st.set_page_config(layout="wide", page_title="AI-Researcher")

#     if "button_clicked" not in st.session_state:
#         st.session_state.button_clicked = False
#     if "search_query" not in st.session_state:
#         st.session_state.search_query = ""

#     # LANDING PAGE
#     if not st.session_state.button_clicked:
#         st.header("AI-Researcher")
#         st.markdown("""**INSTRUCTIONS:**
                
#                     Please ask the Researcher to Describe if you want an elaborate and descriptive answer. 
#     By default it returns only short answers.""")

#         # Create the text input below the markdown
#         st.session_state.search_query = st.text_input("", placeholder="Search Query Here...", key="top_search")

#         # When the Search button is clicked
#         if st.button("Search"):
#             st.session_state.button_clicked = True
#             st.rerun()

#     if st.session_state.button_clicked:
#         st.markdown(
#             """
#             <style>
#             .code-background {
#                 background-color: #1a1c24; 
#                 color: #fff;     
#                 padding-top: 3px;
#                 padding-left: 10px;
#                 border-radius: 10px;
#                 font-family: monospace;    
#                 font-size: 16px;
#                 white-space: pre-wrap;     
#             }
#             </style>
#             """,
#             unsafe_allow_html=True
#         )
#         st.subheader("Asked Question:")
#         st.markdown(f'<div class="code-background"><pre>{st.session_state.search_query}</pre></div>', unsafe_allow_html=True)
#         # Create two-column layout for main content and media
#         main_col, media_col = st.columns([3, 1])

#         with main_col:
#             # Asked Question section
            
#             question = st.text_area("Enter your question:", height=100)
            
#             # Previous URLs section
#             st.subheader("Previous URLs:")
#             urls_container = st.container()
#             with urls_container:
#                 cols = st.columns(5)
#                 for i in range(5):
#                     with cols[i]:
#                         st.markdown(f"[URL {i+1}](https://example.com)")
                
#                 # +12 more indicator
#                 st.text("+12 more")
            
#             # Answer section
#             st.subheader("Answer to the Question")
#             st.text_area("Answer:", height=200, key="answer")

#         with media_col:
#             # Images section
#             st.subheader("Images")
#             for i in range(2):
#                 st.image("https://via.placeholder.com/150", caption=f"Image {i+1}")
            
#             # Videos section
#             st.subheader("Videos")
#             st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

#         # Bottom search bar
#         st.text_input("Search:", key="bottom_search")
        
        
        
        
        
        
#         if st.button("Reset"):
#             st.session_state.button_clicked = False
#             st.rerun()




















# if __name__ == "__main__":
#     main()

import streamlit as st

# Set page configuration
st.set_page_config(page_title="Button Display", layout="wide")

# Sample texts for the buttons
button_texts = [
    "Short",
    "Medium Length Text",
    "Longer Text Example",
    "Another Example",
    "Click Me to See All",
]

# Function to display button panel
def display_buttons(texts):
    # Create a container with a grey background
    with st.container():
        st.markdown(
            """
            <style>
            .button-container {
                background-color: #f0f0f0;  /* Grey background */
                padding: 10px;
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                border-radius: 5px;
            }
            .btn {
                width: 100px;
                height: 100px;
                margin: 5px;
                text-align: center;
                display: flex;
                justify-content: center;
                align-items: center;
                border: 1px solid #ccc;
                border-radius: 5px;
                transition: background-color 0.3s;
                cursor: pointer;
            }
            .btn:hover {
                background-color: #e0e0e0;  /* Lighter grey on hover */
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        col1, col2, col3, col4, col5 = st.columns(len(texts))
        
        for i, text in enumerate(texts):
            col = [col1, col2, col3, col4, col5][i]
            with col:
                if i < len(texts) - 1:  # For all buttons except the last one
                    button_html = f"""
                    <div class="btn" title="{text}">{text[:5]}...</div>
                    """
                else:  # For the last button
                    button_html = """
                    <div class="btn" onclick="showPanel()">Click Me to See All</div>
                    <script>
                    function showPanel() {
                        window.parent.streamlit.show_spinner();
                        setTimeout(() => {
                            window.parent.streamlit.empty();
                            window.parent.streamlit.write("<h2>Available Texts</h2>");
                            window.parent.streamlit.write('""" + "<br>".join(texts) + """');
                            window.parent.streamlit.stop_spinner();
                        }, 1000);
                    }
                    </script>
                    """
                st.markdown(button_html, unsafe_allow_html=True)

# Display the buttons
display_buttons(button_texts)






















