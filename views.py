from flask import Flask
from flask_pymongo import PyMongo 		# PyMongo database
import telebot
from telebot import apihelper
from telebot import types
import sqlite_query
import json
import sys

bot = telebot.TeleBot('1092145481:AAGZZoqHGwbJ98UBxqcvYo8RVMESpIxzemA')
keyboard2 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard2.row('IP', 'Веб-сайт')

greetingMessage = 'Добро пожаловать! Данный бот предназначен для контроля своего питания.'
default = 'Установлены средние параметры тела!'
loginMessage = 'Ваш вес: {}\nВаш рост: {}\nВаша цель: {}\nСъедено за сегодня: {} ккал\nБелков: {}\nЖиров: {}\nУглеводов: {}'

@bot.message_handler(commands=['start'])
def start_message(message):
	sqlite_query.registration_user(message.chat.id)
	bot.send_message(message.chat.id, greetingMessage)
	bot.send_message(message.chat.id, loginMessage.format(75, 175, "рост мышц", 0,0,0,0), reply_markup=keyboard_cabinet(message.chat.id))


@bot.message_handler(content_types=['text'])
def send_text(message):
	chat_id = message.chat.id
	try:
		state = sqlite_query.get_user_state(chat_id)[0][0]
	except IndexError:
		bot.send_message(chat_id, "Не найдено состояния")

	if state == 'new_product':
		print(message.text)
		product = sqlite_query.get_product_info(message.text)
		print(product)
		if product:
			sqlite_query.set_user_buffer(chat_id, product)
			sqlite_query.set_user_state(chat_id, "wait_count")
			bot.send_message(chat_id, "Введите съеденное количество в граммах")
		else:
			sqlite_query.set_user_buffer(chat_id, message.text)
			bot.send_message(chat_id, "Продукта не нашлось в БД. Желаете записать в базу?", reply_markup=keyboard_ask_product())
	elif state == "wait_count":
		try:
			float(message.text)
		except ValueError:
			bot.send_message(chat_id, "Необходимо писать цифрой, без пробелов!")
		print()
		buffer = json.loads(sqlite_query.get_user_buffer(chat_id)[0].replace("\'","\""))
		sqlite_query.set_user_ate(chat_id, buffer["kkal"], buffer["whey"],buffer["fat"],buffer["carboh"],float(message.text))
		sqlite_query.set_user_state(chat_id, "")
		bot.send_message(chat_id, "Принято!",reply_markup=keyboard_cabinet(chat_id))
	elif state == 'new_product_kkal':
		try:
			float(message.text)
			buffer = sqlite_query.get_user_buffer(chat_id)
			sqlite_query.set_user_buffer(chat_id, buffer[0]+"|+|"+message.text)
			sqlite_query.set_user_state(chat_id, "new_product_whey")
			bot.send_message(chat_id, "Принято! Теперь напишите цифрой кол-во белков на 100гр")
		except ValueError:
			bot.send_message(chat_id, "Необходимо писать цифрой, без пробелов!")
	elif state == 'new_product_whey':
		try:
			float(message.text)
			buffer = sqlite_query.get_user_buffer(chat_id)
			sqlite_query.set_user_buffer(chat_id, buffer[0]+"|+|"+message.text)
			sqlite_query.set_user_state(chat_id, "new_product_fat")
			bot.send_message(chat_id, "Принято! Теперь напишите цифрой кол-во жиров на 100гр")
		except ValueError:
			bot.send_message(chat_id, "Необходимо писать цифрой, без пробелов!")
	elif state == 'new_product_fat':
		try:
			float(message.text)
			buffer = sqlite_query.get_user_buffer(chat_id)
			sqlite_query.set_user_buffer(chat_id, buffer[0]+"|+|"+message.text)
			sqlite_query.set_user_state(chat_id, "new_product_carboh")
			bot.send_message(chat_id, "Принято! Теперь напишите цифрой кол-во углеводов на 100гр")
		except ValueError:
			bot.send_message(chat_id, "Необходимо писать цифрой, без пробелов!")
	elif state == 'new_product_carboh':
		try:
			float(message.text)
			buffer = sqlite_query.get_user_buffer(chat_id)
			sqlite_query.set_user_buffer(chat_id, buffer[0]+"|+|"+message.text)
			#[name_product, kkal, whey, fat, carboh]
			buffer_list = buffer[0].split("|+|")
			sqlite_query.save_product(buffer_list[0], buffer_list[1],buffer_list[2],buffer_list[3],float(message.text))
			sqlite_query.set_user_state(chat_id, "how_much")
			bot.send_message(chat_id, "Принято! Теперь напишите цифрой кол-во съеденного продукта:")
		except ValueError:
			bot.send_message(chat_id, "Необходимо писать цифрой, без пробелов!")
	elif state == 'how_much':
		try:
			float(message.text)
		except ValueError:
			print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
			bot.send_message(chat_id, "Необходимо писать цифрой, без пробелов!")
			return True
		#[name_product, whey, fat, carboh]
		buffer = sqlite_query.get_user_buffer(chat_id)[0].split("|+|")
		sqlite_query.set_user_ate(chat_id, buffer[1],buffer[2],buffer[3],buffer[4],float(message.text))
		sqlite_query.set_user_state(chat_id, "")
		bot.send_message(chat_id, "Записано",reply_markup=keyboard_cabinet(chat_id))
	elif state == "set_weight":
		try:
			float(message.text)
			sqlite_query.set_weight(chat_id, float(message.text))
			sqlite_query.set_user_state(chat_id, "")
			bot.send_message(chat_id, "Записано",reply_markup=keyboard_cabinet(chat_id))
		except ValueError:
			bot.send_message(chat_id, "Необходимо писать цифрой, без пробелов!")
	elif state == "set_long":
		try:
			float(message.text)
			sqlite_query.set_body_long(chat_id, float(message.text))
			sqlite_query.set_user_state(chat_id, "")
			bot.send_message(chat_id, "Записано",reply_markup=keyboard_cabinet(chat_id))
		except ValueError:
			bot.send_message(chat_id, "Необходимо писать цифрой, без пробелов!")


	print("it works!")
	print(state)




