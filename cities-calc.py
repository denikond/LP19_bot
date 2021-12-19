from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import settings
import logging
from datetime import datetime, timedelta
import locale, ephem
import random
import mycalc

logging.basicConfig(filename="mybot.log", level=logging.INFO)


def mysplit(str1): #Функция для деления предложения на слова принимает str, возвращает list
    word_component = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    #str1 = '  У  луркоморья дуб , зеленый,злотая цепь на дубе то м'
    i = 0
    strlen = len(str1) - 1
    strlist = []
    not_end = True
    while i < strlen and not_end:
        if str1[i] not in word_component:
            i = i + 1
        else:
            j = i
            while str1[j] in word_component and not_end:
                if j < strlen:
                    j += 1
                else:
                    not_end = False
            if not_end:
                strlist.append(str1[i:j])
            else:
                strlist.append(str1[i:j+1])
            i = j
    if str1[i] in word_component and str1[i-1] not in word_component:
        strlist.append(str1[i])
    return strlist



def talk_to_me(update, context):
    text = update.message.text
    if text == "o/":
        text = "\o"
    update.message.reply_text(text)
    

def greet_user(update, context):
    #print("вызван /start")
    #print(update)
    #Помогатор "что я умею"
    update.message.reply_text("я поддерживаю следующие команды")
    update.message.reply_text("/calc <математическое выражение>")
    update.message.reply_text("/cities <название города>")
    update.message.reply_text("/next_full_moon YYYY-MM-DD")
    update.message.reply_text("/planet <Solar system planet>")
    update.message.reply_text("/wordcount <строка>")

def calc(update, context):
    text = update.message.text
    if len(text) == 5:
        update.message.reply_text("Вы можете ввести")
        update.message.reply_text("/calc <математическое выражение>")
        update.message.reply_text("я попробую посчитать")
        update.message.reply_text("я понимаю действия +-*/, отрицательные числа, десятичные значения с .")
        update.message.reply_text("скобки увы меня не научили понимать")
    else:
        result = mycalc.mycalc(text[5:])
        update.message.reply_text(result)

def next_full_moon(update, context): #Функция возвращающая ближайшее полнолуние
    #locale.setlocale(locale.LC_ALL, "russian") В данном случае не используется
    text = update.message.text
    spl = text.split()
    try:
        dt = datetime.strptime(spl[1], '%Y-%m-%d')
    except ValueError:
        update.message.reply_text("Введен неверный формат даты. Поддерживается YYYY-MM-DD")
    else:
        out_text = str(ephem.next_full_moon(dt))
        update.message.reply_text(out_text)

def wordcount(update, context): #Функция возвращающая количество слов в предложении
    text = update.message.text
    spl = mysplit(text)
    word_count = len(spl) - 1
    out_text = str(word_count) + ' слов(а)'
    update.message.reply_text(out_text)

