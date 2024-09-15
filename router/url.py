from fastapi import APIRouter,status,HTTPException
from fastapi.responses import RedirectResponse
import logging
import colorlog
from bs4 import BeautifulSoup
from langchain_community.document_loaders import AsyncHtmlLoader
logger = colorlog.getLogger()
logger.setLevel(logging.DEBUG)
import re
from models.classmodels import AuthorProfile,WriterInfo,ArticleDescriptionUrl
from helperfunctions.htmlloader import load_html_content,scrape_necessary_content,website_content_loader
from helperfunctions.cleancontent import clean_this_content
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.llm import LLMChain
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from templates.template import SummaryGenerationPrompt,SummaryGenerationPrompt2,ArticleSummaryGenerationTemplate,ArticleSummaryParser
from dotenv import load_dotenv
from langchain_community.document_transformers import BeautifulSoupTransformer
load_dotenv()
llm=ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.4,
    max_retries=3
)
llm2=ChatGoogleGenerativeAI(
    # Ignoring explicit content blocker here , hopefully
    # there is nothing explicit in research paper
    model="gemini-1.5-flash-latest",
    temperature=0.5,
    max_retries=2
)
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s: %(message)s',
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

router=APIRouter()
@router.get("/", include_in_schema=False)  
async def root():
    return RedirectResponse(url="/docs")
@router.post("/returnwriterinfo")
async def return_writer_info(writer_info:WriterInfo):
    logging.info("THis worked")
    urls=f"https://scholar.google.com/citations?hl=en&user={writer_info.author_id}&pagesize=100"
    documents=await load_html_content(urls)
    return scrape_necessary_content(str(documents))
@router.post("/returnaidescrition")
async def return_ai_description(writer_info:WriterInfo):
    logging.info("Calling the AI description endpoint")
    # Here I think page size is not neeeded
    url=f"https://scholar.google.com/citations?hl=en&user={writer_info.author_id}"
    docs=await website_content_loader(url)
    chain=create_stuff_documents_chain(llm,SummaryGenerationPrompt2)
    result=chain.invoke(
        {
            "context":docs
        }
    )
    return result
@router.post("/returnIndividualArticle")
async def return_individual_article(article:ArticleDescriptionUrl):
    logging.info("Calling the article description end point")
    """
    Here, I am assuming that whole URL is being passed,
    from the frontend if not I would need to append url to http://gooogle scholar or similar website
    """
    # for loading the html content
    try:

        loader=AsyncHtmlLoader(article.url)
        docs=loader.load()
    except Exception as e:
        return HTTPException(status_code=500,detail=str(e))
    bs_transformer = BeautifulSoupTransformer()
    docs_transformed = bs_transformer.transform_documents(
        docs, tags_to_extract=["p", "li", "div", "a"]
    )
    print(docs_transformed)
    text=str(docs_transformed[0].metadata)+str(docs_transformed[0].page_content)
    print(text)
    cleaned_text = re.sub(r'\[\w+.*?\]', '', text)  # Remove content within square brackets
    cleaned_text = re.sub(r'Privacy.*Help \(javascript:void\(0\)\)', '', cleaned_text)  # Remove Privacy/Terms/Help section
    cleaned_text = re.sub(r'<.*?>', '', cleaned_text)  # Remove HTML tags
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with a single space
    cleaned_text = re.sub(r'^\s+|\s+$', '', cleaned_text)  # Trim leading and trailing spaces
    cleaned_text=re.sub(r"Loading\.\.\. The system can't perform the operation now\. Try again later\.", "", cleaned_text)
    cleaned_text = re.sub(r">Sorry, some features may not work in this version of Internet Explorer\.Please use Google Chrome or Mozilla Firefox for the best experience\.<!", "", cleaned_text)
    cleaned_text = re.sub(r"(My profile|My library|Metrics|Alerts|Settings|Sign in)", "", cleaned_text)
    cleaned_text = re.sub(r"Sign in \(https?://[^\)]+\)", "", cleaned_text)
    cleaned_text = re.sub(r"About Scholar \(/intl/en/scholar/about\.html\) Search help \(//support\.google\.com/websearch\?p=scholar_dsa&hl=en&oe=ASCII\)", "", cleaned_text)
    
    # f. Remove HTML Tags
    cleaned_text = re.sub(r"<[^>]+>", "", cleaned_text)
    
    # g. Replace Encoded Characters
    cleaned_text = re.sub(r"&nbsp;", " ", cleaned_text)
    cleaned_text = re.sub(r"&lt;", "<", cleaned_text)
    cleaned_text = re.sub(r"&gt;", ">", cleaned_text)
    cleaned_text = re.sub(r"&amp;", "&", cleaned_text)
    
    print(cleaned_text)
    # Now I am assuming little bit good text stored in cleaned_text
    chain=ArticleSummaryGenerationTemplate|llm2|ArticleSummaryParser
    output=chain.invoke({"content":cleaned_text})
    print(output)
    return output