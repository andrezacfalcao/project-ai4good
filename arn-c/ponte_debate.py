"""
Módulo Refinado de Execução e Avaliação do Qwen Local (Ollama)
Controles:
1. Esquema JSON estrito (risco e pergunta)
2. Trava anti-vazamento de temas passados (negative_anchors)
3. Trava anti-repetição isolada no campo 'risco' (Turno 1 vs Turno 2)
4. Âncora ideológica estritamente liberal de livre mercado
5. Anti-eco de n-gramas e similaridade histórica
"""

import datetime as dt
import difflib
import json
import os
import re
import time
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODEL = 'qwen2.5:1.5b'
ENDPOINT = 'http://127.0.0.1:11434/api/chat'

PROFILE = (
    'Você é estritamente um economista LIBERAL DE LIVRE MERCADO que debate com um trabalhista. '
    'Fale somente por si. Responda em português brasileiro em DUAS frases curtas. '
    'Na primeira frase, explique um custo financeiro, obstáculo à contratação ou incentivo econômico adverso que a proposta ignora, defendendo livre iniciativa e corte de encargos. '
    'Na segunda frase, proponha uma solução voluntária de mercado ou faça uma pergunta prática e concreta. '
    'Nunca defenda aumento de gastos públicos, tributos, subsídios estatais ou imposição de obrigações compulsórias a empresas. '
    'Não fale como juiz, não atribua falas ao juiz, não copie instruções e não invente dados.'
)

def now():
    return dt.datetime.now().astimezone().isoformat()

def normalize(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9 ]', ' ', value)

def words(value):
    return normalize(value).split()

def grams(value, n=6):
    tokens = words(value)
    return set(tuple(tokens[i:i+n]) for i in range(max(0, len(tokens)-n+1)))

def assess(response, prompt, topic, prior, finish, fields=None, own_previous=""):
    reasons = []
    tokens = words(response)
    norm = ' '.join(tokens)
    
    # 1. Comprimento
    if not (12 <= len(tokens) <= 125):
        reasons.append(f'comprimento fora de 12–125 palavras (total: {len(tokens)})')
    if finish == 'length':
        reasons.append('resposta interrompida pelo limite de tokens')
        
    # 2. Idioma português
    pt = {'o','a','os','as','de','do','da','dos','das','em','que','para','uma','um','na','no','com','por','se','mas','e','ao','sem','isso','pode','custos','trabalho','empresa','mercado'}
    en = {'the','and','should','would','with','workers','this','that','is','are','be','must','because','of','to'}
    pt_hits = sum(x in pt for x in tokens)
    en_hits = sum(x in en for x in tokens)
    if pt_hits < 2 or en_hits > pt_hits:
        reasons.append('indício de idioma diferente de português')
        
    # 3. Não simular outros papéis ou instruções
    for phrase in ['voce e o agente', 'responda somente', 'escreva um argumento', 'fala recebida', 'nao copie', 'known evidence', 'round ', 'sua tarefa']:
        if phrase in norm:
            reasons.append('reprodução de instruções do prompt')
            break
    if any(p in norm for p in ['o juiz sugere','o juiz afirma','o juiz menciona','o juiz propoe','o juiz recomenda']):
        reasons.append('atribui fala indevidamente ao juiz')
        
    # 4. Anti-eco de entrada
    output_grams = grams(response)
    prompt_grams = grams(prompt)
    copy_ratio = len(output_grams & prompt_grams) / max(1, len(output_grams))
    if copy_ratio > 0.45:
        reasons.append('mais de 45% dos trechos de seis palavras copiam a entrada')
        
    # 5. Trava específica anti-repetição de RISCO (Turno 1 vs Turno 2 da mesma rodada)
    if fields and own_previous:
        prev_lines = own_previous.split('\n')
        prev_risco = prev_lines[0].replace('Risco:', '').strip() if len(prev_lines) > 0 else ""
        curr_risco = fields.get('risco', '').strip()
        if prev_risco and curr_risco:
            sim_risco = difflib.SequenceMatcher(None, normalize(curr_risco), normalize(prev_risco)).ratio()
            if sim_risco >= 0.65:
                reasons.append(f'o risco formulado é quase idêntico ao do turno 1 ({round(sim_risco*100)}% similar); traga uma objeção nova')

    # 6. Trava anti-vazamento de temas passados (negative_anchors)
    negative_anchors = topic.get('negative_anchors', [])
    for neg in negative_anchors:
        if normalize(neg).strip() in norm:
            reasons.append(f'vazamento de tema anterior detectado (termo indesejado: "{neg}")')
            break
            
    # 7. Similaridade global com respostas locais anteriores
    max_sim = max((difflib.SequenceMatcher(None, norm, ' '.join(words(p))).ratio() for p in prior), default=0)
    if max_sim >= 0.85:
        reasons.append('similaridade global superior a 85% com uma resposta recente')
        
    # 8. Menção aos termos-âncora do tema atual
    anchors = topic.get('anchors', [])
    if anchors and not any(normalize(a).strip() in norm for a in anchors):
        reasons.append('não menciona nenhum termo específico do tema atual')
        
    return {
        'passed': not reasons,
        'reasons': reasons,
        'words': len(tokens),
        'max_similarity': round(max_sim, 3),
        'input_copy_ratio': round(copy_ratio, 3)
    }

