from typing import List
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


class SchemaCanonicalizer:
    # The class to handle the last stage: Schema Canonicalization
    def __init__(
        self,
        target_schema_dict: dict,
        embedder: SentenceTransformer,
        verify_model: AutoTokenizer = None,
        verify_tokenizer: AutoTokenizer = None,
        verify_openai_model: AutoTokenizer = None,
    ) -> None:
        # The canonicalizer uses an embedding model to first fetch candidates from the target schema, then uses a verifier schema to decide which one to canonicalize to or not
        # canonoicalize at all.

        assert verify_openai_model is not None or (verify_model is not None and verify_tokenizer is not None)
        self.verifier_model = verify_model
        self.verifier_tokenizer = verify_tokenizer
        self.verifier_openai_model = verify_openai_model
        self.schema_dict = target_schema_dict

        self.embedder = embedder

        # Embed the target schema
        self.schema_embedding_dict = {}

        print("Embedding target schema...")
        for relation, relation_definition in tqdm(target_schema_dict.items()):
            embedding = self.embedder.encode(relation_definition)
            self.schema_embedding_dict[relation] = embedding

    def retrieve_similar_relations(self, query_relation_definition: str, top_k=5):
        target_relation_list = list(self.schema_embedding_dict.keys())
        target_relation_embedding_list = list(self.schema_embedding_dict.values())
        
        print(f"[DEBUG] 开始检索与定义相似的关系: '{query_relation_definition}'")
        
        if "sts_query" in self.embedder.prompts:
            query_embedding = self.embedder.encode(query_relation_definition, prompt_name="sts_query")
        else:
            query_embedding = self.embedder.encode(query_relation_definition)

        scores = np.array([query_embedding]) @ np.array(target_relation_embedding_list).T

        scores = scores[0]
        highest_score_indices = np.argsort(-scores)

        similar_relations = {
            target_relation_list[idx]: self.schema_dict[target_relation_list[idx]]
            for idx in highest_score_indices[:top_k]
        }
        similar_scores = [scores[idx] for idx in highest_score_indices[:top_k]]
        
        print(f"[DEBUG] 检索到的相似关系:")
        for rel, score in zip(similar_relations.keys(), similar_scores):
            print(f"  - {rel}: {similar_relations[rel]} (相似度: {score:.4f})")
        
        return similar_relations, similar_scores

    def extract_option_letter(self, text):
        """从文本中提取选项字母（A-Z）"""
        # 尝试多种模式匹配选项字母
        print(f"[DEBUG] 尝试从文本中提取选项字母: '{text}'")
        
        # 1. 直接匹配单个字母（如果文本只有一个字符且是字母）
        if len(text) == 1 and text.isalpha():
            print(f"[DEBUG] 匹配到单个字母: {text.upper()}")
            return text.upper()
        
        # 2. 匹配"选项X"模式
        option_match = re.search(r'选项\s*([A-Za-z])', text)
        if option_match:
            print(f"[DEBUG] 匹配到'选项X'模式: {option_match.group(1).upper()}")
            return option_match.group(1).upper()
        
        # 3. 匹配"X选项"模式
        option_match = re.search(r'([A-Za-z])\s*选项', text)
        if option_match:
            print(f"[DEBUG] 匹配到'X选项'模式: {option_match.group(1).upper()}")
            return option_match.group(1).upper()
        
        # 4. 匹配"选择X"模式
        choose_match = re.search(r'选择\s*([A-Za-z])', text)
        if choose_match:
            print(f"[DEBUG] 匹配到'选择X'模式: {choose_match.group(1).upper()}")
            return choose_match.group(1).upper()
        
        # 5. 匹配"Answer: X"或"答案: X"模式
        answer_match = re.search(r'[Aa]nswer\s*[:：]\s*([A-Za-z])', text)
        if answer_match:
            print(f"[DEBUG] 匹配到'Answer: X'模式: {answer_match.group(1).upper()}")
            return answer_match.group(1).upper()
        
        answer_match = re.search(r'答案\s*[:：]\s*([A-Za-z])', text)
        if answer_match:
            print(f"[DEBUG] 匹配到'答案: X'模式: {answer_match.group(1).upper()}")
            return answer_match.group(1).upper()
        
        # 6. 匹配开头的字母后跟着标点或空格
        start_match = re.search(r'^([A-Za-z])[.,。，\s]', text)
        if start_match:
            print(f"[DEBUG] 匹配到开头字母: {start_match.group(1).upper()}")
            return start_match.group(1).upper()
        
        # 7. 匹配任意位置的单独字母（前后有空格或标点）
        any_match = re.search(r'[^A-Za-z]([A-Za-z])[^A-Za-z]', ' ' + text + ' ')
        if any_match:
            print(f"[DEBUG] 匹配到任意位置的单独字母: {any_match.group(1).upper()}")
            return any_match.group(1).upper()
        
        # 8. 匹配"更合适"前面的字母
        suitable_match = re.search(r'([A-Za-z])\s*更合适', text)
        if suitable_match:
            print(f"[DEBUG] 匹配到'X更合适'模式: {suitable_match.group(1).upper()}")
            return suitable_match.group(1).upper()
        
        # 9. 最后尝试提取文本中的任何字母
        letters = [c.upper() for c in text if c.isalpha()]
        if letters:
            # 优先选择A-F范围内的字母，因为这些是常用选项
            for letter in letters:
                if 'A' <= letter <= 'F':
                    print(f"[DEBUG] 从文本中提取到A-F范围内的字母: {letter}")
                    return letter
            # 如果没有A-F范围内的字母，返回第一个字母
            print(f"[DEBUG] 从文本中提取到的第一个字母: {letters[0]}")
            return letters[0]

        print(f"[DEBUG] 无法从文本中提取到任何字母")
            return None

    def llm_verify(
        self,
        input_text_str: str,
        query_triplet: List[str],
        query_relation_definition: str,
        prompt_template_str: str,
        candidate_relation_definition_dict: dict,
        relation_example_dict: dict = None,
    ):
        canonicalized_triplet = copy.deepcopy(query_triplet)
        choice_letters_list = []
        choices = ""
        candidate_relations = list(candidate_relation_definition_dict.keys())
        candidate_relation_descriptions = list(candidate_relation_definition_dict.values())
        print(f"[DEBUG] ===== LLM验证过程 =====")
        print(f"[DEBUG] 验证三元组: {query_triplet}")
        print(f"[DEBUG] 原始关系定义: '{query_triplet[1]}': {query_relation_definition}")
        
        for idx, rel in enumerate(candidate_relations):
            choice_letter = chr(ord("@") + idx + 1)
            choice_letters_list.append(choice_letter)
            choices += f"{choice_letter}. '{rel}': {candidate_relation_descriptions[idx]}\n"
            if relation_example_dict is not None:
                choices += f"Example: '{relation_example_dict[candidate_relations[idx]]['triple']}' can be extracted from '{candidate_relations[idx]['sentence']}'\n"
        choices += f"{chr(ord('@')+len(candidate_relations)+1)}. None of the above.\n"
        
        print(f"[DEBUG] 候选选项:")
        for i, letter in enumerate(choice_letters_list):
            print(f"  {letter}. '{candidate_relations[i]}': {candidate_relation_descriptions[i]}")
        print(f"  {chr(ord('@')+len(candidate_relations)+1)}. None of the above.")

        verification_prompt = prompt_template_str.format_map(
            {
                "input_text": input_text_str,
                "query_triplet": query_triplet,
                "query_relation": query_triplet[1],
                "query_relation_definition": query_relation_definition,
                "choices": choices,
            }
                )
        
        print(f"[DEBUG] 发送给模型的验证提示:\n{verification_prompt}")

        messages = [{"role": "user", "content": verification_prompt}]
        if self.verifier_openai_model is None:
            # 增加max_new_token以获取更完整的回答
            verification_result = llm_utils.generate_completion_transformers(
                messages, self.verifier_model, self.verifier_tokenizer, answer_prepend="Answer: ", max_new_token=50
                )
            print(f"[DEBUG] 模型完整输出: '{verification_result}'")
            
            # 使用新方法从输出中提取选项字母
            extracted_letter = self.extract_option_letter(verification_result)
            print(f"[DEBUG] 从输出中提取的选项字母: '{extracted_letter}'")
            
        else:
            verification_result = llm_utils.openai_chat_completion(
                self.verifier_openai_model, None, messages, max_tokens=10
                    )
            print(f"[DEBUG] OpenAI模型输出: '{verification_result}'")
            extracted_letter = self.extract_option_letter(verification_result)

        print(f"[DEBUG] 最终选择的选项: '{extracted_letter}'")
        print(f"[DEBUG] 有效选项列表: {choice_letters_list}")

        if extracted_letter in choice_letters_list:
            selected_index = choice_letters_list.index(extracted_letter)
            selected_relation = candidate_relations[selected_index]
            canonicalized_triplet[1] = selected_relation
            print(f"[DEBUG] 选择了选项 {extracted_letter}, 映射到关系: '{selected_relation}'")
            return canonicalized_triplet
                else:
            print(f"[DEBUG] 无法映射选项 '{extracted_letter}', 返回None")
            return None

    def canonicalize(
        self,
        input_text_str: str,
        open_triplet,
        open_relation_definition_dict: dict,
        verify_prompt_template: str,
        enrich=False,
    ):
        print(f"\n[DEBUG] ======= 开始标准化三元组: {open_triplet} =======")
        open_relation = open_triplet[1]

        if open_relation in self.schema_dict:
            # The relation is already canonical
            print(f"[DEBUG] 关系 '{open_relation}' 已经在标准模式中，无需标准化")
            return open_triplet, {}

        candidate_relations = []
        candidate_scores = []

        if len(self.schema_dict) != 0:
            if open_relation not in open_relation_definition_dict:
                print(f"[DEBUG] 关系 '{open_relation}' 在定义字典中不存在，无法标准化")
                canonicalized_triplet = None
            else:
                print(f"[DEBUG] 关系 '{open_relation}' 的定义: {open_relation_definition_dict[open_relation]}")
                candidate_relations, candidate_scores = self.retrieve_similar_relations(
                    open_relation_definition_dict[open_relation]
                )
                canonicalized_triplet = self.llm_verify(
                    input_text_str,
                    open_triplet,
                    open_relation_definition_dict[open_relation],
                    verify_prompt_template,
                    candidate_relations,
                    None,
                )
        else:
            print(f"[DEBUG] 标准模式为空，无法标准化")
            canonicalized_triplet = None

        if canonicalized_triplet is None:
            # Cannot be canonicalized
            if enrich:
                print(f"[DEBUG] 无法标准化，但enrich=True，将添加到标准模式中")
                self.schema_dict[open_relation] = open_relation_definition_dict[open_relation]
                if "sts_query" in self.embedder.prompts:
                    embedding = self.embedder.encode(
                        open_relation_definition_dict[open_relation], prompt_name="sts_query"
                    )
                else:
                    embedding = self.embedder.encode(open_relation_definition_dict[open_relation])
                self.schema_embedding_dict[open_relation] = embedding
                canonicalized_triplet = open_triplet
            else:
                print(f"[DEBUG] 无法标准化，返回None")
                
        print(f"[DEBUG] 标准化结果: {canonicalized_triplet}")
        print(f"[DEBUG] ======= 标准化完成 =======\n")
        return canonicalized_triplet, dict(zip(candidate_relations, candidate_scores))