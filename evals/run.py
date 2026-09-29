#!/usr/bin/env python3
"""Synthetic orchestrator-stage ablation; never evidence of downstream skill effect."""
import argparse, copy, datetime, json, os, re, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ARMS=['full','baseline','without_value_filter','without_natural_trigger']

def fixtures():
    evidence={'source_complete':True,'baseline_hosts_failed':['host-a','host-b'],'explicit_improved':True,'natural_triggered':True,'natural_output_improved':True,'ablation_supports':True,'generalization_pass':True,'negative_control_pass':True,'independent_review_pass':True,'post_install_verified':False}
    def case(id,domain,pain,source,expected,**extra):
        return {'id':id,'domain':domain,'confirmed_user_context':pain,'source':{'url':'https://example.org/method/'+id,'body':source},'existing_skills':[],'evidence':copy.deepcopy(evidence),'expected':expected,**extra}
    a=case('work_delivery','work','过去四次客户交接三次漏写负责人，导致返工和一天延期。目标是减少交接遗漏。','交接前把每个交付事项与负责人、截止时间对应。信息缺失先向当前负责人核实，再形成可执行交接。','activate')
    b=case('life_packing','life','每周带孩子外出，最近四次有三次漏带已计划的物品，途中折返。已有每周行程复盘。','在既有出行复盘中，根据下次行程逐项确定要带的物品；离家前按实际行程复核已装包物品。','activate')
    c=case('unrelated_hobby','life','用户当前核心任务是缩短项目交接返工；没有陶艺学习计划，也没有相关困难。','欣赏陶器时依次看釉色、器型和纹样，每周整理一张偏好图。','reject')
    d=case('already_covered','work','交接遗漏是反复痛点，但已有技能已完整实施此方法，没有新增问题或方法差别。','交接时列出事项、负责人和截止日期，缺失信息先核实。','reject',existing_skills=[{'name':'handoff','description':'交接时自动逐项核实事项、负责人、截止日期。','body':'生成交接前核实事项、负责人和截止日期，缺项先询问。'}])
    e=case('incomplete_source','work','多次需求讨论漏记验收条件，造成返工。','只有标题：让需求沟通更高效。正文无法访问。','retain');e['evidence']['source_complete']=False
    f=copy.deepcopy(a);f['id']='baseline_already_green';f['evidence']['baseline_hosts_failed']=[];f['evidence']['baseline_success_all']=True;f['expected']='retain'
    g=copy.deepcopy(b);g['id']='explicit_only';g['evidence']['natural_triggered']=False;g['evidence']['natural_output_improved']=False;g['expected']='retain'
    h=copy.deepcopy(a);h['id']='negative_regression';h['evidence']['negative_control_pass']=False;h['expected']='retain'
    return [a,b,c,d,e,f,g,h]

def method(root,arm):
    if arm=='baseline': return ''
    files=['SKILL.md','references/evaluation.md']
    texts={f:(root/f).read_text() for f in files}
    full='\n\n'.join('## '+f+'\n'+t for f,t in texts.items())
    if arm=='without_value_filter':
        # Remove entire value-classification stage plus every cross-reference to its gate.
        full=re.sub(r'### 2\. 生成前判断价值.*?(?=### 3\.)','',full,flags=re.S)
        full=full.replace('先筛 P0/P1 价值，','').replace('本规程只用于 P0/P1 候选，','本规程用于候选，').replace('仅 P0/P1、','仅').replace('P0/P1 因果路径；','')
        full=full.replace('先检查宿主提供的技能名称和描述，读最相关已有技能。可补强则制作修订候选；目标/消费者实质不同才新建。不做一篇笔记一个 skill。','检查已有技能；有相同目标则修订，否则新建。')
    if arm=='without_natural_trigger':
        # Remove only the natural-discovery requirement; preserve neighboring gates.
        full=full.replace('真实改善与自然触发后启用','真实改善后启用').replace('验证效果与无感触发','验证效果')
        full=full.replace('另测普通请求的自然触发、不同形状场景和不适用反例','另测不同形状场景和不适用反例')
        full=full.replace('提醒后有用也不能证明无感使用。','').replace('真实改善、自然触发均成立','真实改善成立')
        full=full.replace('name/description 实际可见、自然调用及产物改善','name/description 实际可见及显式调用的产物改善')
        full=full.replace('安装后触发或效果不成立','安装后显式调用效果不成立')
        full=full.replace('消融效果、自然触发、安装后可用','消融效果、安装后可用')
        full=full.replace('不计入自然触发','验证显式调用')
        full=full.replace('| 正常安装候选，原普通请求 | 没提醒能否自然发现、使用并改善？ |\n','')
        full=full.replace('自然触发臂只通过宿主正常发现 description；不显式塞正文，不点技能名，不暗示使用新方法。无法隔离就不能报触发/效果 PASS。','')
        full=full.replace('自然触发且产物改善；','').replace('实际宿主可见与自然消费','实际宿主可见与显式消费').replace('各臂触发和改善数及分母','各臂改善数及分母')
    return full

