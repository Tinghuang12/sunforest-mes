FX = 4.4   # TWD per RMB (assumption)
W = 9.0    # 萬 RMB / person-year
def r(x): return round(x,2)

print("== A. buy-only per 千片日 ==")
S1_items = {"封口改順序":0.63,"剪線(機台自動剪線)":1.24,"燈箱台(第0層)":2.0,"隧道檢針":2.5,"套袋機":1.27,"封箱機":0.18,"打孔上環一體機":0.50}
S1_cost = {"燈箱台":(5,20),"隧道檢針":(3,5),"套袋機":(8,15),"封箱機":(1,3),"一體機":(5,10)}
s1 = sum(S1_items.values()); c1=(sum(v[0] for v in S1_cost.values()), sum(v[1] for v in S1_cost.values()))
s2 = s1 + 1.02+0.4+0.34; c2=(c1[0]+9, c1[1]+24)
s3 = s2 + 2.24; c3=(c2[0]+15, c2[1]+30)
full = 13.3
for name,s,c in [("S1",s1,c1),("S2",s2,c2),("S3",s3,c3)]:
    sav = s*W
    print(name, "省人",r(s), "占13.3", f"{s/full:.0%}", "年省(萬RMB)",r(sav), "設備",c, "回收(月)", r(c[0]/sav*12), r(c[1]/sav*12))
# Vietnam
for vn in (3.8,4.6):
    print("VN S1 年省", r(s1*vn), "回收年", r(c1[0]/(s1*vn)), r(c1[1]/(s1*vn)))

print("== B. New Tech first-year budget ==")
nt = (1800+150+1000, 2400+250+1600)
print("TWD萬", nt, "RMB萬", r(nt[0]/FX), r(nt[1]/FX))
ntr = (nt[0]/FX, nt[1]/FX)
print("= 幾個千片日的S1設備", r(ntr[0]/c1[1]), r(ntr[1]/c1[0]))
print("= 幾個千片日的S3設備", r(ntr[0]/c3[1]), r(ntr[1]/c3[0]))
print("= S1 年省的幾倍(千片日·年)", r(ntr[0]/(s1*W)), r(ntr[1]/(s1*W)))
# AI layer incremental for self-use
for inc in (0.5,1.0):
    print("AI層自用增量",inc,"人 → 年省",inc*W,"萬; 首年預算回收需 千片日·年", r(ntr[0]/(inc*W)), r(ntr[1]/(inc*W)))
inc_hi = 1.0+2.24
print("AI+摺疊 增量", inc_hi, "年省", r(inc_hi*W), "千片日·年", r(ntr[0]/(inc_hi*W)), r(ntr[1]/(inc_hi*W)))

print("== C. 24-month burn (TWD萬) ==")
# Year1 lines
Y1 = {
 "台灣10人全成本":(1800,2400),
 "招募費":(150,250),
 "台中研發中心首年":(1000,1600),
 "昆山端2-3人":(150,385),
 "T1樣機1台料件":(round(15.45*FX),round(40.65*FX)),
 "技術合夥人A路徑【假設】":(200,600),
 "差旅派駐【假設】":(100,250),
 "法務專利會計日本顧問【假設】":(150,400),
}
y1=(sum(v[0] for v in Y1.values()), sum(v[1] for v in Y1.values()))
for k,v in Y1.items(): print(" Y1",k,v)
print("Y1 total", y1, "RMB", r(y1[0]/FX), r(y1[1]/FX), "月均", r(y1[0]/12), r(y1[1]/12))
YA = {
 "台灣10人(+5%調薪)":(round(1800*1.05),round(2400*1.05)),
 "昆山端2-3人":(150,385),
 "研發中心營運(首年30%)【假設】":(300,480),
 "關卡三3台試點料件":(round(3*15.45*FX),round(3*40.65*FX)),
 "差旅":(100,250),
 "法務專利":(100,300),
}
ya=(sum(v[0] for v in YA.values()), sum(v[1] for v in YA.values()))
for k,v in YA.items(): print(" Y2A",k,v)
print("Y2 PathA", ya, "24m A", (y1[0]+ya[0], y1[1]+ya[1]), "RMB", r((y1[0]+ya[0])/FX), r((y1[1]+ya[1])/FX))
hw_B = (45+47+100, 85+96+300)  # RMB萬: 4.6放捲 + 5.1外購 + 自研模組【假設】
YB_extra = {"加招5-10人":(5*180,10*240), "走布段片段硬體":(round(hw_B[0]*FX), round(hw_B[1]*FX))}
yb=(ya[0]+sum(v[0] for v in YB_extra.values()), ya[1]+sum(v[1] for v in YB_extra.values()))
print(" Y2B extra", YB_extra, "hwB RMB", hw_B)
print("Y2 PathB", yb, "24m B", (y1[0]+yb[0], y1[1]+yb[1]), "RMB", r((y1[0]+yb[0])/FX), r((y1[1]+yb[1])/FX))
A24=(y1[0]+ya[0], y1[1]+ya[1]); B24=(y1[0]+yb[0], y1[1]+yb[1])