def is_ru(str_in, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя- ')):
    #функция проверки строки для игры города
    return set(str_in.lower()).issubset(alphabet)

def cities_set_init():
    #Функция инициализации игрового окружения игры в города
    cities_set = {}
    #считываем каталог городов
    with open('RU_cities.txt','r', encoding='utf-8') as fi:
        for line in fi:
            a = line.rstrip().title()
            cities_set[a] = { 'is_used' : False, 'first_lett' : a[0].lower(), 'last_lett' : (lambda x: x[-1] if x[-1] not in set('ьыъ') else x[-2]) (a) }
            #cities_set[a] = 0, a[0].lower(), (lambda x: x[-1] if x[-1] not in set('ьыъ') else x[-2]) (a)
        return cities_set

def cities_init():
    user_data = {}
    user_data['cities_set'] = cities_set_init()
#    user_data['cities_first'] = ''
    user_data['cities_last'] = ''
    return user_data

def check_city(game_env, city_name):
    #На входе идет dict окружение игры, str название города
    city_name = city_name.lower()
    if city_name not in game_env.keys().lower():
        #такого названия нет в справочнике
        return -1
    elif game_env[city_name] == 0:
        #такое название города есть и оно не использовалось
        return 1
    else:
        #такое название города есть и оно использовалось
        return 0

def do_response(cities_set, letter):
    #Генерация list-а содержащего свободные ответы
    result = [ set_ for set_ in cities_set.keys() if cities_set[set_]['is_used'] == False and cities_set[set_]['first_lett'] == letter ]
    if len(result) == 0:
        return 0
    elif len(result) > 1:
        result = result[random.randrange(len(result))]
        return result
    else:
        return result[0]
    

def cities(update, context):
    #print("вызван /cities")
    end_game = 0
    text = update.message.text
    spl = text.split()
    len_spl = len(spl)
    #Название города может быть составным Великие луки, Нижний Новгород
    if len_spl == 3:
        #Если название города из 2 слов - сцепляем название в одну строку
        spl = [ '/cities' , spl[1] + ' ' + spl[2]]
        len_spl = 2
        #продолжить анализ сложного слова
    if len_spl > 3:
        #Если название города из более, чем 2 слов 
        update.message.reply_text("Название города России не бывает больше 2 слов")
    elif len_spl == 1:
        #Если ничего не ввели после команды /cities
        update.message.reply_text("Вы можете ввести /cities restart - для перезапуска игры")
        update.message.reply_text("Вы можете ввести /cities <Название города>")
        update.message.reply_text("Название города России принимается на русском языке, бывают города из 2 слов, бывают города, название которых пишется через -") 
        #Проверяем, чтобы слово было на русском языке
    elif len_spl == 2:
        if spl[1] == 'restart':
            #пользователь ввел /cities restart
            #начинаем реинициализацию игрового окружения
            #устанавливаем игровое окружение пользователю
            context.user_data['cities_game'] = cities_init()
            #Сообщаем об этом пользователю, переводим ход
            update.message.reply_text("Игра города России начата заново, делайте первый ход")
        else:
            city_name = spl[1].title()
            #Если название города на русском и соотевтствует правилам ввода
            if is_ru(city_name):
            #Нужно проверить начата ли игра (есть ли окружение игры в context.user_data)
                if 'cities_game' in context.user_data.keys():
                    #Если игра начата ранее
                    if context.user_data['cities_game']['cities_last'] == '':
                        #Это первое название города, нужно проверить есть ли введенный город в справочнике
                        if city_name.lower() in set(x.lower() for x in context.user_data['cities_game']['cities_set'].keys()):
                            #Город есть в списке, выбор принимается, нужно отметить его как использованый
                            context.user_data['cities_game']['cities_set'][city_name]['is_used'] = True
                            #Ответный ход в do_response передается множство городов и последняя буква города игрока
                            resp = do_response(context.user_data['cities_game']['cities_set'], (lambda x: x[-1] if x[-1] not in set('ьыъ') else x[-2]) (city_name.lower()))
                            if resp == 0:
                                #Если в сете не нашелся ответ
                                update.message.reply_text("Я проиграл")
                                #Удаляем игровое окружение
                                end_game = 1
                            else:
                                #Если ответ нашелся, его помечаем как использованый
                                context.user_data['cities_game']['cities_set'][resp]['is_used'] = True
                                #Ответ выводим игроку
                                update.message.reply_text(resp)
                                #Записываем последнюю букву ответа 
                                context.user_data['cities_game']['cities_last'] = (lambda x: x[-1] if x[-1] not in set('ьыъ') else x[-2]) (resp.lower())
                                #Есть ли ход у игрока?
                                you_loose = do_response(context.user_data['cities_game']['cities_set'], context.user_data['cities_game']['cities_last'])
                                if you_loose == 0:
                                    update.message.reply_text("У вас нет ходов, вы проиграли")                                
                                    #Удаляем игровое окружение
                                    end_game = 1
                        else:
                            #Города нет в списке
                            update.message.reply_text("Такого города не существует")
                            #Тут по идее можно предложить записать фантазию пользователя в отдельный файл для передачи на анализ админу (вдруг новый город)
                    else:
                        #Это не первое название города в игре, нужно проверить есть ли введенный город в справочнике
                        if city_name.lower() in set(x.lower() for x in context.user_data['cities_game']['cities_set'].keys()):
                            #Город есть в списке, проверяем не использовался ли он раньше
                            if context.user_data['cities_game']['cities_set'][city_name]['is_used'] == False:
                                #Город не использовался
                                if city_name[0].lower() == context.user_data['cities_game']['cities_last']:
                                    context.user_data['cities_game']['cities_set'][city_name]['is_used'] = True
                                    #Ответный ход
                                    resp = do_response(context.user_data['cities_game']['cities_set'], (lambda x: x[-1] if x[-1] not in set('ьыъ') else x[-2]) (city_name.lower()))
                                    if resp == 0:
                                        update.message.reply_text("Я проиграл")
                                        moves_ = 0
                                        for x in context.user_data['cities_game']['cities_set'].keys():
                                            if context.user_data['cities_game']['cities_set'][x]['is_used'] == True:
                                                moves_ += 1
                                        update.message.reply_text("Всего использовано " + str(moves_) + " названий городов")
                                        #Удаляем игровое окружение
                                        end_game = 1
                                        #type(context.user_data)
                                    else:
                                        context.user_data['cities_game']['cities_set'][resp]['is_used'] = True
                                        update.message.reply_text(resp)
                                        context.user_data['cities_game']['cities_last'] = (lambda x: x[-1] if x[-1] not in set('ьыъ') else x[-2]) (resp.lower())
                                        #Есть ли ход у игрока?
                                        you_loose = do_response(context.user_data['cities_game']['cities_set'], context.user_data['cities_game']['cities_last'])
                                        if you_loose == 0:
                                            update.message.reply_text("У вас нет ходов, вы проиграли")
                                            #Удаляем игровое окружение
                                            end_game = 1
                                else:
                                    update.message.reply_text("Мой город закончился на " + context.user_data['cities_game']['cities_last'] )    
                            else:
                                #Город использовался ранее
                                update.message.reply_text("Это название использовалось ранее")
                        else:
                            #Города нет в списке
                            update.message.reply_text("Такого города не существует")
                            #Тут по идее можно предложить записать фантазию пользователя в отдельный файл для передачи на анализ админу (вдруг новый город)
                else:
                    #игра не начата, инициализируем окружение игры
                    context.user_data['cities_game'] = cities_init()
                    #Проверяем есть ли название города в справочнике
                    if city_name.lower() in set(x.lower() for x in context.user_data['cities_game']['cities_set'].keys()):
                        #Город есть в списке, выбор принимается, нужно отметить его как использованый
                        context.user_data['cities_game']['cities_set'][city_name]['is_used'] = True
                        #Ответный ход в do_response передается множство городов и последняя буква города игрока
                        resp = do_response(context.user_data['cities_game']['cities_set'], (lambda x: x[-1] if x[-1] not in set('ьыъ') else x[-2]) (city_name.lower()))
                        if resp == 0:
                            #Если в сете не нашелся ответ
                            update.message.reply_text("Я проиграл")
                            #Удаляем игровое окружение
                            end_game = 1                        
                        else:
                            #Если ответ нашелся, его помечаем как использованый
                            context.user_data['cities_game']['cities_set'][resp]['is_used'] = True
                            #Ответ выводим игроку
                            update.message.reply_text(resp)
                            #Записываем последнюю букву ответа 
                            context.user_data['cities_game']['cities_last'] = (lambda x: x[-1] if x[-1] not in set('ьыъ') else x[-2]) (resp.lower())
                            #есть ли ход у игрока?
                            you_loose = do_response(context.user_data['cities_game']['cities_set'], context.user_data['cities_game']['cities_last'])
                            if you_loose == 0:
                                update.message.reply_text("У вас нет ходов, вы проиграли")
                                #Удаляем игровое окружение
                                end_game = 1                            
                    else:
                        #Города нет в списке
                        update.message.reply_text("Такого города не существует")
                        #Тут по идее можно предложить записать фантазию пользователя в отдельный файл для передачи на анализ админу (вдруг новый город)

            else:
            #Название города ввели не из русских букв, или содержит недопустимые символы
                update.message.reply_text("Название города России принимается на русском языке, бывают города из 2 слов, бывают города, название которых пишется через -") 
    if end_game == 1:
        try:
            del context.user_data['cities_game']
        except KeyError:
            pass      



def planet_const(update, context):
    #print("вызван /planet")

    #выгружаем перечень объектов из ephem втроенной функцией
    ep_obj = ephem._libastro.builtin_planets()
    #оставляем только объекты с кодом Planet
    ep_planet = [ep_obj[x][2] for x in range(len(ep_obj)) if ep_obj[x][1] == 'Planet']
    text = update.message.text
    spl = mysplit(text)
    #А имя планеты то есть в сообщении чата?
    if len(spl) == 1:
        #Выдать перечень планет
        update.message.reply_text("Допустимые имена планет:")
        for planet in ep_planet:
            out_text = planet
            update.message.reply_text(out_text)
    else:
        #выделяем имя планеты
        planet = spl[1]
        #Нормализуем ее вид (с большой буквы, остальные мал)
        planet = planet.capitalize()
        #если то что ввели, соответствует одному элементу из библиотеки ephem с тегом Planet
        if planet in ep_planet:
            #формируем команду для получения объекта ephem.планета blah-bla
            #comm = 'ephem.'+ planet + '(datetime.now())'
            #выполняем эту команду, получаем указатель на объект
            #p_obj = eval(comm)
            ephem_planet = getattr(ephem, planet)
            p_obj = ephem_planet(datetime.now())
            #получаем созвездие
            constellation = ephem.constellation(p_obj)
            #Нормализуем вывод к правилам англ.языка
            if planet == 'Moon' or planet =='Sun':
                tex = 'The '
            else:
                tex = ''
            #Формируем вывод сообщения в человечесокм виде
            tex = tex + planet + ' is in ' + constellation[1] + ' constellation now.'
            #Выводим сообщение в канал чатбота
            update.message.reply_text(tex)
        else:
            #Выводим сообщение в канал чатбота
            update.message.reply_text("Unknown planet")

def main():


    mybot = Updater(settings.API_KEY, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("wordcount", wordcount))
    dp.add_handler(CommandHandler("next_full_moon", next_full_moon))
    dp.add_handler(CommandHandler("planet", planet_const))
    dp.add_handler(CommandHandler("cities", cities))
    dp.add_handler(CommandHandler("calc", calc))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info(str(datetime.now()) +" Бот стартовал")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()
