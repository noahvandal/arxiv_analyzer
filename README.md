# ArXiv Assessor

A command-line tool to fetch and summarize recent arXiv papers from specific categories using AI-powered summarization.

## Description

ArXiv Assessor helps researchers stay up-to-date with the latest papers by:

- Fetching papers published today in a specified arXiv category
- Downloading and extracting text from the PDFs
- Generating concise AI-powered summaries
- Saving results to a dated output file

## Installation

1. Clone this repository
2. Install the required dependencies:

   `pip install requests beautifulsoup4 PyPDF2 aisuite`
3. Install the AI provider package you want to use:

   1. For Anthropic's Claude (default)
      1. `pip install 'aisuite[anthropic]`
   2. For OpenAI
      1. `pip install 'aisuite[openai]'`
   3. For other supported providers
      1. `pip install 'aisuite[provider_name]'`

## Usage

Basic usage with default settings (Anthropic's Claude):

    `python arxiv_assessor.py cs.AI`

Specify a different provider and model:

    `python arxiv_assessor.py cs.AI --provider openai --model gpt-4 --api-key your_api_key`

### Arguments

- `subfolder`: Required. The arXiv category to analyze (e.g., cs.AI, physics.comp-ph)
- `--provider`: Optional. AI provider to use (default: anthropic)
- `--model`: Optional. Specific model to use (defaults available for each provider)
- `--api-key`: Optional. API key for the AI provider

### Supported Providers

- anthropic (default model: claude-3-sonnet)
- openai (default model: gpt-4)
- google (default model: gemini-pro)
- groq (default model: llama3-8b-8192)

## Output

The tool creates a dated output file (e.g., `arxiv_summaries_cs.AI_2024-03-20.txt`) containing:

- Paper IDs and URLs
- AI-generated summaries
- Direct links to PDFs

## Environment Variables

Instead of passing API keys via command line, you can set them as environment variables:

- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- etc.

## Author

Noah Vandal, 2024
