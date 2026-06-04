import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

def run_research_pipeline(topic : str) -> dict:
    state = {}

    # Search Agent Working
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about {topic}. Return titles, URLs, and snippets of the search results.")]
    })

    state['search_result'] = search_result['messages'][-1].content
    print("Search Agent Result:", state['search_result'])

    # Step 2 Reader Agent
    print("\n"+" ="*50)
    print("step 2 - reader agent is working ...")
    print("="*50)
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_result'][:800]}"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content
    print("\n Scrapped content: \n", state['scraped_content'])

    # Step 3 Writer Chain
    print("\n"+" ="*50)
    print("step 3 - writer chain is working ...")
    print("="*50)

    research_combined = (
        f"Search Results:\n{state['search_result']}\n\n"
        f"Scraped Content:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Research Report: \n", state['report'])

    #critic report 

    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report":state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state



if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)
