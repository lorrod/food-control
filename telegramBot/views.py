#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simple echo bot using decorators and webhook with flask
# It echoes any incoming text messages and does not use the polling method.

import logging
import time
import telebot
from telebot import types
from telebot import apihelper

import flask

from app import app
#import flask
import mongodb_query

import sys

import json

import messages

bot = telebot.TeleBot(app.config["TG_TOKEN"])

def req_addr(text):
	return addr_detect.check_if_addr(text)

#   index, return nothing, just for testing
@app.route('/receive_info', methods=['POST'])
def index():
	if request.method == 'POST':
		return ''


# Process webhook calls
@app.route(app.config["WEBHOOK_URL_PATH"], methods=['POST'])
def webhook():
	if flask.request.headers.get('content-type') == 'application/json':
		json_string = flask.request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		bot.process_new_updates([update])
		return ''
	else:
		flask.abort(403)


# Handle '/start' and '/help'



@bot.message_handler(commands=['start'])
def start_message(message):
	mongodb_query.registration_user(message.chat.id)
	bot.send_message(message.chat.id, messages.greetingMessage)
	bot.send_message(message.chat.id, messages.stat_info.format(75, 175,10, "рост мышц", 0,"?",0,"?",0,"?",0,"?"), reply_markup=keyboard_cabinet(message.chat.id))


@bot.message_handler(content_types=['text'])
def send_text(message):
	chat_id = message.chat.id
	state = mongodb_query.get_user_state(chat_id)

	if state == 'new_product':
		products = mongodb_query.get_product_info(message.text)
		if products:
			if len(products) == 1:
				mongodb_query.set_user_buffer(chat_id, products[0])
				mongodb_query.set_user_state(chat_id, "wait_count")
				bot.send_message(chat_id, messages.enter_ate_count)
			else:
				bot.send_message(chat_id, messages.found_several)
				for product in products:
					bot.send_message(chat_id, messages.product_text.format(product["product"],
																	product["kkal"],
																	product["whey"],
																	product["fat"],
																	product["carboh"]), reply_markup=keyboard_select_food(product["_id"]))

		else:
			mongodb_query.set_user_buffer(chat_id, message.text)
			bot.send_message(chat_id, messages.no_product_write, reply_markup=keyboard_ask_product())
	elif state == "wait_count":
		if check_float(chat_id, message.text):
			buffer = mongodb_query.get_user_buffer(chat_id)
			print(buffer)
			print(type(buffer))
			mongodb_query.set_user_ate(chat_id, buffer["kkal"], buffer["whey"],buffer["fat"],buffer["carboh"],float(message.text))
			mongodb_query.set_user_state(chat_id, "")
			bot.send_message(chat_id, messages.accepted,reply_markup=keyboard_cabinet(chat_id))
	elif state == 'new_product_kkal':
		if check_float(chat_id, message.text):
			bot.send_message(chat_id, messages.type_num)
			buffer = mongodb_query.get_user_buffer(chat_id)
			mongodb_query.set_user_buffer(chat_id, buffer+"|+|"+message.text)
			mongodb_query.set_user_state(chat_id, "new_product_whey")
			bot.send_message(chat_id, messages.wait_whey, reply_markup=decline_new())
	elif state == 'new_product_whey':
		if check_float(chat_id, message.text):
			buffer = mongodb_query.get_user_buffer(chat_id)
			mongodb_query.set_user_buffer(chat_id, buffer+"|+|"+message.text)
			mongodb_query.set_user_state(chat_id, "new_product_fat")
			bot.send_message(chat_id, messages.wait_fat, reply_markup=decline_new())
	elif state == 'new_product_fat':
		if check_float(chat_id, message.text):
			buffer = mongodb_query.get_user_buffer(chat_id)
			mongodb_query.set_user_buffer(chat_id, buffer+"|+|"+message.text)
			mongodb_query.set_user_state(chat_id, "new_product_carboh")
			bot.send_message(chat_id, messages.wait_carboh, reply_markup=decline_new())
	elif state == 'new_product_carboh':
		if check_float(chat_id, message.text):
			buffer = mongodb_query.get_user_buffer(chat_id)
			mongodb_query.set_user_buffer(chat_id, buffer+"|+|"+message.text)
			#[name_product, kkal, whey, fat, carboh]
			buffer_list = buffer.split("|+|")
			mongodb_query.save_product(buffer_list[0], buffer_list[1],buffer_list[2],buffer_list[3],float(message.text))
			mongodb_query.set_user_state(chat_id, "how_much")
			bot.send_message(chat_id, messages.wait_count, reply_markup=decline_new())
	elif state == 'how_much':
		if check_float(chat_id, message.text):
			#[name_product, whey, fat, carboh]
			buffer = mongodb_query.get_user_buffer(chat_id) .split("|+|")
			mongodb_query.set_user_ate(chat_id, buffer[1],buffer[2],buffer[3],buffer[4],float(message.text))
			mongodb_query.set_user_state(chat_id, "")
			bot.send_message(chat_id, messages.product_wrtten_ate,reply_markup=keyboard_cabinet(chat_id))
	elif state == "set_weight":
		if check_float(chat_id, message.text):
			mongodb_query.set_weight(chat_id, float(message.text))
			mongodb_query.set_user_state(chat_id, "")
			mongodb_query.update_user_perfect_ate(chat_id)
			bot.send_message(chat_id, messages.set_body_weight,reply_markup=keyboard_cabinet(chat_id))
	elif state == "set_long":
		if check_float(chat_id, message.text):
			mongodb_query.set_body_long(chat_id, float(message.text))
			mongodb_query.set_user_state(chat_id, "")
			mongodb_query.update_user_perfect_ate(chat_id)
			bot.send_message(chat_id, messages.set_body_long,reply_markup=keyboard_cabinet(chat_id))
	elif state == "set_body_fat":
		if check_float(chat_id, message.text):
			if int(message.text) < 50 and int(message.text) > 0:
				mongodb_query.set_body_fat(chat_id, float(message.text))
				mongodb_query.set_user_state(chat_id, "")
				mongodb_query.update_user_perfect_ate(chat_id)
				bot.send_message(chat_id, messages.set_body_fat,reply_markup=keyboard_cabinet(chat_id))
			else:
				bot.send_message(chat_id, messages.expect_0_50)
	else:
		user_info = mongodb_query.get_user_data(chat_id)
		if user_info:
			bot.send_message(chat_id, messages.stat_info.format(user_info["weight"],
																user_info["body_long"],
																user_info["body_fat"],
																user_info["score"],
																user_info["kkal"],
																int(user_info["total_kkal"]),
																user_info["whey"],
																int(user_info["total_whey"]),
																user_info["fat"],
																int(user_info["total_fat"]),
																user_info["carboh"],
																int(user_info["total_carboh"])), reply_markup=keyboard_cabinet(chat_id))


	print("it works!")
	print(state)




