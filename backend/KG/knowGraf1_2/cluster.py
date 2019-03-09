if __name__ == '__main__':
    strtemp='start'
    templine=[]
    lstr=''
    istr=''
    with open('C:\python\pythonwork\knowGraf1_2_2\knowGraf1_2\\all.txt', mode='r', encoding='utf-8') as code:
        lines=code.readlines()
        for line in lines:
            l=line.split('\n')[0]
            if l[:2]=='概念':
                lstr=lstr+l[4:]
                lset=set(lstr.split(' '))
            if l[:2]=='实例':
                istr=istr+l[4:]
                iset=set(istr.split(' '))
            if l[:2] != '实例' and l[:2] != '概念' :
                templine.append(line)

    con=[]
    ins=[]
    num=0
    str=''
    for s in lset:
        num=num+1
        str=str+' '+s
        if num%10==0:
            con.append('概念+='+str)
            str=''
    for s in iset:
        num = num + 1
        str = str + ' ' + s
        if num % 10 == 0:
            ins.append('实例+=' + str)
            str = ''
        print(ins)



    with open('C:\python\pythonwork\knowGraf1_2_2\medicine\\newall613.txt', mode='w', encoding='utf-8') as wcode:
        for c in con:
            wcode.write(c)
            wcode.write('\n')
        for i in ins:
            wcode.write(i)
            wcode.write('\n')
        for l in templine:
            wcode.write(l)
    #     pass
    #     for ww in w:
    #         print(ww)
    #         wcode.write(ww)
    #         wcode.write('\n')