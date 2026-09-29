#!/usr/bin/env python3
"""Pre-generation decision stage, separate from activation permission."""
import argparse,copy,datetime,json,os,shutil,subprocess,tempfile
from pathlib import Path
from run import ROOT,fixtures,method,run_stage
ARMS=['full','baseline','without_value_filter']

def cases():
    return [{**{k:v for k,v in c.items() if k not in ('evidence','expected')}, 'expected_create':i<2} for i,c in enumerate(fixtures()[:4])]

def validate(data,items):
    rows=data.get('decisions',[]) if isinstance(data,dict) else []
    found={r.get('id'):r for r in rows if isinstance(r,dict)}
    results=[{'id':c['id'],'expected_create':c['expected_create'],'actual_create':found.get(c['id'],{}).get('create_candidate'),'pass':found.get(c['id'],{}).get('create_candidate') is c['expected_create'] and bool(found.get(c['id'],{}).get('reason','').strip())} for c in items]
    return {'pass':len(rows)==len(items) and len(found)==len(items) and all(r['pass'] for r in results),'cases':results}

def selftest(items):
    good={'decisions':[{'id':c['id'],'create_candidate':c['expected_create'],'reason':'evidence supports this action'} for c in items]};assert validate(good,items)['pass']
    for i in range(len(items)):
        bad=copy.deepcopy(good);bad['decisions'][i]['create_candidate']=not bad['decisions'][i]['create_candidate'];assert not validate(bad,items)['pass']
    assert not validate({'decisions':[]},items)['pass']
    return {'positive':1,'negative':5,'pass':True}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare-only','--selftest-only',dest='selftest_only',action='store_true');ap.add_argument('--timeout',type=int,default=180);ap.add_argument('--output-dir',type=Path);args=ap.parse_args()
    items=cases();check=selftest(items)
    if args.selftest_only:print(json.dumps(check));return 0
    schema={'type':'object','properties':{'decisions':{'type':'array','items':{'type':'object','properties':{'id':{'type':'string'},'create_candidate':{'type':'boolean'},'reason':{'type':'string'}},'required':['id','create_candidate','reason'],'additionalProperties':False}}},'required':['decisions'],'additionalProperties':False}
    prompts={}
    for arm in ARMS:
        prompt='请根据下面的用户上下文、收藏正文和已有技能，判断是否现在制作方法候选（包括新技能或对既有技能的修订候选），供以后验证。create_candidate=true 表示这一步实际应生成候选，false 表示不生成。这里只决定下一步，不安装、不执行方法、不调用工具。逐项给出判断及理由。\n'
        instructions=method(ROOT/'frozen-skill',arm)
        if instructions:prompt+='\n工作方法：\n'+instructions
        prompt+='\n输入：\n'+json.dumps([{k:v for k,v in c.items() if k!='expected_create'} for c in items],ensure_ascii=False)
        prompts[arm]=prompt
    fixture_document={'provenance':'entirely synthetic, not real incidents','cases':items}
    return run_stage(args.output_dir.resolve() if args.output_dir else ROOT/'results/generation',args.output_dir,ARMS,items,prompts,schema,validate,args.timeout,3,'generation',fixture_document)
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,json.JSONDecodeError) as e:raise SystemExit(str(e))
