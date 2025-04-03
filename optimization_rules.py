import re  # Add missing import at the top of the file

# optimization_rules.py
# ... (other rules remain the same) ...

# *** REFINED PATTERN ***
# New: Simple Text Navigation Menu Pattern
# Matches 4 or more consecutive lines, each 1-60 chars long, likely starting capitalized, not ending with sentence punctuation.
SIMPLE_TEXT_NAV_MENU_PATTERN = re.compile(
    r"^(?:(?=.{1,60}$)\s*[A-Z][\w &'-]+(?:\s+[A-Z][\w &'-]+){0,4}(?<![.?!])\s*\n){4,}", # Increased lines to 4, added length limit, negative lookbehind for punctuation
    re.MULTILINE
)

# *** REFINED PATTERN ***
# Updated Form Content Pattern - Made underline optional, less greedy field matching
FORM_CONTENT_PATTERN = re.compile(
    r"(?:^|\n{2,})" # Start of block after blank lines
    # Form Header/Title (Keep this part)
    r"((?:Subscribe|Contact|Sign up|Join|Register|Booking|Enquiry|Get in Touch|Send Message|Newsletter|Email Updates)[\s\w]*?)\n"
    r"(?:[-=]{3,}\s*\n+)?" # Optional Underline

    # Form Body - Match typical form elements non-greedily until a likely end-of-form indicator
    r"(?P<form_body>" # Capture form body for potential later inspection if needed
        r"(?:" # Start of elements group
            # Required field indicator (match non-greedily to newline)
            r"(?:\*\s*indicates required[^\n]*\n+)"
            # Common Form Fields (Match label, then non-greedily consume lines until next known field/marker)
            # Using non-greedy .*? but anchored by lookahead for next field or end marker
            r"|(?:(?:First Name|Last Name|Name|Email|Phone|Address|Message|Comments|Company|Organisation|Subject|Enquiry)[\s\w]*(?:\*|)\s*[:\n].*?\n+(?=(?:(?:First Name|Last Name|Name|Email|Phone|Address|Message|Comments|Company|Organisation|Subject|Enquiry)[\s\w]*(?:\*|)\s*[:\n]|Submit|Send|Register|Subscribe|Book Now|POWERED BY|Sutton Coldfield Quakers\.{3,}|\Z)))"
            # Bot-prevention comment
            r"|(?:/\*.*?real people should not fill this in.*?\*/\s*\n*)"
            # GDPR/Privacy message (non-greedy)
            r"|(?:Your (?:data|privacy|information) is important.*?\n+)"
            r"|(?:.*?unsubscribe.*?(?:bottom of|link in).*?(?:message|email).*?\n+)"
            # Buttons / Submit actions (match line non-greedily)
            r"|(?:(?:Submit|Send|Register|Subscribe|Book Now)[^\n]*\n+)"
            # Catch-all for other potential lines within the form (very non-greedy)
            # r"|(?:\s*.*?\n+)" # Use with caution - may match too much if lookahead fails
        r")+" # Match one or more form elements
    r")", # End of form_body capture group
    re.DOTALL | re.MULTILINE | re.IGNORECASE
)

# --- Notion Export Specific Patterns ---

# Notion ID pattern (32 hex characters, typically preceded by space or underscore)
NOTION_ID_PATTERN = re.compile(r'([^/\\]+?)[ _]([a-f0-9]{32})(?:\.[^/\\]*)?$')

# Notion export dividers (3+ dashes with optional spaces)
NOTION_DIVIDERS_PATTERN = re.compile(r'^---+\s*$', re.MULTILINE)

# Notion export properties block
NOTION_PROPERTIES_PATTERN = re.compile(r'^(?:Property|Properties):\s*\n(?:(?:[^\n]+: [^\n]+\n)+)', re.MULTILINE)

# Notion created/edited timestamps
NOTION_TIMESTAMPS_PATTERN = re.compile(r'^(?:Created|Last Edited)(?:[ :]+).*?\d{4}\s*$', re.MULTILINE)

