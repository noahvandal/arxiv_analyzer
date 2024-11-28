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
        self.subfolder = subfolder
        self.base_url = f"https://arxiv.org/list/{self.subfolder}/recent"
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
        papers = []
        current_page = 0
        
        # Get the first page to find today's date
        url = f"{self.base_url}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all date headers
        date_headers = soup.find_all('h3', string=re.compile(r'\w+,\s+\d+\s+\w+\s+\d{4}'))
        if not date_headers:
            return papers
        
        # Get today's date from the first header
        today_match = re.search(r'(\w+,\s+\d+\s+\w+\s+\d{4})', date_headers[0].text)
        if not today_match:
            return papers
        
        today_date = datetime.strptime(today_match.group(1).strip(), '%a, %d %b %Y')
        
        while True:
            url = f"{self.base_url}?skip={current_page * 25}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the current section's date header
            date_header = soup.find('h3', string=re.compile(r'\w+,\s+\d+\s+\w+\s+\d{4}'))
            if date_header:
                date_match = re.search(r'(\w+,\s+\d+\s+\w+\s+\d{4})', date_header.text)
                if date_match:
                    current_date = datetime.strptime(date_match.group(1).strip(), '%a, %d %b %Y')
                    # Stop if we've moved to a different date
                    if current_date != today_date:
                        break
            
            # Get the dl element containing the papers
            papers_list = soup.find('dl')
            if not papers_list:
                break
                
            new_papers = []
            for dt in papers_list.find_all('dt'):
                pdf_link = dt.find_next('a', title='Download PDF')
                if pdf_link:
                    new_papers.append({
                        'pdf_url': f"https://arxiv.org{pdf_link['href']}",
                        'paper_id': pdf_link['href'].split('/')[-1]
                    })
            
            # If no new papers found, we've reached the end
            if not new_papers:
                break
                
            papers.extend(new_papers)
            current_page += 1
        
        print(f"Found {len(papers)} papers in {self.subfolder} for {today_date.strftime('%Y-%m-%d')}")
        return papers

    def summarize_pdf(self, pdf_url: str) -> str:
        """
        Download PDF, extract text, and generate a concise summary
        """
        # Download PDF
        response = requests.get(pdf_url)
        temp_pdf = Path("temp.pdf")
        temp_pdf.write_bytes(response.content)
        
        try:
            # Extract text from first few pages (abstract + intro usually sufficient)
            text = ""
            with open(temp_pdf, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages[:10]:  # First ten pages
                    text += page.extract_text()
        finally:
            # Ensure file handle is closed before attempting deletion
            try:
                temp_pdf.unlink()
            except PermissionError:
                # If file is still locked, try again after a brief delay
                import time
                time.sleep(0.1)
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
    try:
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
        
        assessor = ArxivAssessor(
            args.subfolder,
            provider=args.provider,
            model=model,
            api_key=args.api_key
        )
        papers = assessor.get_daily_papers()
        
        # Create output filename with date
        today = datetime.now().strftime('%Y-%m-%d')
        output_file = f"arxiv_summaries_{args.subfolder}_{today}.txt"
        
        print(f"Processing papers and saving to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"ArXiv Summaries for {args.subfolder} on {today}\n")
            f.write("=" * 80 + "\n\n")
            
            for paper in papers:
                print(f"\nProcessing paper: {paper['paper_id']}")
                summary = assessor.summarize_pdf(paper['pdf_url'])
                # Write to file
                f.write(f"Paper ID: {paper['paper_id']}\n")
                f.write(f"URL: https://arxiv.org/abs/{paper['paper_id']}\n")
                f.write(f"PDF: {paper['pdf_url']}\n")
                f.write("\nSummary:\n")
                
                # Split summary into chunks of ~200 chars at whitespace
                remaining = summary
                while len(remaining) > 150:
                    split_index = remaining[:150].rindex(' ')
                    f.write(remaining[:split_index] + '\n')
                    remaining = remaining[split_index+1:]   
                f.write(remaining)
                
                f.write("\n" + "-" * 80 + "\n\n")
                
                # Also print to console
                print("Summary saved.")
                print(summary)
                print("-" * 80)
        
        print(f"\nAll summaries have been saved to {output_file}")
            
    except ImportError as e:
        print(f"\nError: {e}")
        print("\nMake sure you have installed the required package:")
        print(f"pip install 'aisuite[{args.provider}]'")

if __name__ == "__main__":
    main()