print("== C2. 4.5 首線含開發 vs 5.3 24個月團隊 ==")
team24 = (1800*2+150+1000, 2400*2+250+1600)
print("team24 TWD", team24, "RMB", r(team24[0]/FX), r(team24[1]/FX), "vs 首線 800-1500 RMB")

print("== D. subsidies (TWD萬) ==")
sub_low=0; sub_base=(100, 150+600); sub_high=150+1200*0.5+1000
print("base", sub_base, "high", sub_high)
for nm,b in [("A",A24),("B",B24)]:
    print(nm, "cover base", f"{sub_base[0]/b[1]:.1%}-{sub_base[1]/b[0]:.1%}", "high", f"{sub_high/b[1]:.1%}-{sub_high/b[0]:.1%}")
    net = (b[0]-sub_base[1], b[1]-sub_base[0])
    print("  net after base", net, "RMB", r(net[0]/FX), r(net[1]/FX))

print("== E. curtain revenue to earn back at 3.9% ==")
for nm,b in [("A",A24),("B",B24)]:
    rmb=(b[0]/FX, b[1]/FX)
    rev=(rmb[0]/0.039, rmb[1]/0.039)
    print(nm,"burn RMB萬",r(rmb[0]),r(rmb[1]),"需營收 億RMB", r(rev[0]/1e4), r(rev[1]/1e4), "TWD億", r(rev[0]*FX/1e4), r(rev[1]*FX/1e4))
    for p in (21.6,53.6,57.6):
        print("   單價",p,"元 → 片數(萬片)", r(rev[0]/p), r(rev[1]/p), "= 昆山線(15萬片/年)幾年", r(rev[0]/p/15), r(rev[1]/p/15))
    for m in (0.02,0.06):
        print("   margin",m,"需營收億", r(rmb[0]/m/1e4), r(rmb[1]/m/1e4))

print("== F. group size threshold ==")
y1r=(y1[0]/FX, y1[1]/FX)
for share in (1.0,0.5,0.3):
    print("Y1 burn = ",share,"of pre-tax profit at 3.9%: group rev 億RMB", r(y1r[0]/0.039/share/1e4), r(y1r[1]/0.039/share/1e4))
# stress: revenue -15%, margin 2%
for share in (0.3,):
    print("stress margin 2%: group rev for 30%", r(y1r[0]/0.02/share/1e4), r(y1r[1]/0.02/share/1e4))
# PathB Y2
ybr=(yb[0]/FX,yb[1]/FX)
print("Y2B burn RMB", r(ybr[0]), r(ybr[1]), "group rev for 100% profit", r(ybr[0]/0.039/1e4), r(ybr[1]/0.039/1e4))

