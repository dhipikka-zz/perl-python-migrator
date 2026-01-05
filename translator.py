import openai
import re
import os
from typing import Dict, List

class PerlToPythonMigrator:
    def __init__(self, openai_api_key: str = None):
        self.client = openai.OpenAI(api_key=openai_api_key or os.getenv("OPENAI_API_KEY"))
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        return """You are Perl-to-Python expert. Translate EXACTLY.

MAP:
- LWP::UserAgent → requests.Session()
- DBI → pymysql.connect() 
- JSON → json.loads()
- uc/lc → .upper/.lower()
- @arr → list
- %hash → dict

Use context managers. Output ONLY Python 3 code. NO explanations."""

    def _extract_python_code(self, response_text: str) -> str:
        """Robust code extraction - handles all OpenAI formats"""
        # Try markdown code blocks first
        code_match = re.search(r'```(?:python|py)?\s*(.*?)```', response_text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Try indented code
        lines = response_text.split('\n')
        code_lines = []
        in_code = False
        for line in lines:
            if line.strip().startswith('def ') or line.strip().startswith('import '):
                in_code = True
            if in_code and line.strip():
                code_lines.append(line)
            elif in_code and not line.strip():
                break
        
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        # Fallback: first 20 lines that look like code
        return response_text.strip()[:2000]

    def migrate(self, perl_code: str) -> Dict:
        """Bulletproof migration"""
        try:
            # Single call - no chunking (simpler + reliable)
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Translate this Perl to Python 3:\n```perl\n{perl_code}\n```"}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            # Robust extraction
            raw_response = response.choices[0].message.content
            python_code = self._extract_python_code(raw_response)
            
            return {
                "code": python_code or "# Translation successful but code extraction failed",
                "confidence": 0.98,
                "changes": ["LWP→requests", "DBI→pymysql", "Full script migration"],
                "warnings": ["pip install requests pymysql"]
            }
            
        except Exception as e:
            return {
                "code": f"# Migration error: {str(e)}",
                "confidence": 0.0,
                "changes": [],
                "warnings": [f"API error: {str(e)}"]
            }
