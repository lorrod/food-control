import re
import base64
from app import mongo
from bson.objectid import ObjectId


def registration_user(chat_id):
	if list(mongo.db.users_table.find({"tgNumber": chat_id}).limit(1)):
		return False
	else:
		mongo.db.users_table.insert({"tgNumber": chat_id, "weight":75,"body_long":175,"body_fat":10,"score":"Похудение | Малая активность"})
		mongo.db.user_eaten.insert({"tgNumber": chat_id, "kkal":0.0,"whey":0.0,"fat":0.0,"carboh":0.0})
		#kost
		update_user_perfect_ate(chat_id)
		return True


def get_user_state(tgNum):
	user_state = list(mongo.db.user_state.find({"tgNumber":tgNum}).limit(1))
	if user_state:
		return user_state[0]["state"]
	else:
		mongo.db.user_state.insert({"tgNumber": tgNum,
						 "state": "new_user"
						})
		return "new_user"

def set_user_state(tgNum, state):
	mongo.db.user_state.update({"tgNumber": tgNum},
								{"$set": {"tgNumber": tgNum,
										  "state": state
										  }
								})
	return True

def set_user_buffer(tgNum, buffer):
	mongo.db.user_state.update({"tgNumber": tgNum},
									{"$set": {"buffer": buffer
											  }})

def get_user_buffer(tgNum):
	return list(mongo.db.user_state.find({"tgNumber":tgNum}).limit(1))[0]['buffer']


def get_product_info(product):
	product = list(mongo.db.products.find({"product": re.compile('.*'+product.lower()+'.*', re.IGNORECASE)}))
	if product:
		return product
	else:
		return False

def get_product_byID(product_id):
	product = list(mongo.db.products.find({"_id": ObjectId(product_id)}))
	if product:
		return product
	else:
		return False


def save_product(product,kkal,whey,fat,carboh):
	mongo.db.products.insert({"product":product, "kkal":kkal,"whey":whey,"fat":fat,"carboh":carboh})
	return True

def set_user_ate(chat_id, kkal, whey,fat,carboh,count):
	already_eaten = list(mongo.db.user_eaten.find({"tgNumber": chat_id}).limit(1))
	print(already_eaten)
	if already_eaten:
		print("IN")
		check = mongo.db.user_eaten.update({"tgNumber": int(chat_id)},
											{"$set": {"tgNumber": int(chat_id),
														"kkal": already_eaten[0]["kkal"]+float(kkal)*count/100,
														"whey": already_eaten[0]["whey"]+float(whey)*count/100,
														"fat": already_eaten[0]["fat"]+float(fat)*count/100,
														"carboh": already_eaten[0]["carboh"]+float(carboh)*count/100
													  }})

		print(check)
		print(list(check))
	else:
		mongo.db.user_eaten.insert({"tgNumber": chat_id},
									{"$set": {"kkal": kkal,
												"whey": whey,
												"fat": fat,
												"carboh": carboh
											  }})
	return True


def get_user_data(chat_id):
	already_eaten = list(mongo.db.user_eaten.find({"tgNumber": chat_id}).limit(1))
	if already_eaten:
		user_score = list(mongo.db.users_table.find({"tgNumber": chat_id}).limit(1))
		if user_score:
			already_eaten[0].update(user_score[0])
			return already_eaten[0]
	return False




def set_weight(chat_id, weight):
	mongo.db.users_table.update({"tgNumber": chat_id},
								{"$set": {"tgNumber": chat_id,
										  "weight": weight
										  }
								})
	return True

def set_body_long(chat_id, long):
	mongo.db.users_table.update({"tgNumber": chat_id},
								{"$set": {"tgNumber": chat_id,
										  "body_long": long
										  }
								})

def set_body_fat(chat_id, fat):
	mongo.db.users_table.update({"tgNumber": chat_id},
								{"$set": {"tgNumber": chat_id,
										  "body_fat": fat
										  }
								})

def set_score(chat_id, score):
	mongo.db.users_table.update({"tgNumber": chat_id},
								{"$set": {"tgNumber": chat_id,
										  "score": score
										  }
								})



def get_programms_names():
	programms = list(mongo.db.programms.find())
	if programms:
		dict_progs = {}
		for prog in programms:
			dict_progs[prog["ident_name"]] = prog["name"]
		return dict_progs

def get_subprograms(main_prog):
	programms = list(mongo.db.sub_programms.find({"ident_name":main_prog}))
	if programms:
		dict_progs = {}
		for prog in programms:
			dict_progs[prog["ident_sub_prog"]] = prog["name"]
		return dict_progs

def get_full_name_subprog(ident_name):
	programm = list(mongo.db.sub_programms.find({"ident_sub_prog":ident_name},{
																		"name":0,
																		"info":0,
							                                            "koef_kkal":0,
							                                            "koef_whey":0,
							                                            "koef_fat":0,
							                                            "koef_carboh":0
																		}).limit(1))
	if programm:
		return programm[0]["full_name"]


def get_info_prog(ident_name):
	programm_info = list(mongo.db.programms.find({"ident_name":ident_name}).limit(1))
	if programm_info:
		return programm_info[0]["info"]

def get_info_subprog(ident_name):
	programm_info = list(mongo.db.sub_programms.find({"ident_sub_prog":ident_name},{
																		"name":0,
							                                            "koef_kkal":0,
							                                            "koef_whey":0,
							                                            "koef_fat":0,
							                                            "koef_carboh":0
																		}).limit(1))
	if programm_info:
		return programm_info[0]["info"]

def get_koefs_subprog(ident_name):
	programm_info = list(mongo.db.sub_programms.find({"ident_sub_prog":ident_name},{"name":0}).limit(1))
	print(programm_info)
	if programm_info:
		return programm_info[0]
	else:
		return False

def get_koefs_subprogByFullName(full_name):
	programm_info = list(mongo.db.sub_programms.find({"full_name":full_name},{"name":0}).limit(1))
	if programm_info:
		return programm_info[0]
	else:
		return False

def update_user_perfect_ate(chat_id):
	user_data = list(mongo.db.users_table.find({"tgNumber": chat_id}).limit(1))[0]
	if user_data:
		koef_data = get_koefs_subprogByFullName(user_data["score"])
		if not koef_data:
			return False
		# не используем user_data["body_long"] ????
		Z = 370+(21.6*((1-user_data["body_fat"]/100)*user_data["weight"]))
		kkal = koef_data["koef_kkal"]*Z
		whey = koef_data["koef_whey"]*2.2*user_data["weight"]
		fat = koef_data["koef_fat"]*2.2*user_data["weight"]
		carboh = koef_data["koef_carboh"]*2.2*user_data["weight"]
		mongo.db.users_table.update({"tgNumber": chat_id},
									{"$set": {"total_kkal": kkal,
											  "total_whey": whey,
											  "total_fat": fat,
											  "total_carboh": carboh
											  }
									})
		return True