@bot.callback_query_handler(func=lambda message:True)
def answerOnInline(message):
	chat_id = message.message.chat.id
	state = mongodb_query.get_user_state(chat_id)

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
			user_info = mongodb_query.get_user_data(chat_id)
			if user_info:
				bot.send_message(chat_id, messages.stat_info.format(user_info["weight"],
																	user_info["body_long"],
																	user_info["body_fat"],
																	user_info["score"],
																	user_info["kkal"],
																	int(user_info["total_kkal"]),
																	user_info["whey"],
																	int(user_info["total_whey"]),
																	user_info["fat"],
																	int(user_info["total_fat"]),
																	user_info["carboh"],
																	int(user_info["total_carboh"])), reply_markup=keyboard_body_set(chat_id))
			else:
				bot.send_message(chat_id, messages.not_in_db)
		#добавить продукт
		elif num == '1':
			mongodb_query.set_user_state(chat_id, 'new_product')
			bot.send_message(chat_id, messages.wait_product_name)
	elif "body_" in message.data:
		num = message.data.split('_')[1]#inline num of function
		#изменить вес
		if num == '0':
			mongodb_query.set_user_state(chat_id, 'set_weight')
			bot.send_message(chat_id, messages.wait_body_weight)
		#изменить рост
		elif num == '1':
			mongodb_query.set_user_state(chat_id, 'set_long')
			bot.send_message(chat_id, messages.wait_body_long)
		#изменить % жира
		elif num == '2':
			mongodb_query.set_user_state(chat_id, 'set_body_fat')
			hint_body_fat = open('static/img/hint_body_fat.jpg', 'rb')
			bot.send_photo(chat_id, hint_body_fat)
			hint_body_fat.close()
			bot.send_message(chat_id, messages.wait_body_fat)
		#изменить программу
		elif num == '3':
			mongodb_query.set_user_state(chat_id, 'set_score')
			bot.send_message(chat_id, messages.choose_main_prog, reply_markup=keyboard_score(chat_id))
	elif "score_" in message.data:
		ident_prog = message.data.split('_')[1]#inline num of function
		bot.send_message(chat_id, messages.wait_subprog,reply_markup=keyboard_detailedScore(ident_prog))
	elif "infoScore_" in message.data:
		ident_prog = message.data.split('_')[1]
		info = mongodb_query.get_info_prog(ident_prog)
		bot.send_message(chat_id, info,reply_markup=keyboard_score(chat_id))
	elif "detailedScore_" in message.data:
		ident_prog = message.data.split('_')[1]
		prog_full_name = mongodb_query.get_full_name_subprog(ident_prog)
		mongodb_query.set_score(chat_id, prog_full_name)
		mongodb_query.update_user_perfect_ate(chat_id)
		bot.send_message(chat_id, messages.set_subprog.format(prog_full_name),reply_markup=keyboard_cabinet(chat_id))
	elif "infoDetailedScore_" in message.data:
		ident_prog = message.data.split('_')[1]
		main_ident = message.data.split('_')[2]
		info = mongodb_query.get_info_subprog(ident_prog)
		bot.send_message(chat_id, info,reply_markup=keyboard_detailedScore(main_ident))
	elif "asknew_" in message.data:
		num = message.data.split('_')[1]#inline num of function
		if num == '0':
			#Согласен внести новый продукт
			mongodb_query.set_user_state(chat_id, 'new_product_kkal')
			buffer = mongodb_query.get_user_buffer(chat_id)
			if "|+|" in buffer:
				bot.send_message(chat_id, messages.bug_fix)
			else:
				bot.send_message(chat_id, messages.wait_kkal, reply_markup=decline_new())
		elif num == '1':
			#Отмена
			mongodb_query.set_user_state(chat_id, '')
			mongodb_query.set_user_buffer(chat_id, "")
			bot.send_message(chat_id, messages.canceled_new_prod)
	elif "declineNew" in message.data:
		mongodb_query.set_user_buffer(chat_id, "")
		mongodb_query.set_user_state(chat_id, '')
		bot.send_message(chat_id, messages.canceled_in_prog)
	elif "foodSelect_" in message.data:
		food_id =  message.data.split('_')[1]

		product = mongodb_query.get_product_byID(food_id)
		if product:
			mongodb_query.set_user_buffer(chat_id, product[0])
			mongodb_query.set_user_state(chat_id, "wait_count")
			bot.send_message(chat_id, messages.wait_eaten_count, reply_markup=decline_new())

