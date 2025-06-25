import os
from typing import Annotated
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
import markdownify
from fastmcp.server.auth.provider import AccessToken
from pathlib import Path
import readabilipy
import PyPDF2
import re
from typing import List
from pydantic import BaseModel

TOKEN = "193905b485d6"
MY_NUMBER = "918583949261"

def clean_resume_text(raw_text: str) -> str:
    """Clean and format resume text into proper markdown"""
    text = fix_encoding_issues(raw_text)
    text = fix_spacing_issues(text)
    text = add_line_breaks_for_resume(text)
    text = structure_resume_markdown(text)
    return text.strip()

def fix_encoding_issues(text: str) -> str:
    """Fix common PDF extraction encoding problems"""
    text = text.replace('â¢', '•')
    text = text.replace('â', '-')
    text = text.replace('â€™', "'")
    text = text.replace('â€œ', '"')
    text = text.replace('â€', '"')
    return text

def fix_spacing_issues(text: str) -> str:
    """Fix broken spacing from PDF extraction"""
    # Fix LinkedIn URL specifically
    text = re.sub(r'linkedin\.com/in/(\w+)\s*-\s*(\w+)\s*-\s*(\w+)', r'linkedin.com/in/\1-\2-\3', text)
    text = re.sub(r'linkedin\.com/in/(\w+)\s*-\s*(\w+)', r'linkedin.com/in/\1-\2', text)
    
    # Fix general hyphenated words
    text = re.sub(r'\b(\w+)\s*-\s*(\w+)\b', r'\1-\2', text)
    
    # Fix URLs and emails
    text = re.sub(r'(https?://[^\s]+)\s*-\s*([^\s]+)', r'\1-\2', text)
    text = re.sub(r'(@\w+)\s+(\.\w+)', r'\1\2', text)
    
    # Fix common broken phrases
    text = re.sub(r'\breal\s*-\s*world\b', 'real-world', text)
    text = re.sub(r'\bhands\s*-\s*on\b', 'hands-on', text)
    text = re.sub(r'\btime\s*-\s*slot\b', 'time-slot', text)
    text = re.sub(r'\bAI\s*-\s*powered\b', 'AI-powered', text)
    text = re.sub(r'\bOCR\s*-\s*based\b', 'OCR-based', text)
    
    return text

