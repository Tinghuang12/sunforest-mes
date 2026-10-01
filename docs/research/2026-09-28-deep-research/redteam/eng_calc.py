import math
# 1. accumulation days for n=598 per class at 500 pcs/day
print("== days to 598 ==")
for p in [0.02,0.01,0.005,0.002,0.001,0.0005]:
    d=598/(500*p); print(f"p={p:.2%} days={d:,.0f} months(26d)={d/26:.1f} years(312d)={d/312:.2f}")
# with train+test split: need test 598 + train (assume 300) and 12 classes -> rarest class dominates
# 2. what can 12 weeks prove? W9-12 = 4 weeks*6 days*500 = 12000 pcs; full 12 weeks=36000
def ub(n): return 1-0.05**(1/n) if n>0 else 1
for pcs,label in [(12000,'W9-12'),(36000,'all 12 weeks')]:
    for p in [0.01,0.005,0.002,0.001]:
        n=pcs*p; print(label,f"p={p:.1%} n={n:.0f} UB95={ub(n):.2%}")
# 3. pinhole reject rate if any detectable pinhole -> reject; Poisson lambda per curtain
for lam in [0.01,0.03,0.05,0.1,0.3]:
    print(f"lambda={lam} reject={1-math.exp(-lam):.2%}")
# 4-point system: 40 pts/100 sq yd; curtain 2.0x2.7=5.4 m2
sqyd=5.4/0.83613; print("sqyd",round(sqyd,2),"pts allowed",round(40*sqyd/100,2))
sqyd2=1.4*1.6/0.83613; print("small curtain sqyd",round(sqyd2,2),"pts",round(40*sqyd2/100,2))
# 4. night run: MTBF interpretations
for label,mh in [('A: MTBF4h all, 80% self-recover -> human MTBF 20h',20),('B: MTBF 4h human-required',4),('C: 10h',10)]:
    P=math.exp(-8/mh); E=mh*(1-math.exp(-8/mh)); print(label,f"P(8h clean)={P:.1%} E[run]={E:.2f}h ({E/8:.0%})")
# station MTBF in series: line MTBF 4h, N stations
for N in [12,15,18]:
    print(f"N={N} station MTBF needed (all faults) = {N*4} h")
# 5. splices
for n,label in [(76,'30m roll'),(4,'600m roll'),(2,'1200m roll')]:
    for q in [0.99,0.995,0.999]:
        print(label,f"splices={n} q={q} P(all ok)={q**n:.1%}")
print("50/50 success lower bound 95%:",f"{0.05**(1/50):.2%}", "n for 99%:", math.ceil(math.log(0.05)/math.log(0.99)))
print("200/200 implanted -> UB miss", f"{ub(200):.2%}")
# 6. measurement strain tolerance
print("strain tol ±2mm/2700mm =",f"{2/2700:.3%}", "±2mm/1400mm =", f"{2/1400:.3%}")
# 7. schedule: 4.7 phases sequential
lo=4/4.345+8/4.345+4+3; hi=6/4.345+12/4.345+6+3
print(f"P0+P1+P2+P3 months: {lo:.1f}-{hi:.1f}")
for q,k in [(0.8,6),(0.9,6),(0.8,8)]:
    print(f"q={q} k={k} P(all on time)={q**k:.1%}")
# 8. four preconditions joint
for q in [0.5,0.6,0.7,0.8]:
    print(f"each {q} -> all four {q**4:.1%}")
# 9. same-recipe batch night
print("night batch 150*8*0.8..1.0 =",150*8*0.8,150*8)
# 10. images for 1万张 : W5-8 4 weeks*6*500
print("W5-8 pieces", 4*6*500)
print("== extra ==")
# Clopper-Pearson lower bound for 475/500 successes, one-sided 95%
from math import comb
def binom_cdf(k,n,p):
    return sum(comb(n,i)*p**i*(1-p)**(n-i) for i in range(k+1))
# lower bound on success prob: find p_s such that P(X>=475 | p_s)=0.05, i.e. failures<=25 with failure prob f: P(F<=25|f)=0.05
lo,hi=0.0,0.2
for _ in range(60):
    mid=(lo+hi)/2
    if binom_cdf(25,500,mid)>0.05: lo=mid
    else: hi=mid
print("475/500: failure UB",f"{lo:.2%}","success LB",f"{1-lo:.2%}")
# per-action reliability for night
pcs_h=150; actions=20
for mh in [4,20]:
    human_rate=1/mh  # per hour
    allf=human_rate/0.2
    per_action_all=allf/(pcs_h*actions)
    print(f"MTBF_h={mh}h: all-fault rate {allf:.2f}/h, per-action fault <= {per_action_all*1e6:.0f} ppm, reliability {1-per_action_all:.5%}, zero-fail trials to prove={3/per_action_all:,.0f}")
# P1 95% success per action -> faults per hour
print("P1 95%: faults/h =",pcs_h*actions*0.05)
# output under night scenarios
for night in [0.40,0.76]:
    out=150*(16*0.65+8*night); print(f"night OEE {night}: {out:,.0f} pcs/day, payback 1.2*2800/out={1.2*2800/out:.2f} y")
print("p needed so 12 weeks (36000) yields 598:",f"{598/36000:.2%}")
print("critical pooled 0.3%:",598/(500*0.003),"days")
# minor stop check: 147 stops per 8h shift
print("147 per 8h -> every",round(480/147,1),"min")
# with minor stop rate 6/h over 8h=48; human faults allowed 2 (MTBF4h) or 0.4 (MTBF20h)
for allowed in [2,0.4]:
    print("self-recovery needed", f"{1-allowed/48:.1%}")
# roll unattended time
for L in [30,600,1200]:
    print(L, f"{2*L/300:.1f}-{2*L/270:.1f} h")
