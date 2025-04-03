"""
Helper module for processing email content
"""

import re
import email
from email.parser import Parser
from email.policy import default
from collections import defaultdict
import json
from datetime import datetime

from .base_helper import ContentHelperBase

# Email-specific patterns
EMAIL_HEADER_PATTERN = re.compile(r'^(?:From|To|Subject|Date|Cc|Bcc|Reply-To|Sender|Message-ID):\s.*?$', re.MULTILINE)
EMAIL_QUOTE_PATTERN = re.compile(r'(?:^>.*?$(?:\n|$))+', re.MULTILINE)
EMAIL_SIGNATURE_PATTERN = re.compile(r'(?:^--+\s*$\n)(?:.+\n)*(?:.*?@.*?\n)?(?:.*?(?:T|t)el[:\.].*?\n)?(?:.*?(?:www|http).*?\n)?', re.MULTILINE)
EMAIL_DISCLAIMER_PATTERN = re.compile(r'(?:DISCLAIMER|CONFIDENTIAL|LEGAL\s+NOTICE).*?(?=\n\n|\Z)', re.IGNORECASE | re.DOTALL)
EMAIL_FORWARDED_PATTERN = re.compile(r'^-{3,}\s*(?:Forwarded|Original)\s+(?:message|Message).*?$', re.MULTILINE)
EMAIL_FOOTER_PATTERN = re.compile(r'(?:\n\n.*?[Ss]ent from my (?:iPhone|iPad|Android|Samsung|mobile).*?|\n\n.*?[Ss]ent via .*?$)', re.MULTILINE)