def add_line_breaks_for_resume(text: str) -> str:
    """Add line breaks before section headers and bullet points"""
    # Handle punctuation before section headers
    text = re.sub(r'([.!?])\s*(SUMMARY|EXPERIENCE|EDUCATION|SKILLS|CERTIFICATIONS|AWARDS)\b', r'\1\n\n\2', text)
    text = re.sub(r'([.!?])\s*(MAJOR\s+PROJECTS|OTHER\s+PROJECTS)\b', r'\1\n\n\2', text)
    text = re.sub(r'([.!?\w])\s+(PROJECTS)\b', r'\1\n\n\2', text)
    
    # Handle cases without punctuation
    text = re.sub(r'(\w)\s+(SUMMARY|EXPERIENCE|EDUCATION|SKILLS)\b', r'\1\n\n\2', text)
    
    # Handle after year patterns
    text = re.sub(r'(\d{4})\s+(EDUCATION|SKILLS)\b', r'\1\n\n\2', text)
    text = re.sub(r'(Models|Tools|Technologies)\s+(SKILLS)\b', r'\1\n\n\2', text)
    
    # Handle after URLs or brackets
    text = re.sub(r'(\])\s+(EDUCATION|SKILLS)\b', r'\1\n\n\2', text)
    text = re.sub(r'(/)\s+(EDUCATION|SKILLS)\b', r'\1\n\n\2', text)
    
    # Add line breaks before bullet points
    text = re.sub(r'([.!?\w])\s+(• )', r'\1\n\2', text)
    text = re.sub(r'([.!?\w])\s+(- )', r'\1\n\2', text)
    text = re.sub(r'(\])\s+(• )', r'\1\n\2', text)
    text = re.sub(r'(\])\s+(- )', r'\1\n\2', text)
    
    # Add line break after portfolio
    text = re.sub(r'(portfolioamritanshulahiri\.super\.site)\s+([A-Z])', r'\1\n\n\2', text)
    
    # Clean up spacing
    text = re.sub(r'MAJOR\s*\n\s*PROJECTS', 'MAJOR PROJECTS', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def structure_resume_markdown(text: str) -> str:
    """Convert resume text to proper markdown structure"""
    lines = text.split('\n')
    formatted_lines = []
    
    for index, line in enumerate(lines):
        if not line.strip():
            formatted_lines.append('')
            continue
            
        formatted_line = format_line(line.strip(), index, lines)
        if formatted_line:
            formatted_lines.append(formatted_line)
    
    result = '\n'.join(formatted_lines)
    result = clean_final_spacing(result)
    return result

def format_line(line: str, index: int, all_lines: List[str]) -> str:
    """Format individual lines based on resume patterns"""
    if line.strip() == "# My Resume":
        return ""
    
    if index <= 2 and is_name_line(line):
        return f"# {line}\n"
    
    if is_section_header(line):
        return f"\n## {line}\n"
    
    if is_contact_line(line):
        return f"**{line}**\n"
    
    if is_bullet_line(line):
        clean_bullet = clean_bullet_point(line)
        return f"- {clean_bullet}"
    
    if is_job_title_line(line, index, all_lines):
        return f"\n### {line}\n"
    
    return line

def is_name_line(line: str) -> bool:
    """Detect if line is a person's name"""
    words = line.split()
    if len(words) in [2, 3] and line.isupper():
        return True
    return False

def is_section_header(line: str) -> bool:
    """Check if line is a section header"""
    line = line.strip().upper()
    section_headers = [
        'SUMMARY', 'EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS',
        'MAJOR PROJECTS', 'OTHER PROJECTS', 'CERTIFICATIONS', 'AWARDS',
        'ACHIEVEMENTS', 'TECHNICAL SKILLS'
    ]
    
    for header in section_headers:
        if line == header or line.startswith(header + ' '):
            return True
    return False

def is_contact_line(line: str) -> bool:
    """Detect contact information lines"""
    contact_patterns = [
        r'\+?\d{2}\s?\d{10}',
        r'\S+@\S+\.\S+',
        r'LinkedIn:',
        r'GitHub:',
        r'Portfolio:',
        r'Kolkata, India'
    ]
    return any(re.search(pattern, line, re.IGNORECASE) for pattern in contact_patterns)

def is_bullet_line(line: str) -> bool:
    """Detect bullet points"""
    return line.startswith('•') or line.startswith('-') or line.startswith('*')

def clean_bullet_point(line: str) -> str:
    """Clean up bullet point text"""
    clean_line = line.lstrip('•-* ').strip()
    return clean_line

def is_job_title_line(line: str, index: int, all_lines: List[str]) -> bool:
    """Detect job titles and experience entries"""
    if '|' in line and any(word in line for word in ['Engineer', 'Developer', 'Manager', 'Analyst']):
        return True
    
    if index + 1 < len(all_lines):
        next_line = all_lines[index + 1]
        if is_bullet_line(next_line):
            return True
    return False

def clean_final_spacing(text: str) -> str:
    """Final cleanup of spacing and formatting"""
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'\n(#{1,3}[^#\n]+)\n', r'\n\n\1\n', text)
    text = text.replace('\n\n\n', '\n\n')
    return text

def format_resume(raw_text: str) -> str:
    """Main function to format resume"""
    cleaned_text = clean_resume_text(raw_text)
    
    if not cleaned_text.startswith('#'):
        cleaned_text = f"# AMRITANSHU LAHIRI\n\n{cleaned_text}"
    
    cleaned_text = cleaned_text.replace('Sreamlit', 'Streamlit')
    return cleaned_text

def clean_extracted_text(text: str) -> str:
    """Clean up common PDF extraction issues"""
    text = re.sub(r'\s+', ' ', text)
    
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            cleaned_lines.append('')
            continue
            
        words = line.split(' ')
        if len(words) > 3 and all(len(word) <= 1 for word in words[:6]):
            cleaned_line = ''.join(words)
            cleaned_line = re.sub(r'([a-zA-Z])@([a-zA-Z])', r'\1@\2', cleaned_line)
            cleaned_line = re.sub(r'([a-zA-Z])\.([a-zA-Z])', r'\1.\2', cleaned_line)
            cleaned_line = re.sub(r'([a-z])([A-Z])', r'\1 \2', cleaned_line)
            cleaned_line = re.sub(r'(\d)([A-Z])', r'\1 \2', cleaned_line)
            cleaned_line = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', cleaned_line)
            cleaned_lines.append(cleaned_line)
        else:
            cleaned_lines.append(line)
    
    result = '\n'.join(cleaned_lines)
    result = result.replace('   ', ' ')
    result = result.replace('  ', ' ')
    return result

