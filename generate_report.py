# Report generation functions for Content Optimizer

def generate_report(report_filename: str, stats: dict):
    """
    Generates a detailed markdown report file summarizing the optimization run.

    Args:
        report_filename: The path where the markdown report will be saved.
        stats: A dictionary containing all collected statistics from the run.
               Expected keys include 'timestamp', 'mode', 'input_source', 'source_type',
               'output_file', 'original_chars', 'optimized_chars', 'char_reduction',
               'original_tokens', 'optimized_tokens', 'token_reduction', 'files_processed',
               'files_skipped', 'policy_pages_skipped', 'policy_pages_list',
               'policy_filter_enabled', 'processing_time', 'warnings', 'scan_extensions',
               'scan_ignore_patterns', 'scan_use_gitignore', 'rule_trigger_stats'.
    """
    print_info(f"Generating optimization report: {report_filename}")
    # Prepare source description string for clarity
    source_desc = f"`{stats.get('input_source', 'N/A')}` ({stats.get('source_type', 'N/A')})"

    try:
        with open(report_filename, 'w', encoding='utf-8') as f_rep:
            # --- Report Header ---
            f_rep.write("# Optimization Report\n\n")
            f_rep.write(f"**Run Timestamp:** {stats.get('timestamp', 'N/A')}\n")
            f_rep.write(f"**Optimization Mode:** `{stats.get('mode', 'N/A')}`\n")
            f_rep.write(f"**Input Source:** {source_desc}\n\n")

            # --- Output File Info ---
            f_rep.write("## Output File\n")
            f_rep.write(f"- **Output Path:** `{stats.get('output_file', 'N/A')}`\n\n")

            # --- Scan Config (Only if Directory Scan) ---
            if stats.get('source_type') == 'Directory Scan':
                 f_rep.write("## Scan Configuration\n")
                 f_rep.write(f"- **Included Extensions:** `{stats.get('scan_extensions', 'N/A')}`\n")
                 # Format ignore patterns nicely
                 ignore_pats = stats.get('scan_ignore_patterns', [])
                 ignore_pats_str = ', '.join(f"`{p}`" for p in ignore_pats) if ignore_pats else 'None'
                 f_rep.write(f"- **Ignored Patterns:** {ignore_pats_str}\n")
                 # Indicate if gitignore was used and if the parser was available
                 use_gi = stats.get('scan_use_gitignore', False)
                 gitignore_status = 'Yes' if use_gi else 'No'
                 if use_gi and not GITIGNORE_AVAILABLE:
                     gitignore_status += ' (gitignore-parser unavailable)'
                 f_rep.write(f"- **Used .gitignore:** {gitignore_status}\n\n")

            # --- Overall Optimization Statistics Table ---
            f_rep.write("## Optimization Statistics\n")
            f_rep.write("| Metric           | Original            | Optimized           | Reduction       |\n")
            f_rep.write("|------------------|---------------------|---------------------|----------------|\n")
            # Use format_stat for consistent formatting, align columns using f-string padding
            f_rep.write(f"| Character Count  | {format_stat(stats.get('original_chars', 0)):>18} | {format_stat(stats.get('optimized_chars', 0)):>18} | {format_stat(stats.get('char_reduction', -1)):>14} |\n")
            f_rep.write(f"| Token Count      | {format_stat(stats.get('original_tokens', -1)):>18} | {format_stat(stats.get('optimized_tokens', -1)):>18} | {format_stat(stats.get('token_reduction', -1)):>14} |\n")
            f_rep.write(f"| Files Processed  | {format_stat(stats.get('files_processed', 0)):>18} | {'':<18} | {'':<14} |\n")
            # Conditionally show skipped files and policy pages
            files_skipped = stats.get('files_skipped', 0)
            if files_skipped > 0:
                f_rep.write(f"| Files Skipped    | {format_stat(files_skipped):>18} | {'':<18} | {'':<14} |\n")
            # Check for policy pages skipped specifically
            policy_skipped = stats.get('policy_pages_skipped', 0)
            if policy_skipped > 0:
                f_rep.write(f"| Policy Pages Skipped | {format_stat(policy_skipped):>18} | {'':<18} | {'':<14} |\n")
            proc_time = stats.get('processing_time', 0)
            f_rep.write(f"| Processing Time  | {proc_time:.2f} seconds{' ' * 10} | {'':<18} | {'':<14} |\n\n")

            # --- Optimizations Applied Summary (with corrected category calculation) ---
            f_rep.write("## Optimizations Applied (Summary)\n")

            rule_stats = stats.get("rule_trigger_stats", {})
            total_optimizations = sum(rule_stats.values())
            files_processed = stats.get('files_processed', 0)

            # Mention Repomix-specific parsing if applicable
            if stats.get('source_type') == 'Repomix File':
                # Check if summary was actually removed (could look for a specific stat if needed)
                f_rep.write("- Removed initial `File Summary` section (if present).\n")

            # Overall count and average
            avg_opt_str = ""
            if files_processed > 0 and total_optimizations > 0:
                 avg_opt_str = f" (average {total_optimizations/files_processed:.1f} optimizations per file)"
            f_rep.write(f"- Applied **{total_optimizations:,}** total optimizations across {files_processed} files{avg_opt_str}.\n")

            # Data on character and token reduction (if available and meaningful)
            if stats.get('original_chars', 0) > 0 and stats.get('optimized_chars', 0) >= 0:
                chars_removed = stats['original_chars'] - stats['optimized_chars']
                if chars_removed > 0 and stats.get('char_reduction', -1) > 0: # Only report positive reduction
                    f_rep.write(f"- Removed **{chars_removed:,}** characters, reducing content size by {format_stat(stats['char_reduction'])}.\n")

            if stats.get('original_tokens', -1) > 0 and stats.get('optimized_tokens', -1) >= 0:
                tokens_removed = stats['original_tokens'] - stats['optimized_tokens']
                if tokens_removed > 0 and stats.get('token_reduction', -1) > 0: # Only report positive reduction
                     f_rep.write(f"- Reduced token count by **{tokens_removed:,}** tokens ({format_stat(stats['token_reduction'])}).\n")

            # Mention structural changes if any rules for them exist/triggered
            # This is a placeholder, could be made more specific if rules target structure explicitly
            if any(rule in rule_stats for rule in ["Markdown Horizontal Rule", "Redundant Headers", "Weebly Header Table"]):
                 f_rep.write("- Simplified structure by removing redundant headers, separators, or specific HTML elements.\n")

            # --- Analysis by Optimization Category (Corrected Calculation Logic) ---
            # Define categories based on rule names in optimization_rules.py
            categories = {
                "Metadata/Artifacts": {"Meta Title/URL", "Published Time", "Scraper Warning"},
                "Website Chrome/Nav": {"WP Nav List", "WP Sidebar Sections", "WP Address/Connect Footer",
                                   "General Website Header", "General Website Footer", "WP Slider Nav",
                                   "Weebly Header Table", "Weebly Footer", "Sutton Quaker Dotted Footer",
                                   "Simple Text Nav Menu", "Modal Docs Header"},
                "Prompts/Notices/Forms": {"WP Comment Prompt", "WP Cookie Notice", "Form Content"},
                "Assets/Logos": {"Logo Image Line"},
                "Links/Tracking": {"WP Tracking Pixel", "GitHub Link", "Trailing Nav Links",
                                   "Consecutive Markdown Link List"},
                "Boilerplate/Instructions": {"TryThis Modal Pattern"}, # Only Modal pattern remains here (if applied conditionally)
                "Redundancy/Formatting": {"Excessive Newlines", "Markdown Horizontal Rule", "Redundant Headers",
                                         "Zero Width Space"},
            }

            category_counts = {name: 0 for name in categories}
            category_counts["Other/Uncategorized"] = 0 # Initialize 'Other' explicitly

            # Iterate through the triggered rules and assign counts to categories
            for rule_name, count in rule_stats.items():
                found_category = False
                for cat_name, rule_set in categories.items():
                    if rule_name in rule_set:
                        category_counts[cat_name] += count
                        found_category = True
                        break
                if not found_category:
                    # Add to "Other/Uncategorized" if rule isn't listed above
                    category_counts["Other/Uncategorized"] += count

            # Report counts for each category if non-zero
            if total_optimizations > 0:
                 f_rep.write("\n**Breakdown by Optimization Type:**\n")
                 # Now iterate through the calculated category_counts
                 sorted_categories = sorted(category_counts.items())
                 for cat_name, count in sorted_categories:
                     if count > 0:
                         percentage = (count / total_optimizations) * 100
                         # Use friendly name or fallback to key
                         category_desc = {
                             "Metadata/Artifacts": "Metadata & Scraper Artifacts",
                             "Website Chrome/Nav": "Website Chrome & Navigation",
                             "Prompts/Notices/Forms": "Prompts, Notices & Forms",
                             "Assets/Logos": "Asset & Logo Links",
                             "Links/Tracking": "Redundant Links & Tracking",
                             "Boilerplate/Instructions": "Boilerplate Instructions",
                             "Redundancy/Formatting": "Formatting & Redundancy",
                             "Other/Uncategorized": "Other/Uncategorized"
                         }.get(cat_name, cat_name)
                         f_rep.write(f"- **{category_desc}:** {count:,} instances removed ({percentage:.1f}% of total).\n")
                 f_rep.write("\n")


            # Top optimization rules by trigger count
            if rule_stats:
                # Sort rules by count, descending
                sorted_rules = sorted(rule_stats.items(), key=lambda item: item[1], reverse=True)
                top_n = 3 # Show top 3 most frequent rules
                if sorted_rules:
                    top_rules_text = ", ".join([f"**{rule}** ({count:,})" for rule, count in sorted_rules[:top_n]])
                    f_rep.write(f"- Most frequent optimizations: {top_rules_text}.\n")

            # Policy pages information (if filtering was enabled and pages were skipped)
            if stats.get('policy_filter_enabled', False) and stats.get('policy_pages_skipped', 0) > 0:
                policy_pages = stats['policy_pages_skipped']
                f_rep.write(f"- Excluded **{policy_pages}** potential policy pages (e.g., privacy, terms) based on filter settings.\n")

            # Performance metric
            if proc_time > 0 and stats.get('original_chars', 0) > 0:
                chars_per_second = stats['original_chars'] / proc_time
                f_rep.write(f"- Processing speed: Approximately {chars_per_second:,.0f} characters per second.\n")

            # Mode-specific description
            if stats.get('mode') == 'code':
                f_rep.write("- **Code Mode Active:** Optimization focused on preserving code structure.\n")
            elif stats.get('mode') == 'docs':
                f_rep.write("- **Docs Mode Active:** Optimization focused on retaining descriptive text while removing web elements.\n")

            f_rep.write("\n")

            # --- Add Notion-specific report section if applicable ---
            if stats.get('is_notion_export', False):
                f_rep.write("## Notion Export Processing\n")
                f_rep.write("This content was identified as a Notion.so export and processed accordingly:\n\n")
                f_rep.write("- Notion content IDs were extracted and referenced in the output\n")
                f_rep.write("- Directory and file names were cleaned of Notion IDs for improved readability\n")
                f_rep.write("- Notion-specific artifacts were removed from the content\n")

                # Statistics on found IDs
                notion_ids_count = stats.get('notion_ids_count', 0)
                if notion_ids_count > 0:
                    f_rep.write(f"- **{notion_ids_count}** Notion content IDs were identified and indexed\n\n")

                # If there are specific Notion rule applications, show those
                if "Notion Properties" in stats.get("rule_trigger_stats", {}):
                    f_rep.write("### Notion-Specific Optimizations\n")
                    f_rep.write("| Rule | Count |\n")
                    f_rep.write("|------|------:|\n")
                    for rule_name, count in sorted(stats.get("rule_trigger_stats", {}).items()):
                        if rule_name.startswith("Notion ") and count > 0:
                            f_rep.write(f"| {rule_name} | {count:,} |\n")
                    f_rep.write("\n")

            # --- Detailed Rule Trigger Statistics Table ---
            f_rep.write("## Rule Trigger Statistics\n")
            rule_stats = stats.get("rule_trigger_stats", {})
            # Always generate table to show non-triggered rules from the defined list
            if rule_stats is not None: # Check if rule_stats exists (even if empty)
                # Get all defined rule names for the table
                defined_rule_names_set = set()
                # Check if rules module and list exist before accessing
                if hasattr(rules, 'OPTIMIZATION_RULES_ORDERED') and isinstance(rules.OPTIMIZATION_RULES_ORDERED, list):
                    defined_rule_names_set = {name for name, _ in rules.OPTIMIZATION_RULES_ORDERED}

                # Add rules applied manually/separately if not already in list and pattern exists
                if hasattr(rules, 'EXCESSIVE_NEWLINES_PATTERN') and "Excessive Newlines" not in defined_rule_names_set:
                     defined_rule_names_set.add("Excessive Newlines")

                all_rules_report = {}
                # Populate with counts for defined rules, defaulting to 0
                for name in defined_rule_names_set:
                    all_rules_report[name] = rule_stats.get(name, 0)

                # Add any triggered rules that *aren't* currently defined (helps catch rule file mismatches)
                triggered_rule_names_set = set(rule_stats.keys())
                undefined_triggered = triggered_rule_names_set - defined_rule_names_set
                if undefined_triggered:
                     for rule_name in undefined_triggered:
                          all_rules_report[rule_name] = rule_stats[rule_name] # Add to report
                          # Optionally add a marker? (e.g., "[Undefined]") - skip for now

                # Sort alphabetically for the report table
                sorted_rules_report = sorted(all_rules_report.items())

                f_rep.write("| Rule Name                      | Total Triggers |\n")
                f_rep.write("|--------------------------------|----------------|\n")
                if not sorted_rules_report:
                    f_rep.write("| (No rules defined or triggered) | N/A            |\n")
                else:
                    for rule_name, count in sorted_rules_report:
                        # Add marker if rule was triggered but not defined in current list
                        marker = " *" if rule_name in undefined_triggered else ""
                        f_rep.write(f"| {rule_name:<30}{marker} | {format_stat(count):<14} |\n")
                if undefined_triggered:
                    f_rep.write("\n\\* Triggered rule not found in current `OPTIMIZATION_RULES_ORDERED` list.\n")


            else: # Should not happen if rule_stats is initialized, but as a fallback
                f_rep.write("Rule trigger statistics could not be determined.\n")
            f_rep.write("\n")


            # --- Policy Pages Section (if filtering was active) ---
            if stats.get('policy_filter_enabled', False):
                f_rep.write("## Policy Pages Handling\n")
                f_rep.write(f"- **Policy Filter Enabled:** Yes\n")
                policy_skipped_count = stats.get('policy_pages_skipped', 0)
                f_rep.write(f"- **Policy Pages Skipped/Excluded:** {policy_skipped_count}\n")

                # List the skipped policy pages if any were found
                skipped_list = stats.get('policy_pages_list', [])
                if skipped_list:
                    f_rep.write("\n### Excluded Policy Page Files/Sections\n")
                    # Sort list for consistency
                    for policy_page in sorted(skipped_list):
                        f_rep.write(f"- `{policy_page}`\n")
                elif policy_skipped_count == 0 :
                    f_rep.write("- No files/sections were identified as policy pages during this run.\n")
                f_rep.write("\n")
            else:
                 # Explicitly state if the filter was off
                 f_rep.write("## Policy Pages Handling\n")
                 f_rep.write("- **Policy Filter Enabled:** No\n")
                 f_rep.write("- All files/sections were processed regardless of potential policy content.\n\n")


            # --- Warnings Section ---
            f_rep.write("## Warnings Encountered During Processing\n")
            warnings_list = stats.get('warnings', [])
            if warnings_list:
                for warning in warnings_list:
                    # Format warnings as code blocks for visibility
                    f_rep.write(f"- `{warning}`\n")
            else:
                f_rep.write("None\n")
            f_rep.write("\n")


            # --- Conclusion ---
            f_rep.write("## Conclusion\n")
            # Generate a summary sentence reflecting the success and key outcome
            token_red_str = format_stat(stats.get('token_reduction', -1))
            char_red_str = format_stat(stats.get('char_reduction', -1))
            conclusion_text = f"The script successfully processed the input from {source_desc} in `{stats.get('mode', 'N/A')}` mode."

            reductions = []
            if char_red_str != "N/A" and stats.get('char_reduction', -1) > 0:
                 reductions.append(f"a **{char_red_str}** character reduction")
            if token_red_str != "N/A" and stats.get('token_reduction', -1) > 0:
                 reductions.append(f"a **{token_red_str}** token reduction")

            if reductions:
                 conclusion_text += f" This resulted in { ' and '.join(reductions) }."
            elif stats.get('files_processed', 0) > 0 : # Avoid saying "no reduction" if no files processed
                 conclusion_text += " Optimizations were applied, but overall content size reduction was minimal."
            else:
                 conclusion_text += " No files were processed based on the configuration."


            conclusion_text += f"\nProcessed {stats.get('files_processed', 0)} files/sections in {stats.get('processing_time', 0):.2f} seconds."
            f_rep.write(conclusion_text + "\n")

        print_success("Report generation complete.")
    except IOError as e:
        print_error(f"Failed to write report file '{report_filename}': {e}")
    except Exception as e:
        # Catch other potential errors during report generation
        print_error(f"An unexpected error occurred during report generation: {e}")
        traceback.print_exc()