import akinator
from random import *
from akinator import Akinator
import telebot
from telebot import types
from telebot.types import InlineKeyboardButton as btn
from telebot.types import InlineKeyboardMarkup as km
from kvsqlite.sync import Client

start = km(
    [
        [
            btn('- CH', "cn_world.t.me")
        ]
    ]
)

bot = telebot.TeleBot("6624054899:AAHmKFKNCb7On9NZJAT7FN7L_x0koJCq7Q4")

db = Client("akinator.sqlite")

@bot.message_handler(commands=["start"])
def startt(message):
	name = message.from_user.first_name
	id = message.from_user.id
	mention = "["+name+"](tg://user?id="+str(id)+")"
	bot.reply_to(message,f"""مرحبا بك {mention} في بوت أكاينتور (المارد الازرق)

استطيع معرفة الشخصية التي تدور في بالك بمجموعة من الاسئلة فقط.

اضغط /play لبدء اللعب

اضغط /info لمعرفة معلومات لعبك""",reply_markup=start,parse_mode="markdown")

@bot.message_handler(commands=["info"])
def info(message):
	id = message.from_user.id
	if not db.exists(f"yes_guess_{id}"):
		db.set(f"yes_guess_{id}",0)
		yes = db.get(f"yes_guess_{id}")
	else:
		yes = db.get(f"yes_guess_{id}")
		
	if not db.exists(f"no_guess_{id}"):
		db.set(f"no_guess_{id}",0)
		no = db.get(f"no_guess_{id}")
	else:
		no = db.get(f"no_guess_{id}")
	all_attempts = yes+no
	bot.reply_to(message,"""
أجمالي المحاولات: {}

عدد المحاولات التي فزت بها: {}
عدد الخسارات عند لعبك معي: {}
""".format(all_attempts,yes,no))
@bot.message_handler(commands=["play"])
def play(message):
	name = message.from_user.first_name
	id = message.from_user.id
	mention = "["+name+"](tg://user?id="+str(id)+")"
	aki = akinator.Akinator()
	q = aki.start_game(language='Arabic')
	photo=open('aki_pics/aki_01.png', 'rb')
	msg = bot.send_photo(message.chat.id,photo,caption="جاري بدء اللعبة...",reply_to_message_id=message.message_id)
	db.set(f"aki_{id}",aki)
	db.set(f"q_{id}",q)
	db.set(f"ques_{id}",1)
	db.set(f"total_questions_{id}",1)
	
	aki_play = km(
	    [
	        [
	            btn("- نعم .", callback_data=f'{id}_play_0'),
	            btn("- لا .", callback_data=f'{id}_play_1'),
	            btn("- من المحتمل .", callback_data=f'{id}_play_3')
	        ],
	        [
	            btn("- لا اعلم .", callback_data=f'{id}_play_2'),
	            btn("- على الاغلب لا .", callback_data=f'{id}_play_4')
	        ],
	        [   btn("- العوده .", callback_data= f'{id}_play_5')
	        ]
	    ]
	)
	
	aki_win = km(
    	[
     	   [
    	        btn("- نعم .", callback_data=f'{id}_win_y'),
   	         btn("- لا .", callback_data=f'{id}_win_n'),
  	      ]
 	   ]
	)
	
	bot.edit_message_caption(
		chat_id=message.chat.id,
		message_id=msg.message_id,
		caption=q,
		reply_markup=aki_play
	)

@bot.callback_query_handler(func=lambda call: True)
def call(call):
	id = call.from_user.id
	aki_play = km(
	    [
	        [
	            btn("- نعم .", callback_data=f'{id}_play_0'),
	            btn("- لا .", callback_data=f'{id}_play_1'),
	            btn("- من المحتمل .", callback_data=f'{id}_play_3')
	        ],
	        [
	            btn("- لا اعلم .", callback_data=f'{id}_play_2'),
	            btn("- على الاغلب لا .", callback_data=f'{id}_play_4')
	        ],
	        [   btn("- العوده .", callback_data= f'{id}_play_5')
	        ]
	    ]
	)
	aki_win = km(
    	[
     	   [
    	        btn("- نعم .", callback_data=f'{id}_win_y'),
   	         btn("- لا .", callback_data=f'{id}_win_n'),
  	      ]
 	   ]
	)
	if f"{id}_play" in call.data:
		aki = db.get(f"aki_{id}")
		q = db.get(f"q_{id}")
		total = db.get(f"total_questions_{id}") + 1
		db.set(f"total_questions_{id}",total)
		a = call.data.split('_')[-1]
		if a == '5':
			total = db.get(f"total_questions_{id}") - 1
			db.set(f"total_questions_{id}",total)
			try:
				q = aki.back()
			except akinator.exceptions.CantGoBackAnyFurther:
				bot.answer_callback_query(call.id,"هذا هو السؤال الأول. لا يمكنك العودة إلى أبعد من ذلك!", show_alert=True)
		else:
			print(call.message.message_id)
			q = aki.answer(a)
		if aki.progression < 90:
			print(aki.first_guess)
			bot.edit_message_media(
				chat_id=call.message.chat.id,
				message_id=call.message.message_id,
				media=types.InputMediaPhoto(
					open(f'aki_pics/aki_0{randint(1,5)}.png','rb'),caption=q),
				reply_markup=aki_play
				)
			db.set(f"aki_{id}",aki)
			db.set(f"q_{id}",q)
		else:
			aki.win()
			aki = aki.first_guess
			print(aki)
			if aki['picture_path'] == 'none.jpg':
				aki['absolute_picture_path'] = open('aki_pics/none.jpg', 'rb')
			bot.edit_message_media(
				chat_id=call.message.chat.id,
				message_id=call.message.message_id,
				media=types.InputMediaPhoto(
					aki['absolute_picture_path'],caption=f"أنه/ا {aki['name']} ({aki['description']})! صحيح؟"),
				reply_markup=aki_win
			)
			db.delete(f"aki_{id}")
			db.delete(f"q_{id}")
	else:
		ans = call.data.split('_')[-1]
		if ans == "y":
			bot.edit_message_media(
				chat_id=call.message.chat.id,
				message_id=call.message.message_id,
				media=types.InputMediaPhoto(
					open('aki_pics/aki_win.png', 'rb'),
					caption="gg!"),
				reply_markup=None
				)
			if not db.exists(f"yes_guess_{id}"):
				db.set(f"yes_guess_{id}",1)
			else:
				guess = db.get(f"yes_guess_{id}") + 1
				db.set(f"yes_guess_{id}",guess)
		else:
			bot.edit_message_media(
				chat_id=call.message.chat.id,
				message_id=call.message.message_id,
				media=types.InputMediaPhoto(
					open('aki_pics/aki_defeat.png', 'rb'),
					caption="bruh :("),
				reply_markup=None
				)
			if not db.exists(f"no_guess_{id}"):
				db.set(f"no_guess_{id}",1)
			else:
				guess = db.get(f"no_guess_{id}") + 1
				db.set(f"no_guess_{id}",guess)
bot.infinity_polling()