def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text from PDF using PyPDF2"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                text += page_text + "\n"
            
            cleaned_text = clean_extracted_text(text)
            return cleaned_text.strip()
            
    except Exception as e:
        raise Exception(f"Failed to read PDF: {str(e)}")

def extract_and_convert_resume(file_path: Path) -> str:
    """Extract content from resume file and convert to markdown"""
    try:
        if file_path.suffix.lower() == '.pdf':
            try:
                result = readabilipy.simple_json_from_html_string(
                    f"<embed src='{file_path.absolute()}' type='application/pdf'>"
                )
                
                if result and 'content' in result:
                    content = result['content']
                else:
                    content = extract_text_from_pdf(file_path)
                    
            except Exception:
                content = extract_text_from_pdf(file_path)
        
        elif file_path.suffix.lower() in ['.html', '.htm']:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            result = readabilipy.simple_json_from_html_string(html_content)
            content = result.get('content', html_content) if result else html_content
            content = markdownify.markdownify(content, heading_style="ATX")
            
        elif file_path.suffix.lower() in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
        else:
            raise Exception(f"Unsupported file format: {file_path.suffix}")
        
        if not content or len(content.strip()) < 50:
            raise Exception("File appears to be empty or content could not be extracted")
        
        content = content.strip()
        
        if not content.startswith('#'):
            first_line = content.split('\n')[0].strip()
            if first_line and len(first_line) < 50 and not first_line.startswith('•'):
                content = f"# {first_line}\n\n{content}"
            else:
                content = f"# My Resume\n\n{content}"
        
        return content
        
    except Exception as e:
        raise Exception(f"Failed to process resume file: {str(e)}")

class RichToolDescription(BaseModel):
    description: str
    use_when: str
    side_effects: str | None

class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(
            public_key=k.public_key, jwks_uri=None, issuer=None, audience=None
        )
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="unknown",
                scopes=[],
                expires_at=None,
            )
        return None

mcp = FastMCP(
    "My MCP Server",
    auth=SimpleBearerAuthProvider(TOKEN),
)

ResumeToolDescription = RichToolDescription(
    description="Serve your resume in plain markdown.",
    use_when="Puch (or anyone) asks for your resume; this must return raw markdown, no extra formatting.",
    side_effects=None,
)

@mcp.tool(description=ResumeToolDescription.model_dump_json())
async def resume() -> str:
    """Return resume as clean, formatted markdown text."""
    try:
        current_dir = Path(".")
        
        resume_patterns = [
            "resume.pdf", "resume.html", "resume.txt", "resume.md",
            "cv.pdf", "cv.html", "cv.txt", "cv.md",
            "my_resume.pdf", "my_resume.html", "my_resume.txt", "my_resume.md",
            "Resume.pdf", "Resume.html", "Resume.txt", "Resume.md",
            "CV.pdf", "CV.html", "CV.txt", "CV.md"
        ]
        
        resume_file = None
        for pattern in resume_patterns:
            potential_file = current_dir / pattern
            if potential_file.exists():
                resume_file = potential_file
                break
        
        if not resume_file:
            raise Exception("No resume file found. Please save your resume as 'resume.pdf', 'resume.html', 'resume.txt', or 'resume.md'")
        
        raw_content = extract_and_convert_resume(resume_file)
        cleaned_content = format_resume(raw_content)
        
        return cleaned_content
        
    except Exception as e:
        error_msg = f"Error processing resume: {str(e)}"
        return f"# Resume Processing Error\n\n{error_msg}\n\nPlease ensure your resume file is accessible."

@mcp.tool
async def validate() -> str:
    """Return phone number for validation."""
    return MY_NUMBER

async def main():
    # Railway automatically provides PORT environment variable
    port = int(os.environ.get("PORT", 8085))
    
    await mcp.run_async(
        "streamable-http",
        host="0.0.0.0",
        port=port,
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
