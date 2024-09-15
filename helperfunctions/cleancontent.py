import re
def clean_this_content(text):
    """
    This function cleans the passed the HTML so that only necessary
    information is passed to the LLM
    """
    cleaned_text = re.sub(r'\[\w+.*?\]', '', text)  # Remove content within square brackets
    cleaned_text = re.sub(r'Privacy.*Help \(javascript:void\(0\)\)', '', cleaned_text)  # Remove Privacy/Terms/Help section
    cleaned_text = re.sub(r'<.*?>', '', cleaned_text)  # Remove HTML tags
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with a single space
    cleaned_text = re.sub(r'^\s+|\s+$', '', cleaned_text)  # Trim leading and trailing spaces
    return cleaned_text