import json, re, statistics as st, collections
# brand: (regex, sector, rpm_tier 3=finance/payments, 2=tech/auto/luxury, 1=consumer/food/media)
B = {
"Visa":(r"\bvisa\b","paiements",3),"Mastercard":(r"mastercard","paiements",3),"American Express":(r"american express|\bamex\b","paiements",3),
"PayPal":(r"paypal","paiements",3),"Apple Pay":(r"apple pay","paiements",3),"Klarna":(r"klarna","paiements",3),"Affirm":(r"\baffirm\b","paiements",3),
"Robinhood":(r"robinhood","courtage",3),"Coinbase":(r"coinbase","crypto",3),"BlackRock":(r"blackrock","finance",3),"Berkshire Hathaway":(r"berkshire|buffett","finance",3),
"JPMorgan":(r"jp ?morgan|jamie dimon","banque",3),"Goldman Sachs":(r"goldman","banque",3),"Wells Fargo":(r"wells fargo","banque",3),"Chase":(r"\bchase\b","banque",3),
"Capital One":(r"capital one","banque",3),"Stripe":(r"\bstripe\b","paiements",3),"Venmo":(r"venmo","paiements",3),"Cash App":(r"cash app|block inc","paiements",3),
"Costco":(r"costco","grande distribution",2),"Walmart":(r"walmart","grande distribution",2),"Amazon":(r"amazon","tech/commerce",2),"Target":(r"\btarget\b","grande distribution",1),
"Aldi":(r"\baldi\b","grande distribution",1),"Trader Joe's":(r"trader joe","grande distribution",1),"Kroger":(r"kroger","grande distribution",1),
"Apple":(r"\bapple\b(?! pay)|iphone|steve jobs","tech",2),"Google":(r"google|alphabet","tech",2),"Microsoft":(r"microsoft","tech",2),"Meta":(r"\bmeta\b|facebook|zuckerberg","tech",2),
"Nvidia":(r"nvidia","tech",2),"Tesla":(r"tesla","auto",2),"SpaceX":(r"spacex","tech",2),"Netflix":(r"netflix","médias",1),"Disney":(r"disney","médias",1),
"Spotify":(r"spotify","médias",1),"Uber":(r"\buber\b","tech",2),"Airbnb":(r"airbnb","tech",2),"DoorDash":(r"doordash","tech",2),"OpenAI":(r"openai|chatgpt|sam altman","tech",2),
"Samsung":(r"samsung","tech",2),"Intel":(r"\bintel\b","tech",2),"TSMC":(r"tsmc","tech",2),"ASML":(r"asml","tech",2),"Oracle":(r"oracle","tech",2),"IBM":(r"\bibm\b","tech",2),
"McDonald's":(r"mcdonald","restauration",1),"Starbucks":(r"starbucks","restauration",1),"Coca-Cola":(r"coca|\bcoke\b","grande conso",1),"Pepsi":(r"pepsi","grande conso",1),
"Chipotle":(r"chipotle","restauration",1),"Subway":(r"\bsubway\b","restauration",1),"Burger King":(r"burger king","restauration",1),"Domino's":(r"domino","restauration",1),
"Nike":(r"\bnike\b","mode",1),"Adidas":(r"adidas","mode",1),"Lululemon":(r"lululemon","mode",1),"Shein":(r"shein","mode",1),"Temu":(r"temu","commerce",1),"Zara":(r"\bzara\b|inditex","mode",1),
"Rolex":(r"rolex","luxe",2),"LVMH":(r"lvmh|louis vuitton|arnault","luxe",2),"Hermès":(r"herm[eè]s|birkin","luxe",2),"Ferrari":(r"ferrari","auto",2),"Toyota":(r"toyota","auto",2),
"Ford":(r"\bford\b","auto",2),"GM":(r"general motors|\bgm\b","auto",2),"Boeing":(r"boeing","industrie",2),"Home Depot":(r"home depot","grande distribution",1),"IKEA":(r"ikea","grande distribution",1),
"Nintendo":(r"nintendo","jeux",1),"Sony":(r"\bsony\b|playstation","jeux",1),"Lego":(r"\blego\b","jeux",1),"Red Bull":(r"red bull","grande conso",1),"Tesla/Musk":(r"elon musk","tech",2),
"Peloton":(r"peloton","conso",1),"WeWork":(r"wework","immobilier",2),"Blockbuster":(r"blockbuster","médias",1),"Kodak":(r"kodak","tech",1),"Nokia":(r"nokia","tech",2),
"BlackBerry":(r"blackberry","tech",2),"Sears":(r"\bsears\b","grande distribution",1),"Toys R Us":(r"toys ?r ?us","grande distribution",1),"Enron":(r"enron","finance",3),
"FTX":(r"\bftx\b","crypto",3),"Lehman":(r"lehman","banque",3),"Theranos":(r"theranos|holmes","santé",2),"Walgreens":(r"walgreens","santé",2),"CVS":(r"\bcvs\b","santé",2),
"UnitedHealth":(r"unitedhealth","santé",3),"Ozempic/Novo":(r"ozempic|novo nordisk|wegovy","santé",2),"Pfizer":(r"pfizer","santé",2),"TikTok":(r"tiktok|bytedance","tech",2),
"YouTube":(r"youtube","tech",2),"Twitter/X":(r"twitter","tech",2),"Ticketmaster":(r"ticketmaster|live nation","médias",2),"Southwest":(r"southwest","aérien",2),
"Spirit Airlines":(r"spirit airlines","aérien",2),"Delta":(r"\bdelta\b","aérien",2),"Hertz":(r"hertz","auto",2),"Carvana":(r"carvana","auto",2),"Zillow":(r"zillow","immobilier",3),
"Duolingo":(r"duolingo","tech",2),"Dollar General":(r"dollar general|dollar tree","grande distribution",1),"In-N-Out":(r"in-n-out","restauration",1),"Chick-fil-A":(r"chick-fil-a","restauration",1),
"Taco Bell":(r"taco bell","restauration",1),"Krispy Kreme":(r"krispy","restauration",1),"Five Guys":(r"five guys","restauration",1),"Netflix/HBO":(r"\bhbo\b|warner","médias",1),
"Rockefeller/Standard Oil":(r"rockefeller|standard oil","histoire",2),"Bezos":(r"bezos","tech",2),"Gucci":(r"gucci","luxe",2),"Patagonia":(r"patagonia","mode",1),
"Philips":(r"philips","tech",1),"HP":(r"\bhp\b|hewlett","tech",2),"Dell":(r"\bdell\b","tech",2),"Xerox":(r"xerox","tech",2),"GE":(r"general electric","industrie",2),
"Walt Disney Parks":(r"disneyland|disney world","médias",1),"Monopoly Visa/MC":(r"interchange|swipe fee","paiements",3),"Credit cards":(r"credit card","paiements",3),
"Amex Platinum":(r"platinum card","paiements",3),"Vanguard":(r"vanguard","finance",3),"Fidelity":(r"fidelity","finance",3),"Charles Schwab":(r"schwab","finance",3),
"Rocket Mortgage":(r"rocket mortgage","finance",3),"H&R Block/TurboTax":(r"turbotax|intuit|h&r block","finance",3),"Moody's/S&P":(r"moody|s&p global","finance",3),
"Mattel/Barbie":(r"mattel|barbie","jouets",1),"Hasbro":(r"hasbro","jouets",1),"Labubu/Pop Mart":(r"labubu|pop mart","jouets",1),"Crocs":(r"\bcrocs\b","mode",1),
"Victoria's Secret":(r"victoria'?s secret","mode",1),"Abercrombie":(r"abercrombie","mode",1),"Hooters":(r"hooters","restauration",1),"Red Lobster":(r"red lobster","restauration",1),
"Bed Bath":(r"bed bath","grande distribution",1),"Kmart":(r"kmart","grande distribution",1),"Pan Am":(r"pan am","aérien",2),"Boeing 737":(r"737","industrie",2),
}
cat = json.load(open("catalogs.json"))
disc = json.load(open("discover.json"))
rows = []
seen=set()
for h,c in cat.items():
    L=[v for v in c["videos"] if v["dur"]>180]
    if not L: continue
    med = st.median(v["views"] for v in L)
    for v in L:
        seen.add(v["id"]); rows.append((h, med, v))