@bot.callback_query_handler(func=lambda message:True)
def answerOnInline(message):
	chat_id = message.message.chat.id
	state = sqlite_query.get_user_state(chat_id)

	###########################################
	###										###
	###        Answer on body               ###
	###				       					###
	###				        				###
	###				        				###
	###########################################
	if "main_" in message.data:
		num = message.data.split('_')[1]#inline num of function
		#изменить параметры
		if num == '0':
			sqlite_query.set_user_state(chat_id, 'set_body')
			user_info = sqlite_query.get_user_data(chat_id)
			if user_info:
				bot.send_message(chat_id, loginMessage.format(user_info["weight"],
																	user_info["body_long"],
																	user_info["score"],
																	user_info["kkal"],
																	user_info["whey"],
																	user_info["fat"],
																	user_info["carboh"]), reply_markup=keyboard_body_set(chat_id))
			else:
				bot.send_message(chat_id, "Вас нету в базе, обратитесь к @lorrodx")
		#добавить продукт
		elif num == '1':
			sqlite_query.set_user_state(chat_id, 'new_product')
			bot.send_message(chat_id, 'Напишите название продукта')
	elif "body_" in message.data:
		num = message.data.split('_')[1]#inline num of function
		#изменить вес
		if num == '0':
			sqlite_query.set_user_state(chat_id, 'set_weight')
			bot.send_message(chat_id, 'Отправьте ваш вес цифрой')
		#изменить рост
		elif num == '1':
			sqlite_query.set_user_state(chat_id, 'set_long')
			bot.send_message(chat_id, 'Отправьте ваш рост цифрой')
		#изменить цель
		elif num == '2':
			sqlite_query.set_user_state(chat_id, 'set_score')
			bot.send_message(chat_id, 'Выберите цель!', reply_markup=keyboard_score(chat_id))
	elif "score_" in message.data:
		num = message.data.split('_')[1]#inline num of function
		if num == '0':
			#похудение
			sqlite_query.set_score(chat_id, 'lower_weight')
			bot.send_message(chat_id, 'Цель похудение установлена',reply_markup=keyboard_cabinet(chat_id))
		elif num == '1':
			#рост мышц
			sqlite_query.set_score(chat_id, 'gain_muscles')
			bot.send_message(chat_id, 'Цель рост мышечной массы установлена',reply_markup=keyboard_cabinet(chat_id))
		elif num == '2':
			#сбалансированное питание
			sqlite_query.set_score(chat_id, 'be_cool')
			bot.send_message(chat_id, 'Цель оставаться в форме установлена!',reply_markup=keyboard_cabinet(chat_id))
	elif "asknew_" in message.data:
		num = message.data.split('_')[1]#inline num of function
		if num == '0':
			#Согласен внести новый продукт
			sqlite_query.set_user_state(chat_id, 'new_product_kkal')
			bot.send_message(chat_id, 'Вам предстоит ввести информацию о продукте на 100 гр.\nВведите цифрой количество ккал.', reply_markup=decline_new())
		elif num == '1':
			#Отмена
			sqlite_query.set_user_state(chat_id, '')
			sqlite_query.set_user_buffer(chat_id, "")
			bot.send_message(chat_id, 'Добавление продукта отменено.')
	elif "declineNew" in message.data:
		sqlite_query.set_user_buffer(chat_id, "")
		sqlite_query.set_user_state(chat_id, '')
		bot.send_message(chat_id, 'Отменено!')




@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
	print(message)




def keyboard_body_set(chat_id):
	keyboard = types.InlineKeyboardMarkup()
	keys = ["Изменить вес", "Изменить рост", "Изменить цель"]
	for i in range(len(keys)):
		keyboard.add(types.InlineKeyboardButton(text=keys[i],callback_data="body_"+str(i)))
	return keyboard

def keyboard_score(chat_id):
	keyboard = types.InlineKeyboardMarkup()
	keys = ["Похудение", "Набор массы", "Оставаться в форме"]
	for i in range(len(keys)):
		keyboard.add(types.InlineKeyboardButton(text=keys[i],callback_data="score_"+str(i)))
	return keyboard

def keyboard_cabinet(chat_id):
	keyboard = types.InlineKeyboardMarkup()
	keys = ["Изменить параметры", "Записать продукт"]
	for i in range(len(keys)):
		keyboard.add(types.InlineKeyboardButton(text=keys[i],callback_data="main_"+str(i)))
	return keyboard

def keyboard_ask_product():
	keyboard = types.InlineKeyboardMarkup()
	keys = ["Записать в БД", "Отменить"]
	for i in range(len(keys)):
		keyboard.add(types.InlineKeyboardButton(text=keys[i],callback_data="asknew_"+str(i)))
	return keyboard

def decline_new():
	keyboard = types.InlineKeyboardMarkup()
	keyboard.add(types.InlineKeyboardButton(text="Отменить",callback_data="declineNew"))
	return keyboard

bot.infinity_polling(True)
