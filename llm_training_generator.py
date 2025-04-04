"""
LLM Training Data Generator for Content Optimizer

This module extends the Content Optimizer to generate high-quality training data
for Large Language Models (LLMs) in various formats, including instruction tuning,
conversation pairs, and fine-tuning datasets.

The generator takes optimized content and transforms it into structured data formats
suitable for training or fine-tuning LLMs.
"""

import os
import json
import csv
import random
import re
from typing import Dict, List, Tuple, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import yaml

# Check for optional dependencies
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    from datasets import Dataset
    HF_DATASETS_AVAILABLE = True
except ImportError:
    HF_DATASETS_AVAILABLE = False

# Constants for dataset formats
FORMAT_INSTRUCTION = "instruction"
FORMAT_CONVERSATION = "conversation"
FORMAT_COMPLETION = "completion"
FORMAT_QA = "question-answer"
FORMAT_GENERAL = "general"

SUPPORTED_FORMATS = [
    FORMAT_INSTRUCTION,
    FORMAT_CONVERSATION,
    FORMAT_COMPLETION,
    FORMAT_QA,
    FORMAT_GENERAL
]

# Output formats
OUTPUT_JSONL = "jsonl"
OUTPUT_CSV = "csv"
OUTPUT_PARQUET = "parquet"
OUTPUT_HF_DATASET = "hf_dataset"

SUPPORTED_OUTPUT_FORMATS = [
    OUTPUT_JSONL,
    OUTPUT_CSV
]

if PANDAS_AVAILABLE:
    SUPPORTED_OUTPUT_FORMATS.append(OUTPUT_PARQUET)

if HF_DATASETS_AVAILABLE:
    SUPPORTED_OUTPUT_FORMATS.append(OUTPUT_HF_DATASET)

# Templates for different data formats
INSTRUCTION_TEMPLATE = {
    "instruction": "",
    "input": "",
    "output": ""
}

CONVERSATION_TEMPLATE = {
    "messages": []
}

COMPLETION_TEMPLATE = {
    "prompt": "",
    "completion": ""
}

QA_TEMPLATE = {
    "question": "",
    "answer": ""
}