def validate(output,cases):
    rows=output.get('decisions',[]) if isinstance(output,dict) else []
    found={r.get('id'):r for r in rows if isinstance(r,dict)}
    results=[]
    for c in cases:
        r=found.get(c['id'],{})
        allowed=['activate'] if c['expected']=='activate' else ['reject','retain']
        ok=r.get('action') in allowed and isinstance(r.get('reason'),str) and bool(r['reason'].strip())
        results.append({'id':c['id'],'allowed_actions':allowed,'workflow_expected':c['expected'],'actual':r.get('action'),'pass':ok,'workflow_match':r.get('action')==c['expected']})
    return {'pass':len(rows)==len(cases) and len(found)==len(cases) and all(r['pass'] for r in results),'cases':results}

def selftest(cases):
    good={'decisions':[{'id':c['id'],'action':c['expected'],'reason':'预先定义的证据满足相应动作条件。'} for c in cases]}
    assert validate(good,cases)['pass']
    for i in range(len(cases)):
        bad=copy.deepcopy(good);bad['decisions'][i]['action']='activate' if cases[i]['expected']!='activate' else 'reject'
        assert not validate(bad,cases)['pass']
    assert not validate({'decisions':[]},cases)['pass']
    return {'positive_controls':1,'negative_controls':len(cases)+1,'pass':True,'scope':'action-contract only; reason semantics require independent review'}

def preserve_exact(path,text):
    if path.exists() and path.read_text()!=text:
        raise ValueError('Cached experiment input changed: '+str(path.name)+'. Use a new experiment directory; existing outputs were not reused.')
    if not path.exists():path.write_text(text)

def execute(prompt,schema_path,out,timeout,key,private):
    auth=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))/'auth.json'
    h=Path(tempfile.mkdtemp(prefix='stp-eval-'));(h/'.codex').mkdir();(h/'work').mkdir()
    try:
        if auth.exists():shutil.copy2(auth,h/'.codex/auth.json')
        env=os.environ.copy();env['HOME']=str(h);env['CODEX_HOME']=str(h/'.codex')
        cmd=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json','-C',str(h/'work'),'--output-schema',str(schema_path),'-o',str(out),'-']
        start=datetime.datetime.now(datetime.timezone.utc).isoformat()
        r=subprocess.run(cmd,input=prompt,text=True,capture_output=True,env=env,timeout=timeout)
        (private/(key+'.jsonl')).write_text(r.stdout);(private/(key+'.stderr')).write_text(r.stderr)
        data=json.loads(out.read_text()) if out.exists() else {}
        events=[json.loads(l) for l in r.stdout.splitlines() if l.startswith('{')]
        return data,{'run':key,'status':'completed' if r.returncode==0 else 'host_error','started_at':start,'returncode':r.returncode,'usage':[e['usage'] for e in events if 'usage' in e]}
    except subprocess.TimeoutExpired as e:
        (private/(key+'.timeout.txt')).write_text(str(e.stdout or '')+'\n'+str(e.stderr or ''))
        return {},{'run':key,'status':'timeout'}
    except (json.JSONDecodeError,OSError) as e:
        (private/(key+'.error.txt')).write_text(str(e))
        return {},{'run':key,'status':'output_or_host_error'}
    finally:shutil.rmtree(h)

