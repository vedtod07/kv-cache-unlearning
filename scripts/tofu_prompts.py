"""Shared prompt and reference-answer tokenization for TOFU items.

Implements the conventions agreed on 2026-10-22 (see docs/DECISIONS.md once recorded):
- full-model tokenizer and chat template, system message "You are a helpful assistant.",
  fixed template date "10 Apr 2025" (the template otherwise inserts the current date);
- reference answers are scored in context and include the final end-of-turn token.

Only the tokenizer is needed (no model, no GPU).
"""
import hashlib

SYSTEM_PROMPT = 'You are a helpful assistant.'
TEMPLATE_DATE = '10 Apr 2025'
END_OF_TURN = '<|eot_id|>'
# sha256(tok.chat_template.encode()) recorded by A for the full-model tokenizer
# (results/day2/.../manifest.json, template_sha256).
EXPECTED_TEMPLATE_SHA256 = '5816fce10444e03c2e9ee1ef8a4a1ea61ae7e69e438613f3b17b69d0426223a4'


def template_sha256(tok):
    return hashlib.sha256(tok.chat_template.encode()).hexdigest()


def render_prompt(tok, question, system_prompt=SYSTEM_PROMPT, template_date=TEMPLATE_DATE):
    """Return (prompt_text, prompt_token_ids) for one user question."""
    messages = [{'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': question}]
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                   date_string=template_date)
    encoded = tok.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                      date_string=template_date, return_dict=True)
    return text, list(encoded['input_ids'])


def reference_token_ids(tok, prompt_text, prompt_ids, gold_answer):
    """Tokenize the gold answer in context, ending with the end-of-turn token.

    The answer is tokenized as part of prompt_text + answer + end-of-turn, so token
    boundaries match how the assistant turn appears after the prompt.
    """
    eot_id = tok.convert_tokens_to_ids(END_OF_TURN)
    full = tok(prompt_text + gold_answer + END_OF_TURN, add_special_tokens=False)['input_ids']
    prompt_ids = list(prompt_ids)
    if full[:len(prompt_ids)] != prompt_ids:
        raise ValueError('Prompt tokens are not a prefix of the in-context tokenization')
    answer = full[len(prompt_ids):]
    if len(answer) < 2 or answer[-1] != eot_id:
        raise ValueError('Reference answer must have at least one token and end with end-of-turn')
    return answer


def compare_item(expected_prompt_ids, expected_full_ids, expected_labels,
                 prompt_ids, answer_ids, ignore_index=-100):
    """Dependency-free comparison of rendered tokens with a recorded scoring trace.

    Returns a list of mismatch descriptions (empty when everything matches).
    """
    problems = []
    if list(prompt_ids) != list(expected_prompt_ids):
        problems.append('prompt token IDs differ from fixture')
    full = list(prompt_ids) + list(answer_ids)
    if expected_full_ids is not None and full != list(expected_full_ids):
        problems.append('prompt+answer token IDs differ from scoring trace')
    if expected_labels is not None:
        scored = [t for t in expected_labels if t != ignore_index]
        if scored != list(answer_ids):
            problems.append('answer token IDs differ from scoring-trace labels')
        if len(expected_labels) != len(full):
            problems.append('label length differs from rendered sequence length')
    return problems
