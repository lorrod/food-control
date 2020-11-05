
from app import mongo



def create_main_prog(ident_name, name, info):
    mongo.db.programms.insert({"ident_name":ident_name,"name":name, "info":info})
    return True

def create_personal_prog(ident_name, ident_sub_prog, name, full_name, info, koef_kkal, koef_whey, koef_carboh, koef_fat):
    if list(mongo.db.programms.find({"ident_name":ident_name})):
        if not list(mongo.db.sub_programms.find({"ident_sub_prog":ident_sub_prog})):
            mongo.db.sub_programms.insert({"ident_name":ident_name,
                                            "ident_sub_prog":ident_sub_prog,
                                            "name":name,
                                            "full_name":full_name,
                                            "info":info,
                                            "koef_kkal":koef_kkal,
                                            "koef_whey":koef_whey,
                                            "koef_fat":koef_fat,
                                            "koef_carboh":koef_carboh
                                            })
            return True
    #Либо не найдено главного вектора программы
    #Либо идентификационное название не уникально
    return False


create_main_prog("slimming","Похудение","Информация про похудение")
create_main_prog("gain","Набор массы","Информация про набор массы")
create_main_prog("tonus","Быть в тонусе","Информация про то как оставаться в тонусе")


create_personal_prog("slimming","slimming1","Малая активность","Похудение | Малая активность","Информация про программу похудения n.1", 1.2, 1.2,1.2,1.2*0.2)
create_personal_prog("slimming","slimming2","Средняя активность","Похудение | Средняя активность","Информация про программу похудения n.2", 1.35, 1.35,1.35,1.35*0.2)
create_personal_prog("slimming","slimming3","Высокая активность","Похудение | Высокая активность","Информация про программу похудения n.3", 1.5, 1.5,1.5,1.5*0.2)

create_personal_prog("gain","gain1","Малая активность","Набор массы | Малая активность","Информация про программу набора массы n.1", 1.2,  1.2,1.2*2,1.2*0.4)
create_personal_prog("gain","gain2","Средняя активность","Набор массы | Средняя активность","Информация про программу набора массы n.2", 1.35, 1.35,1.35*2,1.35*0.4)
create_personal_prog("gain","gain3","Высокая активность","Набор массы | Высокая активность","Информация про программу набора массы n.3", 1.5,  1.5,1.5*2,1.5*0.4)

create_personal_prog("tonus","tonus1","Малая активность","Быть в тонусе | Малая активность","Информация про программу сохранения тонуса тела n.1", 1.2,  1.2,1.2*1.6,1.2*0.35)

create_personal_prog("tonus","tonus2","Средняя активность","Быть в тонусе | Средняя активность","Информация про программу сохранения тонуса тела n.2", 1.35, 1.35,1.35*1.6,1.35*0.35)
create_personal_prog("tonus","tonus3","Высокая активность","Быть в тонусе | Высокая активность","Информация про программу сохранения тонуса тела n.3", 1.5,  1.5,1.5*1.6,1.5*0.35)
