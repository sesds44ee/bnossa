import asyncio, sqlite3

from pyromod import listen

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from pyrogram.errors import SessionPasswordNeeded, PhoneCodeExpired

from pyrogram.errors.exceptions.bad_request_400 import PasswordHashInvalid,PhoneCodeInvalid

from pyrogram.errors.exceptions.not_acceptable_406 import PhoneNumberInvalid

from config import *

token = BOT_TOKEN

api_id = API_ID
api_hash = API_HASH

allwod_ids=[ADMIN]
processing = False
clients = []

app = Client(
	"Bot-Sessions/bot",
	api_id=api_id,
	api_hash=api_hash,
	bot_token=token
	)
con = sqlite3.connect("database.db")
cur = con.cursor()
#——————–——–———————————––#
async def setup():
	#cur.execute("""
	#	DROP TABLE IF EXISTS accs"""
	#	)
	
	cur.execute("""
		CREATE TABLE IF NOT EXISTS accs (
			stringe VARCHAR(363),
			acc_name TEXT,
			acc_number TEXT,
			id TEXT
			)"""
		)
	
	cur.execute("""
	CREATE TABLE IF NOT EXISTS admins(
		id TEXT
		)
		""")
	con.commit()
#——————–——–———————————––#
async def save_session(string,name,nu,iD):
	cmd = f"""
	INSERT INTO `accs` 
	(`stringe`,`acc_name`,`acc_number`,`id`)
	VALUES ('{string}','{name}','{nu}', '{iD}')"""
	cur.execute(cmd)
	con.commit()
#——————–——–———————————––#
async def add_admin(iD):
	cmd = f"""
	INSERT INTO `admins` 
	(`id`)
	VALUES ('{iD}')"""
	cur.execute(cmd)
	con.commit()

async def remove_admin(iD):
	cmd = f"""
	DELETE FROM `admins` WHERE `id` = {iD}"""
	cur.execute(cmd)
	con.commit()

async def update_admins():
	del allwod_ids[:]
	allwod_ids.append(ADMIN)
	cur.execute("""
		SELECT id FROM admins
		""")
	ids = cur.fetchall()
	for id in ids:
		allwod_ids.append(int(id[0]))
#——————–——–———————————––#
async def sessions_num():
	try:
		cur.execute("SELECT COUNT(*) FROM accs")
		result = cur.fetchone()
		row_count = result[0]
		return row_count
	except Exception as e:
		print(f"Error counting files: {e}")
		return None
#——————–——–———————————––#
async def accounts():
	apps = []
	cur.execute("SELECT stringe FROM accs")
	sess = cur.fetchall()
	
	for app in sess:
		apps.append(
			Client(
				api_id=api_id,
				api_hash=api_hash,
				name="None",
				session_string=app[0],
				in_memory=True
			))
	del clients[:]
	await startcls(apps)
	return apps

async def startcls(sessions):
	global clients
	for session in sessions:
		try:
			await session.start()
			clients.append(session)
		except Exception:
			continue
#——————–——–———————————––#
async def get_urls(acc):
	urls = ""
	msgs = acc.get_chat_history(777000)
	async for msg in msgs:
		try:
			if str(msg.service) == "MessageServiceType.GIFT_CODE":
				urls += (f"https://t.me/giftcode/{msg.gift_code.slug}\n\nmonths: {msg.gift_code.months}\n\nChat: {msg.gift_code.boost_peer.username}")
		except: continue
	return urls
#——————–——–———————————––#
async def func(_, __, query):
	return query.data == "menu"
menu_filter = filters.create(func)

async def main_menu():
	sess_num = await sessions_num()
	inline_keyboard = [
	[InlineKeyboardButton("تشغيل/اعادة تشغيل الحسابات", callback_data="start_bot")],
	
	[InlineKeyboardButton("إضافة حساب", callback_data="add_acc")],
	
	[InlineKeyboardButton("جلب الروابط", callback_data="get_urls")]
	]
	reply_markup = InlineKeyboardMarkup(inline_keyboard)
	text = f"""
اهلاً
عدد الحسابات في البوت: {sess_num}

اذا كنت تشغل البوت لاول مرة او بعد اضافة حساب جديد عليك ان تشغل الحسابات من الزر بالاسفل

اختر ما تريد من الاسفل:

"""
	return reply_markup, text
#——————–——–———————————––#
@app.on_message(filters.command("start"))
@app.on_callback_query(menu_filter)
async def start_command(client, message):
	await update_admins()
	chat_id = message.from_user.id
	if int(chat_id) not in allwod_ids:return
	msg = await main_menu()
	
	await client.send_video(
		chat_id=message.from_user.id,
		caption=msg[1],
		reply_markup=msg[0],
		video="https://telegra.ph/file/fca0e84ec96b8c995ce55.mp4"
	)