# Notion URL references
NOTION_URL_PATTERN = re.compile(r'https://www\.notion\.so/[a-f0-9]{32}')

# Notion inline comments (double square brackets with text)
NOTION_COMMENTS_PATTERN = re.compile(r'\[\[([^\]]+)\]\]')

# Notion export citation markers
NOTION_CITATIONS_PATTERN = re.compile(r'\[(\d+)\]\(#cite-[a-f0-9-]+\)')

# ... (rest of the file including OPTIMIZATION_RULES_ORDERED remains the same) ...

# Make sure the refined patterns are used in OPTIMIZATION_RULES_ORDERED
OPTIMIZATION_RULES_ORDERED = [
    # 1. Highly Specific Metadata / Tracking / Prompts / Artifacts (Usually safe)
    ("Scraper Warning", SCRAPER_WARNING_PATTERN),
    ("Published Time", PUBLISHED_TIME_PATTERN),
    ("WP Tracking Pixel", WP_TRACKING_PIXEL_PATTERN),
    ("Meta Title/URL", META_TITLE_URL_PATTERN),
    ("WP Comment Prompt", WP_COMMENT_PROMPT_PATTERN),
    ("WP Cookie Notice", WP_COOKIE_NOTICE_PATTERN),
    ("Form Content", FORM_CONTENT_PATTERN),               # *** Using REFINED pattern ***
    ("GitHub Link", GITHUB_LINK_PATTERN),
    ("Redundant Headers", REDUNDANT_HEADERS_PATTERN),

    # 2. Specific Structural Elements / Platform Boilerplate (Known sources/formats)
    ("Weebly Header Table", WEEBLY_HEADER_TABLE_PATTERN),
    ("Modal Docs Header", MODAL_DOCS_HEADER_PATTERN),
    ("WP Nav List", WP_NAV_LIST_PATTERN),
    ("WP Sidebar Sections", WP_SIDEBAR_SECTIONS_PATTERN),
    ("WP Slider Nav", WP_SLIDER_NAV_PATTERN),
    ("Consecutive Markdown Link List", CONSECUTIVE_LINK_LIST_PATTERN),

    # 3. Common Assets / Less Specific Structural (Logos, Separators, Footers)
    ("Logo Image Line", LOGO_IMAGE_LINE_PATTERN),
    ("Markdown Horizontal Rule", MARKDOWN_HORIZONTAL_RULE_PATTERN),
    ("Sutton Quaker Dotted Footer", SUTTON_QUAKER_DOTTED_FOOTER_PATTERN),
    ("Weebly Footer", WEEBLY_FOOTER_PATTERN),
    ("WP Address/Connect Footer", WP_ADDRESS_CONNECT_FOOTER_PATTERN),

    # 4. General Website Chrome / Navigation (Broader patterns, apply later)
    ("Trailing Nav Links", TRAILING_NAV_LINKS_PATTERN),
    ("Simple Text Nav Menu", SIMPLE_TEXT_NAV_MENU_PATTERN), # *** Using REFINED pattern ***
    ("General Website Header", WEBSITE_HEADER_PATTERN),
    ("General Website Footer", WEBSITE_FOOTER_PATTERN),

    # 5. Final Formatting Cleanup (Applied last in this list or separately)
    ("Zero Width Space", ZERO_WIDTH_SPACE_PATTERN),
]

# Add the Notion rules to the ordered list, but only apply when in notion mode
NOTION_SPECIFIC_RULES = [
    ("Notion Dividers", NOTION_DIVIDERS_PATTERN),
    ("Notion Properties", NOTION_PROPERTIES_PATTERN),
    ("Notion Timestamps", NOTION_TIMESTAMPS_PATTERN),
    ("Notion URLs", NOTION_URL_PATTERN),
    ("Notion Comments", NOTION_COMMENTS_PATTERN),
    ("Notion Citations", NOTION_CITATIONS_PATTERN),
]