class EmailHelper(ContentHelperBase):
    """
    Helper for processing email content
    """
    
    def __init__(self, **kwargs):
        """Initialize the Email helper with optional config"""
        super().__init__(name="Email", **kwargs)
        
        # Configure email-specific optimization settings
        self.preserve_headers = kwargs.get('preserve_headers', False)
        self.preserve_quotes = kwargs.get('preserve_quotes', False)
        self.preserve_signatures = kwargs.get('preserve_signatures', False)
        self.max_quote_depth = kwargs.get('max_quote_depth', 1)  # How many layers of quotes to keep
        
        # Email-specific statistics
        self.stats["helper_specific_data"]["headers_removed"] = 0
        self.stats["helper_specific_data"]["quotes_removed"] = 0
        self.stats["helper_specific_data"]["signatures_removed"] = 0
        self.stats["helper_specific_data"]["disclaimers_removed"] = 0
        self.stats["helper_specific_data"]["footers_removed"] = 0
        self.stats["helper_specific_data"]["threads_processed"] = 0
    
    def detect_content_type(self, file_path, content=None):
        """
        Detect if a file contains email content.
        
        Args:
            file_path: Path to the file
            content: Optional content of the file
            
        Returns:
            float: Confidence score (0.0 to 1.0) that this is email content
        """
        confidence = 0.0
        
        # Check file extension
        if file_path.lower().endswith(('.eml', '.msg')):
            confidence += 0.8
            return min(confidence, 1.0)  # Strong indicator
        
        # If content was not provided, read a sample
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4000)  # Read first 4KB for detection
            except:
                return 0.0  # Cannot read file
        
        # Check for email headers
        header_matches = len(EMAIL_HEADER_PATTERN.findall(content))
        if header_matches >= 3:  # If we find multiple headers, it's likely an email
            confidence += 0.6
        elif header_matches > 0:
            confidence += 0.3
        
        # Check for email quotes
        if EMAIL_QUOTE_PATTERN.search(content):
            confidence += 0.3
        
        # Check for email signatures
        if EMAIL_SIGNATURE_PATTERN.search(content):
            confidence += 0.2
        
        # Check for forwarded message markers
        if EMAIL_FORWARDED_PATTERN.search(content):
            confidence += 0.4
        
        # Check for "Sent from my..." footers
        if EMAIL_FOOTER_PATTERN.search(content):
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def preprocess_content(self, content, file_path=None):
        """
        Prepare email content for optimization.
        
        Args:
            content: String content to preprocess
            file_path: Optional path to the file (for context)
            
        Returns:
            str: Preprocessed content or structured data
        """
        # For .eml files, try to parse with email module
        if file_path and file_path.lower().endswith('.eml'):
            try:
                return self._parse_eml_content(content)
            except:
                # Fall back to regular text processing if parsing fails
                pass
        
        # Regular text processing
        return content
    
    def _parse_eml_content(self, content):
        """Parse .eml format email content into a structured dictionary"""
        parser = Parser(policy=default)
        email_msg = parser.parsestr(content)
        
        # Extract key email parts
        email_data = {
            'headers': {},
            'body_text': "",
            'body_html': "",
            'attachments': [],
            'is_structured': True
        }
        
        # Extract headers
        for header, value in email_msg.items():
            email_data['headers'][header] = value
        
        # Extract body parts
        for part in email_msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition') or '')
            
            # Handle attachments
            if 'attachment' in content_disposition:
                filename = part.get_filename()
                if filename:
                    email_data['attachments'].append({
                        'filename': filename,
                        'content_type': content_type
                    })
                continue
            
            # Handle text parts
            if content_type == 'text/plain':
                email_data['body_text'] += part.get_content() + "\n"
            elif content_type == 'text/html':
                email_data['body_html'] += part.get_content() + "\n"
        
        return email_data
    
    def optimize_content(self, content, file_path=None):
        """
        Apply email-specific optimizations.
        
        Args:
            content: String content or structured email data
            file_path: Optional path to the file (for context)
            
        Returns:
            tuple: (optimized_content, optimization_stats)
        """
        stats = defaultdict(int)
        
        # Handle structured email data from .eml parsing
        if isinstance(content, dict) and content.get('is_structured'):
            return self._optimize_structured_email(content, stats)
        
        # Handle regular text content
        if not content:
            return content, {}
        
        result = content
        
        # Remove email headers if configured
        if not self.preserve_headers:
            new_content, count = EMAIL_HEADER_PATTERN.subn('', result)
            if count > 0:
                result = new_content
                stats["Email Headers"] = count
                self.stats["helper_specific_data"]["headers_removed"] += count
        
        # Process email quotes if configured
        if not self.preserve_quotes:
            # Fully remove quotes or limit to configured depth
            if self.max_quote_depth <= 0:
                # Remove all quotes
                new_content, count = EMAIL_QUOTE_PATTERN.subn('', result)
                if count > 0:
                    result = new_content
                    stats["Email Quotes"] = count
                    self.stats["helper_specific_data"]["quotes_removed"] += count
            else:
                # Process quotes to keep only up to max_quote_depth levels
                result = self._limit_quote_depth(result)
                stats["Email Quotes Truncated"] = 1
        
        # Remove email signatures if configured
        if not self.preserve_signatures:
            new_content, count = EMAIL_SIGNATURE_PATTERN.subn('', result)
            if count > 0:
                result = new_content
                stats["Email Signatures"] = count
                self.stats["helper_specific_data"]["signatures_removed"] += count
        
        # Remove common email disclaimer text
        new_content, count = EMAIL_DISCLAIMER_PATTERN.subn('', result)
        if count > 0:
            result = new_content
            stats["Email Disclaimers"] = count
            self.stats["helper_specific_data"]["disclaimers_removed"] += count
        
        # Remove "Sent from my..." footers
        new_content, count = EMAIL_FOOTER_PATTERN.subn('', result)
        if count > 0:
            result = new_content
            stats["Email Footers"] = count
            self.stats["helper_specific_data"]["footers_removed"] += count
        
        return result, dict(stats)
    
    def _optimize_structured_email(self, email_data, stats):
        """
        Optimize structured email data.
        
        Args:
            email_data: Dictionary with structured email parts
            stats: Statistics dictionary to update
            
        Returns:
            tuple: (optimized_content, stats)
        """
        # Start with the plain text body or fall back to HTML
        body_text = email_data['body_text'] or self._html_to_text(email_data['body_html'])
        
        # Apply the same optimizations to the body text
        optimized_body, body_stats = self.optimize_content(body_text)
        
        # Update stats
        for key, count in body_stats.items():
            stats[key] = count
        
        # Record that we processed a thread if we removed quotes
        if "Email Quotes" in body_stats and body_stats["Email Quotes"] > 0:
            self.stats["helper_specific_data"]["threads_processed"] += 1
        
        # Create a formatted version with select headers and optimized body
        crucial_headers = ['From', 'To', 'Subject', 'Date']
        formatted_result = []
        
        # Add important headers
        for header in crucial_headers:
            if header in email_data['headers']:
                formatted_result.append(f"{header}: {email_data['headers'][header]}")
        
        # Add a separator
        formatted_result.append("\n---\n")
        
        # Add the optimized body
        formatted_result.append(optimized_body)
        
        # Add a note about attachments if any
        if email_data['attachments']:
            att_names = [a['filename'] for a in email_data['attachments']]
            formatted_result.append(f"\n\n[Note: Email had {len(att_names)} attachment(s): {', '.join(att_names)}]")
        
        return "\n".join(formatted_result), stats
    
    def _html_to_text(self, html_content):
        """
        Convert HTML to plain text (very basic implementation).
        For production, consider using a proper HTML->text library.
        """
        if not html_content:
            return ""
            
        # Very basic HTML tag removal - just for demonstration
        # In production, use a proper HTML parser like BeautifulSoup
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _limit_quote_depth(self, email_content, max_depth=None):
        """
        Limit the depth of quoted text in an email to improve readability.
        
        Args:
            email_content: The email content to process
            max_depth: Maximum quote depth to preserve (defaults to self.max_quote_depth)
            
        Returns:
            str: Email content with quote depth limited
        """
        if max_depth is None:
            max_depth = self.max_quote_depth
            
        lines = email_content.split('\n')
        result_lines = []
        current_quote_section = []
        in_quote = False
        
        for line in lines:
            # Count quote depth by counting '>' characters at the start
            quote_level = 0
            for char in line:
                if char == '>':
                    quote_level += 1
                elif not char.isspace():
                    break
            
            if quote_level > 0:
                # This is a quoted line
                in_quote = True
                if quote_level <= max_depth:
                    # Keep this line as it's within our depth limit
                    current_quote_section.append(line)
            else:
                # Not a quoted line
                if in_quote:
                    # We just exited a quote section, decide what to do with it
                    if current_quote_section:
                        # Add a separator if keeping quotes
                        if max_depth > 0:
                            result_lines.append("---")
                            result_lines.extend(current_quote_section)
                            result_lines.append("---")
                        # Otherwise discard the quotes
                        current_quote_section = []
                    in_quote = False
                
                # Add the non-quoted line
                result_lines.append(line)
        
        # Handle case where email ends with a quote
        if in_quote and current_quote_section and max_depth > 0:
            result_lines.append("---")
            result_lines.extend(current_quote_section)
            result_lines.append("---")
        
        return '\n'.join(result_lines)
    
    def postprocess_content(self, content, file_path=None):
        """
        Apply final processing after optimization.
        
        Args:
            content: String content to postprocess
            file_path: Optional path to the file (for context)
            
        Returns:
            str: Postprocessed content
        """
        # Clean up the formatted content
        if not content:
            return content
            
        # Ensure proper spacing and remove extra blank lines
        result = re.sub(r'\n{3,}', '\n\n', content.strip())
        
        return result
