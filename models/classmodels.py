from pydantic import BaseModel,Field,HttpUrl
from typing import List,Optional
class WriterInfo(BaseModel):
    author_id:str
class CoAuthor(BaseModel):
    name:str
    link:str
class CitationStats(BaseModel):
    """
    All indicates total number of citations
    & since2019 indicates citations since 2019
    """
    all:int
    since2019:int

class Article(BaseModel):
    """
    title indicates, title of the article
    cited by indicates total citations in that publication
    year indicates when was that publication published

    """
    title:str
    cited_by:str
    year:str
    link:str
    articleId:int
class GraphData(BaseModel):
    """
    year indicates the year of a publication
    publications indicate total no of publication made in that year
    """
    year:int
    publications:int
class Stats(BaseModel):
    h_index: str
    i10_index: str
    citations: str
    publication: str
class ArticleDescriptionUrl(BaseModel):
    url:str

class AuthorProfile(BaseModel):
    name:str
    affiliation:str
    verified_email:str
    interests: List[str]
    citation_stats: CitationStats
    articles: List[Article]
    graph_data: List[GraphData]
    # ai_description: str = Field(alias="aiDescription")
    stats: Stats
    co_authors:List[CoAuthor]

class ArticleInfo(BaseModel):
    title: Optional[str] = Field(None, description="Title of the article")
    authors: Optional[List[str]] = Field(None, description="List of authors")
    publication_date: Optional[str] = Field(None, description="Publication date in YYYY/MM/DD format")
    journal: Optional[str] = Field(None, description="Journal name")
    volume: Optional[str] = Field(None, description="Volume number")
    pages: Optional[str] = Field(None, description="Page range")
    publisher: Optional[str] = Field(None, description="Publisher name")
    summary: Optional[str] = Field(None, description="Based on all the fields , generate a description of the research article")
    total_citations: Optional[int] = Field(None, description="Total number of citations")
    citation_by_year: Optional[dict] = Field(None, description="Dictionary of citations by year. In the given content, you may find something like 2010 2011 5 6 which means in 2010 there were 5 citations and 6 in 2011 so you should output like  2010:5 2011:6 in a dictionary")
    article_link: Optional[HttpUrl] = Field(None, description="Direct link to the article")
    pdf_link: Optional[HttpUrl] = Field(None, description="Direct link to the PDF version of the article")
    google_scholar_link: Optional[HttpUrl] = Field(None, description="Link to the article on Google Scholar")
    related_articles_link: Optional[HttpUrl] = Field(None, description="Link to related articles")
    all_versions_link: Optional[HttpUrl] = Field(None, description="Link to all versions of the article")