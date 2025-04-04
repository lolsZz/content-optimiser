"""
Report generation module for Content Optimizer

This module provides enhanced report generation capabilities, creating detailed
markdown reports with statistics, visualizations, and analysis of optimizations.
"""

import os
import sys
from datetime import datetime
from collections import defaultdict

# Check for optional dependencies for enhanced reports
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

def format_stat(value):
    """Formats statistics (numbers, percentages, N/A) for display in the report."""
    if value is None:
        return "N/A"
    elif value == -1:
        return "N/A"
    elif isinstance(value, float):
        return f"{value:.2f}%"
    else:
        try:
            return f"{value:,}"
        except (ValueError, TypeError):
            return str(value)

def generate_report(report_filename: str, stats: dict):
    """
    Generates a detailed markdown report file summarizing the optimization run.

    Args:
        report_filename: The path where the markdown report will be saved.
        stats: A dictionary containing all collected statistics from the run.
    """
    print(f"Generating optimization report: {report_filename}")
    
    # Prepare source description string for clarity
    source_desc = f"`{stats.get('input_source', 'N/A')}` ({stats.get('source_type', 'N/A')})"

    try:
        # Ensure report directory exists
        report_dir = os.path.dirname(report_filename)
        if report_dir and not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            # --- Report Header ---
            f.write("# Content Optimization Report\n\n")
            f.write(f"**Run Timestamp:** {stats.get('timestamp', 'N/A')}\n")
            f.write(f"**Optimization Mode:** `{stats.get('mode', 'N/A')}`\n")
            f.write(f"**Input Source:** {source_desc}\n\n")

            # --- Output File Info ---
            f.write("## Output File\n")
            f.write(f"- **Output Path:** `{stats.get('output_file', 'N/A')}`\n\n")

            # --- Scan Config (Only if Directory Scan) ---
            if stats.get('source_type') == 'Directory Scan':
                f.write("## Scan Configuration\n")
                f.write(f"- **Included Extensions:** `{stats.get('scan_extensions', 'N/A')}`\n")
                # Format ignore patterns nicely
                ignore_pats = stats.get('scan_ignore_patterns', [])
                ignore_pats_str = ', '.join(f"`{p}`" for p in ignore_pats) if ignore_pats else 'None'
                f.write(f"- **Ignored Patterns:** {ignore_pats_str}\n")
                # Indicate if gitignore was used and if the parser was available
                use_gi = stats.get('scan_use_gitignore', False)
                gitignore_status = 'Yes' if use_gi else 'No'
                if use_gi and not stats.get('GITIGNORE_AVAILABLE', True) == False:
                    gitignore_status += ' (gitignore-parser unavailable)'
                f.write(f"- **Used .gitignore:** {gitignore_status}\n\n")

            # --- Content Type Detection Results (if auto mode) ---
            if stats.get('mode') == 'auto' and stats.get('detected_types'):
                f.write("## Content Type Detection\n")
                f.write("| Content Type | Files | Percentage |\n")
                f.write("|-------------|------:|-----------:|\n")
                
                detected_types = stats.get('detected_types', {})
                total_files = sum(detected_types.values())
                
                for content_type, count in sorted(detected_types.items()):
                    percentage = (count / total_files * 100) if total_files > 0 else 0
                    f.write(f"| {content_type} | {count} | {percentage:.1f}% |\n")
                f.write("\n")

            # --- Overall Optimization Statistics Table ---
            f.write("## Optimization Statistics\n")
            f.write("| Metric | Original | Optimized | Reduction |\n")
            f.write("|--------|----------|-----------|----------|\n")
            f.write(f"| Character Count | {format_stat(stats.get('original_chars', 0))} | {format_stat(stats.get('optimized_chars', 0))} | {format_stat(stats.get('char_reduction', -1))} |\n")
            f.write(f"| Token Count | {format_stat(stats.get('original_tokens', -1))} | {format_stat(stats.get('optimized_tokens', -1))} | {format_stat(stats.get('token_reduction', -1))} |\n")
            f.write(f"| Files Processed | {format_stat(stats.get('files_processed', 0))} | | |\n")
            
            # Conditionally show skipped files and policy pages
            files_skipped = stats.get('files_skipped', 0)
            if files_skipped > 0:
                f.write(f"| Files Skipped | {format_stat(files_skipped)} | | |\n")
            
            policy_skipped = stats.get('policy_pages_skipped', 0)
            if policy_skipped > 0:
                f.write(f"| Policy Pages Skipped | {format_stat(policy_skipped)} | | |\n")
            
            proc_time = stats.get('processing_time', 0)
            f.write(f"| Processing Time | {proc_time:.2f} seconds | | |\n\n")

            # --- Processing Speed and Performance ---
            f.write("## Processing Performance\n")
            
            # Calculate and display processing speed metrics
            chars_per_second = "N/A"
            files_per_second = "N/A"
            
            if proc_time > 0:
                if stats.get('original_chars', 0) > 0:
                    chars_per_second = stats.get('original_chars', 0) / proc_time
                    f.write(f"- **Processing Speed:** {chars_per_second:,.0f} characters per second\n")
                
                if stats.get('files_processed', 0) > 0:
                    files_per_second = stats.get('files_processed', 0) / proc_time
                    f.write(f"- **File Processing Rate:** {files_per_second:.2f} files per second\n")
            
            # Token processing information if available
            if TIKTOKEN_AVAILABLE and stats.get('original_tokens', -1) > 0:
                f.write(f"- **Token Processing Rate:** {stats.get('original_tokens', 0) / proc_time:,.0f} tokens per second\n")
            
            # Size reduction visual indicator using markdown
            if stats.get('char_reduction', -1) > 0:
                reduction_percentage = stats.get('char_reduction', 0)
                reduction_blocks = min(int(reduction_percentage / 5), 20)  # Max 20 blocks
                reduction_visual = "▓" * reduction_blocks + "░" * (20 - reduction_blocks)
                f.write(f"\n**Size Reduction:** {reduction_visual} ({reduction_percentage:.1f}%)\n\n")
            else:
                f.write("\n**Size Reduction:** None or minimal\n\n")

            # --- Optimizations Applied Summary ---
            f.write("## Optimizations Applied\n")
            
            rule_stats = stats.get("rule_trigger_stats", {})
            aggregated_stats = stats.get("aggregated_stats", {})
            total_optimizations = sum(rule_stats.values())
            files_processed = stats.get('files_processed', 0)

            # Overall count and average
            avg_opt_str = ""
            if files_processed > 0 and total_optimizations > 0:
                avg_opt_str = f" (average {total_optimizations/files_processed:.1f} optimizations per file)"
            f.write(f"- Applied **{total_optimizations:,}** total optimizations across {files_processed} files{avg_opt_str}.\n")

            # Data on character and token reduction (if available and meaningful)
            if stats.get('original_chars', 0) > 0 and stats.get('optimized_chars', 0) >= 0:
                chars_removed = stats['original_chars'] - stats['optimized_chars']
                if chars_removed > 0 and stats.get('char_reduction', -1) > 0:
                    f.write(f"- Removed **{chars_removed:,}** characters, reducing content size by {format_stat(stats['char_reduction'])}.\n")

            if stats.get('original_tokens', -1) > 0 and stats.get('optimized_tokens', -1) >= 0:
                tokens_removed = stats['original_tokens'] - stats['optimized_tokens']
                if tokens_removed > 0 and stats.get('token_reduction', -1) > 0:
                    f.write(f"- Reduced token count by **{tokens_removed:,}** tokens ({format_stat(stats['token_reduction'])}).\n")

            # Show mode-specific information
            mode = stats.get('mode', 'N/A')
            if mode == 'code':
                f.write("- **Code Mode Active:** Optimization focused on preserving code structure while removing non-essential elements.\n")
            elif mode == 'docs':
                f.write("- **Docs Mode Active:** Optimization focused on retaining descriptive text while removing web elements and boilerplate.\n")
            elif mode == 'notion':
                f.write("- **Notion Mode Active:** Specialized handling for Notion.so exports, preserving content while cleaning export artifacts.\n")
            elif mode == 'email':
                f.write("- **Email Mode Active:** Optimized for email content, cleaning up signatures, quotes, and metadata.\n")
            elif mode == 'markdown':
                f.write("- **Markdown Mode Active:** Enhanced handling of Markdown and HTML content, preserving structure while removing clutter.\n")
            elif mode == 'auto':
                f.write("- **Auto Mode Active:** Content types detected and optimized with specialized helpers.\n")

            # --- Detailed Optimization Categories ---
            if rule_stats:
                f.write("\n### Optimization Categories\n")
                
                # Define categories based on rule names
                categories = {
                    "Metadata & Headers": ["Meta Title/URL", "Published Time", "Modal Docs Header"],
                    "Navigation & Structure": ["WP Nav List", "Simple Text Nav Menu", "Consecutive Markdown Link List", "Trailing Nav Links"],
                    "Website Elements": ["WP Sidebar Sections", "Weebly Header Table", "Weebly Footer", "General Website Header", "General Website Footer"],
                    "Forms & Interactions": ["Form Content", "Subscription Form", "Enhanced Form Content", "Erdington Baths Form"],
                    "Tracking & Prompts": ["WP Tracking Pixel", "WP Comment Prompt", "WP Cookie Notice", "Scraper Warning"],
                    "Redundant Content": ["Duplicate Headings", "Redundant Headers"],
                    "Assets & Links": ["Logo Image Line", "GitHub Link"],
                    "Formatting & Styling": ["Markdown Horizontal Rule", "Zero Width Space"],
                    "Notion-specific": ["Notion Dividers", "Notion Properties", "Notion Timestamps", "Notion URLs", "Notion Comments", "Notion Citations"]
                }
                
                # Count optimizations by category
                category_counts = defaultdict(int)
                uncategorized = []
                
                for rule, count in rule_stats.items():
                    found_category = False
                    for category, rules in categories.items():
                        if rule in rules:
                            category_counts[category] += count
                            found_category = True
                            break
                    
                    if not found_category:
                        category_counts["Other"] += count
                        uncategorized.append(rule)
                
                # Display category breakdown with percentages
                f.write("| Category | Optimizations | Percentage |\n")
                f.write("|----------|-------------:|-----------:|\n")
                
                for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_optimizations * 100) if total_optimizations > 0 else 0
                    f.write(f"| {category} | {count:,} | {percentage:.1f}% |\n")
                
                # List uncategorized rules if any
                if uncategorized and category_counts["Other"] > 0:
                    f.write("\n**Other Optimizations:** ")
                    f.write(", ".join(uncategorized))
                    f.write("\n")

            # --- Top Optimization Rules ---
            if rule_stats:
                # Sort rules by count, descending
                sorted_rules = sorted(rule_stats.items(), key=lambda item: item[1], reverse=True)
                
                f.write("\n### Top Optimization Rules\n")
                f.write("| Rule | Count | Percentage |\n")
                f.write("|------|------:|-----------:|\n")
                
                # Show top 10 rules or all if fewer
                top_n = min(10, len(sorted_rules))
                for rule, count in sorted_rules[:top_n]:
                    percentage = (count / total_optimizations * 100) if total_optimizations > 0 else 0
                    f.write(f"| {rule} | {count:,} | {percentage:.1f}% |\n")
                
            # --- Full Rule Stats Table ---
            if rule_stats:
                f.write("\n### All Rules Applied\n")
                f.write("| Rule | Count |\n")
                f.write("|------|------:|\n")
                
                for rule, count in sorted(rule_stats.items()):
                    if count > 0:
                        f.write(f"| {rule} | {count:,} |\n")
                    
                f.write("\n")

            # --- Policy Pages Section ---
            if stats.get('policy_filter_enabled', False):
                f.write("## Policy Pages Handling\n")
                policy_skipped_count = stats.get('policy_pages_skipped', 0)
                
                f.write(f"- **Policy Filter:** Enabled\n")
                f.write(f"- **Pages Excluded:** {policy_skipped_count}\n")
                
                skipped_list = stats.get('policy_pages_list', [])
                if skipped_list:
                    f.write("\n### Excluded Policy Pages\n")
                    for policy_page in sorted(skipped_list):
                        f.write(f"- `{policy_page}`\n")
                f.write("\n")
            else:
                f.write("## Policy Pages Handling\n")
                f.write("- **Policy Filter:** Disabled\n")
                f.write("- All pages were processed regardless of potential policy content.\n\n")

            # --- Notion-specific Reporting (if relevant) ---
            if stats.get('mode') == 'notion' or 'notion_ids_count' in stats.get('helper_specific_data', {}):
                f.write("## Notion Export Processing\n")
                
                notion_stats = stats.get('helper_specific_data', {})
                
                f.write("- **Notion IDs Found:** ")
                f.write(f"{notion_stats.get('notion_ids_count', 0):,}\n")
                
                f.write("- **Files Cleaned:** ")
                f.write(f"{notion_stats.get('cleaned_files', 0):,}\n")
                
                f.write("- **Properties Converted:** ")
                f.write(f"{notion_stats.get('properties_converted', 0):,}\n")
                
                # List specific Notion optimizations if available
                if any(rule.startswith('Notion ') for rule in rule_stats.keys()):
                    f.write("\n### Notion-specific Optimizations\n")
                    f.write("| Rule | Count |\n")
                    f.write("|------|------:|\n")
                    
                    for rule, count in sorted(rule_stats.items()):
                        if rule.startswith('Notion ') and count > 0:
                            f.write(f"| {rule} | {count:,} |\n")
                f.write("\n")

            # --- Warnings and Issues ---
            f.write("## Warnings and Issues\n")
            warnings_list = stats.get('warnings', [])
            
            if warnings_list:
                for warning in warnings_list:
                    f.write(f"- `{warning}`\n")
            else:
                f.write("None\n")
            f.write("\n")

            # --- Conclusion ---
            f.write("## Conclusion\n")
            
            # Generate a contextual conclusion based on results
            token_red_str = format_stat(stats.get('token_reduction', -1))
            char_red_str = format_stat(stats.get('char_reduction', -1))
            
            conclusion = f"The optimization process successfully processed content from {source_desc} "
            conclusion += f"using `{stats.get('mode', 'N/A')}` mode. "
            
            if stats.get('files_processed', 0) > 0:
                conclusion += f"A total of {stats.get('files_processed', 0):,} files were processed"
                
                if total_optimizations > 0:
                    conclusion += f", applying {total_optimizations:,} optimizations"
                
                conclusion += ". "
            
            # Add reduction information if available
            char_reduction = stats.get('char_reduction', -1)
            token_reduction = stats.get('token_reduction', -1)
            
            if char_reduction > 0 or token_reduction > 0:
                conclusion += "The optimization achieved "
                
                if char_reduction > 0:
                    conclusion += f"a {char_red_str} reduction in character count"
                    
                    if token_reduction > 0:
                        conclusion += f" and a {token_red_str} reduction in token count"
                elif token_reduction > 0:
                    conclusion += f"a {token_red_str} reduction in token count"
                
                conclusion += ", "
                
                # Add benefit statement
                if char_reduction > 30 or token_reduction > 30:
                    conclusion += "significantly improving the signal-to-noise ratio for LLM processing."
                elif char_reduction > 15 or token_reduction > 15:
                    conclusion += "meaningfully improving content quality for LLM processing."
                else:
                    conclusion += "helping to improve content quality for LLM processing."
            else:
                conclusion += "While optimizations were applied, the overall content reduction was minimal, "
                conclusion += "suggesting the content may already have been well-optimized or consisted primarily of essential information."
            
            f.write(conclusion + "\n\n")
            
            # Add recommendation based on results
            f.write("### Recommendation\n")
            
            if char_reduction > 25 or token_reduction > 25:
                f.write("The significant content reduction suggests that using this optimized content will likely lead to:")
                f.write("\n- More focused LLM responses")
                f.write("\n- Lower token usage and associated costs")
                f.write("\n- Improved context window utilization")
            elif char_reduction > 10 or token_reduction > 10:
                f.write("The moderate content reduction suggests this optimized content should provide:")
                f.write("\n- Somewhat improved LLM response quality")
                f.write("\n- Modest token usage savings")
            else:
                f.write("The minimal content reduction suggests:")
                f.write("\n- The original content was already well-optimized")
                f.write("\n- You may want to try a different optimization mode if further reduction is desired")
                f.write("\n- Manual review might identify additional optimization opportunities")
            
            # Add report generation timestamp
            f.write(f"\n\n---\n*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            
        print(f"Report generated: {report_filename}")
        return True
        
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return False
