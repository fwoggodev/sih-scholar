from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models.classmodels import ArticleInfo
ArticleSummaryParser=JsonOutputParser(
    pydantic_object=ArticleInfo
)
SummaryGenerationPrompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", 
            """
            You are an expert biographer with a deep understanding of academic achievements and research contributions. 
            Provided below is the content extracted from Google Scholar about a researcher. 
            Please craft a detailed, engaging, and professional summary of this individual, 
            including their significant contributions, key research areas, publications, and any other relevant details.
            Ensure the summary is well-structured, highlights the impact of their work, and is suitable for inclusion in a professional profile or biography.
            Remember, I only need summary Nothing else , You must not start with things like "Here is a detailed Summary" etc. , Just directly provide me the summary
            \n\n{context}
            """
        )
    ]
)
prompt2="""
You are an expert biographer with a deep understanding of academic achievements and research contributions. 
            Provided below is the content extracted from Google Scholar about a researcher. 
            Please craft a concise, engaging, and professional summary of this individual, 
            highlighting their significant contributions, key research areas, and any other relevant details.
            Ensure the summary is well-structured, impactful , and suitable for a professional profile or biography.
            The summary should be brief yet informative covering all the necessary details without unnecessary elaboration.
            Remember, I only need summary Nothing else , You must not start with things like "Here is a detailed Summary" etc. , Just directly provide me the summary
            \n\n{context}
"""
SummaryGenerationPrompt2=PromptTemplate(
    template=prompt2,
    input_variables=['context']
)

ArticleSummaryGenerationTemplate=PromptTemplate(
    template="""As input, I am giving you some extracted content from the website which includes some important things like research paper links, citations, coauthors , and research paper description. \n\n Here is the extracted content which you should process\n\n{content} You must return me output according to the {format_instructions}.""",
    partial_variables={"format_instructions": ArticleSummaryParser.get_format_instructions()},
)