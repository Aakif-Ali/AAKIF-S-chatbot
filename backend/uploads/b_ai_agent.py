##basic ai agent with web ui
import streamlit as st
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM  

llm = OllamaLLM(model="mistral")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

prompt= PromptTemplate(
        input_variables=["chat_history", "question"],
        template="previous conversation: {chat_history}\n user:{question}\n AI:"
    )
def run_chain(question):
    chat_history_text= "\n".join([f"{msg.type.capitalize()}: {msg.content}" for msg in st.session_state.chat_history.messages ])
    response = llm.invoke(prompt.format(chat_history=chat_history_text, question=question))
    st.session_state.chat_history.add_user_message(question)
    st.session_state.chat_history.add_ai_message(response)
    return response

st.title("AAKIF's AI")
st.write("Ask me anything!")
user_input = st.text_input(" your question: ")
if user_input:
    response = run_chain(user_input)
    st.write(f"**you:** {user_input}")
    st.write(f"**AI:**{response}")

    st.subheader("chat history")
    for msg in st.session_state.chat_history.messages:
        st.write(f"**{msg.type.capitalize()}**: {msg.content}")


    
##Ai with memory 

# from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_core.prompts import PromptTemplate
# from langchain_ollama import OllamaLLM

# llm = OllamaLLM(model='mistral')
# chat_h = ChatMessageHistory()
# prompt= PromptTemplate(
#     input_variables=["chat_history","question"],
#     template="Previous Conversation: {chat_h}\nuser: {question}\nAI"
# )

# def run_chain(question):
#     chat_history_text= "\n".join([f"{msg.type.capitalize}: {msg.content}" for msg in chat_h.messages ])
#     response = llm.invoke(prompt.format(chat_h=chat_history_text, question=question))
#     chat_h.add_user_message(question)
#     chat_h.add_ai_message(response)
#     return response

# print("\n AI chatbot with MEMORY")
# print("type 'exit' to stop.")

# while True:
#     user_input= input("you: ")
#     if user_input.lower() == 'exit':
#         print("thank you")
#         break
#     ai_response = run_chain(user_input)
#     print(f"\n AI: {ai_response}")


# #AI without memory program 
# from langchain_ollama import OllamaLLM

# llm=OllamaLLM(model="mistral")
# print("\n welcome to your AI Agent! Ask me anything")
# while True:
#     q= input("your question Or type 'exit' to stop  ")
#     if q.lower() == 'exit':
#         print("thank you")
#         break
#     r= llm.invoke(q)
#     print('AI response:', r)