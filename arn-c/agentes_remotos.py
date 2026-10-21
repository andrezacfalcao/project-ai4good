"""Gemini REST com busca nativa e thinking; sem respostas remotas pré-definidas."""
import json
import os
import re
import urllib.error
import urllib.request
from copy import deepcopy
from datetime import datetime
from pathlib import Path


def now():
    return datetime.now().astimezone().isoformat()


def load_json_response(text):
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*|\s*```$', '', text)
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError('A resposta remota precisa ser um objeto JSON.')
    return value


def public_response(raw):
    """Registra saídas públicas e metadados, sem textos de pensamento interno."""
    value = deepcopy(raw)
    for candidate in value.get('candidates', []):
        parts = candidate.get('content', {}).get('parts', [])
        candidate.setdefault('content', {})['parts'] = [p for p in parts if not p.get('thought')]
    return value


class GeminiAgent:
    def __init__(self, root: Path, name: str, settings: dict):
        self.name = name
        self.settings = settings
        self.model = os.environ.get('GEMINI_MODEL', settings['model'])
        if not re.fullmatch(r'[A-Za-z0-9._-]+', self.model):
            raise ValueError('GEMINI_MODEL inválido.')
        self.profile = (root / settings['prompt_file']).read_text(encoding='utf8')
        self.key = os.environ.get('GEMINI_API_KEY')
        if not self.key:
            raise RuntimeError('Defina GEMINI_API_KEY no ambiente. Nenhuma chamada remota foi feita.')

    def generate(self, prompt, *, schema=None, search=False):
        if len(prompt) > self.settings['context_max_chars']:
            raise ValueError(f'Contexto excede o limite da aplicação para {self.name}; reduza a memória.')
        thinking = {'includeThoughts': False}
        if self.model.startswith('gemini-2.5'):
            thinking['thinkingBudget'] = self.settings['thinking_budget']
        elif self.model.startswith(('gemini-3', 'gemini-4')):
            thinking['thinkingLevel'] = 'high'
        else:
            raise ValueError('Modelo sem configuração de thinking documentada neste adaptador.')
        generation = {'temperature': self.settings['temperature'],
                      'maxOutputTokens': self.settings['max_output_tokens'],
                      'thinkingConfig': thinking}
        if schema:
            generation.update(responseMimeType='application/json', responseSchema=schema)
        payload = {'systemInstruction': {'parts': [{'text': self.profile}]},
                   'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
                   'generationConfig': generation}
        if search:
            payload['tools'] = [{'google_search': {}}]
        record = {'agent': self.name, 'requested_model': self.model, 'started': now(),
                  'request': payload, 'search_requested': search, 'thinking_requested': True}
        url = f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent'
        request = urllib.request.Request(url, data=json.dumps(payload, ensure_ascii=False).encode(),
                                         headers={'x-goog-api-key': self.key, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                raw = json.load(response)
        except urllib.error.HTTPError as error:
            # Não registrar cabeçalhos de autenticação nem corpo que possa conter dados da credencial.
            record.update(accepted=False,finished=now(),error=f'Gemini retornou HTTP {error.code}; verifique modelo, credencial, cota e ferramentas.')
            return record
        except (urllib.error.URLError, TimeoutError) as error:
            record.update(accepted=False,finished=now(),error='Falha de conexão ou timeout na API Gemini.')
            return record
        candidates = raw.get('candidates', [])
        candidate = candidates[0] if candidates else {}
        text = '\n'.join(p.get('text', '') for p in candidate.get('content', {}).get('parts', []) if not p.get('thought'))
        grounding = candidate.get('groundingMetadata', {})
        chunks = grounding.get('groundingChunks', [])
        urls = [c['web']['uri'] for c in chunks if c.get('web', {}).get('uri')]
        usage = raw.get('usageMetadata', {})
        record.update(finished=now(), response=text, raw_response=public_response(raw),
                      model_version=raw.get('modelVersion'), grounding=grounding,
                      web_search_executed=bool(grounding.get('webSearchQueries') and urls),
                      thought_tokens_observed=usage.get('thoughtsTokenCount'),
                      public_sources=urls, finish_reason=candidate.get('finishReason'))
        if not text or candidate.get('finishReason') not in ('STOP', None):
            record['accepted'] = False
            record['error'] = 'Saída remota vazia, bloqueada ou interrompida.'
            return record
        if search and not record['web_search_executed']:
            record['accepted'] = False
            record['error'] = 'A API não retornou consultas e fontes que comprovem a execução da busca.'
            return record
        try:
            record['data'] = load_json_response(text) if schema else {'text': text}
            record['accepted'] = True
        except ValueError:
            record['accepted'] = False
            record['error'] = 'O modelo não cumpriu o JSON solicitado.'
        return record
