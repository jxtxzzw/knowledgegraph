rels={'常见症状':'疾病常见症状','会被引起':'疾病会被引起','发病率':'疾病发病率','高危人群':'疾病高危人群','传播途径':'疾病传播途径','特征':'疾病特征','引起症状':'疾病引起症状','影像学特征':'疾病影像学特征','临床特征':'疾病临床特征','体征':'疾病体症','鉴别诊断':'疾病鉴别诊断','诊断依据':'疾病诊断依据','并发症':'疾病并发症','后遗症':'疾病后遗症','放疗原则':'疾病放疗原则','治疗手术方式':'疾病治疗手术方式','并发证':'疾病并发症','检查项目':'疾病检查项目','预防方法':'疾病预防方法','治疗方式':'疾病治疗方式','诱因':'疾病诱因','别名':'name','全称':'name','包含':'child','包括':'child','病因':'疾病病因'}
def tri2w(triples):
    con1=[]
    con2=[]
    csyn=[]
    ins=[]
    w=[]
    rel_ins={}
    rel='常见症状'
    for t in triples:

        if t[0] not in con1:
            con1.append(t[0])
        if rels[t[1]]=='child':
            con2.append(t[2])
        if rels[t[1]]=='name':
            csyn.append(t[2])
        if rels[t[1]]!='name' and rels[t[1]]!='child':
            if t[1]!=rel:
                rel_ins[rels[t[1]]]=ins
                ins=[]
                rel=t[1]
                ins.append(t[2])
            else:
                ins.append(t[2])
                rel=t[1]
            rel_ins[rels[t[1]]] = ins


    if con2:
        s1='概念+='+con1[0]
        s0='疾病.child'+'+='+con1[0]
        s2=con1[0]+'.'+'child'+'+='
        for c in con2:
            s1=s1+' '+c
            s2=s2+' '+c

        w.append(s1)
        w.append(s0)
        w.append(s2)
        # print(s1,s2)
    if csyn:
        s3=con1[0]+'.'+'name'+'+='
        for cs in csyn:
            s3=s3+' '+cs
        w.append(s3)
    for (k, v) in rel_ins.items():
        s4='实例'+'+='
        s5=k[2:]+'.ins'+'+='
        s6=con1[0]+'.'+k+'+='
        for vs in v:
            s4=s4+' '+vs
            s5 = s5 + ' ' + vs
            s6 = s6 + ' ' + vs
        w.append(s4)
        w.append(s5)
        w.append(s6)

    return w
if __name__ == '__main__':
    strtemp='start'
    triples=[]
    with open('C:\python\pythonwork\knowGraf1_2_2\medicine\纵隔肿物.txt', mode='r', encoding='utf-8') as code:
        lines=code.readlines()
    for l in lines:
        temp=l.split('\n')
        triples.append(temp[0].split('\t'))
    tritemp=[]
    w=[]
    for tri in triples:
        if(strtemp!=tri[0]):
            w1=tri2w(tritemp)
            w=w+w1
            tritemp = []
            tritemp.append(tri)
        else:
            tritemp.append(tri)
        strtemp=tri[0]
    w2=tri2w(tritemp)
    w=w+w2

    with open('C:\python\pythonwork\knowGraf1_2_2\medicine\\zgzw.txt', mode='w', encoding='utf-8') as wcode:
        for ww in w:
            print(ww)
            wcode.write(ww)
            wcode.write('\n')