for v in disc:
    if v["id"] not in seen and v["dur"]>180: rows.append(("search:"+v["channel"], None, v))
json.dump([(h,m,v) for h,m,v in rows], open("allrows.json","w"))
res = {}
for b,(rx,sec,t) in B.items():
    r = re.compile(rx, re.I)
    hits = [(h,m,v) for h,m,v in rows if r.search(v["title"])]
    if not hits: res[b]=dict(n=0,sec=sec,t=t); continue
    vs=[v["views"] for _,_,v in hits]
    rel=[v["views"]/m for _,m,v in hits if m]
    recent=[v for _,_,v in hits if v["date"]>="2025-11-05"]
    strong_recent=[(v["views"],v["date"],h) for h,_,v in hits if v["date"]>="2025-11-05" and v["views"]>=300000]
    top=sorted(hits,key=lambda x:-x[2]["views"])[:3]
    res[b]=dict(n=len(hits),sec=sec,t=t,max=max(vs),med=int(st.median(vs)),rel=round(st.median(rel),2) if rel else None,
       n_recent=len(recent),strong_recent=sorted(strong_recent,reverse=True)[:3],
       last=max(v["date"] for _,_,v in hits),
       top=[(x[0],x[2]["views"],x[2]["date"],x[2]["title"][:60]) for x in top])
json.dump(res, open("brands.json","w"), ensure_ascii=False)
for b,d in sorted(res.items(), key=lambda kv:-(kv[1].get("med") or 0)):
    print(b, d["sec"], d["t"], d.get("n"), d.get("med"), d.get("max"), d.get("rel"), d.get("n_recent"), [(s[0]//1000,s[1][:7]) for s in d.get("strong_recent",[])])