def run_stage(pub,explicit_output,arms,items,prompts,schema,validator,timeout,repeats,stage,fixture_document):
    # No explicit output directory means a read-only replay, with no CLI invocation.
    live=explicit_output is not None
    if live:pub.mkdir(parents=True,exist_ok=True)
    schema_text=json.dumps(schema,indent=2)+'\n'
    fixture_text=json.dumps(fixture_document,ensure_ascii=False,indent=2)+'\n'
    for path,expected in [(pub/'output.schema.json',schema_text),(pub/'fixtures.json',fixture_text)]+[(pub/(arm+'.prompt.txt'),prompts[arm]) for arm in arms]:
        if live:preserve_exact(path,expected)
        elif not path.exists() or path.read_text()!=expected:raise ValueError('Replay input missing or changed: '+path.name)
    if live:
        config={'cli':subprocess.check_output(['codex','--version'],text=True).strip(),'flags':['--ignore-user-config','--ephemeral','--skip-git-repo-check','--sandbox','read-only','--json'],'model_override':None,'isolation':'temporary HOME and CODEX_HOME, auth only, empty cwd','stage':stage}
        preserve_exact(pub/'run-config.json',json.dumps(config,sort_keys=True,indent=2)+'\n')
    previous=json.loads((pub/'summary.json').read_text()).get('runs',[]) if (pub/'summary.json').exists() else []
    previous={r['run']:r for r in previous};summary=[]
    for arm in arms:
        for repeat in range(1,repeats+1):
            key=f'{arm}-{repeat}';out=pub/(key+'.json')
            if out.exists():
                data=json.loads(out.read_text());rec={**previous.get(key,{}),'run':key,'status':previous.get(key,{}).get('status','replayed')}
            elif live:
                private=pub/'.private-raw';private.mkdir(exist_ok=True)
                data,rec=execute(prompts[arm],pub/'output.schema.json',out,timeout,key,private)
            else:data,rec={},{'run':key,'status':'missing_output'}
            rec.update(validator(data,items));summary.append(rec);print(json.dumps(rec,ensure_ascii=False),flush=True)
            if live:(pub/'summary.json').write_text(json.dumps({'scope':'synthetic '+stage+' stage; repeated draws are not independent real incidents','runs':summary},ensure_ascii=False,indent=2)+'\n')
    fatal=any(r['status'] not in ('completed','replayed') or (r['run'].startswith('full-') and not r['pass']) for r in summary)
    return 1 if fatal else 0

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--skill-root',type=Path,default=ROOT/'frozen-skill');ap.add_argument('--repeats',type=int,default=3);ap.add_argument('--timeout',type=int,default=180);ap.add_argument('--selftest-only',action='store_true');ap.add_argument('--output-dir',type=Path);ap.add_argument('--arms',nargs='+',choices=ARMS,default=ARMS);args=ap.parse_args()
    if args.repeats<1:ap.error('--repeats must be positive')
    if args.timeout<1:ap.error('--timeout must be positive')
    items=fixtures();check=selftest(items)
    if args.selftest_only:print(json.dumps(check));return 0
    schema={'type':'object','properties':{'decisions':{'type':'array','items':{'type':'object','properties':{'id':{'type':'string'},'action':{'type':'string','enum':['reject','retain','activate']},'reason':{'type':'string'}},'required':['id','action','reason'],'additionalProperties':False}}},'required':['decisions'],'additionalProperties':False}
    prompts={}
    for arm in args.arms:
        instructions=method(args.skill_root,arm)
        prompt='处理下面提供的收藏方法及当前证据，决定每项下一步。activate 表示允许开始安装并随后验证宿主消费；retain 表示保留待证候选、不启用；reject 表示不生成/不继续该方法。证据字段是上游已给出的评估记录，按其值判断，不调用工具，不读其他文件，不实施安装。给出每项 action 与具体理由。\n'
        if instructions:prompt+='\n工作方法：\n'+instructions
        prompt+='\n输入：\n'+json.dumps([{k:v for k,v in c.items() if k!='expected'} for c in items],ensure_ascii=False)
        prompts[arm]=prompt
    fixture_document={'provenance':'Entirely synthetic public fixtures; not actual user incidents. Evidence fields are supplied upstream stage inputs, not real experimental outcomes.','cases':items}
    return run_stage(args.output_dir.resolve() if args.output_dir else ROOT/'results',args.output_dir,args.arms,items,prompts,schema,validate,args.timeout,args.repeats,'activation',fixture_document)
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,json.JSONDecodeError) as e:raise SystemExit(str(e))
