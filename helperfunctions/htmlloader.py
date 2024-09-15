from langchain_community.document_loaders import AsyncHtmlLoader
from fastapi import HTTPException
from typing import List
import logging
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader
from models.classmodels import AuthorProfile,CitationStats,Article,GraphData,Stats,CoAuthor
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])
from dotenv import load_dotenv
import os
load_dotenv()
custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

# Create the header template with the custom User-Agent
header_template = {
    "User-Agent": custom_user_agent
}
# import requests

USERNAME = os.getenv("PROXY_USERNAME")
PASSWORD = os.getenv("PROXY_PASSWORD")

proxiesn = {
    'http': f'http://{USERNAME}:{PASSWORD}@unblock.oxylabs.io:60000',
    'https': f'https://{USERNAME}:{PASSWORD}@unblock.oxylabs.io:60000',
}
async def load_html_content(url:str):
    try:
        loader=AsyncHtmlLoader(
            url)
        docs= loader.load()
        return docs
    except ValueError as e:  
        logging.error(str(e))
        raise HTTPException(status_code=400, detail=f"Invalid URL: {str(e)}")
    except ConnectionError as e:  
        logging.error(str(e))
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except TimeoutError as e:  
        logging.error(str(e))
        raise HTTPException(status_code=504, detail=f"Request timed out: {str(e)}")
    except Exception as e:  # Catch-all for other exceptions
        logging.error(str(e))
        raise HTTPException(status_code=500, detail=f"An unexpected error occured, Cause: {str(e)}")
async def website_content_loader(url:str):
    try:

        loader=WebBaseLoader(
            url,
            header_template=header_template,
            proxies=proxiesn,
            verify_ssl=False

        )
        docs=loader.load()
        return docs
    except ValueError as e:  # Catch issues related to URL formatting or validation
        logging.error(str(e))
        raise HTTPException(status_code=400, detail=f"Invalid URL: {str(e)}")
        
    except ConnectionError as e:  # Handle connection-related errors
        logging.error(str(e))
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
        
    except TimeoutError as e:  # Handle timeout errors
        logging.error(str(e))
        raise HTTPException(status_code=504, detail=f"Request timed out: {str(e)}")
    except Exception as e:  # Catch-all for other exceptions
        logging.error(str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
def scrape_necessary_content(content: str):
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extracting basic profile information
    name = soup.find('div', id='gsc_prf_in').get_text(strip=True)
    affiliation = soup.find('div', class_='gsc_prf_il').get_text(strip=True)
    verified_email = soup.find('div', id='gsc_prf_ivh', class_='gsc_prf_il').get_text(strip=True)
    interests = [a.get_text(strip=True) for a in soup.find_all('a', class_='gsc_prf_inta gs_ibl')]
    
    # Extracting author achievements (citations, h-index, i10-index)
    author_achievements = [td.get_text(strip=True) for td in soup.find_all('td', class_='gsc_rsb_std')]
    
    # Extracting research articles information
    articles_tags = soup.find_all('a', class_='gsc_a_at')
    research_titles = [a.get_text(strip=True) for a in articles_tags]
    article_links = [a['href'] for a in articles_tags]  # Extracting the href links

    citations_corresponding = [a.get_text(strip=True) for a in soup.find_all('a', class_='gsc_a_ac gs_ibl')]
    years_corresponding = [span.get_text(strip=True) for span in soup.find_all('span', class_='gsc_a_h gsc_a_hc gs_ibl')]
    
    co_authors = []
    co_author_spans = soup.find_all('span', class_='gsc_rsb_a_desc')
    for span in co_author_spans:
        co_author_name_tag = span.find('a')
        if co_author_name_tag:
            co_author_name = co_author_name_tag.text
            co_author_link = co_author_name_tag['href']
            co_authors.append(CoAuthor(name=co_author_name, link=co_author_link))
    
    citation_stats = CitationStats(
        all=int(author_achievements[0]),
        since2019=int(author_achievements[1])
    )
    
    stats = Stats(
        h_index=author_achievements[2],
        i10_index=author_achievements[4],
        citations=author_achievements[0],
        publication=str(len(research_titles))
    )
    
    # Mapping titles, citations, years, and links into Article instances
    articles = [
    Article(title=title, cited_by=cited_by, year=year, link=link, articleId=index + 1)
    for index, (title, cited_by, year, link) in enumerate(zip(research_titles, citations_corresponding, years_corresponding, article_links))
]

    year_to_publication_count = {}
    for year in years_corresponding:
        if year.isdigit():
            year = int(year)
            if year in year_to_publication_count:
                year_to_publication_count[year] += 1
            else:
                year_to_publication_count[year] = 1
    
    graph_data = [
        GraphData(year=year, publications=publications)
        for year, publications in sorted(year_to_publication_count.items())
    ]
    
    author_profile = AuthorProfile(
        name=name,
        affiliation=affiliation,
        verified_email=verified_email,
        interests=interests,
        citation_stats=citation_stats,
        articles=articles,
        graph_data=graph_data,
        stats=stats,
        co_authors=co_authors
    )
    
    return author_profile