print("== G. delay cost ==")
print("6個月延誤 (以Y1月均) TWD萬", r(y1[0]/2), r(y1[1]/2))
print("lean team Y1 personnel: TW", (round((120+75+250)*1.71), round((180+140+350)*1.71)))

print("== H. CEO hours ==")
h = {"招募(10人終面+技術長)":(60,120),"技術合夥人談判與試合作檢查":(30,60),"政府與鎮談判":(60,120),"兩岸法務與股權地圖":(40,80),"月度治理會議":(36,60),"客戶與工廠訪談":(60,120),"週會與技術檢查":(50,100),"差旅(台北-台中-昆山)":(80,160)}
tot=(sum(v[0] for v in h.values()), sum(v[1] for v in h.values()))
print(tot, f"{tot[0]/2200:.0%}-{tot[1]/2200:.0%} of 2200h")

print("== I. group revenue table (TWD) ==")
for rev in (10,20,30,50):
    prof = rev*1e4*0.039  # 萬TWD
    prof_s = rev*0.9*1e4*0.02
    print(rev,"億 → 稅前",round(prof),"萬; Y1燒錢占", f"{y1[0]/prof:.0%}-{y1[1]/prof:.0%}", "; 壓力(營收-10%,2%)稅前",round(prof_s),"占", f"{y1[0]/prof_s:.0%}-{y1[1]/prof_s:.0%}", "; Y2B占", f"{yb[0]/prof:.0%}-{yb[1]/prof:.0%}")
print("stress profit ratio", 0.9*0.02/0.039)

print("== J. 上櫃 ==")
for cap in (3e4,5e4):  # 萬TWD
    need4 = cap*0.04
    for nm,b in [("Y2A",ya),("Y2B",yb)]:
        need = (need4+b[0], need4+b[1])
        print("股本",cap/1e4,"億",nm,"本業稅前需≥",need, "營收(3.9%)億", r(need[0]/0.039/1e4), r(need[1]/0.039/1e4))

print("== K. 11.10 一期投資 2億RMB ==")
print("vs 24m A RMB", r(20000/(A24[1]/FX)), r(20000/(A24[0]/FX)), "倍; vs B", r(20000/(B24[1]/FX)), r(20000/(B24[0]/FX)))
print("2億 /3.9% =", r(2/0.039), "億RMB 營收")
print("補助一期 2000-3000 / 2億 =", 2000/20000, 3000/20000)

print("== L. phased curve Path A (TWD萬) ==")
p1=(800+150+720+60+68+60+40+75, 1280+250+960+154+179+180+100+200)
p2=(y1[0]-p1[0], y1[1]-p1[1])
p3=(ya[0]/2, ya[1]/2)
cum=[p1,(p1[0]+p2[0],p1[1]+p2[1]),(y1[0]+p3[0],y1[1]+p3[1]),A24]
print(p1,p2,p3,cum)
print("B extra Y2", (yb[0]-ya[0], yb[1]-ya[1]))

print("== M. tranche 1 lean (9 months) ==")
t1 = {"視覺主管":(round(120*1.71*0.75),round(180*1.71*0.75)),"機構工程師":(round(75*1.71*0.75),round(140*1.71*0.75)),
"技術長(或顧問,半年)":(round(250*1.71*0.5),round(350*1.71*0.5)),"昆山2人(9月)":(round(150*0.75),round(300*0.75)),
"T1樣機":(68,179),"合夥人8週試合作【假設】":(50,100),"律師意見與股權地圖":(100,150),"差旅":(50,100),"研發場地租用與可移轉設備":(150,300),"招募費":(100,150)}
tt=(sum(v[0] for v in t1.values()), sum(v[1] for v in t1.values()))
for k,v in t1.items(): print(" ",k,v)
print("tranche1 total", tt)
print("retreat: severance 10人", (round(10*88.9/12*0.5), round(10*116.7/12*1.0)), "equipment loss 50-70% of infra", (round(1000*0.5), round(1600*0.7)))
