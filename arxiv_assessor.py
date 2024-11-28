"""
2024, Noah Vandal
Basic modules for a cli tool to assess arxiv papers published in the past day. 
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from pathlib import Path
import PyPDF2
import aisuite as ai
from aisuite.provider import ProviderFactory
import argparse

class ArxivAssessor:
    def __init__(self, subfolder: str, provider: str = "anthropic", model: str = "claude-3-sonnet", api_key: str = None):
        """
        Initialize the assessor with the arxiv subfolder to analyze
        (e.g., 'cs.AI' for Artificial Intelligence papers)
        """
        self.base_url = f"https://arxiv.org/list/{subfolder}/recent"
        self.provider = provider
        self.model = model
        
        # Initialize client with proper provider configuration
        provider_configs = {
            provider: {"api_key": api_key}
        } if api_key else {}
        self.client = ai.Client(provider_configs)
    
    def get_daily_papers(self) -> list:
        """
        Scrape the arxiv subfolder and return list of papers from the most recent day
        """
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the date header for the most recent papers
        date_header = soup.find('h3', text=re.compile(r'\w+,\s+\d+\s+\w+\s+\d{4}'))
        
        # Get the dl element containing the papers
        papers_list = soup.find('dl', id='articles')
        
        papers = []
        if papers_list:
            for dt in papers_list.find_all('dt'):
                # Get the PDF link
                pdf_link = dt.find_next('a', title='Download PDF')
                if pdf_link:
                    papers.append({
                        'pdf_url': f"https://arxiv.org{pdf_link['href']}",
                        'paper_id': pdf_link['href'].split('/')[-1]
                    })
        
        return papers

    def summarize_pdf(self, pdf_url: str) -> str:
        """
        Download PDF, extract text, and generate a concise summary
        """
        # Download PDF
        response = requests.get(pdf_url)
        temp_pdf = Path("temp.pdf")
        temp_pdf.write_bytes(response.content)
        
        # Extract text from first few pages (abstract + intro usually sufficient)
        text = ""
        with open(temp_pdf, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages[:2]:  # First two pages
                text += page.extract_text()
        
        # Clean up
        temp_pdf.unlink()
        
        # Generate summary
        summary = self.summarize_text(text[:1024])
        return summary

    def summarize_text(self, text: str) -> str:
        """
        Generate a concise summary using the specified LLM
        """
        messages = [
            {
                "role": "system",
                "content": "You are a scientific paper summarizer. Create a very concise summary (5 sentences or less) of the paper text provided. Focus on the main accomplishments and findings.",
            },
            {"role": "user", "content": text},
        ]
        
        response = self.client.chat.completions.create(
            model=f"{self.provider}:{self.model}",
            messages=messages,
            temperature=0.3,
            max_tokens=200,
        )
        
        return response.choices[0].message.content

def main():
    parser = argparse.ArgumentParser(description='Assess recent arXiv papers from a specific subfolder')
    parser.add_argument('subfolder', help='ArXiv subfolder to analyze (e.g., cs.AI)')
    parser.add_argument('--provider', default='anthropic', help='AI provider (e.g., anthropic, openai)')
    parser.add_argument('--model', help='Model name (e.g., claude-3-sonnet, gpt-4)')
    parser.add_argument('--api-key', help='API key for the provider')
    args = parser.parse_args()
    
    # Get supported providers from aisuite
    supported_providers = ProviderFactory.get_supported_providers()
    
    if args.provider not in supported_providers:
        print(f"Error: Provider '{args.provider}' is not supported.")
        print("\nSupported providers:")
        for provider in supported_providers:
            print(f"  - {provider}")
        print("\nTo use a provider, first install its package:")
        print("pip install 'aisuite[provider_name]'")
        return
    
    # Default models for each provider
    model = args.model or {
        'anthropic': 'claude-3-sonnet',
        'openai': 'gpt-4',
        'google': 'gemini-pro',
        'groq': 'llama3-8b-8192',
    }.get(args.provider)
    
    try:
        assessor = ArxivAssessor(
            args.subfolder,
            provider=args.provider,
            model=model,
            api_key=args.api_key
        )
        papers = assessor.get_daily_papers()
        
        for paper in papers:
            print(f"\nPaper ID: {paper['paper_id']}")
            summary = assessor.summarize_pdf(paper['pdf_url'])
            print(f"Summary: {summary}\n")
            print("-" * 80)
            
    except ImportError as e:
        print(f"\nError: {e}")
        print("\nMake sure you have installed the required package:")
        print(f"pip install 'aisuite[{args.provider}]'")

if __name__ == "__main__":
    main()