def call_qwen(n, stage, prompt_text, topic, history, second_task="", own_previous="", *, persist=True, agent_settings=None):
    settings = agent_settings or {}
    schema = {
        'type': 'object',
        'properties': {
            'risco': {'type': 'string'},
            'pergunta': {'type': 'string'}
        },
        'required': ['risco', 'pergunta'],
        'additionalProperties': False
    }
    attempts = []
    chosen = None
    
    # Trava de instruções no prompt
    negative_clause = ""
    if topic.get('negative_anchors'):
        negative_clause = f" (Atenção: Não mencione temas anteriores como {', '.join(topic['negative_anchors'])})."
    
    for attempt in range(1, 4):
        feedback = ""
        if attempts:
            feedback = f"\nATENÇÃO: A tentativa anterior foi rejeitada pelo motivo: {', '.join(attempts[-1]['quality']['reasons'])}. Reformule de forma original e estritamente liberal sobre {topic['title']}."
            
        system = PROFILE + f" Retorne exclusivamente um JSON com 'risco' e 'pergunta'. Foque exclusivamente em {topic['title']}{negative_clause}."
        messages = [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt_text}]
        
        if stage == 'abertura' and own_previous:
            messages.append({'role': 'assistant', 'content': own_previous})
            messages.append({'role': 'user', 'content': second_task + feedback})
        elif feedback:
            messages[-1]['content'] += feedback
            
        options = {
            'temperature': settings.get('temperature_attempts', [0.25, 0.55, 0.8])[attempt - 1],
            'seed': 20261010 + n * 23 + (0 if stage == 'resposta' else 9) + attempt,
            'num_predict': settings.get('num_predict', 140),
            'num_ctx': settings.get('num_ctx', 1024),
            'repeat_penalty': settings.get('repeat_penalty', 1.18)
        }
        payload = {
            'model': MODEL,
            'stream': False,
            'messages': messages,
            'options': options,
            'format': schema,
            'keep_alive': '15m'
        }
        started = now()
        record = {'attempt': attempt, 'started': started, 'request': payload}
        try:
            req = urllib.request.Request(
                ENDPOINT,
                data=json.dumps(payload, ensure_ascii=False).encode(),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                result = json.load(resp)
            raw = result['message']['content'].strip()
            try:
                fields = json.loads(raw)
                response = f"Risco: {fields['risco']}\nPergunta: {fields['pergunta']}"
            except Exception:
                fields = None
                response = raw
                
            quality = assess(response, '\n'.join(m['content'] for m in messages), topic, history, result.get('done_reason'), fields=fields, own_previous=own_previous)
            if fields is None:
                quality['passed'] = False
                quality['reasons'].append('formato JSON solicitado não cumprido')
                
            record.update({
                'finished': now(),
                'raw_response': result,
                'response': response,
                'quality': quality,
                'parsed_fields': fields
            })
            attempts.append(record)
            if quality['passed']:
                chosen = record
                break
        except Exception as exc:
            record.update({
                'finished': now(),
                'response': '',
                'error': str(exc),
                'quality': {'passed': False, 'reasons': ['erro de conexão ou geração']}
            })
            attempts.append(record)
            time.sleep(1)

    accepted = chosen is not None
    if not chosen:
        valid = [a for a in attempts if a.get('response')]
        chosen = min(valid, key=lambda a: len(a['quality']['reasons'])) if valid else attempts[-1]
        
    entry = {
        'round': n,
        'stage': stage,
        'topic': topic['title'],
        'model': MODEL,
        'protocol_version': 6,
        'location': 'local, Ollama no computador da usuária',
        'accepted': accepted,
        'response': chosen.get('response', ''),
        'selected_attempt': chosen['attempt'],
        'quality': chosen['quality'],
        'attempts': attempts
    }
    path = ROOT / 'chamadas_locais' / f'rodada-{n:02d}-{stage}.json'
    if persist:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2))
    return entry