#——————–——–———————————––#
@app.on_callback_query()
async def handle_callback_query(client, callback_query):
	global processing, clients
	data = callback_query.data
	msg = callback_query.message
	chat_id = callback_query.from_user.id

	if data == 'add_acc':
		if processing:
			await app.send_message(msg.chat.id,"هناك عملية جارايه الأن، يرجى انتظارها الي ان تنتهي");return
		processing = True
		try:
			sess_num = await sessions_num()
			name=f"ses-{(sess_num+1)}"
			c = Client(
				f"Sessions/{name}",
				api_id, api_hash,
				device_model="AccountsCTRL",
				in_memory=True
				)
			await c.connect()
			
			phone_ask = await msg.chat.ask(
				"ارسل رقم الهاتف مع رمز الدولة:",
				filters=filters.text
				)
			phone = phone_ask.text
	
			try:
				send_code=await c.send_code(phone)
			except PhoneNumberInvalid:
				return await phone_ask.reply("رقم الهاتف غير صحيح", quote=True)
			except Exception:
				return await phone_ask.reply("حدث خطأ جرب مرة اخرى", quote=True)
	
			hash = send_code.phone_code_hash
			
			code_ask = await msg.chat.ask(
				"ارسل الكود الذي وصلك:\n[ ! ] اذا كنت داخل الحساب الذي تسجل به الان فأدخل الكود مع وضع مسافات بين الارقام مثال: 1 2 3 4 5", 
				filters=filters.text
				)
			code = code_ask.text.replace(" ", "")
			try:
				await c.sign_in(phone, hash, code)
			except SessionPasswordNeeded:
				password_ask = await msg.chat.ask("ارسل كلمة سر الحساب:", filters=filters.text)
				password = password_ask.text
				try:
					await c.check_password(password)
				except PasswordHashInvalid:
					return await password_ask.reply("كلمة السر غير صالحة يرجى اعادة تسجيل الدخول من البداية", quote=True)
			except (PhoneCodeInvalid, PhoneCodeExpired):
				return await code_ask.reply("رمز تسجيل الدخول غير صحيح يرجى تسجيل الدخول من البداية", quote=True)
			try:
				await c.sign_in(phone, hash, code)
			except Exception:
				pass
			get = await c.get_me()
			text = '**✅ تم تسجيل الدخول بنجاح\n'
			text += f'👤 الاسم الأول : {get.first_name}\n'
			text += f'🆔 بطاقة تعريف : {get.id}\n'
			text += f'📞 رقم الهاتف : {phone}\n'
			text += '\n/start'
			await app.send_message(msg.chat.id, text)
			
			string_session = await c.export_session_string()
			await save_session(
				string_session,
				get.first_name,
				phone,
				get.id
				)
			
			processing = False
			return
		except Exception as e:
			print(e)
		finally:
			processing = False
#——————–——–———————————––#
	elif data == "get_urls":
		if processing:
			await app.send_message(msg.chat.id,"هناك عملية جارايه الأن، يرجى انتظارها الي ان تنتهي");return
		processing = True
		temp_msg = await client.send_message(
		chat_id=chat_id,
		text="تم البدأ في جلب الروابط")
		try:
			urls = ""
			for acc in clients:
				try:
					data = await get_urls(acc)
					urls += data
				except Exception as e:
					continue
			await temp_msg.delete()
			if urls == "":
				await client.send_message(
				text="لا يوجد اي روابط في اي حساب",
				chat_id=chat_id
				)
			else:
				await client.send_message(
				text=f"""تم ايجاد هذة الروابط:
{urls}""",
				chat_id=chat_id
				)
		except Exception as e:
			await client.send_message(
			text="حدث خطأ اثناء جلب الروابط",
			chat_id=chat_id
			)
			print(e)
		finally:
			processing = False
		return
#——————–——–———————————––#
	elif data == "start_bot":
		msg = await client.send_message(
			chat_id=chat_id,
			text="تم البدأ في تشغيل جميع الجلسات")
		try:
			await accounts()
			await msg.edit_text(f"تم الانتهاء من تشغيل: {len(clients)} حساب")
		except Exception as e:
			await msg.edit_text(f"حدث خطأ اثناء تشغيل الحسابات {e}")
#——————–——–———————————––#
	elif data == "temp_menu":
		menu = await main_menu()
		await app.edit_message_caption(
		chat_id=chat_id,
		message_id=msg.id,
		caption=menu[1],
		reply_markup= menu[0])
#——————–——–———————————––#
@app.on_message(filters.command("add"))
async def add_admin_cmd(client, message):
	chat_id = message.from_user.id
	if int(chat_id) != ADMIN:return
	try:
		id = message.text.split(" ")[1]
		allwod_ids.append(int(id))
		await add_admin(id)
		await message.reply_text(f"تم اضافة: {id} الي الادمنية بنجاح") 
	except: 
		await message.reply_text("ارسل الايدي مع الامر")

@app.on_message(filters.command("remove"))
async def remove_admin_cmd(client, message):
	try:
		chat_id = message.from_user.id
		if int(chat_id) != ADMIN:return
		id = message.text.split(" ")[1]
		if int(id) in allwod_ids:
			allwod_ids.remove(int(id))
			await remove_admin(int(id))
			await message.reply_text(f"تم ازالة: {id} من الادمنية بنجاح")
		else: 
			await message.reply_text(f"{id} ليس موجوداً في الادمنية")
	except: 
		await message.reply_text("ارسل الايدي مع الامر")


print("Bot Started \nHave Fun <3")

loop = asyncio.get_event_loop()
loop.run_until_complete(setup())

asyncio.run(app.run())