class LLMTrainingDataGenerator:
    """
    Generator for creating training data for Large Language Models from optimized content.
    
    This class provides functionality to:
    1. Parse optimized content from Content Optimizer
    2. Transform it into structured training data
    3. Export it in various formats suitable for LLM training
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the LLM Training Data Generator with optional configuration.
        
        Args:
            config: Configuration dictionary with options for data generation
        """
        self.config = config or {}
        self.data_format = self.config.get("data_format", FORMAT_INSTRUCTION)
        self.output_format = self.config.get("output_format", OUTPUT_JSONL)
        self.max_examples = self.config.get("max_examples", 10000)
        self.min_token_count = self.config.get("min_token_count", 50)
        self.max_token_count = self.config.get("max_token_count", 1024)
        self.include_metadata = self.config.get("include_metadata", True)
        self.split_sections = self.config.get("split_sections", True)
        self.separator = self.config.get("separator", "================================================================")
        self.verbose = self.config.get("verbose", True)
        
        # Initialize statistics tracking
        self.stats = {
            "examples_generated": 0,
            "examples_filtered": 0,
            "total_tokens": 0,
            "avg_tokens_per_example": 0,
            "data_formats": {},
            "categories": {}
        }
        
        # For token counting
        if TIKTOKEN_AVAILABLE:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        else:
            self.tokenizer = None
            if self.verbose:
                print("Warning: tiktoken not available. Token counts will be estimated.")
    
    def generate_from_file(self, input_file: str, output_path: str = None) -> str:
        """
        Generate training data from an optimized content file.
        
        Args:
            input_file: Path to the optimized content file
            output_path: Directory to save the generated data (default: same as input)
            
        Returns:
            Path to the generated data file
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Determine output path and filename
        if output_path is None:
            output_dir = os.path.dirname(input_file)
            output_name = f"{os.path.splitext(os.path.basename(input_file))[0]}-training-data"
        else:
            output_dir = output_path
            output_name = f"{os.path.splitext(os.path.basename(input_file))[0]}-training-data"
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Read optimized content
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate training data
        examples = self.generate_from_content(content)
        
        # Save the data
        output_file = self._save_examples(examples, output_dir, output_name)
        
        if self.verbose:
            print(f"Generated {len(examples)} training examples in {output_file}")
            
        return output_file
    
    def generate_from_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Generate training examples from optimized content.
        
        Args:
            content: The optimized content text
            
        Returns:
            List of training examples in the specified format
        """
        # Reset statistics
        self.stats = {
            "examples_generated": 0,
            "examples_filtered": 0,
            "total_tokens": 0,
            "avg_tokens_per_example": 0,
            "data_formats": {},
            "categories": {}
        }
        
        # Parse content into sections
        sections = self._parse_sections(content)
        
        # Generate examples from sections
        examples = []
        
        for section in sections:
            new_examples = self._generate_examples_from_section(section)
            examples.extend(new_examples)
            
            # Update statistics
            self.stats["examples_generated"] += len(new_examples)
        
        # Apply token filtering
        filtered_examples = []
        for example in examples:
            token_count = self._count_tokens(example)
            if self.min_token_count <= token_count <= self.max_token_count:
                filtered_examples.append(example)
                self.stats["total_tokens"] += token_count
            else:
                self.stats["examples_filtered"] += 1
        
        # Update final stats
        if filtered_examples:
            self.stats["avg_tokens_per_example"] = self.stats["total_tokens"] / len(filtered_examples)
        
        # Limit to max examples if specified
        if self.max_examples and len(filtered_examples) > self.max_examples:
            filtered_examples = filtered_examples[:self.max_examples]
        
        return filtered_examples
    
    def _parse_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Parse the content into sections for example generation.
        
        Args:
            content: The full optimized content
            
        Returns:
            List of content sections with metadata
        """
        sections = []
        
        # Check if content has the standard format with separators
        if self.separator in content:
            # Split by the separator
            raw_sections = content.split(self.separator)
            
            # Process each section
            current_section = {"content": "", "type": "unknown", "metadata": {}}
            
            for i, section in enumerate(raw_sections):
                section = section.strip()
                if not section:
                    continue
                
                # Check if this is a header section
                if i == 0 and "Repository Snapshot" in section:
                    current_section["type"] = "header"
                    current_section["content"] = section
                    sections.append(current_section)
                    current_section = {"content": "", "type": "unknown", "metadata": {}}
                
                # Check if this is a directory structure section
                elif "Directory Structure" in section or "```" in section and "└──" in section:
                    current_section["type"] = "directory"
                    current_section["content"] = section
                    sections.append(current_section)
                    current_section = {"content": "", "type": "unknown", "metadata": {}}
                
                # Otherwise, it's a file content section
                elif "--- FILE:" in section:
                    # Extract file path and content
                    file_marker_match = re.search(r"--- FILE: (.*?) ---", section)
                    if file_marker_match:
                        file_path = file_marker_match.group(1).strip()
                        content_part = section.split("--- FILE: " + file_path + " ---", 1)[-1].strip()
                        
                        current_section["type"] = "file"
                        current_section["content"] = content_part
                        current_section["metadata"]["file_path"] = file_path
                        
                        # Try to determine file type from extension
                        extension = os.path.splitext(file_path)[1].lower()
                        if extension:
                            current_section["metadata"]["file_type"] = extension[1:]  # Remove the dot
                        
                        sections.append(current_section)
                        current_section = {"content": "", "type": "unknown", "metadata": {}}
            
        else:
            # If no separator found, treat the entire content as one section
            sections.append({
                "type": "content",
                "content": content,
                "metadata": {}
            })
        
        return sections
    
    def _generate_examples_from_section(self, section: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Generate training examples from a content section.
        
        Args:
            section: Dictionary containing content and metadata
            
        Returns:
            List of generated examples for this section
        """
        examples = []
        
        # Skip header and directory sections for now as they contain less valuable training data
        if section["type"] in ["header", "directory"]:
            return examples
        
        # Generate based on the data format
        if self.data_format == FORMAT_INSTRUCTION:
            examples.extend(self._generate_instruction_examples(section))
        elif self.data_format == FORMAT_CONVERSATION:
            examples.extend(self._generate_conversation_examples(section))
        elif self.data_format == FORMAT_COMPLETION:
            examples.extend(self._generate_completion_examples(section))
        elif self.data_format == FORMAT_QA:
            examples.extend(self._generate_qa_examples(section))
        elif self.data_format == FORMAT_GENERAL:
            examples.extend(self._generate_general_examples(section))
        
        return examples
    
    def _generate_instruction_examples(self, section: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Generate instruction-tuning style examples.
        
        Args:
            section: Content section with metadata
            
        Returns:
            List of instruction-tuning examples
        """
        examples = []
        content = section["content"]
        
        # For file sections, create instructions based on file type and content
        if section["type"] == "file" and "file_path" in section["metadata"]:
            file_path = section["metadata"]["file_path"]
            file_type = section.get("metadata", {}).get("file_type", "")
            
            # Create example for file content summarization
            example = INSTRUCTION_TEMPLATE.copy()
            example["instruction"] = f"Summarize the key points in this {file_type} file"
            example["input"] = content[:min(len(content), 4000)]  # Limit input size
            
            # Generate a summary response
            summary = self._generate_summary(content, max_length=200)
            example["output"] = summary
            
            if self.include_metadata:
                example["metadata"] = {
                    "source_type": "file",
                    "file_path": file_path,
                    "file_type": file_type,
                    "task": "summarization"
                }
            
            examples.append(example)
            
            # For code files, add example for code explanation
            if file_type in ["py", "js", "java", "cpp", "c", "ts", "go", "rb", "php"]:
                example = INSTRUCTION_TEMPLATE.copy()
                example["instruction"] = f"Explain what this {file_type} code does and its main components"
                example["input"] = content[:min(len(content), 4000)]
                
                # Generate code explanation
                explanation = self._generate_code_explanation(content, file_type)
                example["output"] = explanation
                
                if self.include_metadata:
                    example["metadata"] = {
                        "source_type": "file",
                        "file_path": file_path,
                        "file_type": file_type,
                        "task": "code_explanation"
                    }
                
                examples.append(example)
            
            # For markdown or text files, extract potential Q&A pairs
            if file_type in ["md", "txt", "markdown"]:
                qa_pairs = self._extract_qa_pairs(content)
                for q, a in qa_pairs:
                    example = INSTRUCTION_TEMPLATE.copy()
                    example["instruction"] = q
                    example["input"] = ""
                    example["output"] = a
                    
                    if self.include_metadata:
                        example["metadata"] = {
                            "source_type": "file",
                            "file_path": file_path,
                            "file_type": file_type,
                            "task": "qa"
                        }
                    
                    examples.append(example)
        
        # Add general examples based on content structure
        if len(content.split("\n\n")) > 1:
            paragraphs = content.split("\n\n")
            
            # Create an example with a paragraph continuation task
            for i in range(min(5, len(paragraphs) - 1)):
                if len(paragraphs[i]) < 30 or len(paragraphs[i+1]) < 30:
                    continue
                    
                example = INSTRUCTION_TEMPLATE.copy()
                example["instruction"] = "Continue the text with a relevant paragraph"
                example["input"] = paragraphs[i]
                example["output"] = paragraphs[i+1]
                
                if self.include_metadata:
                    example["metadata"] = {
                        "source_type": section["type"],
                        "task": "paragraph_continuation"
                    }
                    
                examples.append(example)
        
        # Update statistics
        self.stats["data_formats"][FORMAT_INSTRUCTION] = self.stats["data_formats"].get(FORMAT_INSTRUCTION, 0) + len(examples)
        
        return examples
    
    def _generate_conversation_examples(self, section: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Generate conversation-style training examples.
        
        Args:
            section: Content section with metadata
            
        Returns:
            List of conversation examples
        """
        examples = []
        content = section["content"]
        
        # For file sections, create a conversational Q&A about the content
        if section["type"] == "file" and "file_path" in section["metadata"]:
            file_path = section["metadata"]["file_path"]
            file_type = section.get("metadata", {}).get("file_type", "")
            
            # Create an initial conversation example
            example = CONVERSATION_TEMPLATE.copy()
            example["messages"] = [
                {"role": "system", "content": "You are a helpful assistant that provides information about files and their contents."},
                {"role": "user", "content": f"What can you tell me about this {file_type} file: {file_path}?"}
            ]
            
            # Generate a response based on the file content
            summary = self._generate_summary(content, max_length=300)
            example["messages"].append({"role": "assistant", "content": summary})
            
            # Add a follow-up question and response
            if file_type in ["py", "js", "java", "cpp", "c", "ts", "go", "rb", "php"]:
                example["messages"].append({"role": "user", "content": "What are the main functions or classes in this file?"})
                functions = self._extract_functions_and_classes(content, file_type)
                example["messages"].append({"role": "assistant", "content": functions})
            else:
                example["messages"].append({"role": "user", "content": "What are the key topics or sections in this file?"})
                topics = self._extract_topics(content)
                example["messages"].append({"role": "assistant", "content": topics})
            
            if self.include_metadata:
                example["metadata"] = {
                    "source_type": "file",
                    "file_path": file_path,
                    "file_type": file_type,
                    "turns": len(example["messages"]) // 2
                }
            
            examples.append(example)
            
            # For markdown files with headings, create a conversation about the content structure
            if file_type in ["md", "markdown"] and "# " in content:
                example = CONVERSATION_TEMPLATE.copy()
                example["messages"] = [
                    {"role": "system", "content": "You are a helpful assistant that guides users through document content."},
                    {"role": "user", "content": f"Can you show me the structure of this document: {file_path}?"}
                ]
                
                # Extract and format headings
                headings = self._extract_headings(content)
                headings_text = "Here's the document structure:\n\n" + "\n".join(headings)
                example["messages"].append({"role": "assistant", "content": headings_text})
                
                # Add follow-up interaction
                if headings:
                    example["messages"].append({"role": "user", "content": f"Tell me more about the '{headings[0]}' section"})
                    section_content = self._extract_section_content(content, headings[0])
                    example["messages"].append({"role": "assistant", "content": section_content})
                
                if self.include_metadata:
                    example["metadata"] = {
                        "source_type": "file",
                        "file_path": file_path,
                        "file_type": file_type,
                        "turns": len(example["messages"]) // 2
                    }
                
                examples.append(example)
        
        # Update statistics
        self.stats["data_formats"][FORMAT_CONVERSATION] = self.stats["data_formats"].get(FORMAT_CONVERSATION, 0) + len(examples)
        
        return examples
    
    def _generate_completion_examples(self, section: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Generate completion-style training examples.
        
        Args:
            section: Content section with metadata
            
        Returns:
            List of completion examples
        """
        examples = []
        content = section["content"]
        
        # For code files, create code completion examples
        if section["type"] == "file" and "file_path" in section["metadata"]:
            file_path = section["metadata"]["file_path"]
            file_type = section.get("metadata", {}).get("file_type", "")
            
            if file_type in ["py", "js", "java", "cpp", "c", "ts", "go", "rb", "php"]:
                # Split code into chunks for completing functions, classes, etc.
                chunks = self._split_code_into_chunks(content, file_type)
                
                for i, (prompt, completion) in enumerate(chunks):
                    if not prompt or not completion:
                        continue
                        
                    example = COMPLETION_TEMPLATE.copy()
                    example["prompt"] = prompt
                    example["completion"] = completion
                    
                    if self.include_metadata:
                        example["metadata"] = {
                            "source_type": "file",
                            "file_path": file_path,
                            "file_type": file_type,
                            "chunk_index": i
                        }
                    
                    examples.append(example)
        
        # For text content, create sentence/paragraph completion examples
        elif section["type"] in ["content", "file"] and len(content) > 100:
            # Split into paragraphs and create completion examples
            paragraphs = content.split("\n\n")
            
            for i in range(len(paragraphs) - 1):
                if len(paragraphs[i]) < 30:
                    continue
                    
                # Create examples with varying amounts of completion text
                sentences = re.split(r'(?<=[.!?])\s+', paragraphs[i])
                
                if len(sentences) > 3:
                    prompt_text = " ".join(sentences[:-2])
                    completion_text = " ".join(sentences[-2:])
                    
                    example = COMPLETION_TEMPLATE.copy()
                    example["prompt"] = prompt_text
                    example["completion"] = completion_text
                    
                    if self.include_metadata:
                        example["metadata"] = {
                            "source_type": section["type"],
                            "paragraph_index": i,
                            "completion_type": "sentence"
                        }
                    
                    examples.append(example)
        
        # Update statistics
        self.stats["data_formats"][FORMAT_COMPLETION] = self.stats["data_formats"].get(FORMAT_COMPLETION, 0) + len(examples)
        
        return examples
    
    def _generate_qa_examples(self, section: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Generate question-answer style training examples.
        
        Args:
            section: Content section with metadata
            
        Returns:
            List of Q&A examples
        """
        examples = []
        content = section["content"]
        
        # Extract Q&A pairs from content
        extracted_qa = self._extract_qa_pairs(content)
        
        # Add the extracted Q&A pairs
        for question, answer in extracted_qa:
            example = QA_TEMPLATE.copy()
            example["question"] = question
            example["answer"] = answer
            
            if self.include_metadata:
                example["metadata"] = {
                    "source_type": section["type"],
                    "extraction_method": "pattern"
                }
            
            examples.append(example)
        
        # For markdown files with headings, generate Q&A about sections
        if section["type"] == "file" and "file_path" in section["metadata"]:
            file_type = section.get("metadata", {}).get("file_type", "")
            
            if file_type in ["md", "markdown"] and "# " in content:
                headings = self._extract_headings(content)
                
                for heading in headings:
                    section_content = self._extract_section_content(content, heading)
                    if not section_content or len(section_content) < 50:
                        continue
                    
                    # Create a question about this section
                    example = QA_TEMPLATE.copy()
                    example["question"] = f"What is {heading} about?"
                    example["answer"] = section_content
                    
                    if self.include_metadata:
                        example["metadata"] = {
                            "source_type": "file",
                            "file_type": file_type,
                            "heading": heading,
                            "generation_method": "heading_based"
                        }
                    
                    examples.append(example)
                    
                    # Generate additional specific questions for longer sections
                    if len(section_content) > 200:
                        specific_questions = self._generate_questions_from_text(section_content, heading)
                        
                        for q, a in specific_questions:
                            example = QA_TEMPLATE.copy()
                            example["question"] = q
                            example["answer"] = a
                            
                            if self.include_metadata:
                                example["metadata"] = {
                                    "source_type": "file",
                                    "file_type": file_type,
                                    "heading": heading,
                                    "generation_method": "content_based"
                                }
                            
                            examples.append(example)
        
        # Update statistics
        self.stats["data_formats"][FORMAT_QA] = self.stats["data_formats"].get(FORMAT_QA, 0) + len(examples)
        
        return examples
    
    def _generate_general_examples(self, section: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Generate general-purpose training examples combining multiple formats.
        
        Args:
            section: Content section with metadata
            
        Returns:
            List of mixed-format examples
        """
        # For general format, collect examples from all other formats
        examples = []
        examples.extend(self._generate_instruction_examples(section))
        examples.extend(self._generate_conversation_examples(section))
        examples.extend(self._generate_completion_examples(section))
        examples.extend(self._generate_qa_examples(section))
        
        # Update statistics
        self.stats["data_formats"][FORMAT_GENERAL] = self.stats["data_formats"].get(FORMAT_GENERAL, 0) + len(examples)
        
        return examples
    
    def _extract_qa_pairs(self, content: str) -> List[Tuple[str, str]]:
        """
        Extract potential Q&A pairs from content.
        
        Args:
            content: Text content to analyze
            
        Returns:
            List of (question, answer) tuples
        """
        qa_pairs = []
        
        # Pattern 1: Look for question-like headings followed by content
        q_heading_pattern = re.compile(r'#+\s+(.*?\?)\s*\n+(.*?)(?=\n#|\Z)', re.DOTALL)
        matches = q_heading_pattern.findall(content)
        
        for question, answer in matches:
            question = question.strip()
            answer = answer.strip()
            
            if question and answer and len(answer) > 20:
                qa_pairs.append((question, answer))
        
        # Pattern 2: Look for FAQ-style Q: A: format
        qa_pattern = re.compile(r'(?:Q|Question)[:.]\s*(.*?)\s*\n+(?:A|Answer)[:.]\s*(.*?)(?=\n+(?:Q|Question)[:.]\s*|\Z)', re.DOTALL | re.IGNORECASE)
        matches = qa_pattern.findall(content)
        
        for question, answer in matches:
            question = question.strip()
            answer = answer.strip()
            
            if question and answer and len(answer) > 20:
                qa_pairs.append((question, answer))
        
        # Pattern 3: Look for bullet points with questions
        bullet_q_pattern = re.compile(r'(?:^|\n)[*-]\s+(.*?\?)\s*\n+(.*?)(?=\n[*-]|\Z)', re.DOTALL)
        matches = bullet_q_pattern.findall(content)
        
        for question, answer in matches:
            question = question.strip()
            answer = answer.strip()
            
            if question and answer and len(answer) > 20:
                qa_pairs.append((question, answer))
        
        return qa_pairs
    
    def _extract_headings(self, content: str) -> List[str]:
        """
        Extract headings from markdown content.
        
        Args:
            content: Markdown content
            
        Returns:
            List of headings (without # symbols)
        """
        headings = []
        heading_pattern = re.compile(r'^#+\s+(.*?)$', re.MULTILINE)
        
        for match in heading_pattern.finditer(content):
            headings.append(match.group(1).strip())
        
        return headings
    
    def _extract_section_content(self, content: str, heading: str) -> str:
        """
        Extract content under a specific heading.
        
        Args:
            content: The full markdown content
            heading: The heading text (without # symbols)
            
        Returns:
            The content under the specified heading
        """
        # Escape special regex characters in heading
        escaped_heading = re.escape(heading)
        
        # Find the heading and capture content until the next heading or end
        pattern = rf'#+\s+{escaped_heading}\s*\n+(.*?)(?=\n#+\s+|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_functions_and_classes(self, content: str, file_type: str) -> str:
        """
        Extract information about functions and classes from code.
        
        Args:
            content: Code content
            file_type: Type of file/language
            
        Returns:
            Description of functions and classes
        """
        result = "The file contains the following main components:\n\n"
        
        if file_type == "py":
            # Python function and class detection
            function_pattern = re.compile(r'def\s+([a-zA-Z0-9_]+)\s*\((.*?)\)(?:\s*->.*?)?:', re.DOTALL)
            class_pattern = re.compile(r'class\s+([a-zA-Z0-9_]+)(?:\(.*?\))?:', re.DOTALL)
            
            functions = function_pattern.findall(content)
            classes = class_pattern.findall(content)
            
            if classes:
                result += "Classes:\n"
                for cls in classes:
                    result += f"- {cls}\n"
                result += "\n"
            
            if functions:
                result += "Functions:\n"
                for func_name, params in functions:
                    result += f"- {func_name}({params.strip()})\n"
        
        elif file_type in ["js", "ts"]:
            # JavaScript/TypeScript function detection
            function_pattern = re.compile(r'(?:function\s+([a-zA-Z0-9_]+)\s*\((.*?)\)|const\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>)', re.DOTALL)
            class_pattern = re.compile(r'class\s+([a-zA-Z0-9_]+)(?:\s+extends\s+[a-zA-Z0-9_]+)?', re.DOTALL)
            
            functions = function_pattern.findall(content)
            classes = class_pattern.findall(content)
            
            if classes:
                result += "Classes:\n"
                for cls in classes:
                    result += f"- {cls}\n"
                result += "\n"
            
            if functions:
                result += "Functions:\n"
                for match in functions:
                    if match[0]:  # Function declaration
                        result += f"- {match[0]}({match[1].strip()})\n"
                    else:  # Arrow function
                        result += f"- {match[2]}({match[3].strip()})\n"
        
        else:
            # Generic code analysis for other languages
            # Use simple heuristics to identify important components
            lines = content.split('\n')
            components = []
            
            for line in lines:
                line = line.strip()
                if (line.startswith("function ") or line.startswith("def ") or
                    line.startswith("class ") or "function(" in line or
                    " = function(" in line or " = (" in line and ") =>" in line):
                    components.append(line)
            
            if components:
                result += "Key components:\n"
                for comp in components[:10]:  # Limit to first 10 for brevity
                    result += f"- {comp}\n"
            else:
                result = "Could not detect specific functions or classes in this code."
        
        return result
    
    def _extract_topics(self, content: str) -> str:
        """
        Extract main topics from text content.
        
        Args:
            content: Text content
            
        Returns:
            Description of main topics
        """
        # First try to extract headings
        headings = self._extract_headings(content)
        
        if headings:
            result = "The content covers the following topics:\n\n"
            for heading in headings:
                result += f"- {heading}\n"
            return result
        
        # If no headings, look for paragraph topics
        paragraphs = content.split("\n\n")
        if len(paragraphs) > 3:
            result = "The content includes the following key sections:\n\n"
            
            for i, para in enumerate(paragraphs[:5]):  # Limit to first 5 paragraphs
                if len(para) < 30:
                    continue
                    
                # Try to summarize the paragraph in a few words
                first_sentence = re.split(r'(?<=[.!?])\s+', para)[0]
                topic = first_sentence[:100] + "..." if len(first_sentence) > 100 else first_sentence
                
                result += f"- {topic}\n"
            
            return result
        
        # If all else fails, provide a generic response
        return "The content appears to be a single block of text without clear section divisions."
    
    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """
        Generate a simple summary of content.
        
        Args:
            content: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Generated summary
        """
        # In a real implementation, this would use a sophisticated summarization technique
        # Here, we'll use a simple extractive approach
        
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        if not sentences:
            return "The content is empty or could not be summarized."
        
        # For short content, just return the first sentence
        if len(sentences) <= 2:
            return sentences[0]
        
        # For longer content, try to extract key sentences
        important_sentences = []
        
        # Add the first sentence as it often contains important context
        important_sentences.append(sentences[0])
        
        # Look for sentences with keywords indicating importance
        keywords = ["important", "key", "main", "primary", "critical", "essential", "significant"]
        for sentence in sentences[1:]:
            if any(keyword in sentence.lower() for keyword in keywords):
                important_sentences.append(sentence)
                if len(" ".join(important_sentences)) > max_length:
                    break
        
        # If we haven't found enough important sentences, add more from the beginning
        if len(" ".join(important_sentences)) < max_length / 2:
            for sentence in sentences[1:]:
                if sentence not in important_sentences:
                    important_sentences.append(sentence)
                    if len(" ".join(important_sentences)) > max_length:
                        break
        
        summary = " ".join(important_sentences)
        
        # Truncate to max_length if still too long
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
            
        return summary
    
    def _generate_code_explanation(self, code: str, language: str) -> str:
        """
        Generate a simple explanation of code.
        
        Args:
            code: The code to explain
            language: Programming language
            
        Returns:
            Explanation of the code
        """
        # In a real implementation, this would use a sophisticated code analysis technique
        # Here, we'll use a simple template-based approach
        
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if not non_empty_lines:
            return "The code file is empty."
        
        # Count imports/includes
        imports_count = 0
        for line in non_empty_lines:
            if language == "py" and (line.startswith("import ") or line.startswith("from ")):
                imports_count += 1
            elif language in ["js", "ts"] and ("import " in line or "require(" in line):
                imports_count += 1
            elif language in ["java", "cpp", "c"] and ("#include" in line or "import " in line):
                imports_count += 1
        
        # Count functions/methods and classes
        functions_count = 0
        classes_count = 0
        
        for line in non_empty_lines:
            if language == "py":
                if line.strip().startswith("def "):
                    functions_count += 1
                elif line.strip().startswith("class "):
                    classes_count += 1
            elif language in ["js", "ts"]:
                if "function " in line or "=> {" in line or "=> (" in line:
                    functions_count += 1
                elif line.strip().startswith("class "):
                    classes_count += 1
            elif language in ["java", "c", "cpp"]:
                if "void " in line or "int " in line or "String " in line or "boolean " in line or "double " in line:
                    if "(" in line and ")" in line and "{" in line:
                        functions_count += 1
                elif line.strip().startswith("class ") or line.strip().startswith("public class "):
                    classes_count += 1
        
        # Create explanation
        explanation = f"This is a {language} code file containing "
        components = []
        
        if imports_count > 0:
            components.append(f"{imports_count} import statements")
        
        if classes_count > 0:
            components.append(f"{classes_count} class definition{'s' if classes_count > 1 else ''}")
        
        if functions_count > 0:
            components.append(f"{functions_count} function{'s' if functions_count > 1 else ''}/method{'s' if functions_count > 1 else ''}")
        
        if components:
            explanation += ", ".join(components) + "."
        else:
            explanation += "code that appears to be primarily procedural or declarative in nature."
        
        # Add purpose if possible
        if language == "py" and '"""' in code:
            # Try to extract docstring
            docstring_match = re.search(r'"""(.*?)"""', code, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1).strip()
                explanation += f"\n\nPurpose according to docstring: {docstring[:200]}..."
        
        return explanation
    
    def _generate_questions_from_text(self, text: str, context: str = "") -> List[Tuple[str, str]]:
        """
        Generate questions and answers from text content.
        
        Args:
            text: Content to generate questions from
            context: Additional context (like section heading)
            
        Returns:
            List of (question, answer) tuples
        """
        questions = []
        
        # Split into sentences for answer extraction
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if len(sentences) < 2:
            return questions
        
        # Generate factual questions based on key sentences
        for i, sentence in enumerate(sentences):
            if len(sentence) < 40 or not re.search(r'[a-zA-Z]{3,}', sentence):
                continue
                
            # Create variations of questions based on content
            
            # 1. What-style questions
            if context:
                question = f"What does {context} say about {self._extract_topic(sentence)}?"
                answer = sentence
                questions.append((question, answer))
            
            # 2. How/Why questions for sentences with explanations
            explanation_markers = ["because", "since", "therefore", "thus", "consequently", "as a result", "due to", "leads to"]
            if any(marker in sentence.lower() for marker in explanation_markers):
                if "because" in sentence.lower() or "since" in sentence.lower() or "due to" in sentence.lower():
                    parts = re.split(r'because|since|due to', sentence, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        effect = parts[0].strip()
                        cause = parts[1].strip()
                        
                        question = f"Why {effect.lower()}?"
                        answer = f"Because {cause}."
                        questions.append((question, answer))
                else:
                    topic = self._extract_topic(sentence)
                    question = f"How does {topic} work according to the text?"
                    answer = sentence
                    questions.append((question, answer))
        
        # If we have enough sentences, also create a comprehension question
        if len(sentences) >= 3:
            combined_answer = " ".join(sentences[:min(3, len(sentences))])
            question = f"Summarize what the text says about {context if context else 'this topic'}."
            questions.append((question, combined_answer))
        
        # Limit to 3 questions maximum
        return questions[:3]
    
    def _extract_topic(self, sentence: str) -> str:
        """
        Extract a potential topic from a sentence.
        
        Args:
            sentence: The sentence to analyze
            
        Returns:
            Extracted topic or subject
        """
        # Check for nouns with adjectives
        noun_phrases = re.findall(r'(?:the|a|an)\s+(?:[a-z]+\s+)?[a-z]+', sentence.lower())
        if noun_phrases:
            return noun_phrases[0].strip()
        
        # Fall back to first noun
        words = sentence.split()
        for word in words:
            if len(word) > 3 and word[0].isalpha():
                return word.lower()
        
        # Last resort
        return "this topic"
    
    def _split_code_into_chunks(self, code: str, language: str) -> List[Tuple[str, str]]:
        """
        Split code into chunks suitable for completion examples.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            List of (prompt, completion) tuples
        """
        chunks = []
        
        if language == "py":
            # Split Python code by functions and classes
            function_pattern = re.compile(r'(def\s+[a-zA-Z0-9_]+\s*\(.*?\):(?:\s*""".*?""")?(?:\s*#.*?)?(?:\s*[^\n]+)*?)(\s+[^\s][^\n]*(?:\n+\s+[^\n]+)*)', re.DOTALL)
            class_pattern = re.compile(r'(class\s+[a-zA-Z0-9_]+(?:\([^)]*\))?:(?:\s*""".*?""")?(?:\s*#.*?)?(?:\s*[^\n]+)*?)(\s+[^\s][^\n]*(?:\n+\s+[^\n]+)*)', re.DOTALL)
            
            # Find function chunks
            for match in function_pattern.finditer(code):
                signature = match.group(1)
                body = match.group(2)
                
                if len(signature) > 20 and len(body) > 30:
                    chunks.append((signature, body))
            
            # Find class chunks
            for match in class_pattern.finditer(code):
                signature = match.group(1)
                body = match.group(2)
                
                if len(signature) > 20 and len(body) > 30:
                    chunks.append((signature, body))
                    
        elif language in ["js", "ts"]:
            # Split JavaScript/TypeScript code by functions
            function_pattern = re.compile(r'(function\s+[a-zA-Z0-9_]+\s*\(.*?\)\s*{(?:\s*//.*?)?(?:\s*[^\n]+)*?)(\s+[^\s][^\n]*(?:\n+\s+[^\n]+)*\n*})', re.DOTALL)
            arrow_pattern = re.compile(r'(const\s+[a-zA-Z0-9_]+\s*=\s*(?:async\s*)?\(.*?\)\s*=>\s*{(?:\s*//.*?)?(?:\s*[^\n]+)*?)(\s+[^\s][^\n]*(?:\n+\s+[^\n]+)*\n*})', re.DOTALL)
            class_pattern = re.compile(r'(class\s+[a-zA-Z0-9_]+(?:\s+extends\s+[a-zA-Z0-9_]+)?\s*{(?:\s*//.*?)?(?:\s*[^\n]+)*?)(\s+[^\s][^\n]*(?:\n+\s+[^\n]+)*\n*})', re.DOTALL)
            
            # Find function chunks
            for match in function_pattern.finditer(code):
                signature = match.group(1)
                body = match.group(2)
                
                if len(signature) > 20 and len(body) > 30:
                    chunks.append((signature, body))
            
            # Find arrow function chunks
            for match in arrow_pattern.finditer(code):
                signature = match.group(1)
                body = match.group(2)
                
                if len(signature) > 20 and len(body) > 30:
                    chunks.append((signature, body))
            
            # Find class chunks
            for match in class_pattern.finditer(code):
                signature = match.group(1)
                body = match.group(2)
                
                if len(signature) > 20 and len(body) > 30:
                    chunks.append((signature, body))
        
        else:
            # Generic approach for other languages
            # Look for block patterns with a consistent indent level
            lines = code.split('\n')
            
            block_start = -1
            block_indent = -1
            for i, line in enumerate(lines):
                if i < len(lines) - 1 and line.strip() and lines[i+1].strip():
                    current_indent = len(line) - len(line.lstrip())
                    next_indent = len(lines[i+1]) - len(lines[i+1].lstrip())
                    
                    # Found a potential block start where indentation increases
                    if next_indent > current_indent:
                        # Complete the previous block if exists
                        if block_start >= 0 and block_indent >= 0:
                            header = "\n".join(lines[block_start:i])
                            body = "\n".join(lines[i:])
                            if len(header) > 20 and len(body) > 30:
                                chunks.append((header, body))
                            
                        block_start = i
                        block_indent = current_indent
        
        # Ensure we have at least some chunks, even if pattern matching failed
        if not chunks and len(code) > 100:
            # Split into approximately equal chunks
            lines = code.split('\n')
            lines = [line for line in lines if line.strip()]  # Remove empty lines
            
            if len(lines) >= 6:
                chunk_size = len(lines) // 3
                
                for i in range(0, len(lines) - chunk_size, chunk_size):
                    prompt = "\n".join(lines[i:i+chunk_size//2])
                    completion = "\n".join(lines[i+chunk_size//2:i+chunk_size])
                    
                    if len(prompt) > 20 and len(completion) > 20:
                        chunks.append((prompt, completion))
        
        return chunks
    
    def _count_tokens(self, example: Dict[str, Any]) -> int:
        """
        Count tokens in an example.
        
        Args:
            example: Training example
            
        Returns:
            Approximate token count
        """
        # If tiktoken is available, use it for accurate counting
        if TIKTOKEN_AVAILABLE and self.tokenizer:
            text = ""
            
            # Combine all text fields based on format
            if self.data_format == FORMAT_INSTRUCTION:
                text = example.get("instruction", "") + " " + example.get("input", "") + " " + example.get("output", "")
            elif self.data_format == FORMAT_CONVERSATION:
                for msg in example.get("messages", []):
                    text += msg.get("content", "") + " "
            elif self.data_format == FORMAT_COMPLETION:
                text = example.get("prompt", "") + " " + example.get("completion", "")
            elif self.data_format == FORMAT_QA:
                text = example.get("question", "") + " " + example.get("answer", "")
            
            # Count tokens
            return len(self.tokenizer.encode(text))
        
        # Fall back to a rough approximation if tiktoken is not available
        # Average English word is ~4 characters, and GPT tokenization is roughly 0.75 tokens per word
        total_chars = 0
        
        if self.data_format == FORMAT_INSTRUCTION:
            total_chars += len(example.get("instruction", ""))
            total_chars += len(example.get("input", ""))
            total_chars += len(example.get("output", ""))
        elif self.data_format == FORMAT_CONVERSATION:
            for msg in example.get("messages", []):
                total_chars += len(msg.get("content", ""))
        elif self.data_format == FORMAT_COMPLETION:
            total_chars += len(example.get("prompt", ""))
            total_chars += len(example.get("completion", ""))
        elif self.data_format == FORMAT_QA:
            total_chars += len(example.get("question", ""))
            total_chars += len(example.get("answer", ""))
        
        # Rough approximation: 4 chars ≈ 1 word ≈ 0.75 tokens
        return int(total_chars / 4 * 0.75)
    
    def _save_examples(self, examples: List[Dict[str, Any]], output_dir: str, output_name: str) -> str:
        """
        Save examples to the specified format.
        
        Args:
            examples: List of training examples
            output_dir: Directory to save to
            output_name: Base name for output file
            
        Returns:
            Path to the saved file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{output_name}-{self.data_format}-{timestamp}"
        
        if self.output_format == OUTPUT_JSONL:
            output_file = os.path.join(output_dir, f"{base_filename}.jsonl")
            with open(output_file, 'w', encoding='utf-8') as f:
                for example in examples:
                    f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        elif self.output_format == OUTPUT_CSV:
            output_file = os.path.join(output_dir, f"{base_filename}.csv")
            
            # Determine fields based on format
            if self.data_format == FORMAT_INSTRUCTION:
                fieldnames = ["instruction", "input", "output"]
            elif self.data_format == FORMAT_CONVERSATION:
                fieldnames = ["conversation", "metadata"]
            elif self.data_format == FORMAT_COMPLETION:
                fieldnames = ["prompt", "completion"]
            elif self.data_format == FORMAT_QA:
                fieldnames = ["question", "answer"]
            else:
                fieldnames = list(examples[0].keys()) if examples else []
            
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for example in examples:
                    # Special handling for conversation format in CSV
                    if self.data_format == FORMAT_CONVERSATION:
                        row = {
                            "conversation": json.dumps(example.get("messages", []), ensure_ascii=False),
                            "metadata": json.dumps(example.get("metadata", {}), ensure_ascii=False)
                        }
                        writer.writerow(row)
                    else:
                        # Filter to include only the defined fields
                        row = {k: example.get(k, '') for k in fieldnames}
                        writer.writerow(row)
        
        elif self.output_format == OUTPUT_PARQUET and PANDAS_AVAILABLE:
            output_file = os.path.join(output_dir, f"{base_filename}.parquet")
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(examples)
            
            # Special handling for conversation format
            if self.data_format == FORMAT_CONVERSATION:
                # Convert messages list to string representation
                df["messages"] = df["messages"].apply(lambda x: json.dumps(x, ensure_ascii=False))
            
            # Write to parquet
            df.to_parquet(output_file, index=False)
        
        elif self.output_format == OUTPUT_HF_DATASET and HF_DATASETS_AVAILABLE:
            output_file = os.path.join(output_dir, base_filename)
            
            # Convert to Hugging Face Dataset
            dataset = Dataset.from_pandas(pd.DataFrame(examples))
            
            # Save as directory of Arrow files
            dataset.save_to_disk(output_file)
        
        else:
            # Default to JSONL if requested format is not available
            output_file = os.path.join(output_dir, f"{base_filename}.jsonl")
            with open(output_file, 'w', encoding='utf-8') as f:
                for example in examples:
                    f.write(json.dumps(example, ensure_ascii=False) + '\n')
        
        # Save statistics alongside the data
        stats_file = os.path.join(output_dir, f"{base_filename}-stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def get_stats(self) -> Dict[str, Any]:
        """Get the current statistics about generated data."""
        return self.stats
