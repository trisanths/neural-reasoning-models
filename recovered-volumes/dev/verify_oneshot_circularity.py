import gzip, json, importlib, collections
from src.norm import opsay
items = [json.loads(l) for l in gzip.open("results/norm/oneshot/ladder_items.jsonl.gz","rt")][:200]
opsay.NAME_LINE["protocol"]   = "zzz {system} qqq {op} vvv."
opsay.READ_LINE["protocol"]   = "qqq {op} zzz {item} vvv {list}."
opsay.CLAUSE_LINE["protocol"] = "vvv {cond} zzz {op} qqq {item} vvv {res}."
opsay.FALLBACK_LINE["protocol"]="zzz {op} qqq {item} kkk {res}."
opsay.Q_SINGLE = tuple("qqq%d {op} zzz {k} {item}?" % i for i in range(len(opsay.Q_SINGLE)))
from src.norm import opitems, opdata
import src.norm.opread as opread
importlib.reload(opread); opread._CACHE.clear()
new=[]
for r in items:
    inst = opdata.instance_of(r); inst["page_name"]=r["inst"]["page_name"]
    e = opitems.episode(inst, r["fid"], "single", r["ask_key"], mode="protocol", n_pages=1, def_pos=r["def_pos"])
    if e is not None: e["fid"]=r["fid"]; new.append(e)
print("regenerated", len(new))
print("--- one episode ---"); print(new[0]["text"][:700])
ok=0; st=collections.Counter(); why=collections.Counter()
for r in new:
    a=opread.answer(r["text"], r["fid"]); st[a["state"]]+=1
    if a["state"]!="ran": why[(a.get("stage"), a["reason"][:70])]+=1
    ok += (a["state"]=="ran" and a["answer"]==r["gold"])
print("strict", round(ok/max(1,len(new)),4), dict(st)); print(why.most_common(5))
