"""Is the ladder floor the right null, and how many independent items are there?"""
import gzip, json, collections, math
LAD="results/norm/oneshot/ladder_items.jsonl.gz"
items=[json.loads(l) for l in gzip.open(LAD,"rt")]
by=collections.defaultdict(list)
for r in items: by[r["id"].split("/")[1]].append(r)
runs={"acq_a2c1_2":[1,2,4,16,64,256,1024],"acq_a3c1_26":[1,2,4,16,64,256,1024],
      "acq_a3c2_144":[1,2,4,16,64,256],"acq_a2c2_157":[1,2,4,16,64,256]}
out={}
for pool,ks in runs.items():
    rs=by[pool]; n=len(rs)
    keys=sorted({r["ask_key"] for r in rs})
    gold_by_key={k:{r["gold"] for r in rs if r["ask_key"]==k} for k in keys}
    dist=collections.Counter(r["gold"] for r in rs)
    maj=dist.most_common(1)[0][1]/n
    fl=sum(r["floor"] for r in rs)/n
    row={"n":n,"distinct_keys":len(keys),"gold_by_key":{k:sorted(v) for k,v in gold_by_key.items()},
         "stated_floor":round(fl,4),"majority_class":round(maj,4),"ks":{}}
    for k in ks:
        f=f"results/norm/oneshot/n_{pool}_k{k}_ladder.jsonl.gz"
        rows=[json.loads(l) for l in gzip.open(f,"rt") if json.loads(l)["id"].split("/")[1]==pool]
        c=sum(1 for r in rows if r["greedy"]["state"]=="ran" and r["greedy"]["answer"]==r["gold"])
        acc=c/len(rows)
        se=math.sqrt(fl*(1-fl)/len(rows))
        # per key accuracy, the cluster the item set actually varies over
        perkey=[sum(1 for r in rows if r["ask_key"]==kk and r["greedy"]["answer"]==r["gold"])/
                max(1,sum(1 for r in rows if r["ask_key"]==kk)) for kk in keys] if "ask_key" in rows[0] else []
        row["ks"][k]={"acc":round(acc,4),"z_vs_stated_floor":round((acc-fl)/se,2),
                      "beats_majority":acc>maj,"exact":sum(1 for r in rows if r["greedy"].get("exact")==1)}
    out[pool]=row
print(json.dumps(out,indent=1))
json.dump(out,open("/home/ec2-user/oneshot_floor_check.json","w"),indent=1)
