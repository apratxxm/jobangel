import requests
from bs4 import BeautifulSoup

def scrape_website_text(url: str)-> str:

    # Pretending to be a browser 

    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    try:
        response=requests.get(url,headers=headers, timeout=10)

        #if the website crashes stop here and raise status
        response.raise_for_status()

        # Hand the raw HTML to beautifulsoup to strip away the <div> and <span> tags
        soup= BeautifulSoup(response.text, "html.parser")

        #extract just the readable text and clean up the extra spaces
        text= soup.get_text(separator= " ", strip=True)
        print(f"{text[:100]}")
        return text
    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

if __name__ == "__main__":
    print("Testing enricher")
    scrape_website_text("https://groww.in")