import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import scrape_website, scrape_url
from dotenv import load_dotenv

load_dotenv()

# Support Mistral via OpenAI-compatible API settings.
mistral_api_key = os.getenv("MISTRAL_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
if mistral_api_key:
    os.environ["OPENAI_API_KEY"] = mistral_api_key
elif openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
else:
    raise EnvironmentError("Missing MISTRAL_API_KEY or OPENAI_API_KEY in environment.")

mistral_api_base = os.getenv("MISTRAL_API_BASE") or os.getenv("OPENAI_API_BASE") or "https://api.mistral.ai/v1"
os.environ["OPENAI_API_BASE"] = mistral_api_base
os.environ.setdefault("OPENAI_API_TYPE", "openai")

mistral_model = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
llm = ChatOpenAI(model=mistral_model, temperature=0)


#1st agent 
def build_search_agent():
    return create_agent(
        model = llm,
        tools= [scrape_website]
    )

#2nd agent 

def build_reader_agent():
    return create_agent(
        model = llm,
        tools = [scrape_url]
    )


#writer chain 

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

#critic_chain 

critic_prompt = ChatPromptTemplate.from_messages([
     ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