@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
	print(message)

def check_float(chat_id, num):
	try:
		float(num)
		return True
	except ValueError:
		print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
		bot.send_message(chat_id, messages.wait_float, reply_markup=decline_new())
		return False



def keyboard_body_set(chat_id):
	keyboard = types.InlineKeyboardMarkup()
	keys = ["Изменить вес", "Изменить рост", "Изменить % жира", "Изменить программу"]
	for i in range(len(keys)):
		keyboard.add(types.InlineKeyboardButton(text=keys[i],callback_data="body_"+str(i)))
	return keyboard

def keyboard_score(chat_id):
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	programms = mongodb_query.get_programms_names()
	#programms = ["slimming":"Похудение", "gain":"Набор массы", "tonus":"Быть в тонусе"]
	for key in programms:
		set_but = types.InlineKeyboardButton(text=programms[key],callback_data="score_"+key)
		info_but = types.InlineKeyboardButton(text="Описание",callback_data="infoScore_"+key)
		keyboard.row(set_but, info_but)
	return keyboard

def keyboard_detailedScore(main_prog):
	keyboard = types.InlineKeyboardMarkup(row_width=2)
	programms = mongodb_query.get_subprograms(main_prog)
	for key in programms:
		set_but = types.InlineKeyboardButton(text=programms[key],callback_data="detailedScore_"+key+"_"+main_prog)
		info_but = types.InlineKeyboardButton(text="Описание",callback_data="infoDetailedScore_"+key+"_"+main_prog)
		keyboard.row(set_but, info_but)
	return keyboard

def keyboard_cabinet(chat_id):
	keyboard = types.InlineKeyboardMarkup(row_width=3)
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


def keyboard_select_food(id):
	keyboard = types.InlineKeyboardMarkup()
	keyboard.add(types.InlineKeyboardButton(text="⬆️Выбрать⬆️",callback_data="foodSelect_"+str(id)))
	return keyboard





# Set webhook
try:
	# Remove webhook, it fails sometimes the set if there is a previous webhook
	bot.remove_webhook()
	time.sleep(5)
	bot.set_webhook(url=app.config["WEBHOOK_URL_BASE"] + app.config["WEBHOOK_URL_PATH"], certificate=open(app.config["WEBHOOK_SSL_CERT"], 'r'))
except Exception as e:
	print("couldnt set webhook, probably it wasn't removed")
	print(e)
