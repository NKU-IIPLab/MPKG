from typing import List, Tuple, Dict, Optional
import os
from pathlib import Path
import edc.utils.llm_utils as llm_utils
import re
from edc.utils.e5_mistral_utils import MistralForSequenceEmbedding
from transformers import AutoModelForCausalLM, AutoTokenizer
import numpy as np
import copy
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class SchemaCanonicalizer_CoT:

    def __init__(
        self,
        target_schema_dict: dict,
        embedder: SentenceTransformer,
        verify_model: AutoTokenizer = None,
        verify_tokenizer: AutoTokenizer = None,
        verify_openai_model: str = None,
        language: str = 'zh',
        max_tokens: int = 400,
    ) -> None:
        """

        Args:
            target_schema_dict: Dictionary of target schema relations and definitions
            embedder: Sentence transformer for relation embedding
            verify_model: Local LLM model for verification (optional)
            verify_tokenizer: Tokenizer for local model (optional)
            verify_openai_model: OpenAI model name (optional, e.g., "gpt-4")
            language: Language for CoT prompts ('zh' or 'en')
            max_tokens: Maximum tokens for LLM output (CoT requires more, default 400)
        """
        assert verify_openai_model is not None or (verify_model is not None and verify_tokenizer is not None), \
            "Must provide either OpenAI model or local model with tokenizer"

        self.verifier_model = verify_model
        self.verifier_tokenizer = verify_tokenizer
        self.verifier_openai_model = verify_openai_model
        self.schema_dict = target_schema_dict
        self.embedder = embedder

        # CoT-specific configuration
        self.language = language
        self.max_tokens = max_tokens

        # Load CoT template
        print(f"[CoT] Loading CoT template for language: {language}")
        self.prompt_template = self._load_cot_template(language)

        # Embed the target schema
        self.schema_embedding_dict = {}
        print("Embedding target schema...")
        for relation, relation_definition in tqdm(target_schema_dict.items()):
            embedding = self.embedder.encode(relation_definition)
            self.schema_embedding_dict[relation] = embedding

        print(f"[CoT] Initialized with max_tokens={max_tokens}, language={language}")

    def _load_cot_template(self, language: str) -> str:
       
        template_file = f"sc_template_cot_{language}.txt"
        # Get path relative to this file
        current_dir = Path(__file__).parent
        template_path = current_dir.parent / "prompt_templates" / template_file

        if not template_path.exists():
            raise FileNotFoundError(
                f"CoT template file not found: {template_path}\n"
                f"Expected one of: sc_template_cot_zh.txt or sc_template_cot_en.txt"
            )

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        print(f"[CoT] Loaded template from: {template_path}")
        print(f"[CoT] Template length: {len(template_content)} characters")

        return template_content

    def retrieve_similar_relations(self, query_relation_definition: str, top_k=5):
       
        target_relation_list = list(self.schema_embedding_dict.keys())
        target_relation_embedding_list = list(self.schema_embedding_dict.values())

        if "sts_query" in self.embedder.prompts:
            query_embedding = self.embedder.encode(query_relation_definition, prompt_name="sts_query")
        else:
            query_embedding = self.embedder.encode(query_relation_definition)

        scores = np.array([query_embedding]) @ np.array(target_relation_embedding_list).T
        scores = scores[0]
        highest_score_indices = np.argsort(-scores)

        return {
            target_relation_list[idx]: self.schema_dict[target_relation_list[idx]]
            for idx in highest_score_indices[:top_k]
        }, [scores[idx] for idx in highest_score_indices[:top_k]]

    def extract_option_letter(self, text: str) -> Optional[str]:
       
        # Try multiple patterns
        patterns = [
            (r'^([A-Z])$', "Single letter"),
            (r'选项\s*([A-Z])', "'Option X' pattern"),
            (r'([A-Z])\s*选项', "'X Option' pattern"),
            (r'选择\s*([A-Z])', "'Choose X' pattern"),
            (r'[Aa]nswer\s*[:：]\s*([A-Z])', "'Answer: X' pattern"),
            (r'答案\s*[:：]\s*([A-Z])', "'答案: X' pattern"),
            (r'^([A-Z])[.,。，\s]', "Starting letter pattern"),
            (r'([A-Z])\s*更合适', "'X more suitable' pattern"),
        ]

        text = text.strip()

        # Single letter check
        if len(text) == 1 and text.isalpha():
            return text.upper()

        # Pattern matching
        for pattern, desc in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        # Extract any isolated letter
        match = re.search(r'[^A-Z]([A-Z])[^A-Z]', ' ' + text + ' ')
        if match:
            return match.group(1).upper()

        # Last resort: find any A-F letter
        letters = [c.upper() for c in text if c.isalpha()]
        for letter in letters:
            if 'A' <= letter <= 'F':
                return letter

        return None

    def extract_cot_answer(self, cot_text: str) -> Tuple[str, Optional[str], float]:
       
        # Strategy 1: Match explicit final answer formats (highest confidence)
        patterns = [
            (r'最终答案\s*[:：]\s*([A-Z])', 1.0, "Chinese final answer"),
            (r'Final Answer\s*[:：]\s*([A-Z])', 1.0, "English final answer"),
            (r'答案\s*[:：]\s*([A-Z])', 0.9, "Chinese answer"),
            (r'Answer\s*[:：]\s*([A-Z])', 0.9, "English answer"),
        ]

        for pattern, confidence, desc in patterns:
            match = re.search(pattern, cot_text, re.IGNORECASE)
            if match:
                option = match.group(1).upper()
                reasoning = cot_text[:match.start()].strip()
                print(f"[CoT] ✓ Matched '{desc}' pattern, answer: {option}, confidence: {confidence}")
                return reasoning, option, confidence

        # Strategy 2: Extract from last line (medium confidence)
        lines = [l.strip() for l in cot_text.strip().split('\n') if l.strip()]
        if lines:
            last_line = lines[-1]
            option = self.extract_option_letter(last_line)
            if option:
                reasoning = '\n'.join(lines[:-1]).strip()
                print(f"[CoT] ✓ Extracted from last line: {option}, confidence: 0.7")
                return reasoning, option, 0.7

        # Strategy 3: Scan full text (low confidence)
        option = self.extract_option_letter(cot_text)
        if option:
            print(f"[CoT] ⚠ Extracted from full text: {option}, confidence: 0.5")
            return cot_text, option, 0.5

        # Strategy 4: Failed
        print(f"[CoT] ✗ Failed to extract answer. Output preview: {cot_text[:200]}...")
        return cot_text, None, 0.0

    def llm_verify(
        self,
        input_text_str: str,
        query_triplet: List[str],
        query_relation_definition: str,
        candidate_relation_definition_dict: dict,
        relation_example_dict: dict = None,
    ) -> Optional[Dict]:
        """
        Returns:
            Dictionary containing:
            - 'triplet': Canonicalized triplet with selected relation
            - 'reasoning': Full reasoning text from LLM
            - 'confidence': Confidence score of answer extraction
            - 'raw_output': Raw LLM output
            - 'selected_option': Option letter (A, B, C, etc.)

            Returns None if no valid answer could be extracted
        """
        canonicalized_triplet = copy.deepcopy(query_triplet)
        choice_letters_list = []
        choices = ""
        candidate_relations = list(candidate_relation_definition_dict.keys())
        candidate_relation_descriptions = list(candidate_relation_definition_dict.values())

        print(f"[CoT] ===== LLM Verification (CoT Mode) =====")
        print(f"[CoT] Language: {self.language}, Max tokens: {self.max_tokens}")
        print(f"[CoT] Verifying triplet: {query_triplet}")
        print(f"[CoT] Query relation: '{query_triplet[1]}' = {query_relation_definition}")

      
        for idx, rel in enumerate(candidate_relations):
            choice_letter = chr(ord("@") + idx + 1)  # A, B, C, ...
            choice_letters_list.append(choice_letter)
            choices += f"{choice_letter}. '{rel}': {candidate_relation_descriptions[idx]}\n"

     
        none_option_letter = chr(ord('@') + len(candidate_relations) + 1)
        choices += f"{none_option_letter}. None of the above.\n"

        print(f"[CoT] Candidate options: {len(choice_letters_list)} relations + None")

    
        verification_prompt = self.prompt_template.format_map({
            "input_text": input_text_str,
            "query_triplet": query_triplet,
            "query_relation": query_triplet[1],
            "query_relation_definition": query_relation_definition,
            "choices": choices,
        })

        print(f"[CoT] Prompt length: {len(verification_prompt)} characters")

       
        messages = [{"role": "user", "content": verification_prompt}]

        if self.verifier_openai_model is None:
            # Local model
            verification_result = llm_utils.generate_completion_transformers(
                messages,
                self.verifier_model,
                self.verifier_tokenizer,
                answer_prepend="",  # No prepend for CoT
                max_new_token=self.max_tokens
            )
        else:
           
            verification_result = llm_utils.openai_chat_completion(
                self.verifier_openai_model,
                None,
                messages,
                max_tokens=self.max_tokens
            )

        print(f" LLM output length: {len(verification_result)} characters")
        print(f" Output preview (first 200 chars):\n{verification_result[:200]}\n...")

      
        reasoning, extracted_letter, confidence = self.extract_cot_answer(verification_result)

        print(f"Extracted answer: '{extracted_letter}'")
        print(f" Confidence: {confidence}")
        print(f" Reasoning length: {len(reasoning)} characters")

        if extracted_letter and extracted_letter in choice_letters_list:
            selected_index = choice_letters_list.index(extracted_letter)
            selected_relation = candidate_relations[selected_index]
            canonicalized_triplet[1] = selected_relation

            print(f" Selected option {extracted_letter} → '{selected_relation}'")
            print(f" ===== Verification Complete =====\n")

            return {
                'triplet': canonicalized_triplet,
                'reasoning': reasoning,
                'confidence': confidence,
                'raw_output': verification_result,
                'selected_option': extracted_letter
            }
        else:
            print(f" Failed to map option '{extracted_letter}' to a valid relation")
            print(f" Valid options were: {choice_letters_list}")
            print(f" ===== Verification Failed =====\n")
            return None

    def canonicalize(
        self,
        input_text_str: str,
        open_triplet: List[str],
        open_relation_definition_dict: dict,
        enrich: bool = False,
    ) -> Tuple[Optional[List[str]], Dict]:
        print(f"\n ======= Starting Canonicalization =======")
        print(f" Open triplet: {open_triplet}")

        open_relation = open_triplet[1]

        # Check if already canonical
        if open_relation in self.schema_dict:
            print(f" Relation '{open_relation}' already in standard schema, skipping")
            print(f" ======= Canonicalization Complete (No Change) =======\n")
            return open_triplet, {
                'candidates': {},
                'reasoning': '',
                'confidence': 1.0
            }

        candidate_relations = {}
        candidate_scores = []

       
        if len(self.schema_dict) != 0:
            if open_relation not in open_relation_definition_dict:
                print(f"Relation '{open_relation}' not found in definition dict")
                verify_result = None
            else:
                print(f"Relation definition: {open_relation_definition_dict[open_relation]}")

               
                candidate_relations, candidate_scores = self.retrieve_similar_relations(
                    open_relation_definition_dict[open_relation]
                )

                print(f"Retrieved {len(candidate_relations)} candidates:")
                for rel, score in zip(candidate_relations.keys(), candidate_scores):
                    print(f" - {rel}: {score:.4f}")

               
                verify_result = self.llm_verify(
                    input_text_str,
                    open_triplet,
                    open_relation_definition_dict[open_relation],
                    candidate_relations,
                    None,
                )
        else:
            print(f"Target schema is empty, cannot canonicalize")
            verify_result = None

       
        if verify_result is not None:
            canonicalized_triplet = verify_result['triplet']
            reasoning = verify_result['reasoning']
            confidence = verify_result['confidence']

            print(f"Canonicalization successful")
            print(f"Original: {open_triplet[1]} → Canonical: {canonicalized_triplet[1]}")
        else:
            canonicalized_triplet = None
            reasoning = ""
            confidence = 0.0

            if enrich:
                print(f"Failed to canonicalize, but enrich=True")
                print(f"Adding '{open_relation}' to target schema")

                self.schema_dict[open_relation] = open_relation_definition_dict[open_relation]

                # Update embeddings
                if "sts_query" in self.embedder.prompts:
                    embedding = self.embedder.encode(
                        open_relation_definition_dict[open_relation],
                        prompt_name="sts_query"
                    )
                else:
                    embedding = self.embedder.encode(
                        open_relation_definition_dict[open_relation]
                    )
                self.schema_embedding_dict[open_relation] = embedding

                canonicalized_triplet = open_triplet
                print(f"Schema enriched, using original triplet")
            else:
                print(f" Canonicalization failed, returning None")

        result_info = {
            'candidates': dict(zip(candidate_relations.keys() if candidate_relations else [],
                                  candidate_scores if candidate_scores else [])),
            'reasoning': reasoning,
            'confidence': confidence
        }

        print(f"======= Canonicalization Complete =======\n")

        return canonicalized_triplet, result_info
