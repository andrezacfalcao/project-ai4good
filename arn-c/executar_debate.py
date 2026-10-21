"""Arena ARN-C: local + remoto, pesquisa real e thinking. Auditar não gera rodadas."""
import argparse
import hashlib
import json
import os
import sys
import urllib.error
from pathlib import Path

import ponte_debate as local
from agentes_remotos import GeminiAgent, now

ROOT = Path(__file__).resolve().parent


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')
    os.replace(temporary, path)


def read_json(path):
    return json.loads(path.read_text(encoding='utf8'))


def audit(folder):
    paths = sorted((folder / 'rodadas').glob('rodada-*.json'))
    rounds = [read_json(p) for p in paths]
    identifiers = [r['round'] for r in rounds]
    if identifiers != list(range(1, 21)):
        raise ValueError('O conjunto selecionado não contém exatamente as rodadas 01–20, sem lacunas.')
    markdown = sorted((folder / 'rodadas').glob('rodada-*.md'))
    if [p.stem for p in markdown] != [p.stem for p in paths]:
        raise ValueError('Os registros Markdown e JSON não correspondem ao mesmo conjunto.')
    manifest = read_json(folder / 'manifesto.json') if (folder / 'manifesto.json').exists() else {}
    for name, expected in manifest.get('sha256', {}).items():
        if hashlib.sha256((folder / 'rodadas' / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'O registro preservado foi alterado: {name}')
    calls = [r[key] for r in rounds for key in ('local_reply', 'local_opening')]
    report = {'rounds': len(rounds), 'markdown_files': len(markdown), 'json_files': len(paths),
              'local_stages': len(calls), 'local_requests_with_retries': sum(len(c['attempts']) for c in calls),
              'saved_protocols': sorted(set(c.get('protocol_version', 0) for c in calls)),
              'local_models': sorted(set(c['model'] for c in calls)),
              'new_rounds_generated': 0,
              'runtime_web_evidence_rounds': sum(bool(r.get('research', {}).get('web_search_executed')) for r in rounds),
              'thinking_evidence_rounds': sum(any((r.get('remote_calls', {}).get(k, {}).get('thought_tokens_observed') or 0)>0 for k in ('opening','defense','judge')) for r in rounds)}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def object_schema(properties):
    return {'type': 'OBJECT', 'properties': properties, 'required': list(properties)}


SPEECH_SCHEMA = object_schema({'fala': {'type': 'STRING'}, 'justificativa_publica': {'type': 'STRING'},
                              'limite': {'type': 'STRING'}})
STEP_SCHEMA = object_schema({key: {'type': 'STRING'} for key in ('title','action','owner','indicator','limit')})
JUDGE_SCHEMA = object_schema({**{key: {'type': 'STRING'} for key in ('summary','verdict','plan_update','pending','memory','periodic_summary')},
                             'quality_issues': {'type':'ARRAY','items':{'type':'STRING'}},
                             'sources': {'type':'ARRAY','items':{'type':'STRING'}},
                             'final_steps': {'type':'ARRAY','items':STEP_SCHEMA}})


def render_round(entry, folder):
    j = entry['judgment']
    blocks = [f'# Rodada {entry["round"]:02} — {entry["topic"]}',
              f'Cenário: **{entry["scenario"]}**. Protocolo 6. Português brasileiro.',
              '## O que foi discutido', j['summary'],
              '## Turno 1 — Trabalhista remoto', entry['opening'],
              '## Turno 1 — Liberal local', entry['local_reply']['response'],
              '## Turno 2 — Liberal local', entry['local_opening']['response'],
              '## Turno 2 — Defesa trabalhista remota', entry['defense'],
              '## Parecer do juiz remoto', j['verdict'],
              '## Atualização da estratégia', j['plan_update'],
              '## Pendência', j['pending'],
              '## Busca executada nesta rodada', entry['research']['response'],
              '## Fontes da busca', '\n'.join('- '+u for u in entry['research']['public_sources']),
              '## Rastreabilidade',
              'O JSON desta rodada contém os payloads, respostas públicas, consultas, fontes, contadores de thinking e todas as tentativas locais/remotas. Justificativa pública não é transcrição do pensamento interno.']
    if j.get('periodic_summary'):
        blocks += ['## Síntese periódica', j['periodic_summary']]
    for label, call in [('Resposta local',entry['local_reply']),('Abertura local',entry['local_opening'])]:
        blocks += [f'## Qualidade — {label}', f'Aprovada nos filtros: {call["accepted"]}. Motivos: '+', '.join(call['quality']['reasons'])]
    (folder / 'rodadas' / f'rodada-{entry["round"]:02}.md').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')


def execute(config, output, scenario, resume):
    if config['rounds'] != 20 or [t['round'] for t in config['topics']] != list(range(1,21)):
        raise ValueError('Esta arena exige exatamente vinte temas e rodadas por execução.')
    if not os.environ.get('GEMINI_API_KEY'):
        raise RuntimeError('GEMINI_API_KEY não configurada; nenhuma nova rodada foi executada.')
    if output.resolve() == (ROOT / 'resultados' / 'ultima_execucao').resolve():
        raise ValueError('A execução selecionada é preservada. Use outro diretório de saída.')
    settings = config['agents']
    agents = {name:GeminiAgent(ROOT,name,settings[name]) for name in ('trabalhista','juiz','pesquisador')}
    local.MODEL = settings['liberal']['model']
    local.PROFILE = (ROOT / settings['liberal']['prompt_file']).read_text(encoding='utf8')
    effective_models = {name:agent.model for name,agent in agents.items()}
    effective_models['liberal'] = local.MODEL
    config_digest = hashlib.sha256(json.dumps({'config':config,'effective_models':effective_models},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    dependencies = [ROOT/name for name in ('executar_debate.py','agentes_remotos.py','ponte_debate.py')]
    dependencies += sorted((ROOT/'prompts').glob('*.md'))
    code_digest = hashlib.sha256(b''.join(p.read_bytes() for p in dependencies)).hexdigest()
    header_file = output / 'execucao.json'
    if output.exists():
        if not resume or not header_file.exists():
            raise ValueError('O destino já existe. Use um diretório novo ou --retomar para esta mesma configuração.')
        header = read_json(header_file)
        if (header.get('config_sha256'),header.get('code_sha256'),header.get('scenario')) != (config_digest,code_digest,scenario):
            raise ValueError('Não é possível misturar configurações, código ou cenários na mesma execução.')
    else:
        output.mkdir(parents=True)
        header = {'status':'em_execucao','protocol_version':6,'started':now(),'scenario':scenario,
                  'rounds_completed':0,'config_sha256':config_digest,'code_sha256':code_digest,
                  'effective_models':effective_models}
        write_json(header_file,header)
        write_json(output/'configuracao.json',config)
    (output/'rodadas').mkdir(exist_ok=True)
    (output/'parcial').mkdir(exist_ok=True)
    history = []; memory = ''; completed = []
    for topic in config['topics']:
        n = topic['round']; final = output/'rodadas'/f'rodada-{n:02}.json'
        if final.exists():
            entry=read_json(final);completed.append(entry);memory=entry['judgment']['memory'][:1800]
            history += [entry['local_reply']['response'],entry['local_opening']['response']]
            render_round(entry,output)
            continue
        checkpoint = output/'parcial'/f'rodada-{n:02}.json'
        state = read_json(checkpoint) if checkpoint.exists() else {'round':n,'topic':topic['title'],'scenario':scenario,'previous_memory':memory,'remote_attempts':{}}
        def remote(slot, agent, prompt, schema=None, search=False):
            if state.get(slot,{}).get('accepted'):
                return state[slot]
            attempts=state['remote_attempts'].setdefault(slot,[])
            for _ in range(2):
                feedback='\nCumpra o formato e pesquise efetivamente; não invente fontes.' if attempts else ''
                record=agent.generate(prompt+feedback,schema=schema,search=search)
                attempts.append(record);write_json(checkpoint,state)
                if record['accepted']:
                    state[slot]=record;write_json(checkpoint,state);return record
            raise RuntimeError(f'Rodada {n}: etapa remota {slot} não validada. Veja o checkpoint; não houve substituição por texto fixo.')
        context={'tema':topic['title'],'desafio':topic['challenge'],'cenario':config['scenarios'][scenario],
                 'impacto_ia':'Relacionar o tema a automação, gestão algorítmica, distribuição de ganhos ou acesso a oportunidades.',
                 'memoria_anterior':memory}
        research=remote('research',agents['pesquisador'],json.dumps(context,ensure_ascii=False)+'\nUse Google Search agora e identifique evidências, fontes primárias, contrapontos e incertezas. Não se limite a links conhecidos.',search=True)
        evidence={'pesquisa':research['response'][:6000],'fontes':research['public_sources'][:12]}
        opening=remote('opening',agents['trabalhista'],json.dumps({'contexto':context,'evidencias':evidence,'tarefa':'Abra a rodada com uma proposta trabalhista de até 90 palavras, mecanismo e limite. Não narre outros papéis.'},ensure_ascii=False),schema=SPEECH_SCHEMA)
        speech=opening['data']['fala']
        if 'local_reply' not in state:
            state['local_reply']=local.call_qwen(n,'resposta',f'Tema: {topic["title"]}. O trabalhista disse: {speech}\nConteste o custo ou incentivo. Trate efeitos da IA neste tema. Retorne risco e pergunta.',topic,history[-12:],persist=False,agent_settings=settings['liberal'])
            write_json(checkpoint,state)
        reply=state['local_reply']
        if 'local_opening' not in state:
            question=f'Abra outro argumento liberal sobre {topic["title"]}: {topic["second_focus"]}. Considere IA, sem repetir o risco anterior.'
            state['local_opening']=local.call_qwen(n,'abertura',question,topic,(history+[reply['response']])[-12:],second_task=question,own_previous=reply['response'],persist=False,agent_settings=settings['liberal'])
            write_json(checkpoint,state)
        local_open=state['local_opening']
        defense=remote('defense',agents['trabalhista'],json.dumps({'contexto':context,'evidencias':evidence,'sua_abertura':speech,'resposta_real_qwen':reply['response'],'abertura_real_qwen':local_open['response'],'tarefa':'Responda às objeções realmente recebidas em até 90 palavras. Reconheça falhas, revise sua proposta quando necessário; não atribua ao Qwen argumentos que ele não fez.'},ensure_ascii=False),schema=SPEECH_SCHEMA)
        exchange={'abertura_trabalhista':speech,'resposta_local':reply['response'],'abertura_local':local_open['response'],'defesa_trabalhista':defense['data']['fala']}
        judge=remote('judge',agents['juiz'],json.dumps({'contexto':context,'evidencias':evidence,'quatro_falas':exchange,'filtros_locais':[reply['quality'],local_open['quality']],
              'tarefa':'Julgue o intercâmbio real; resumo, crítica, passo revisto, pendência e memória de até120 palavras. Na rodada múltipla de 5, inclua síntese periódica. Nas demais, periodic_summary vazio. Somente na 20, final_steps tem 6 passos conectados com responsável, indicador e limite; nas demais, array vazio. Não dê vitória automática nem trate hipóteses como resultados empíricos.','rodada':n},ensure_ascii=False),schema=JUDGE_SCHEMA)
        judgment=judge['data']
        if n==20 and len(judgment['final_steps'])!=6:
            raise RuntimeError('A conclusão precisa de seis passos; checkpoint preservado, sem resultado inventado.')
        entry={'round':n,'topic':topic['title'],'challenge':topic['challenge'],'scenario':scenario,'protocol_version':6,
               'opening':speech,'local_reply':reply,'local_opening':local_open,'defense':defense['data']['fala'],
               'judgment':judgment,'previous_memory':memory,'research':research,
               'remote_calls':{k:state[k] for k in ('opening','defense','judge')},
               'remote_attempts':state['remote_attempts'],'created_at':now()}
        write_json(final,entry);render_round(entry,output);checkpoint.unlink(missing_ok=True)
        completed.append(entry);memory=judgment['memory'][:1800];history += [reply['response'],local_open['response']]
        header['rounds_completed']=len(completed);write_json(header_file,header)
        print(f'Rodada {n:02}/20 salva: {topic["title"]}',flush=True)
    header.update(status='concluida',finished=now(),rounds_completed=20,
                  runtime_web_evidence_rounds=sum(bool(e['research']['web_search_executed']) for e in completed),
                  thinking_evidence_rounds=sum(any((e['remote_calls'][k].get('thought_tokens_observed') or 0)>0 for k in ('opening','defense','judge')) for e in completed))
    write_json(header_file,header)
    rows=['# Índice — vinte rodadas desta execução',f'Cenário: {scenario}. Protocolo6.','| Rodada | Tema | O que foi discutido |','|---|---|---|']
    rows += [f'| [Rodada {e["round"]:02}](rodadas/rodada-{e["round"]:02}.md) | {e["topic"]} | {e["judgment"]["summary"].replace("|","/")} |' for e in completed]
    (output/'indice_rodadas.md').write_text('\n\n'.join(rows[:2])+'\n\n'+'\n'.join(rows[2:])+'\n')
    steps=completed[-1]['judgment']['final_steps']
    (output/'resultado_final.md').write_text('# Estratégia final — proposta a avaliar\n\n'+'\n\n'.join(f'## {s["title"]}\n\n{s["action"]}\n\nResponsável: {s["owner"]}. Indicador: {s["indicator"]}. Limite: {s["limit"]}.' for s in steps))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--auditar',action='store_true',help='Conferir as vinte rodadas selecionadas, sem rede e sem gerar falas.')
    mode.add_argument('--executar',action='store_true',help='Executar uma nova arena com APIs reais; exige credencial.')
    parser.add_argument('--saida',type=Path)
    parser.add_argument('--cenario',choices=['utopia','distopia'],default='utopia')
    parser.add_argument('--retomar',action='store_true')
    args=parser.parse_args()
    config=read_json(ROOT/'configuracao.json')
    if args.auditar:
        audit(args.saida or ROOT/config['historical_results']);return
    if args.saida is None:
        parser.error('--executar exige --saida; a execução preservada nunca é sobrescrita.')
    execute(config,args.saida.resolve(),args.cenario,args.retomar)


if __name__=='__main__':
    try:
        main()
    except (RuntimeError,ValueError,urllib.error.URLError) as error:
        print(f'Erro: {error}',file=sys.stderr)
        raise SystemExit(1)
