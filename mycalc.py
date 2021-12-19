def find_md(str_i, pos=0, step=1):
    #функция разыскивающая операции */  в строке
    if str_i.find('*') != -1 \
        or str_i.find('/') != -1:
        while str_i[pos] not in '*/':
            pos += step
        return pos
    else:
        return 0

def find_pm(str_i, pos=0, step=1):
    #функция разыскивающая операции -+  в строке, первый - принимается, как - перед числом, а не операция
    sign = 0
    if pos == 0 and str_i[0] == '-':
        sign = 1
        str_i = str_i[1:]
    if str_i.find('+') != -1 \
        or str_i.find('-') != -1:
        while str_i[pos] not in '+-':
            pos += step
        return pos + sign
    else:
        return 0

def get_dig(str_i, pos=0, step=1):
    #Функция вытаскивающая число из строки str_i с позиции pos, с шагом step +/- 1
    pos_start = pos
    if step == 1:
        if str_i[pos] == '-':
            pos += step
    
    try:
        while str_i[pos] in '0123456789.':
            pos += step
            if pos < 0:
                break
    except IndexError:
        pass

    if step == 1:
        res = str_i[pos_start:pos]
        res_pos = pos
    else:
        if pos > 1:
            if str_i[pos-1] == '-' and str_i[pos-2] in '*/':
                pos += step
        elif pos == 0:
            if str_i[pos] == '-':
                pos += step
        res = str_i[pos+1:pos_start+1]
        res_pos = pos + 1
    return res, res_pos

def check_rules(str_i):
    #Предпроверка строки калькулятора на корректность
    #Строка не может начинаться с * или / не может заканчиваться * / + - . и перечисление недопустимого соседства
    if len(str_i) == 0:
        return 'Длина выражения равна нулю'
    elif set(str_i).isdisjoint('+-*/')\
        or str_i.rfind('-') == 0 and set(str_i).isdisjoint('+*/'):
            return 'Не найдено математических операций'
    elif str_i[0] in '*/+' \
        or str_i[-1] in '*/+-.' \
        or str_i.find('+/') != -1 \
        or str_i.find('-/') != -1 \
        or str_i.find('+*') != -1 \
        or str_i.find('-*') != -1 \
        or str_i.find('+-') != -1 \
        or str_i.find('-+') != -1 \
        or str_i.find('++') != -1 \
        or str_i.find('.+') != -1 \
        or str_i.find('.-') != -1 \
        or str_i.find('.*') != -1 \
        or str_i.find('./') != -1 \
        or str_i.find('**') != -1 \
        or str_i.find('*/') != -1 \
        or str_i.find('/*') != -1 \
        or str_i.find('//') != -1 \
        or str_i.find('/+') != -1 \
        or str_i.find('*+') != -1:
            return "Недопустимое выражение"
    else:
        return ''

def mycalc(str1):
    invalid_sym = ''.join(set(str1).difference('0123456789+-*/. '))
    if invalid_sym =='':
        norm_s = ''.join([x for x in str1 if x in '0123456789+-*/.'])
        #print(str1)
        check_result = check_rules(norm_s)
        if check_result != '':
            #print(check_result)
            return check_result
        else:
            #print("выражение корректно")

            #проход 1 - умножение и деление
            div_by_zero = False
            #print(norm_s)
            act_pos = find_md(norm_s)
            while act_pos != 0 and not div_by_zero:
                #print(act_pos)
                act = norm_s[act_pos]
                #print(act)
                str_b, pos_b = get_dig(norm_s, find_md(norm_s)+1, 1)
                str_a, pos_a = get_dig(norm_s, find_md(norm_s)-1, -1)
                if str_a.count('.') > 1 or str_b.count('.') > 1:
                    return 'Недопустимое выражение, в числе два знака .'
                if act == '*':
                    res = float(str_a)*float(str_b)
                    #print(str_a,act,str_b,'=',res)
                elif act == '/':
                    if float(str_b) != 0:
                        res = float(str_a)/float(str_b)
                    else:
                        #div_by_zero = True
                        #break
                        return 'Недопустимое выражение, деление на 0'
                    #print(str_a,act,str_b,'=',res)
                norm_s = norm_s[:pos_a] + str(res) + norm_s[pos_b:]
                #print(norm_s)
                if norm_s.find('+-') != -1:
                    norm_s = norm_s[:pos_a-1] + norm_s[pos_a:]
                elif norm_s.find('--') != -1:
                    norm_s = norm_s[:pos_a-1] + '+' + norm_s[pos_a+1:]
                act_pos = find_md(norm_s)
                #print(norm_s)

            #проход 2 - сложение и вычитание
            #print(norm_s)
            act_pos = find_pm(norm_s)
            while act_pos != 0 and not div_by_zero:
                #print(act_pos)
                act = norm_s[act_pos]
                #print(act)
                str_b, pos_b = get_dig(norm_s, find_pm(norm_s)+1, 1)
                str_a, pos_a = get_dig(norm_s, find_pm(norm_s)-1, -1)
                if str_a.count('.') > 1 or str_b.count('.') > 1:
                    return 'Недопустимое выражение, в числе два знака .'
                if act == '+':
                    res = float(str_a)+float(str_b)
                    #print(str_a,act,str_b,'=',res)
                elif act == '-':
                    res = float(str_a)-float(str_b)
                    #print(str_a,act,str_b,'=',res)
                norm_s = norm_s[:pos_a] + str(res) + norm_s[pos_b:]
                #print(norm_s)
                act_pos = find_pm(norm_s)
                #print(norm_s)
            return norm_s

    else:
        #print('недопустимый символ', invalid_sym)
        return 'Недопустимый символ \'' + invalid_sym + '\''

def main():
    str1 = '2+.434 * -5*6.2/-3* -7/3.1'
    print(str1)
    print(mycalc(str1))
    print()

    str1 = '2-+.434 * -5*6.2/-3* -7/3.1'
    print(str1)
    print(mycalc(str1))
    print()

    str1 = '2+434 * -5*6.2/-3* -7/3.1'
    print(str1)
    print(mycalc(str1))
    print()

    str1 = '-.3*.2+.2'
    print(str1)
    print(mycalc(str1))
    print()

    str1 = '-17-5*6/3-2+4/2'
    print(str1)
    print(mycalc(str1))
    print()

    str1 = '40 /5 + 12 - 8/ 2'
    print(str1)
    print(mycalc(str1))
    print()

    str1 = '-2*-.001'
    print(str1)
    print(mycalc(str1))
    print()

    str1 = '5/0'
    print(str1)
    print(mycalc(str1))
    print()

    str1 = '.я'
    print(str1)
    print(mycalc(str1))
    print()

    str1 = '-.01/5'
    print(str1)
    print(mycalc(str1))
    print()


if __name__ == "__main__":
    main()
