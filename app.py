
# ...existing imports...


# ...existing imports...

# app.py - بوت منهج Ai (الإصدار النهائي الكامل بدون أخطاء)

import os
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

import warnings
warnings.filterwarnings("ignore")
import logging
logging.getLogger('google').setLevel(logging.ERROR)

import sqlite3
import json
import uuid 
import asyncio 
import time 
import re
import csv
import aiohttp
import secrets
import io
from PIL import Image
from datetime import datetime
import google.generativeai as genai
from telegram.ext import ContextTypes
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler,
    CallbackQueryHandler 
)

print("🚀 بدء تشغيل بوت منهج Ai...")

# الأساسيات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_TOKEN = "8593626753:AAF77_QpHhFjEXG51QmLTkkKoHfr6jJ2JQQ"
CONFIG_FILE = f'{BASE_DIR}/البيانات/config.json' 

# قائمة النماذج المتوفرة للاختبار (مرتبة حسب الأولوية)
AVAILABLE_MODELS = [
    'gemini-2.0-flash',
    'gemini-2.0-flash-exp',
    'gemini-1.5-flash',
    'gemini-1.5-flash-8b', 
    'gemini-1.5-pro',
    'gemini-2.0-flash-thinking-exp',
    'gemini-exp-1121',
    'gemini-exp-1206'
] 

# إعدادات المدير والإعلانات والبريميوم
ADMIN_PASSWORD = "mosap@123123"
AD_LINK = "https://otieu.com/4/10160934"
AD_RESPONSE_LIMIT = 2 

# إعدادات API التحقق من الإعلانات
VERIFY_API_BASE_URL = "https://manhaj-ai-api.vercel.app"
VERIFY_SECRET_KEY = "3HydCoOi2byXBvkjAtG98KOT1u-r18t0G5aPPbHWvcY"

# قائمة الدول والمراحل
ARAB_COUNTRIES = [
    "المملكة العربية السعودية", "مصر", "الإمارات العربية المتحدة", 
    "الكويت", "قطر", "البحرين", "سلطنة عمان", "الأردن", 
    "فلسطين", "سوريا", "لبنان", "العراق", "اليمن", 
    "ليبيا", "تونس", "الجزائر", "المغرب", "السودان", 
    "جيبوتي", "موريتانيا", "الصومال", "جزر القمر"
]

EDUCATION_STAGES = [
    "التعليم الابتدائي (1-6)", 
    "التعليم المتوسط/الإعدادي (7-9)", 
    "التعليم الثانوي/الثالثي (10-12)", 
    "الجامعة/التعليم العالي"
]

# حالات المحادثة
# حالات المحادثة - كاملة ومحدثة 100% (حل نهائي)
(
    NAME, STAGE_SELECTION, COUNTRY_SELECTION, REFERRAL_CODE, MAIN_MENU,
    CONVERT_POINTS, TRANSFER_MONEY, TRANSFER_MONEY_AMOUNT, SUPPORT_MESSAGE, TASKS_MENU,
    ADMIN_PASSWORD_ENTRY, ADMIN_MENU, PREMIUM_ID_ENTRY, PREMIUM_DEACTIVATE_ID_ENTRY,
    BROADCAST_MESSAGE_ENTRY, CHANGE_PRICE_ENTRY, GIFT_PREMIUM_ENTRY,
    ADMIN_SUPPORT_MENU, ADMIN_REPLY_SUPPORT, ADMIN_MANAGE_TASKS,
    ADD_TASK, ADD_TASK_DESC, ADD_TASK_POINTS, ADD_MANAGER, 
    ADMIN_GIVE_POINTS, ADMIN_GIVE_POINTS_USER, ADMIN_GIVE_POINTS_AMOUNT,
    ADMIN_GIVE_MONEY_USER, ADMIN_GIVE_MONEY_AMOUNT,
    ADMIN_TOKENS_MENU, ADD_TOKEN, REMOVE_TOKEN, EDIT_PROMPT,
    ADMIN_BACKUP_MENU, IMPORT_DB, SET_BACKUP_TIME, CHANGE_AD_REWARD, 
    ADD_USER_MANUAL, ADD_USER_MANUAL_NAME, ADD_USER_MANUAL_STAGE,
    COUPON_MENU, GENERATE_COUPON, GENERATE_COUPON_VALUE, USE_COUPON,
    ADMIN_CONTACT_MENU, SET_CONTACT_EMAIL, SET_CONTACT_INSTAGRAM
) = range(47)
# إعدادات الإعلان
AD_START_CALLBACK_DATA = "start_ad_timer"      
AD_CHECK_CALLBACK_DATA = "check_ad_timer"      
AD_CONFIRM_VIEW = "confirm_ad_view"

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# دوال تحميل وحفظ الإعدادات
def load_config():
    """تحميل الإعدادات من ملف JSON"""
    os.makedirs(f'{BASE_DIR}/البيانات', exist_ok=True) 
    default_config = {
        "premium_price": "10 ريال سعودي",
        "contact_email": "mosapadn@gmail.com",
        "contact_instagram": "mos_adn",
        "show_email": True,
        "show_instagram": True,
        "main_gemini_token": "AIzaSyDTqXo6j5Pz5Ki5Y1fjFFGi3Uo6fp5R7b0",
        "premium_points_price": 1000,
        "premium_riyal_price": 10,
        "ad_points_reward": 5
    }
    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
        return default_config
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            for key, default_value in default_config.items():
                config.setdefault(key, default_value)
            return config
    except Exception as e:
        logger.error(f"خطأ في تحميل ملف الإعدادات: {e}")
        return default_config

def save_config(config):
    """حفظ الإعدادات إلى ملف JSON"""
    try:
        # التأكد من وجود المجلد
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # حفظ الإعدادات مع flush للتأكد من الكتابة
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            f.flush()  # فرض كتابة البيانات للقرص
            os.fsync(f.fileno())  # ضمان كتابة البيانات للقرص الفعلي
        
        logger.info(f"[CONFIG] تم حفظ الإعدادات بنجاح في {CONFIG_FILE}")
        return True
        
    except Exception as e:
        logger.error(f"خطأ في حفظ ملف الإعدادات: {e}")
        return False

# تحميل الإعدادات عند بدء التشغيل
GLOBAL_CONFIG = load_config()
PREMIUM_PRICE = GLOBAL_CONFIG.get('premium_price', '10 ريال سعودي')

# نظام التوكنات المتعددة (عادي وبريميم)
GEMINI_TOKENS_STANDARD = GLOBAL_CONFIG.get('gemini_tokens_standard', [])
GEMINI_TOKENS_PREMIUM = GLOBAL_CONFIG.get('gemini_tokens_premium', [])

# ترحيل التوكنات القديمة إلى القائمة العادية
old_tokens = GLOBAL_CONFIG.get('gemini_tokens', [])
if old_tokens:
    for token in old_tokens:
        if token not in GEMINI_TOKENS_STANDARD:
            GEMINI_TOKENS_STANDARD.append(token)
    GLOBAL_CONFIG.pop('gemini_tokens', None)
    GLOBAL_CONFIG['gemini_tokens_standard'] = GEMINI_TOKENS_STANDARD
    save_config(GLOBAL_CONFIG)

# إضافة التوكن الرئيسي القديم للتوافقية إذا لم توجد توكنات
if not GEMINI_TOKENS_STANDARD and not GEMINI_TOKENS_PREMIUM:
    main_token = GLOBAL_CONFIG.get('main_gemini_token', '')
    if main_token:
        GEMINI_TOKENS_STANDARD = [main_token]
        GLOBAL_CONFIG['gemini_tokens_standard'] = GEMINI_TOKENS_STANDARD
        save_config(GLOBAL_CONFIG)

current_token_index_standard = 0
current_token_index_premium = 0

def find_working_model(token):
    """اختبار جميع النماذج المتوفرة والعثور على النموذج الذي يعمل"""
    genai.configure(api_key=token)
    
    for model_name in AVAILABLE_MODELS:
        try:
            logger.info(f"[MODEL-TEST] اختبار النموذج {model_name} مع التوكن {token[:20]}...")
            test_model = genai.GenerativeModel(model_name)
            
            # اختبار سريع
            response = test_model.generate_content("مرحبا")
            
            if response and response.text:
                logger.info(f"[MODEL-TEST] ✅ النموذج {model_name} يعمل بنجاح!")
                return {'model': test_model, 'name': model_name, 'token': token}
                
        except Exception as e:
            logger.warning(f"[MODEL-TEST] ❌ النموذج {model_name} فاشل: {str(e)[:100]}")
            continue
    
    logger.error(f"[MODEL-TEST] ❌ جميع النماذج فاشلة للتوكن {token[:20]}...")
    return None

# تهيئة الذكاء الاصطناعي
AI_جاهز = False
models_standard = []
models_premium = []
current_token_index_standard = 0
current_token_index_premium = 0

def تهيئة_النماذج():
    """تهيئة النماذج مع التوكنات المتاحة (عادي وبريميم)"""
    global models_standard, models_premium, current_token_index_standard, current_token_index_premium, AI_جاهز
    models_standard = []
    models_premium = []
    current_token_index_standard = 0
    current_token_index_premium = 0
    AI_جاهز = False
    
    # تهيئة التوكنات العادية
    for token in GEMINI_TOKENS_STANDARD:
        try:
            model_data = find_working_model(token)
            if model_data:
                models_standard.append(model_data)
                logger.info(f"[INIT] ✅ تم تهيئة توكن عادي بنجاح: {model_data['name']}")
            else:
                logger.error(f"[INIT] ❌ فشل في تهيئة توكن عادي {token[:20]}...")
        except Exception as e:
            logger.error(f"خطأ في تهيئة توكن عادي: {e}")

    # تهيئة توكنات البريميم
    for token in GEMINI_TOKENS_PREMIUM:
        try:
            model_data = find_working_model(token)
            if model_data:
                models_premium.append(model_data)
                logger.info(f"[INIT] 🌟 تم تهيئة توكن بريميم بنجاح: {model_data['name']}")
            else:
                logger.error(f"[INIT] ❌ فشل في تهيئة توكن بريميم {token[:20]}...")
        except Exception as e:
            logger.error(f"خطأ في تهيئة توكن بريميم: {e}")

    if models_standard or models_premium:
        AI_جاهز = True
        print(f"✅ تم تهيئة الذكاء الاصطناعي! (عادي: {len(models_standard)}, بريميم: {len(models_premium)})")
    else:
        print("❌ فشل تهيئة جميع التوكنات")

# تشغيل التهيئة إذا كانت هناك توكنات
if GEMINI_TOKENS_STANDARD or GEMINI_TOKENS_PREMIUM:
    تهيئة_النماذج()
else:
    print("⚠️ لم يتم إضافة أي توكنات جيميني بعد.")

def get_next_model(is_premium=False):
    """الحصول على النموذج التالي بالتناوب (Load Balancing) مع دعم البريميم"""
    global current_token_index_standard, current_token_index_premium
    
    # للمشتركين البريميم: محاولة استخدام توكنات البريميم أولاً
    if is_premium and models_premium:
        model_data = models_premium[current_token_index_premium]
        current_token_index_premium = (current_token_index_premium + 1) % len(models_premium)
        logger.debug(f"[LOAD-BALANCE] 🌟 استخدام نموذج بريميم {model_data['name']}")
        return model_data
    
    # للمستخدمين العاديين أو إذا فشل البريميم (Fallback)
    if models_standard:
        model_data = models_standard[current_token_index_standard]
        current_token_index_standard = (current_token_index_standard + 1) % len(models_standard)
        logger.debug(f"[LOAD-BALANCE] 👤 استخدام نموذج عادي {model_data['name']}")
        return model_data
        
    # إذا كان بريميم ولا يوجد عادي (حالة نادرة جداً)
    if is_premium and not models_standard and models_premium:
         model_data = models_premium[current_token_index_premium]
         current_token_index_premium = (current_token_index_premium + 1) % len(models_premium)
         return model_data

    return None

# إنشاء هيكل المجلدات وقاعدة البيانات
def انشاء_الهيكل():
    مجلدات = [f"{BASE_DIR}/البيانات"]
    for مجلد in مجلدات:
        os.makedirs(مجلد, exist_ok=True)
انشاء_الهيكل()

def تهيئة_قاعدة_البيانات():
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS الطلاب (
                معرف_المستخدم INTEGER PRIMARY KEY,
                الاسم TEXT NOT NULL,
                الصف TEXT NOT NULL,           
                معرف_التحقق_الفريد TEXT UNIQUE,
                عدد_الاسئلة INTEGER DEFAULT 0,
                تاريخ_التسجيل TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                آخر_نشاط TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ردود_منذ_الإعلان INTEGER DEFAULT 0,  
                is_premium INTEGER DEFAULT 0,
                الدولة TEXT DEFAULT 'المملكة العربية السعودية',
                is_gift_premium INTEGER DEFAULT 0,
                رصيد_النقاط INTEGER DEFAULT 0,
                رصيد_الريال INTEGER DEFAULT 0,
                is_manager INTEGER DEFAULT 0,
                احالات_ناجحة INTEGER DEFAULT 0,
                رمز_احالة_مستخدم TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS الاسئلة (
                معرف_سؤال INTEGER PRIMARY KEY AUTOINCREMENT,
                معرف_المستخدم INTEGER,
                السؤال TEXT NOT NULL,
                نوع_البحث TEXT DEFAULT 'عام',
                تاريخ_السؤال TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS المهام (
                مهمة_id INTEGER PRIMARY KEY AUTOINCREMENT,
                رابط TEXT NOT NULL,
                وصف TEXT NOT NULL,
                نقاط INTEGER DEFAULT 10,
                is_active INTEGER DEFAULT 1,
                تاريخ_الإضافة TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS المهام_المكتملة (
                إكمال_id INTEGER PRIMARY KEY AUTOINCREMENT,
                معرف_المستخدم INTEGER,
                مهمة_id INTEGER,
                تاريخ_الإكمال TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS التحويلات (
                تحويل_id INTEGER PRIMARY KEY AUTOINCREMENT,
                مرسل_id INTEGER,
                مستلم_id INTEGER,
                مبلغ INTEGER NOT NULL,
                نوع TEXT NOT NULL,
                تاريخ_التحويل TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS الدعم (
                دعم_id INTEGER PRIMARY KEY AUTOINCREMENT,
                معرف_المستخدم INTEGER,
                الرسالة TEXT NOT NULL,
                الرد TEXT,
                is_answered INTEGER DEFAULT 0,
                تاريخ_الرسالة TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                تاريخ_الرد TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS الكوبونات (
                كوبون_id INTEGER PRIMARY KEY AUTOINCREMENT,
                كود_الكوبون TEXT UNIQUE NOT NULL,
                نوع_المكافأة TEXT NOT NULL,
                قيمة_المكافأة INTEGER NOT NULL,
                is_used INTEGER DEFAULT 0,
                مستخدم_id INTEGER,
                تاريخ_الإنشاء TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                تاريخ_الاستخدام TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ تم تهيئة قاعدة البيانات بنجاح!")
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {e}")

تهيئة_قاعدة_البيانات()

# دوال إدارة البيانات 
def جلب_طالب(معرف_المستخدم):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT الاسم, الصف, الدولة, معرف_التحقق_الفريد, is_premium, is_gift_premium,
                   رصيد_النقاط, رصيد_الريال, is_manager, احالات_ناجحة, رمز_احالة_مستخدم 
            FROM الطلاب WHERE معرف_المستخدم = ?
        ''', (معرف_المستخدم,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"خطأ في جلب الطالب: {e}")
        return None

def حفظ_طالب(معرف_المستخدم, الاسم, المرحلة_الدراسية, الدولة, معرف_التحقق_الفريد=None, رمز_احالة_مستخدم=None):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO الطلاب 
            (معرف_المستخدم, الاسم, الصف, الدولة, معرف_التحقق_الفريد, آخر_نشاط, رمز_احالة_مستخدم)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
        ''', (معرف_المستخدم, الاسم, المرحلة_الدراسية, الدولة, معرف_التحقق_الفريد, رمز_احالة_مستخدم))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ خطأ في حفظ الطالب: {e}")
        return False

def التحقق_من_رمز_الاحالة(رمز_الاحالة):
    """التحقق من وجود رمز الإحالة في قاعدة البيانات"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT معرف_المستخدم, الاسم FROM الطلاب WHERE معرف_التحقق_الفريد = ?', (رمز_الاحالة,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"خطأ في التحقق من رمز الإحالة: {e}")
        return None

def منح_نقاط_الاحالة(معرف_المحيل, معرف_المستخدم_الجديد, اسم_المستخدم_الجديد):
    """منح 100 نقطة للمحيل وإرسال إشعار"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # إضافة النقاط للمحيل
        cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + 100, احالات_ناجحة = احالات_ناجحة + 1 WHERE معرف_المستخدم = ?', (معرف_المحيل,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في منح نقاط الإحالة: {e}")
        return False

def تسجيل_سؤال(معرف_المستخدم, السؤال, نوع_البحث="عام"):
    """تسجيل السؤال وزيادة عداد الإعلانات"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO الاسئلة (معرف_المستخدم, السؤال, نوع_البحث)
            VALUES (?, ?, ?)
        ''', (معرف_المستخدم, السؤال, نوع_البحث))
        
        cursor.execute('''
            UPDATE الطلاب 
            SET عدد_الاسئلة = عدد_الاسئلة + 1, 
                آخر_نشاط = CURRENT_TIMESTAMP
            WHERE معرف_المستخدم = ?
        ''', (معرف_المستخدم,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ خطأ في تسجيل السؤال: {e}")
        return False

# نظام النقاط والتحويلات
def إضافة_نقاط(معرف_المستخدم, نقاط, سبب=""):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + ? WHERE معرف_المستخدم = ?', (نقاط, معرف_المستخدم))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في إضافة نقاط: {e}")
        return False

def تحويل_نقاط_لريال(معرف_المستخدم, نقاط):
    try:
        if نقاط < 100:
            return False, "الحد الأدنى للتحويل 100 نقطة"
        
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # التحقق من الرصيد
        cursor.execute('SELECT رصيد_النقاط FROM الطلاب WHERE معرف_المستخدم = ?', (معرف_المستخدم,))
        رصيد = cursor.fetchone()[0]
        
        if رصيد < نقاط:
            conn.close()
            return False, "رصيد النقاط غير كافي"
        
        ريال = نقاط // 100
        
        # تنفيذ التحويل
        cursor.execute('''
            UPDATE الطلاب 
            SET رصيد_النقاط = رصيد_النقاط - ?,
                رصيد_الريال = رصيد_الريال + ?
            WHERE معرف_المستخدم = ?
        ''', (نقاط, ريال, معرف_المستخدم))
        
        conn.commit()
        conn.close()
        return True, f"تم تحويل {نقاط} نقطة إلى {ريال} ريال"
    except Exception as e:
        logger.error(f"خطأ في تحويل النقاط: {e}")
        return False, "حدث خطأ في التحويل"

def تحويل_ريال(مرسل_id, رمز_المستلم, مبلغ):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # التحقق من رصيد المرسل
        cursor.execute('SELECT رصيد_الريال FROM الطلاب WHERE معرف_المستخدم = ?', (مرسل_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            logger.error(f"المرسل {مرسل_id} غير موجود في قاعدة البيانات")
            return False, "حساب المرسل غير موجود"
        
        رصيد_مرسل = result[0]
        logger.info(f"رصيد المرسل {مرسل_id}: {رصيد_مرسل} ريال، المبلغ المطلوب: {مبلغ}")
        
        if رصيد_مرسل < مبلغ:
            conn.close()
            logger.warning(f"رصيد غير كافي للمرسل {مرسل_id}: {رصيد_مرسل} < {مبلغ}")
            return False, f"رصيد الريال غير كافي\nرصيدك: {رصيد_مرسل} ريال\nالمبلغ المطلوب: {مبلغ} ريال"
        
        # البحث عن المستلم
        cursor.execute('SELECT معرف_المستخدم, الاسم FROM الطلاب WHERE معرف_التحقق_الفريد = ?', (رمز_المستلم,))
        مستلم = cursor.fetchone()
        
        if not مستلم:
            conn.close()
            logger.error(f"المستلم برمز {رمز_المستلم} غير موجود")
            return False, "لم يتم العثور على المستلم"
        
        مستلم_id, اسم_المستلم = مستلم
        logger.info(f"بدء تحويل {مبلغ} ريال من {مرسل_id} إلى {مستلم_id} ({اسم_المستلم})")
        
        # تنفيذ التحويل
        cursor.execute('UPDATE الطلاب SET رصيد_الريال = رصيد_الريال - ? WHERE معرف_المستخدم = ?', (مبلغ, مرسل_id))
        cursor.execute('UPDATE الطلاب SET رصيد_الريال = رصيد_الريال + ? WHERE معرف_المستخدم = ?', (مبلغ, مستلم_id))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ تم التحويل بنجاح: {مبلغ} ريال من {مرسل_id} إلى {مستلم_id}")
        return True, (مستلم_id, اسم_المستلم)
    except sqlite3.Error as e:
        logger.error(f"خطأ في قاعدة البيانات أثناء التحويل: {e}")
        return False, f"خطأ في قاعدة البيانات: {str(e)}"
    except Exception as e:
        logger.error(f"خطأ غير متوقع في تحويل الريال: {e}")
        return False, f"حدث خطأ غير متوقع: {str(e)}"

def شراء_بريميم(معرف_المستخدم):
    try:
        # جلب سعر الريال من الإعدادات
        config = load_config()
        premium_riyal_price = config.get('premium_riyal_price', 10)
        
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('SELECT رصيد_الريال FROM الطلاب WHERE معرف_المستخدم = ?', (معرف_المستخدم,))
        رصيد = cursor.fetchone()[0]
        
        if رصيد < premium_riyal_price:
            conn.close()
            return False, f"رصيد الريال غير كافي. تحتاج {premium_riyal_price} ريال"
        
        cursor.execute('''
            UPDATE الطلاب 
            SET رصيد_الريال = رصيد_الريال - ?,
                is_premium = 1,
                ردود_منذ_الإعلان = 0
            WHERE معرف_المستخدم = ?
        ''', (premium_riyal_price, معرف_المستخدم))
        
        conn.commit()
        conn.close()
        return True, f"تم شراء البريميم بنجاح! تم خصم {premium_riyal_price} ريال"
    except Exception as e:
        logger.error(f"خطأ في شراء البريميم: {e}")
        return False, "حدث خطأ في الشراء"

# نظام المهام
def جلب_المهام_المتاحة(معرف_المستخدم):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT م.مهمة_id, م.رابط, م.وصف, م.نقاط 
            FROM المهام م
            WHERE م.is_active = 1 
            AND م.مهمة_id NOT IN (
                SELECT مهمة_id FROM المهام_المكتملة WHERE معرف_المستخدم = ?
            )
        ''', (معرف_المستخدم,))
        
        مهام = cursor.fetchall()
        conn.close()
        return مهام
    except Exception as e:
        logger.error(f"خطأ في جلب المهام: {e}")
        return []

def إضافة_مهمة(رابط, وصف, نقاط):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO المهام (رابط, وصف, نقاط) VALUES (?, ?, ?)', (رابط, وصف, نقاط))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في إضافة مهمة: {e}")
        return False

def إكمال_مهمة(معرف_المستخدم, مهمة_id):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # الحصول على نقاط المهمة
        cursor.execute('SELECT نقاط FROM المهام WHERE مهمة_id = ?', (مهمة_id,))
        نقاط = cursor.fetchone()[0]
        
        # تسجيل إكمال المهمة
        cursor.execute('INSERT INTO المهام_المكتملة (معرف_المستخدم, مهمة_id) VALUES (?, ?)', (معرف_المستخدم, مهمة_id))
        
        # إضافة النقاط
        cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + ? WHERE معرف_المستخدم = ?', (نقاط, معرف_المستخدم))
        
        conn.commit()
        conn.close()
        return True, نقاط
    except Exception as e:
        logger.error(f"خطأ في إكمال المهمة: {e}")
        return False, 0

# نظام الدعم
def إرسال_رسالة_دعم(معرف_المستخدم, الرسالة):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO الدعم (معرف_المستخدم, الرسالة) VALUES (?, ?)', (معرف_المستخدم, الرسالة))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"خطأ في إرسال رسالة دعم: {e}")
        return False

# ==================== نظام الكوبونات - معاد كتابته بالكامل ====================

def create_coupon_code():
    """توليد كود كوبون فريد"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def توليد_كوبون(نوع_المكافأة, قيمة_المكافأة):
    """
    إنشاء كوبون جديد في قاعدة البيانات
    Returns: (True, coupon_code) عند النجاح أو (False, error_message) عند الفشل
    """
    try:
        # توليد كود جديد
        كود_الكوبون = create_coupon_code()
        logger.info(f"[COUPON-CREATE] محاولة إنشاء كوبون: {كود_الكوبون} ({نوع_المكافأة}: {قيمة_المكافأة})")
        
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db')
        cursor = conn.cursor()
        
        # إدراج الكوبون
        cursor.execute('''
            INSERT INTO الكوبونات (كود_الكوبون, نوع_المكافأة, قيمة_المكافأة, is_used)
            VALUES (?, ?, ?, 0)
        ''', (كود_الكوبون, نوع_المكافأة, قيمة_المكافأة))
        
        conn.commit()
        conn.close()
        
        logger.info(f"[COUPON-CREATE] ✅ نجح! الكود: {كود_الكوبون}")
        return True, كود_الكوبون
        
    except sqlite3.IntegrityError:
        logger.warning(f"[COUPON-CREATE] ⚠️ كود مكرر، إعادة المحاولة...")
        # في حالة التكرار (نادرة جداً)، نحاول مرة أخرى
        return توليد_كوبون(نوع_المكافأة, قيمة_المكافأة)
    except Exception as e:
        logger.error(f"[COUPON-CREATE] ❌ خطأ: {e}")
        return False, f"خطأ في إنشاء الكوبون: {str(e)}"

def استخدام_كوبون(معرف_المستخدم, كود_الكوبون):
    """استخدام كوبون"""
    try:
        logger.info(f"[COUPON-DB] بدء استخدام كوبون: user_id={معرف_المستخدم}, code={كود_الكوبون}")
        
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # التحقق من الكوبون
        cursor.execute('''
            SELECT كوبون_id, نوع_المكافأة, قيمة_المكافأة, is_used
            FROM الكوبونات
            WHERE كود_الكوبون = ?
        ''', (كود_الكوبون.upper(),))
        
        result = cursor.fetchone()
        logger.info(f"[COUPON-DB] نتيجة البحث عن الكوبون: {result}")
        
        if not result:
            logger.warning(f"[COUPON-DB] الكوبون غير موجود: {كود_الكوبون}")
            conn.close()
            return False, "الكوبون غير موجود"
        
        كوبون_id, نوع_المكافأة, قيمة_المكافأة, is_used = result
        logger.info(f"[COUPON-DB] معلومات الكوبون: id={كوبون_id}, نوع={نوع_المكافأة}, قيمة={قيمة_المكافأة}, مستخدم={is_used}")
        
        if is_used:
            logger.warning(f"[COUPON-DB] الكوبون مستخدم مسبقاً")
            conn.close()
            return False, "الكوبون مستخدم مسبقاً"
        
        # تطبيق المكافأة
        if نوع_المكافأة == "نقاط":
            logger.info(f"[COUPON-DB] إضافة {قيمة_المكافأة} نقاط للمستخدم {معرف_المستخدم}")
            cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + ? WHERE معرف_المستخدم = ?', 
                          (قيمة_المكافأة, معرف_المستخدم))
            affected = cursor.rowcount
            logger.info(f"[COUPON-DB] عدد الصفوف المتأثرة (نقاط): {affected}")
        elif نوع_المكافأة == "ريال":
            logger.info(f"[COUPON-DB] إضافة {قيمة_المكافأة} ريال للمستخدم {معرف_المستخدم}")
            cursor.execute('UPDATE الطلاب SET رصيد_الريال = رصيد_الريال + ? WHERE معرف_المستخدم = ?', 
                          (قيمة_المكافأة, معرف_المستخدم))
            affected = cursor.rowcount
            logger.info(f"[COUPON-DB] عدد الصفوف المتأثرة (ريال): {affected}")
        
        # تحديث حالة الكوبون
        logger.info(f"[COUPON-DB] تحديث حالة الكوبون إلى مستخدم")
        cursor.execute('''
            UPDATE الكوبونات
            SET is_used = 1, مستخدم_id = ?, تاريخ_الاستخدام = CURRENT_TIMESTAMP
            WHERE كوبون_id = ?
        ''', (معرف_المستخدم, كوبون_id))
        
        conn.commit()
        logger.info(f"[COUPON-DB] ✅ تم حفظ التغييرات بنجاح")
        conn.close()
        return True, (نوع_المكافأة, قيمة_المكافأة)
    except Exception as e:
        logger.error(f"[COUPON-DB] ❌ خطأ في استخدام الكوبون: {e}", exc_info=True)
        return False, "حدث خطأ في تطبيق الكوبون"

def جلب_الكوبونات():
    """جلب جميع الكوبونات"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT كود_الكوبون, نوع_المكافأة, قيمة_المكافأة, is_used, تاريخ_الإنشاء
            FROM الكوبونات
            ORDER BY تاريخ_الإنشاء DESC
        ''')
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"خطأ في جلب الكوبونات: {e}")
        return []

def جلب_رسائل_الدعم():
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT د.دعم_id, د.معرف_المستخدم, س.الاسم, د.الرسالة, د.تاريخ_الرسالة
            FROM الدعم د
            JOIN الطلاب س ON د.معرف_المستخدم = س.معرف_المستخدم
            WHERE د.is_answered = 0
            ORDER BY د.تاريخ_الرسالة
        ''')
        رسائل = cursor.fetchall()
        conn.close()
        return رسائل
    except Exception as e:
        logger.error(f"خطأ في جلب رسائل الدعم: {e}")
        return []

def الرد_على_دعم(دعم_id, الرد):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('SELECT معرف_المستخدم FROM الدعم WHERE دعم_id = ?', (دعم_id,))
        معرف_المستخدم = cursor.fetchone()[0]
        
        cursor.execute('''
            UPDATE الدعم 
            SET الرد = ?, is_answered = 1, تاريخ_الرد = CURRENT_TIMESTAMP
            WHERE دعم_id = ?
        ''', (الرد, دعم_id))
        
        conn.commit()
        conn.close()
        return True, معرف_المستخدم
    except Exception as e:
        logger.error(f"خطأ في الرد على الدعم: {e}")
        return False, None

# نظام الإعلانات و Premium - مع API التحقق
async def create_ad_verification_token(user_id):
    """إنشاء توكن تحقق عبر API"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            url = f"{VERIFY_API_BASE_URL}/api/create-token"
            logger.info(f"[AD-CREATE] محاولة إنشاء توكن للمستخدم {user_id} على {url}")
            
            async with session.post(
                url,
                json={
                    "user_id": user_id,
                    "secret": VERIFY_SECRET_KEY
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                logger.info(f"[AD-CREATE] استجابة API: status={response.status}")
                
                if response.status == 200:
                    text = await response.text()
                    
                    # التحقق إذا كانت الاستجابة HTML (حماية)
                    if text.strip().startswith('<'):
                        logger.error(f"[AD-CREATE] الموقع يرجع HTML بدلاً من JSON - حماية مفعلة")
                        return None
                    
                    try:
                        data = await response.json()
                        logger.info(f"[AD-CREATE] بيانات API: success={data.get('success')}")
                        if data.get('success'):
                            logger.info(f"[AD-CREATE] ✅ تم إنشاء توكن بنجاح للمستخدم {user_id}")
                            return data
                        else:
                            logger.error(f"[AD-CREATE] API رجع success=false: {data}")
                    except Exception as json_error:
                        logger.error(f"[AD-CREATE] فشل تحليل JSON: {text[:200]} | خطأ: {json_error}")
                else:
                    text = await response.text()
                    logger.error(f"[AD-CREATE] API رجع status {response.status}: {text[:200]}")
                
                return None
    except Exception as e:
        logger.error(f"[AD-CREATE] خطأ في إنشاء توكن التحقق: {e}", exc_info=True)
        return None

async def create_task_verification_token(user_id: int, task_id: int, task_url: str, task_description: str, task_points: int):
    """
    إنشاء توكن تحقق عبر API الخارجي للمهام
    
    Args:
        user_id: معرف المستخدم
        task_id: معرف المهمة
        task_url: رابط المهمة
        task_description: وصف المهمة
        task_points: النقاط المكافأة
    
    Returns:
        dict مع token و verify_url أو None عند الفشل
    """
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{VERIFY_API_BASE_URL}/api/create-task-token"
            payload = {
                "user_id": user_id,
                "task_id": task_id,
                "task_url": task_url,
                "task_description": task_description,
                "task_points": task_points,
                "secret": VERIFY_SECRET_KEY
            }
            
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        logger.info(f"✅ Task token created successfully for user {user_id}, task {task_id}")
                        return data
                
                logger.error(f"API returned status {response.status}")
                return None
                
    except Exception as e:
        logger.error(f"❌ Error creating task verification token: {e}")
        return None

async def check_ad_verification_status(token):
    """التحقق من حالة التوكن عبر API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{VERIFY_API_BASE_URL}/api/check-token",
                json={
                    "token": token,
                    "secret": VERIFY_SECRET_KEY
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                logger.debug(f"[AD-CHECK] فحص التوكن: status={response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    verified = data.get('verified', False)
                    logger.debug(f"[AD-CHECK] النتيجة: verified={verified}")
                    
                    if data.get('success'):
                        return verified
                    else:
                        logger.warning(f"[AD-CHECK] API رجع success=false: {data}")
                else:
                    error_text = await response.text()
                    logger.error(f"[AD-CHECK] خطأ API status={response.status}: {error_text[:100]}")
                
                return False
    except Exception as e:
        logger.error(f"[AD-CHECK] خطأ في التحقق من حالة التوكن: {e}")
        return False

async def monitor_ad_verification(context, user_id, token, chat_id, is_optional=False):
    """
    مراقبة حالة التحقق كل 3 ثواني
    
    Args:
        context: السياق من Telegram
        user_id: معرف المستخدم
        token: توكن التحقق
        chat_id: معرف المحادثة
        is_optional: True إذا كان إعلان اختياري (كسب نقاط)، False إذا كان إجباري (فك الحظر)
    """
    try:
        for attempt in range(60):  # 60 محاولة = دقيقتين (أسرع)
            await asyncio.sleep(2)  # تقليل الانتظار لـ 2 ثانية
            
            logger.debug(f"[AD-MONITOR] محاولة {attempt + 1}/60 للمستخدم {user_id}")
            verified = await check_ad_verification_status(token)
            
            if verified:
                logger.info(f"[AD-MONITOR] ✅ تم التحقق! المستخدم {user_id}")
                # تم التحقق! تحديث البيانات ومنح المكافأة فوراً
                conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
                cursor = conn.cursor()
                
                # قراءة مكافأة الإعلان من الإعدادات المحدثة
                config = load_config()
                ad_reward = config.get('ad_points_reward', 5)
                logger.info(f"[AD-REWARD] إضافة {ad_reward} نقاط للمستخدم {user_id}")
                
                try:
                    if is_optional:
                        # إعلان اختياري - فقط إضافة نقاط
                        cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + ? WHERE معرف_المستخدم = ?', (ad_reward, user_id))
                        affected = cursor.rowcount
                        logger.info(f"[AD-REWARD] صفوف متأثرة (اختياري): {affected}")
                        message = (
                            f"✅ **تم التحقق بنجاح!**\n\n"
                            f"🎁 تم إضافة {ad_reward} نقاط لحسابك\n\n"
                            f"شكراً لدعمك! 🙏"
                        )
                    else:
                        # إعلان إجباري - تصفير العداد + إضافة نقاط
                        cursor.execute('UPDATE الطلاب SET ردود_منذ_الإعلان = 0 WHERE معرف_المستخدم = ?', (user_id,))
                        cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + ? WHERE معرف_المستخدم = ?', (ad_reward, user_id))
                        affected = cursor.rowcount
                        logger.info(f"[AD-REWARD] صفوف متأثرة (إجباري): {affected}")
                        message = (
                            f"✅ **تم التحقق بنجاح!**\n\n"
                            f"🎁 تم إضافة {ad_reward} نقاط لحسابك\n"
                            f"🔓 يمكنك الآن إعادة طرح سؤالك\n\n"
                            f"شكراً لدعمك! 🙏"
                        )
                    
                    conn.commit()
                    logger.info(f"[AD-REWARD] ✅ تم حفظ التغييرات بنجاح")
                    
                except Exception as db_error:
                    logger.error(f"[AD-REWARD] خطأ في قاعدة البيانات: {db_error}")
                    conn.rollback()
                finally:
                    conn.close()
                
                # إشعار المستخدم فوراً
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=message
                    )
                    logger.info(f"[AD-REWARD] تم إرسال إشعار النجاح للمستخدم {user_id}")
                except Exception as e:
                    logger.error(f"خطأ في إرسال إشعار التحقق: {e}")
                
                return True
        
        # انتهى الوقت
        logger.warning(f"[AD-MONITOR] انتهى وقت التحقق للمستخدم {user_id}")
        try:
            timeout_message = (
                "⏱️ انتهى وقت التحقق من الإعلان.\n\n"
                "يمكنك المحاولة مرة أخرى."
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=timeout_message
            )
        except:
            pass
    except Exception as e:
        logger.error(f"خطأ في مراقبة التحقق من الإعلان: {e}")

async def monitor_task_verification(context, user_id, token, task_id, points, chat_id):
    """
    مراقبة حالة التحقق من المهمة كل 3 ثواني
    
    Args:
        context: السياق من Telegram
        user_id: معرف المستخدم
        token: توكن التحقق
        task_id: معرف المهمة
        points: نقاط المكافأة
        chat_id: معرف المحادثة
    """
    try:
        for attempt in range(40):  # 40 محاولة = دقيقتين
            await asyncio.sleep(3)
            
            verified = await check_ad_verification_status(token)
            
            if verified:
                # تم التحقق! إكمال المهمة
                ناجح, نقاط = إكمال_مهمة(user_id, task_id)
                
                if ناجح:
                    message = (
                        f"✅ **تم التحقق بنجاح!**\n\n"
                        f"🎉 **تهانينا!** تم إكمال المهمة\n"
                        f"🎁 **المكافأة:** {نقاط} نقطة\n\n"
                        f"شكراً لك! 🙏"
                    )
                else:
                    message = (
                        "❌ **عذراً!**\n\n"
                        "حدث خطأ في إكمال المهمة أو تم إكمالها مسبقاً.\n"
                        "الرجاء المحاولة مرة أخرى."
                    )
                
                # إشعار المستخدم
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=message
                    )
                except Exception as e:
                    logger.error(f"خطأ في إرسال إشعار التحقق من المهمة: {e}")
                
                return True
        
        # انتهى الوقت
        try:
            timeout_message = (
                "⏱️ انتهى وقت التحقق من المهمة.\n\n"
                "يمكنك المحاولة مرة أخرى."
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=timeout_message
            )
        except:
            pass
    except Exception as e:
        logger.error(f"خطأ في مراقبة التحقق من المهمة: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"خطأ في مراقبة التحقق: {e}")
        return False

async def pre_check_ad_block(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """يتحقق مما إذا كان يجب عرض إعلان ومنع الإجابة عن السؤال التالي."""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('SELECT is_premium, ردود_منذ_الإعلان FROM الطلاب WHERE معرف_المستخدم = ?', (user_id,))
        result = cursor.fetchone()
        
        if result is None:
            conn.close()
            return False

        is_premium, ad_count = result
        
        conn.close()
        
        if is_premium == 0 and ad_count >= AD_RESPONSE_LIMIT:
            # إنشاء توكن تحقق عبر API
            token_data = await create_ad_verification_token(user_id)
            
            if token_data and token_data.get('verify_url'):
                verify_url = token_data['verify_url']
                token = token_data['token']
                
                # قراءة عدد النقاط من الإعدادات
                config = load_config()
                ad_points = config.get('ad_points_reward', 5)
                
                keyboard = [
                    [InlineKeyboardButton("🌐 مشاهدة الإعلان", url=verify_url)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(
                    f"🛑 **نحتاج دعمك (إعلان):**\n\n"
                    f"📺 لقد وصلت للحد المسموح ({AD_RESPONSE_LIMIT} ردود)\n\n"
                    f"⚠️ **الخطوات:**\n"
                    f"1. اضغط على زر 'مشاهدة الإعلان'\n"
                    f"2. شاهد الإعلان كاملاً\n"
                    f"3. اضغط زر التأكيد في الصفحة\n"
                    f"4. عد للبوت (سيتم التحديث تلقائياً)\n\n"
                    f"🎁 ستحصل على {ad_points} نقاط مكافأة!",
                    reply_markup=reply_markup
                )
                
                # بدء مراقبة التحقق في الخلفية
                asyncio.create_task(monitor_ad_verification(context, user_id, token, update.message.chat_id, is_optional=False))
                
                context.user_data['last_question_text'] = update.message.text 
                return True
            else:
                # فشل إنشاء التوكن - نسمح بالرد لكن نحذر
                logger.error(f"فشل إنشاء توكن التحقق للمستخدم {user_id}")
                # لا نمنع الرد، نسمح به
                return False
        
        return False 
        
    except Exception as e:
        logger.error(f"خطأ في فحص الإعلان: {e}")
        return False

# إبقاء المعالجات القديمة للتوافقية
async def handle_ad_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة ضغط زر بدء الإعلان"""
    query = update.callback_query
    await query.answer()  # استجابة فورية
    user_id = query.from_user.id
    
    if query.data == AD_START_CALLBACK_DATA:
        context.user_data['ad_start_time'] = time.time()
        
        keyboard = [
            [InlineKeyboardButton("🌐 افتح الإعلان", url=AD_LINK)],
            [InlineKeyboardButton("✅ المتابعة بعد 5 ثواني", callback_data=AD_CHECK_CALLBACK_DATA)]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"⚠️ **الخطوات المطلوبة:**\n"
                 f"1. **اضغط على الزر أعلاه** وانتظر في الصفحة لمدة 5 ثوانٍ على الأقل.\n"
                 f"2. اضغط على زر **'المتابعة بعد 5 ثواني'**.\n\n"
                 f"🎁 **ستحصل على 5 نقاط مكافأة!**",
            reply_markup=reply_markup
        )

async def handle_ad_check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق من مرور 5 ثوانٍ وتصفير العداد"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()  # استجابة فورية بدون رسالة
    start_time = context.user_data.get('ad_start_time')
    
    if query.data == AD_CHECK_CALLBACK_DATA and start_time:
        elapsed_time = time.time() - start_time
        REQUIRED_TIME = 5
        
        if elapsed_time >= REQUIRED_TIME:
            try:
                conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
                cursor = conn.cursor()
                
                # قراءة مكافأة الإعلان من الإعدادات
                config = load_config()
                ad_reward = config.get('ad_points_reward', 5)
                
                cursor.execute('UPDATE الطلاب SET ردود_منذ_الإعلان = 0 WHERE معرف_المستخدم = ?', (user_id,))
                # إضافة نقاط المكافأة
                cursor.execute('UPDATE الطلاب SET رصيد_النقاط = رصيد_النقاط + ? WHERE معرف_المستخدم = ?', (ad_reward, user_id))
                
                conn.commit()
                conn.close()
                
                context.user_data.pop('ad_start_time', None)
                last_q = context.user_data.pop('last_question_text', "سؤالك الأخير")

                await query.edit_message_text(
                    text=f"✅ **شكراً لدعمك!**\n\n"
                         f"تم تصفير العداد وإضافة {ad_reward} نقطة مكافأة!\n\n"
                         f"يمكنك الآن إعادة طرح سؤالك السابق: `{last_q}`",
                    reply_markup=None 
                )
                
            except Exception as e:
                logger.error(f"خطأ في تصفير عداد الإعلان: {e}")
                await query.edit_message_text(f"❌ حدث خطأ في تصفير العداد. حاول /start.")
        else:
            remaining_time = int(REQUIRED_TIME - elapsed_time) + 1
            await query.answer(f"⏳ يجب الانتظار {remaining_time} ثانية أخرى قبل المتابعة.", show_alert=True)

# دوال إدارة المدير
def جلب_جميع_الطلاب():
    """جلب معلومات جميع الطلاب"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT الاسم, معرف_التحقق_الفريد, الصف, معرف_المستخدم, is_premium, is_gift_premium FROM الطلاب') 
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"خطأ في جلب جميع الطلاب: {e}")
        return []

def إلغاء_اشتراك_بريميم(معرف_فريد):
    """إلغاء تفعيل البريميم بناءً على الرمز الفريد"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE الطلاب 
            SET is_premium = 0, ردود_منذ_الإعلان = 0
            WHERE معرف_التحقق_الفريد = ? AND is_premium = 1
        ''', (معرف_فريد,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
    except Exception as e:
        logger.error(f"خطأ في إلغاء تفعيل البريميم: {e}")
        return False

def تفعيل_بريميم_هدية(معرف_فريد):
    """تفعيل البريميم كهدية"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE الطلاب 
            SET is_premium = 1, is_gift_premium = 1, ردود_منذ_الإعلان = 0
            WHERE معرف_التحقق_الفريد = ?
        ''', (معرف_فريد,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
    except Exception as e:
        logger.error(f"خطأ في تفعيل البريميم هدية: {e}")
        return False

# دوال مساعدة
def جلب_احصائيات_الطالب(معرف_المستخدم):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT الاسم, الصف, عدد_الاسئلة, تاريخ_التسجيل, آخر_نشاط, معرف_التحقق_الفريد, is_premium, is_gift_premium,
                   رصيد_النقاط, رصيد_الريال, is_manager, احالات_ناجحة, رمز_احالة_مستخدم
            FROM الطلاب WHERE معرف_المستخدم = ?
        ''', (معرف_المستخدم,))
        result = cursor.fetchone()
        conn.close()
        return result
    except Exception as e:
        return None

# التحقق من صحة الاسم المحدث
def التحقق_من_الاسم_الكامل(الاسم_الكامل):
    """التحقق من أن الاسم الكامل يحتوي على 3 أسماء وأحرف عربية/إنجليزية فقط"""
    if not الاسم_الكامل or len(الاسم_الكامل.strip()) == 0:
        return False, "❌ الاسم لا يمكن أن يكون فارغاً"
    
    # تقسيم الاسم إلى أجزاء
    أجزاء_الاسم = الاسم_الكامل.strip().split()
    
    # التحقق من أن الاسم مكون من 3 أجزاء
    if len(أجزاء_الاسم) != 3:
        return False, "❌ يجب إدخال الاسم الثلاثي (الاسم الأول + الأب + الجد)\nمثال: محمد عبدالله الفهد"
    
    # التحقق من كل جزء من الاسم
    for جزء in أجزاء_الاسم:
        # التحقق من وجود أرقام أو رموز
        if re.search(r'[0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', جزء):
            return False, f"❌ الجزء '{جزء}' يحتوي على أرقام أو رموز\nيجب أن يحتوي الاسم على أحرف عربية أو إنجليزية فقط"
        
        # التحقق من أن الاسم يحتوي على أحرف صالحة فقط
        if not re.search(r'[a-zA-Zأ-ي]', جزء):
            return False, f"❌ الجزء '{جزء}' غير صالح\nيجب أن يحتوي على أحرف عربية أو إنجليزية"
    
    return True, "✅ الاسم صالح"

# Handlers - التسجيل المحدث
async def handle_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bots_file = f'{BASE_DIR}/البيانات/bots_list.json'
    try:
        with open(bots_file, 'r', encoding='utf-8') as f:
            bots_list = json.load(f)
    except Exception:
        bots_list = []

    if not bots_list or (len(bots_list) == 1 and not bots_list[0]['bot_id']):
        msg = "لا توجد بوتات أخرى مضافة بعد."
    else:
        msg = "🤖 **بوتاتنا الأخرى:**\n\n"
        for bot in bots_list:
            msg += f"🔹 معرف البوت: `{bot['bot_id']}`\n📄 الوصف: {bot['description']}\n\n"
    await update.message.reply_text(msg)
    return MAIN_MENU

async def start(update: Update, context):
    user = update.message.from_user
    معلومات_الطالب = جلب_طالب(user.id) 

    if معلومات_الطالب:
        # تحديث كل بيانات المستخدم من قاعدة البيانات
        context.user_data.update({
            'الاسم': معلومات_الطالب[0],
            'المرحلة_الدراسية': معلومات_الطالب[1],
            'الدولة': معلومات_الطالب[2],
            'معرف_التحقق_الفريد': معلومات_الطالب[3],
            'is_premium': معلومات_الطالب[4],
            'is_gift_premium': معلومات_الطالب[5],
            'رصيد_النقاط': معلومات_الطالب[6],
            'رصيد_الريال': معلومات_الطالب[7],
            'is_manager': معلومات_الطالب[8],
            'احالات_ناجحة': معلومات_الطالب[9],
            'رمز_احالة_مستخدم': معلومات_الطالب[10]
        })
            
        await update.message.reply_text(f"🎓 أهلاً بعودتك {context.user_data['الاسم']}!\n\n")
        await عرض_القائمة_الرئيسية(update, context)
        return MAIN_MENU
    else:
        await update.message.reply_text(
            f"🎓 أهلاً بك {user.first_name}!\n\n"
            f"أنـا بـوت **منهج Ai** 🧠 للإجابات المنهجية الشاملة.\n\n"
            f"**الرجاء إدخال اسمك الثلاثي كاملاً:**\n"
            f"👉 الاسم الأول + اسم الأب + اسم الجد\n\n"
            f"**مثال:** محمد عبدالله الفهد"
        )
        return NAME

async def get_name(update: Update, context):
    الاسم_الكامل = update.message.text.strip()
    
    صالح, رسالة = التحقق_من_الاسم_الكامل(الاسم_الكامل)
    if not صالح:
        await update.message.reply_text(رسالة + "\n\nالرجاء إدخال الاسم الثلاثي مرة أخرى:")
        return NAME
    
    context.user_data['الاسم'] = الاسم_الكامل
    
    # قائمة الأزرار للمراحل الدراسية
    keyboard = []
    for stage in EDUCATION_STAGES:
        keyboard.append([KeyboardButton(stage)])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"👤 تم التسجيل: {الاسم_الكامل}\n\n🏫 الآن اختر **مرحلتك الدراسية**:", reply_markup=reply_markup)
    return STAGE_SELECTION

async def get_stage(update: Update, context):
    stage = update.message.text
    if stage not in EDUCATION_STAGES:
        await update.message.reply_text("❌ مرحلة دراسية غير صالحة. الرجاء اختيار من القائمة:")
        return STAGE_SELECTION
    
    context.user_data['المرحلة_الدراسية'] = stage
    
    # قائمة الأزرار للدول العربية
    keyboard = []
    for i in range(0, len(ARAB_COUNTRIES), 2):
        row = [KeyboardButton(ARAB_COUNTRIES[i])]
        if i + 1 < len(ARAB_COUNTRIES):
            row.append(KeyboardButton(ARAB_COUNTRIES[i+1]))
        keyboard.append(row)

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(f"✅ المرحلة المختارة: {stage}\n\n🌍 الآن اختر **دولتك** ليتم توجيه الإجابات حسب المنهج:", reply_markup=reply_markup)
    return COUNTRY_SELECTION

async def get_country(update: Update, context):
    user_id = update.message.from_user.id
    country = update.message.text
    
    if country not in ARAB_COUNTRIES:
        await update.message.reply_text("❌ دولة غير صالحة. الرجاء اختيار من القائمة:")
        return COUNTRY_SELECTION
        
    context.user_data['الدولة'] = country
    
    await update.message.reply_text(
        f"✅ **أخيراً:**\n\n"
        f"👤 الطالب: {context.user_data['الاسم']}\n"
        f"🏫 المرحلة: {context.user_data['المرحلة_الدراسية']}\n"
        f"🌍 الدولة: {context.user_data['الدولة']}\n\n"
        f"💡 **هل لديك رمز إحالة من صديق؟**\n"
        f"(إذا لم يكن لديك، اضغط /skip)"
    )
    return REFERRAL_CODE

async def get_referral_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    رمز_الاحالة = update.message.text.strip().upper()
    
    # التحقق من رمز الإحالة
    محيل = التحقق_من_رمز_الاحالة(رمز_الاحالة)
    
    if not محيل:
        await update.message.reply_text("❌ رمز الإحالة غير صحيح. الرجاء التحقق والمحاولة مرة أخرى:")
        return REFERRAL_CODE
    
    معرف_المحيل, اسم_المحيل = محيل
    context.user_data['رمز_احالة_مستخدم'] = رمز_الاحالة
    
    # حفظ البيانات في قاعدة البيانات
    معرف_فريد = str(uuid.uuid4()).split('-')[0].upper()
    context.user_data['معرف_التحقق_الفريد'] = معرف_فريد
    context.user_data['is_premium'] = 0 
    context.user_data['is_gift_premium'] = 0
    context.user_data['رصيد_النقاط'] = 50  # مكافأة ترحيب
    context.user_data['رصيد_الريال'] = 0
    context.user_data['is_manager'] = 0
    
    حفظ_طالب(user_id, context.user_data['الاسم'], context.user_data['المرحلة_الدراسية'], 
              context.user_data['الدولة'], معرف_فريد, رمز_الاحالة)
    
    # منح نقاط الإحالة للمحيل
    منح_نقاط_الاحالة(معرف_المحيل, user_id, context.user_data['الاسم'])
    
    # إرسال إشعار للمحيل
    try:
        await context.bot.send_message(
            chat_id=معرف_المحيل,
            text=f"🎉 **إحالة ناجحة!**\n\n"
                 f"تم تسجيل مستخدم جديد برمز إحالتك!\n"
                 f"👤 المستخدم: {context.user_data['الاسم']}\n"
                 f"🎁 **المكافأة:** 100 نقطة\n"
                 f"💎 تم إضافتها لرصيدك تلقائياً"
        )
    except Exception as e:
        logger.error(f"خطأ في إرسال إشعار للمحيل: {e}")
    
    await update.message.reply_text(
        f"✅ **تم التسجيل بنجاح!**\n\n"
        f"👤 الطالب: {context.user_data['الاسم']}\n"
        f"🏫 المرحلة: {context.user_data['المرحلة_الدراسية']}\n"
        f"🌍 الدولة: {context.user_data['الدولة']}\n"
        f"🔑 **الرمز الفريد:** `{معرف_فريد}`\n\n"
        f"🎁 **مكافأة ترحيب:** 50 نقطة!\n"
        f"💎 رصيد النقاط: 50 نقطة\n\n"
        f"✅ **تم تفعيل رمز الإحالة بنجاح!**\n"
        f"👥 المحيل: {اسم_المحيل}\n\n"
        f"**يمكنك الآن:**\n"
        f"• كسب النقاط عبر الإحالات والمهام\n"
        f"• تحويل النقاط لريال سعودي\n"
        f"• شراء البريميم من رصيدك"
    )
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

async def skip_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # حفظ البيانات في قاعدة البيانات بدون رمز إحالة
    معرف_فريد = str(uuid.uuid4()).split('-')[0].upper()
    context.user_data['معرف_التحقق_الفريد'] = معرف_فريد
    context.user_data['is_premium'] = 0 
    context.user_data['is_gift_premium'] = 0
    context.user_data['رصيد_النقاط'] = 50  # مكافأة ترحيب
    context.user_data['رصيد_الريال'] = 0
    context.user_data['is_manager'] = 0
    context.user_data['رمز_احالة_مستخدم'] = None
    
    حفظ_طالب(user_id, context.user_data['الاسم'], context.user_data['المرحلة_الدراسية'], 
              context.user_data['الدولة'], معرف_فريد)
    
    await update.message.reply_text(
        f"✅ **تم التسجيل بنجاح!**\n\n"
        f"👤 الطالب: {context.user_data['الاسم']}\n"
        f"🏫 المرحلة: {context.user_data['المرحلة_الدراسية']}\n"
        f"🌍 الدولة: {context.user_data['الدولة']}\n"
        f"🔑 **الرمز الفريد:** `{معرف_فريد}`\n\n"
        f"🎁 **مكافأة ترحيب:** 50 نقطة!\n"
        f"💎 رصيد النقاط: 50 نقطة\n\n"
        f"**يمكنك الآن:**\n"
        f"• كسب النقاط عبر الإحالات والمهام\n"
        f"• تحويل النقاط لريال سعودي\n"
        f"• شراء البريميم من رصيدك"
    )
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

async def عرض_القائمة_الرئيسية(update, context):
    المرحلة = context.user_data.get('المرحلة_الدراسية')
    الدولة = context.user_data.get('الدولة', 'السعودية')
    is_manager = context.user_data.get('is_manager', 0)
    
    keyboard = []
    
    # السطر 1: المعلومات
    keyboard.append([KeyboardButton("📊 إحصائياتي"), KeyboardButton("🔑 معرف التفعيل")])
    
    # السطر 3: النظام المالي
    keyboard.append([KeyboardButton("💎 نقاطي"), KeyboardButton("📤 تحويل نقاط")])
    keyboard.append([KeyboardButton("🔀 تحويل فلوس ل صديق"), KeyboardButton("🛒 شراء بريميم")])
    keyboard.append([KeyboardButton("🌟 مميزات البريميم")])
    
    # السطر 4: المكافآت
    keyboard.append([KeyboardButton("👥 نظام الإحالة"), KeyboardButton("📋 المهام")])
    keyboard.append([KeyboardButton("🎬 كسب من إعلان"), KeyboardButton("🎟️ استخدام كوبون")])
    keyboard.append([KeyboardButton("📞 تواصل معنا"), KeyboardButton("🔄 تحديث القائمة")])
    keyboard.append([KeyboardButton("🤖 بوتاتنا الأخرى"), KeyboardButton("🏠 القائمة الرئيسية")])
    
    # السطر 6: للمديرين فقط
    if is_manager:
        keyboard.append([KeyboardButton("🛠️ الدخول لوضع المدير")])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # جلب الإعدادات الديناميكية 
    current_config = load_config()
    premium_riyal_price = current_config.get('premium_riyal_price', 10)

    رسالة = f"📚 **بوت منهج Ai - {المرحلة} ({الدولة})**\n\n"
    
    # معلومات الرصيد
    نقاط = context.user_data.get('رصيد_النقاط', 0)
    ريال = context.user_data.get('رصيد_الريال', 0)
    
    رسالة += f"💎 **رصيد النقاط:** {نقاط} نقطة\n"
    رسالة += f"💵 **رصيد الريال:** {ريال} ريال\n\n"
    
    رسالة += f"{'🧠 الذكاء الاصطناعي: جاهز' if AI_جاهز else '⚠️ الوضع المحدود'}"
    
    is_premium = context.user_data.get('is_premium', 0)
    رسالة += f"\n✨ **Premium:** {'✅ مفعل' if is_premium else '❌ غير مفعل'}"
    
    if is_premium == 0:
        رسالة += (f"\n\n💎 **تفعيل Premium (إزالة الإعلانات):**\n"
                   f"💰 السعر: **{premium_riyal_price} ريال**\n"
                   f"💳 ادفع من رصيدك مباشرة!")
        
    await update.message.reply_text(رسالة, reply_markup=reply_markup)

async def handle_photo_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # التحقق من حالة البريميم (الميزة حصرية)
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT is_premium FROM الطلاب WHERE معرف_المستخدم = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        is_premium = result[0] if result else 0
        
        if not is_premium:
            await update.message.reply_text(
                "🔒 **عذراً، هذه الميزة للمشتركين فقط!**\n\n"
                "📸 ميزة **تحليل الصور بالذكاء الاصطناعي** متاحة فقط لمشتركي **Premium**.\n\n"
                "💎 اشترك الآن واستمتع بمزايا حصرية!",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("🌟 مميزات البريميم"), KeyboardButton("🛒 شراء بريميم")],
                     [KeyboardButton("🏠 القائمة الرئيسية")]],
                    resize_keyboard=True
                )
            )
            return MAIN_MENU
            
    except Exception as e:
        logger.error(f"خطأ في التحقق من البريميم للصورة: {e}")
        return MAIN_MENU

    try:
        # تحميل الصورة
        photo_file = await update.message.photo[-1].get_file()
        image_stream = io.BytesIO()
        await photo_file.download_to_memory(image_stream)
        image_stream.seek(0)
        image = Image.open(image_stream)
        
        caption = update.message.caption
        if not caption:
            caption = "اشرح لي هذه الصورة وما فيها من معلومات تعليمية بشكل مفصل."
            
        processing_msg = await update.message.reply_text("📸 **جاري تحليل الصورة...**")
        
        if not AI_جاهز:
             await processing_msg.edit_text("❌ الذكاء الاصطناعي غير متاح حالياً")
             return MAIN_MENU
             
        model_data = get_next_model(is_premium=True)
        if not model_data:
            await processing_msg.edit_text("❌ لا يوجد نماذج AI متاحة")
            return MAIN_MENU
            
        genai.configure(api_key=model_data['token'])
        model = model_data['model']
        
        اسم_الطالب = context.user_data.get('الاسم', 'يا طالب')
        
        # تحسين البرومبت ليكون أكثر دقة ويمنع الهبد
        system_prompt = (
            f"أنت معلم خبير ومساعد تعليمي ذكي. اسم الطالب هو {اسم_الطالب}.\n"
            "مهمتك هي تحليل الصورة المرفقة بدقة عالية جداً.\n"
            "1. اقرأ أي نص موجود داخل الصورة بعناية.\n"
            "2. إذا أرسل الطالب نصاً مع الصورة (Caption)، فإنه يعتبر جزءاً أساسياً من السؤال، فافهمه جيداً.\n"
            "3. قدم شرحاً تعليمياً مفصلاً ودقيقاً بناءً على محتوى الصورة وسؤال الطالب.\n"
            "4. تجنب التأليف أو إعطاء معلومات غير موجودة (لا تهبد). إذا كانت الصورة غير واضحة، اطلب توضيحاً.\n"
            "5. اشرح الخطوات أو المعلومات بأسلوب مبسط ومناسب للمستوى الدراسي."
        )
        
        full_prompt = f"{system_prompt}\n\nسؤال الطالب/الشرح المرفق: {caption}"
        
        # إرسال الصورة والبرومبت للنموذج
        response = model.generate_content([full_prompt, image])
        answer = response.text
        
        await processing_msg.edit_text(f"🎯 **تحليل الصورة:**\n\n{answer}")
            
    except Exception as e:
        logger.error(f"خطأ في معالجة الصورة: {e}")
        await update.message.reply_text("❌ حدث خطأ أثناء تحليل الصورة. حاول مرة أخرى.")
        
    return MAIN_MENU

async def handle_main_menu(update: Update, context):
    user_input = update.message.text
    user_id = update.message.from_user.id

    # استجابة فورية لجميع الأزرار
    await update.message.reply_chat_action("typing")  # إظهار أن البوت يكتب

    # 1. أوامر المدير
    input_lower = user_input.lower().strip()
    if input_lower in ['/admin', '\admin', 'admin']: 
        return await admin_command(update, context) 

    # 2. معالجة الأزرار - استجابة فورية لكل زر
    if user_input == "🌟 مميزات البريميم":
        # استجابة فورية
        await update.message.reply_text(
            "🌟 **لماذا تشترك في Premium؟**\n\n"
            "1️⃣ **بدون إعلانات:** ركز في دروسك بدون أي مقاطعة.\n"
            "2️⃣ **تحليل الصور:** صور أي سؤال وسيقوم البوت بحله وشرحه فوراً.\n"
            "3️⃣ **API خاص وذكي:** نخصص لك API مستقل لضمان أذكى إجابات وأسرع أداء.\n"
            "4️⃣ **دعم VIP:** أنت أولويتنا دائماً.\n\n"
            "⚖️ **مقارنة الاشتراكات:**\n\n"
            "🔹 **الإعلانات**\n"
            "🆓 العادي: ✅ موجودة\n"
            "💎 Premium: 🚫 لا توجد\n\n"
            "🔹 **تحليل الصور**\n"
            "🆓 العادي: ❌ غير متاح\n"
            "💎 Premium: ✅ متاح\n\n"
            "🔹 **قدرات الذكاء الاصطناعي**\n"
            "🆓 العادي: ذكي (مشترك)\n"
            "💎 Premium: 🧠 خارق (API خاص لكل طالب)\n\n"
            "💎 **استثمر في مستقبلك الآن!**"
        )
        
    elif user_input == "🔑 معرف التفعيل":
        # استجابة فورية
        معرف_فريد = context.user_data.get('معرف_التحقق_الفريد', 'غير متوفر')
        is_premium = context.user_data.get('is_premium', 0)
        is_gift = context.user_data.get('is_gift_premium', 0)
        
        رسالة = f"🔑 **الرمز الفريد الخاص بك:**\n\n`{معرف_فريد}`\n\n"
        رسالة += f"✨ **حالة Premium:** {'✅ مفعل' if is_premium else '❌ غير مفعل'}"
        if is_gift:
            رسالة += f" (🎁 هدية)"
        await update.message.reply_text(رسالة)
        
    elif user_input == "📊 إحصائياتي":
        # استجابة فورية
        احصائيات = جلب_احصائيات_الطالب(user_id)
        if احصائيات:
            الاسم, المرحلة_الدراسية, عدد_الاسئلة, تاريخ_التسجيل, آخر_نشاط, معرف_فريد, is_premium, is_gift, نقاط, ريال, is_manager, احالات, رمز_احالة_مستخدم = احصائيات
            await update.message.reply_text(
                f"📊 **إحصائياتك الدراسية**\n\n"
                f"👤 **الطالب:** {الاسم}\n"
                f"🏫 **المرحلة:** {المرحلة_الدراسية}\n"
                f"❓ **عدد الأسئلة:** {عدد_الاسئلة}\n"
                f"💎 **النقاط:** {نقاط} نقطة\n"
                f"💵 **الريال:** {ريال} ريال\n"
                f"👥 **الإحالات الناجحة:** {احالات}\n"
                f"🕒 **آخر نشاط:** {آخر_نشاط[:16] if آخر_نشاط else 'غير متوفر'}"
            )
        else:
            await update.message.reply_text("❌ لا توجد بيانات لإحصائياتك")
            
    elif user_input == "🔄 تحديث القائمة":
        # استجابة فورية
        await update.message.reply_text("🔄 جاري تحديث القائمة...")
        معلومات_الطالب = جلب_طالب(user_id)
        if معلومات_الطالب:
            context.user_data.update({
                'الاسم': معلومات_الطالب[0],
                'المرحلة_الدراسية': معلومات_الطالب[1],
                'الدولة': معلومات_الطالب[2],
                'معرف_التحقق_الفريد': معلومات_الطالب[3],
                'is_premium': معلومات_الطالب[4],
                'is_gift_premium': معلومات_الطالب[5],
                'رصيد_النقاط': معلومات_الطالب[6],
                'رصيد_الريال': معلومات_الطالب[7],
                'is_manager': معلومات_الطالب[8],
                'احالات_ناجحة': معلومات_الطالب[9],
                'رمز_احالة_مستخدم': معلومات_الطالب[10]
            })
        await عرض_القائمة_الرئيسية(update, context)
        
    elif user_input == "💎 نقاطي":
        # استجابة فورية
        نقاط = context.user_data.get('رصيد_النقاط', 0)
        ريال = context.user_data.get('رصيد_الريال', 0)
        await update.message.reply_text(
            f"💎 **رصيدك الحالي:**\n\n"
            f"🎁 **النقاط:** {نقاط} نقطة\n"
            f"💵 **الريال:** {ريال} ريال\n\n"
            f"💡 **طريقة الاستخدام:**\n"
            f"• 100 نقطة = 1 ريال سعودي\n"
            f"• يمكنك تحويل النقاط لريال\n"
            f"• يمكنك تحويل الريال لمستخدمين آخرين\n"
            f"• يمكنك شراء البريميم من رصيدك"
        )
        
    elif user_input == "📤 تحويل نقاط":
        # استجابة فورية
        await update.message.reply_text(
            "📤 **تحويل النقاط لريال سعودي**\n\n"
            "الحد الأدنى للتحويل: 100 نقطة\n"
            "المعادلة: 100 نقطة = 1 ريال\n\n"
            "الرجاء إدخال عدد النقاط التي تريد تحويلها:"
        )
        return CONVERT_POINTS
        
    elif user_input == "🔀 تحويل فلوس ل صديق":
        await update.message.reply_text(
            "🔀 **تحويل فلوس لصديق**\n\n"
            "الرجاء إدخال **الرمز الفريد** للمستلم:"
        )
        return TRANSFER_MONEY
        
    elif user_input == "🛒 شراء بريميم":
        return await شراء_بريميم_Handler(update, context)
        
    elif user_input == "👥 نظام الإحالة":
        رمز_احالة = context.user_data.get('معرف_التحقق_الفريد', 'غير متوفر')
        احالات = context.user_data.get('احالات_ناجحة', 0)
        نقاط_احالات = احالات * 100  # كل إحالة = 100 نقطة
        
        await update.message.reply_text(
            f"👥 **نظام الإحالة**\n\n"
            f"🔑 **رمز الإحالة الخاص بك:**\n`{رمز_احالة}`\n\n"
            f"📊 **إحصائياتك:**\n"
            f"• الإحالات الناجحة: {احالات} مستخدم\n"
            f"• النقاط المكتسبة: {نقاط_احالات} نقطة\n"
            f"• المكافأة لكل إحالة: 100 نقطة\n\n"
            f"💡 **كيفية الاستخدام:**\n"
            f"1. شارك الرمز أعلاه مع أصدقائك\n"
            f"2. عند تسجيلهم، يستخدمون الرمز\n"
            f"3. تحصل على 100 نقطة تلقائياً\n"
            f"4. يمكنك تحويلها لريال أو شراء بريميم\n\n"
            f"🎯 **نصيحة:** شارك الرمز في مجموعاتك!"
        )
        
    elif user_input == "📋 المهام":
        # استجابة فورية
        return await عرض_المهام(update, context)
    
    elif user_input == "🎬 كسب من إعلان":
        # استجابة فورية
        return await كسب_من_إعلان(update, context)
    
    elif user_input == "🎟️ استخدام كوبون":
        # استجابة فورية
        logger.info(f"[COUPON-MENU] المستخدم {update.message.from_user.id} اختار 'استخدام كوبون'")
        await update.message.reply_text(
            "🎟️ **استخدام كوبون**\n\n"
            "الرجاء إدخال كود الكوبون:"
        )
        logger.info(f"[COUPON-MENU] تم إرسال رسالة طلب الكود. الانتقال إلى حالة USE_COUPON")
        return USE_COUPON
        
    elif user_input == "📞 تواصل معنا":
        # استجابة فورية
        config = load_config()
        email = config.get('contact_email', 'غير محدد')
        instagram = config.get('contact_instagram', 'غير محدد')
        show_email = config.get('show_email', True)
        show_instagram = config.get('show_instagram', True)
        
        msg = "📞 **تواصل معنا**\n\n"
        
        if show_email and email != 'غير محدد':
            msg += f"📧 **البريد الإلكتروني:**\n`{email}`\n\n"
            
        if show_instagram and instagram != 'غير محدد':
            msg += f"📸 **انستجرام:**\n`@{instagram}`\n\n"
            
        msg += "💬 **للدعم الفني المباشر:**\nالرجاء كتابة رسالتك للدعم وسيتم الرد عليك في أقرب وقت:"
        
        await update.message.reply_text(msg)
        return SUPPORT_MESSAGE
        
    elif user_input == "🏠 القائمة الرئيسية":
        # تنفيذ start مباشرة - استجابة فورية
        return await start(update, context)
        
    elif user_input == "🛠️ الدخول لوضع المدير":
        if context.user_data.get('is_manager'):
            return await admin_menu(update, context)
        else:
            await update.message.reply_text("❌ ليس لديك صلاحيات المدير")
            
    else:
        await معالجة_سؤال(update, context, user_input)
    
    return MAIN_MENU 

async def معالجة_سؤال(update, context, سؤال):
    user_id = update.message.from_user.id
    اسم_الطالب = context.user_data.get('الاسم', 'يا طالب') 
    مرحلة_الطالب = context.user_data.get('المرحلة_الدراسية', 'الثانوية العامة') 
    دولة_الطالب = context.user_data.get('الدولة', 'السعودية') 
    
    # إظهار استجابة فورية
    await update.message.reply_chat_action("typing")
    
    # التحقق من الإعلانات قبل الإجابة
    is_blocked = await pre_check_ad_block(update, context, user_id)
    if is_blocked:
        return MAIN_MENU
    
    # تحديث عداد الردود للمستخدمين غير المشتركين في البريميم (قبل الرد)
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT is_premium FROM الطلاب WHERE معرف_المستخدم = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0] == 0:  # غير بريميم فقط
            cursor.execute('UPDATE الطلاب SET ردود_منذ_الإعلان = ردود_منذ_الإعلان + 1 WHERE معرف_المستخدم = ?', (user_id,))
            conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"خطأ في تحديث عداد الردود: {e}")
    
    # 1. المعالجة الخاصة لسؤال من برمجك/من سواك 
    question_lower = سؤال.lower().strip()
    if any(phrase in question_lower for phrase in ["من سواك", "من برمجك", "من طورك", "مصممك"]):
         await update.message.reply_text(
             f"👋🏼 أنا بوت منهج Ai، تم تطويري وبرمجتي بواسطة **مصعب فهد**."
         )
         return MAIN_MENU

    # 2. تسجيل السؤال والبدء في المعالجة العادية - مع تسريع
    تسجيل_سؤال(user_id, سؤال, "عام")
    
    # رسالة معالجة أسرع
    processing_msg = await update.message.reply_text("🧠 **جاري المعالجة...**")
    
    try:
        if not AI_جاهز: 
            await processing_msg.edit_text("❌ الذكاء الاصطناعي غير متاح حالياً")
            return MAIN_MENU
        
        # الحصول على البرومبت المخصص
        prompt_template = GLOBAL_CONFIG.get('ai_prompt_template', 
            "أنت معلم خبير في المنهج {country} للمرحلة {stage}. "
            "اسم الطالب هو {name}. "
            "أنت تعمل ضمن بوت تعليمي على تطبيق تيليجرام (Telegram Educational Bot) ومهامك الرئيسية هي مساعدة الطلاب تعليمياً. "
            "مهمتك هي الإجابة على استفسارات الطلاب التعليمية بأعلى درجة من الدقة والموثوقية المنهجية، "
            "مع التركيز على المنهج الدراسي لدولة {country} والمرحلة {stage}. "
            "أجب على السؤال التالي بإجابة تعليمية منهجية دقيقة:\n\n"
            "السؤال: {question}"
        )
        
        # تطبيق المتغيرات على البرومبت
        prompt = prompt_template.format(
            name=اسم_الطالب,
            stage=مرحلة_الطالب,
            country=دولة_الطالب,
            question=سؤال
        )
        
        # التحقق من حالة البريميم لاختيار التوكن المناسب
        is_premium = False
        try:
            conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('SELECT is_premium FROM الطلاب WHERE معرف_المستخدم = ?', (user_id,))
            result = cursor.fetchone()
            if result and result[0] == 1:
                is_premium = True
            conn.close()
        except Exception as e:
            logger.error(f"خطأ في التحقق من البريميم: {e}")

        # استخدام نموذج بالتناوب (مع دعم البريميم)
        model_data = get_next_model(is_premium=is_premium)
        if not model_data:
            await update.message.reply_text("❌ لا يوجد نماذج AI متاحة")
            return MAIN_MENU

        # تهيئة التوكن قبل الاستخدام
        genai.configure(api_key=model_data['token'])
        model = model_data['model']
        
        response = model.generate_content(prompt)
        إجابة = response.text
        
        # تحديث رسالة المعالجة بالإجابة
        await processing_msg.edit_text(f"🎯 **الإجابة التعليمية يا {اسم_الطالب}:**\n\n{إجابة}")
        
        # (تم نقل تحديث العداد لأعلى الدالة)
        try:
            pass
        except Exception as e:
            logger.error(f"خطأ في تحديث عداد الردود: {e}")
        
        await update.message.reply_text("💡 هل لديك سؤال آخر؟ يمكنك كتابته مباشرة، أو اختر **'🔄 تحديث القائمة'** للعودة للقائمة الرئيسية.")
            
    except Exception as e:
        logger.error(f"❌ خطأ فادح في Gemini: {e}")
        await processing_msg.edit_text(f"❌ **حدث خطأ في المعالجة**. جرب سؤالاً آخر.")
    
    return MAIN_MENU 

# Handlers للنقاط والتحويلات
async def convert_points_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    
    # التحقق إذا كان إلغاء
    if user_input in ["🔙 العودة", "الغاء", "cancel", "🏠 القائمة الرئيسية", "🔙 رجوع"]:
        return await start(update, context)

    try:
        نقاط = int(user_input)
        user_id = update.message.from_user.id
        
        ناجح, رسالة = تحويل_نقاط_لريال(user_id, نقاط)
        
        if ناجح:
            # تحديث البيانات
            معلومات_الطالب = جلب_طالب(user_id)
            if معلومات_الطالب:
                context.user_data['رصيد_النقاط'] = معلومات_الطالب[6]
                context.user_data['رصيد_الريال'] = معلومات_الطالب[7]
            
            await update.message.reply_text(f"✅ {رسالة}\n\n💎 رصيد النقاط الجديد: {context.user_data['رصيد_النقاط']}\n💵 رصيد الريال الجديد: {context.user_data['رصيد_الريال']}")
        else:
            await update.message.reply_text(f"❌ {رسالة}")
            
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
        return CONVERT_POINTS
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

async def transfer_money_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    
    # التحقق إذا كان إلغاء
    if user_input in ["🔙 العودة", "الغاء", "cancel", "🏠 القائمة الرئيسية", "🔙 رجوع"]:
        return await start(update, context)

    رمز_المستلم = user_input.upper()
    user_id = update.message.from_user.id
    
    # التحقق من صحة الرمز
    if len(رمز_المستلم) < 4:
        await update.message.reply_text("❌ الرمز غير صحيح. الرجاء إدخال الرمز الفريد الصحيح:")
        return TRANSFER_MONEY
    
    # التحقق من وجود المستلم في قاعدة البيانات
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # البحث عن المستلم
        cursor.execute('SELECT معرف_المستخدم, الاسم FROM الطلاب WHERE معرف_التحقق_الفريد = ?', (رمز_المستلم,))
        مستلم = cursor.fetchone()
        conn.close()
        
        if not مستلم:
            await update.message.reply_text(
                "❌ **الرمز غير موجود!**\n\n"
                "لم يتم العثور على مستخدم بهذا الرمز الفريد.\n"
                "الرجاء التأكد من الرمز والمحاولة مرة أخرى:"
            )
            return TRANSFER_MONEY
        
        مستلم_id, اسم_المستلم = مستلم
        
        # التحقق من أنه لا يحول لنفسه
        if مستلم_id == user_id:
            await update.message.reply_text(
                "❌ **خطأ!**\n\n"
                "لا يمكنك تحويل الريال لنفسك! 😅\n"
                "الرجاء إدخال رمز مستخدم آخر:"
            )
            return TRANSFER_MONEY
        
        # حفظ بيانات المستلم
        context.user_data['رمز_المستلم'] = رمز_المستلم
        context.user_data['مستلم_id'] = مستلم_id
        context.user_data['اسم_المستلم'] = اسم_المستلم
        
        await update.message.reply_text(
            f"✅ **تم العثور على المستلم!**\n\n"
            f"👤 **الاسم:** {اسم_المستلم}\n"
            f"🔑 **الرمز:** `{رمز_المستلم}`\n\n"
            f"💸 الآن أدخل المبلغ (بالريال) الذي تريد تحويله:"
        )
        return TRANSFER_MONEY_AMOUNT
        
    except Exception as e:
        logger.error(f"خطأ في التحقق من المستلم: {e}")
        await update.message.reply_text("❌ حدث خطأ في التحقق. الرجاء المحاولة مرة أخرى:")
        return TRANSFER_MONEY

async def transfer_money_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    
    # التحقق إذا كان إلغاء
    if user_input in ["🔙 العودة", "الغاء", "cancel", "🏠 القائمة الرئيسية", "🔙 رجوع"]:
        return await start(update, context)

    try:
        مبلغ = int(user_input)
        user_id = update.message.from_user.id
        رمز_المستلم = context.user_data.get('رمز_المستلم')
        مستلم_id = context.user_data.get('مستلم_id')
        اسم_المستلم = context.user_data.get('اسم_المستلم')
        
        if مبلغ <= 0:
            await update.message.reply_text(
                "❌ **مبلغ غير صحيح!**\n\n"
                "المبلغ يجب أن يكون أكبر من الصفر.\n"
                "الرجاء إدخال مبلغ صحيح:"
            )
            return TRANSFER_MONEY_AMOUNT
        
        # التحقق من رصيد المرسل
        رصيد_المرسل = context.user_data.get('رصيد_الريال', 0)
        
        if رصيد_المرسل < مبلغ:
            await update.message.reply_text(
                f"❌ **رصيد غير كافي!**\n\n"
                f"💳 رصيدك الحالي: {رصيد_المرسل} ريال\n"
                f"💸 المبلغ المطلوب: {مبلغ} ريال\n\n"
                f"ليس لديك ريال كافي لإتمام هذه العملية.\n"
                f"💡 يمكنك تحويل النقاط إلى ريال أولاً."
            )
            await عرض_القائمة_الرئيسية(update, context)
            context.user_data.pop('رمز_المستلم', None)
            context.user_data.pop('مستلم_id', None)
            context.user_data.pop('اسم_المستلم', None)
            return MAIN_MENU
            
        # تنفيذ التحويل
        ناجح, رسالة = تحويل_ريال(user_id, رمز_المستلم, مبلغ)
        
        if ناجح:
            # تحديث رصيد المرسل
            رصيد_جديد_مرسل = رصيد_المرسل - مبلغ
            context.user_data['رصيد_الريال'] = رصيد_جديد_مرسل
            
            # جلب رصيد المستلم الجديد
            try:
                conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('SELECT رصيد_الريال FROM الطلاب WHERE معرف_المستخدم = ?', (مستلم_id,))
                رصيد_مستلم = cursor.fetchone()[0]
                conn.close()
            except:
                رصيد_مستلم = مبلغ
            
            # إرسال إشعار للمستلم
            try:
                await context.bot.send_message(
                    chat_id=مستلم_id,
                    text=f"🎉 **حوالة واردة!**\n\n"
                         f"👤 **من:** {context.user_data.get('الاسم', 'مستخدم')}\n"
                         f"💸 **المبلغ:** {مبلغ} ريال\n\n"
                         f"💳 **رصيدك الجديد:** {رصيد_مستلم} ريال\n\n"
                         f"✨ تم إضافة المبلغ لحسابك بنجاح!"
                )
            except Exception as e:
                logger.error(f"خطأ في إرسال إشعار للمستلم: {e}")
            
            # إشعار للمرسل
            await update.message.reply_text(
                f"✅ **تم التحويل بنجاح!**\n\n"
                f"💸 **المبلغ المحول:** {مبلغ} ريال\n"
                f"👤 **إلى:** {اسم_المستلم}\n"
                f"🔑 **الرمز:** `{رمز_المستلم}`\n\n"
                f"💳 **رصيدك الجديد:** {رصيد_جديد_مرسل} ريال\n\n"
                f"✨ تم خصم المبلغ من حسابك وإرساله بنجاح!"
            )
        else:
            await update.message.reply_text(f"❌ **فشل التحويل!**\n\n{رسالة}")
            
    except ValueError:
        await update.message.reply_text(
            "❌ **خطأ في المبلغ!**\n\n"
            "الرجاء إدخال رقم صحيح (بدون حروف أو رموز):"
        )
        return TRANSFER_MONEY_AMOUNT
    
    # تنظيف البيانات المؤقتة
    context.user_data.pop('رمز_المستلم', None)
    context.user_data.pop('مستلم_id', None)
    context.user_data.pop('اسم_المستلم', None)
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

async def شراء_بريميم_Handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if context.user_data.get('is_premium'):
        await update.message.reply_text("✅ أنت مشترك بالفعل في البريميم!")
        return MAIN_MENU
        
    ناجح, رسالة = شراء_بريميم(user_id)
    
    if ناجح:
        # تحديث البيانات
        معلومات_الطالب = جلب_طالب(user_id)
        if معلومات_الطالب:
            context.user_data['is_premium'] = 1
            context.user_data['رصيد_الريال'] = معلومات_الطالب[7]
        
        await update.message.reply_text(
            f"🎉 **تم شراء البريميم بنجاح!**\n\n"
            f"✨ **مميزات البريميم:**\n"
            f"• إزالة الإعلانات تماماً\n"
            f"• إجابات أسرع\n"
            f"• دعم مميز\n\n"
            f"💳 **رصيدك الجديد:** {context.user_data['رصيد_الريال']} ريال"
        )
    else:
        await update.message.reply_text(f"❌ {رسالة}")
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

# Handlers للمهام
async def عرض_المهام(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    مهام = جلب_المهام_المتاحة(user_id)
    
    if not مهام:
        await update.message.reply_text(
            "📭 **لا توجد مهام متاحة حالياً.**\n\n"
            "تابع لوحة الإعلانات للحصول على مهام جديدة!"
        )
        await عرض_القائمة_الرئيسية(update, context)
        return MAIN_MENU
    
    رسالة = "📋 **المهام المتاحة:**\n\n"
    
    for i, مهمة in enumerate(مهام, 1):
        مهمة_id, رابط, وصف, نقاط = مهمة
        رسالة += f"**{i}. {وصف}**\n"
        رسالة += f"🔗 الرابط: {رابط}\n"
        رسالة += f"💎 المكافأة: {نقاط} نقطة\n"
        رسالة += f"🆔 رقم المهمة: `{مهمة_id}`\n\n"
        
        # حفظ معلومات المهمة
        context.user_data[f'task_{مهمة_id}'] = مهمة
    
    رسالة += "\n✅ **لإكمال مهمة:**\n"
    رسالة += "أدخل رقم المهمة (مثال: 1 أو 2)"
    
    await update.message.reply_text(رسالة)
    return TASKS_MENU

async def handle_tasks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    user_id = update.message.from_user.id
    
    # استجابة فورية
    await update.message.reply_chat_action("typing")
    
    # التحقق إذا كان إلغاء
    if user_input in ["🔙 العودة", "الغاء", "cancel", "🏠 القائمة الرئيسية", "🔙 رجوع"]:
        return await start(update, context)
    
    # محاولة قراءة رقم المهمة
    try:
        # البحث عن المهمة برقمها المباشر
        مهام = جلب_المهام_المتاحة(user_id)
        
        # إذا أدخل رقم مباشر (1, 2, 3...)
        if user_input.isdigit():
            task_number = int(user_input)
            
            if 1 <= task_number <= len(مهام):
                مهمة = مهام[task_number - 1]
                مهمة_id = مهمة[0]
                رابط = مهمة[1]
                وصف = مهمة[2]
                نقاط = مهمة[3]
                
                # إنشاء توكن عبر API
                token_data = await create_task_verification_token(user_id, مهمة_id, رابط, وصف, نقاط)
                
                if not token_data or not token_data.get('success'):
                    await update.message.reply_text(
                        "❌ **حدث خطأ في إنشاء رابط المهمة**\n\n"
                        "الرجاء المحاولة مرة أخرى لاحقاً."
                    )
                    return TASKS_MENU
                
                verify_url = token_data['verify_url']
                token = token_data['token']
                
                keyboard = [
                    [InlineKeyboardButton("🔗 فتح المهمة", url=verify_url)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"📋 **تفاصيل المهمة:**\n\n"
                    f"📝 {وصف}\n"
                    f"💎 **المكافأة:** {نقاط} نقطة\n\n"
                    f"⚠️ **الخطوات:**\n"
                    f"1. اضغط على زر 'فتح المهمة'\n"
                    f"2. أكمل المهمة المطلوبة\n"
                    f"3. اضغط زر التأكيد في الصفحة\n"
                    f"4. عد للبوت (سيتم التحديث تلقائياً)\n\n"
                    f"🎁 ستحصل على {نقاط} نقطة بعد التحقق!",
                    reply_markup=reply_markup
                )
                
                # بدء مراقبة التحقق في الخلفية
                asyncio.create_task(monitor_task_verification(context, user_id, token, مهمة_id, نقاط, update.message.chat_id))
                
                return TASKS_MENU
            else:
                await update.message.reply_text(f"❌ رقم المهمة غير صحيح. اختر من 1 إلى {len(مهام)}")
                return TASKS_MENU
        else:
            await update.message.reply_text("❌ الرجاء إدخال رقم المهمة فقط (مثال: 1)")
            return TASKS_MENU
    
    except Exception as e:
        logger.error(f"خطأ في معالجة المهمة: {e}")
        await update.message.reply_text("❌ حدث خطأ. الرجاء المحاولة مرة أخرى.")
        await عرض_القائمة_الرئيسية(update, context)
        return MAIN_MENU

# دالة كسب من إعلان (اختياري) - نظام API/Vercel الجديد
async def كسب_من_إعلان(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مشاهدة إعلان اختيارياً للحصول على نقاط"""
    user_id = update.message.from_user.id
    
    # إنشاء توكن عبر API
    token_data = await create_ad_verification_token(user_id)
    
    if not token_data or not token_data.get('success'):
        await update.message.reply_text(
            "❌ **حدث خطأ في إنشاء رابط الإعلان**\n\n"
            "الرجاء المحاولة مرة أخرى لاحقاً."
        )
        await عرض_القائمة_الرئيسية(update, context)
        return MAIN_MENU
    
    verify_url = token_data['verify_url']
    token = token_data['token']
    
    # جلب عدد النقاط من الإعدادات
    ad_points = GLOBAL_CONFIG.get('ad_points_reward', 5)
    
    keyboard = [
        [InlineKeyboardButton("🌐 مشاهدة الإعلان", url=verify_url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🎬 **كسب من مشاهدة إعلان**\n\n"
        f"💎 **المكافأة:** {ad_points} نقاط\n\n"
        f"⚠️ **الخطوات:**\n"
        f"1. اضغط على زر 'مشاهدة الإعلان'\n"
        f"2. شاهد الإعلان كاملاً\n"
        f"3. اضغط زر التأكيد في الصفحة\n"
        f"4. عد للبوت (سيتم التحديث تلقائياً)\n\n"
        f"🎁 ستحصل على {ad_points} نقاط مكافأة بعد التحقق!",
        reply_markup=reply_markup
    )
    
    # بدء مراقبة التحقق في الخلفية
    asyncio.create_task(monitor_ad_verification(context, user_id, token, update.message.chat_id, is_optional=True))
    
    return MAIN_MENU

# معالج زر المشاهدة البسيط
# Handlers للدعم
async def support_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رسالة = update.message.text
    user_id = update.message.from_user.id
    اسم_المستخدم = context.user_data.get('الاسم', 'مستخدم')
    
    if إرسال_رسالة_دعم(user_id, رسالة):
        await update.message.reply_text(
            "✅ **تم إرسال رسالتك للدعم**\n\n"
            "سيتم الرد عليك في أقرب وقت ممكن.\n"
            "شكراً لاتصالك بنا! 📞"
        )
        
        # إشعار المدراء
        try:
            conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('SELECT معرف_المستخدم FROM الطلاب WHERE is_manager = 1')
            managers = cursor.fetchall()
            conn.close()
            
            admin_notification = (
                f"📩 **رسالة دعم جديدة!**\n\n"
                f"👤 **من:** {اسم_المستخدم}\n"
                f"🆔 **المعرف:** `{user_id}`\n"
                f"📝 **الرسالة:**\n{رسالة}\n\n"
                f"⚠️ الرجاء التحقق من '📞 إدارة الدعم' في لوحة المدير."
            )
            
            for manager in managers:
                try:
                    manager_id = manager[0]
                    await context.bot.send_message(
                        chat_id=manager_id,
                        text=admin_notification
                    )
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"خطأ في إشعار المدراء برسالة الدعم: {e}")
            
    else:
        await update.message.reply_text("❌ حدث خطأ في إرسال الرسالة")
    
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

# Handlers للكوبونات
async def use_coupon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    
    # التحقق إذا كان إلغاء
    if user_input in ["🔙 العودة", "الغاء", "cancel", "🏠 القائمة الرئيسية", "🔙 رجوع"]:
        return await start(update, context)

    كود_الكوبون = user_input.upper()
    user_id = update.message.from_user.id
    logger.info(f"[COUPON-HANDLER] ▶️ استلام طلب استخدام كوبون")
    logger.info(f"[COUPON-HANDLER] المستخدم: {user_id}")
    logger.info(f"[COUPON-HANDLER] الكود المدخل: '{كود_الكوبون}'")
    
    logger.info(f"[COUPON-HANDLER] استدعاء دالة استخدام_كوبون...")
    ناجح, نتيجة = استخدام_كوبون(user_id, كود_الكوبون)
    logger.info(f"[COUPON-HANDLER] نتيجة الدالة: ناجح={ناجح}, نتيجة={نتيجة}")
    
    if ناجح:
        نوع, قيمة = نتيجة
        logger.info(f"[COUPON-HANDLER] ✅ نجح! النوع={نوع}, القيمة={قيمة}")
        
        # تحديث البيانات
        logger.info(f"[COUPON-HANDLER] جلب معلومات الطالب المحدثة...")
        معلومات_الطالب = جلب_طالب(user_id)
        if معلومات_الطالب:
            context.user_data['رصيد_النقاط'] = معلومات_الطالب[6]
            context.user_data['رصيد_الريال'] = معلومات_الطالب[7]
            logger.info(f"[COUPON-HANDLER] الرصيد الجديد: نقاط={معلومات_الطالب[6]}, ريال={معلومات_الطالب[7]}")
        
        await update.message.reply_text(
            f"🎉 **تم استخدام الكوبون بنجاح!**\n\n"
            f"🎁 **المكافأة:** {قيمة} {نوع}\n\n"
            f"💎 **رصيد النقاط:** {context.user_data.get('رصيد_النقاط', 0)}\n"
            f"💵 **رصيد الريال:** {context.user_data.get('رصيد_الريال', 0)}"
        )
        logger.info(f"[COUPON-HANDLER] ✅ تم إرسال رسالة النجاح")
    else:
        logger.warning(f"[COUPON-HANDLER] ❌ فشل: {نتيجة}")
        await update.message.reply_text(f"❌ **فشل استخدام الكوبون**\n\n{نتيجة}")
        logger.info(f"[COUPON-HANDLER] تم إرسال رسالة الفشل")
    
    logger.info(f"[COUPON-HANDLER] العودة للقائمة الرئيسية...")
    await عرض_القائمة_الرئيسية(update, context)
    return MAIN_MENU

# دالة اختبار التوكنات
async def اختبار_التوكنات(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اختبار جميع التوكنات المحفوظة مع تفاصيل مفصلة"""
    
    all_tokens = []
    for t in GEMINI_TOKENS_STANDARD:
        all_tokens.append({'token': t, 'type': 'Standard'})
    for t in GEMINI_TOKENS_PREMIUM:
        all_tokens.append({'token': t, 'type': 'Premium'})

    if not all_tokens:
        await update.message.reply_text(
            "❌ **لا توجد توكنات لاختبارها**\n\n"
            "الرجاء إضافة توكن أولاً من '🤖 إدارة توكنات AI'"
        )
        return await admin_menu(update, context)
    
    testing_msg = await update.message.reply_text(
        f"⏳ **جاري اختبار {len(all_tokens)} توكن...**\n\n"
        f"🔍 سيتم إرسال رسالة تجريبية لكل توكن\n"
        f"⏱️ قد يستغرق بضع ثوان..."
    )
    
    نتائج = []
    ناجح = 0
    فاشل = 0
    تفاصيل_الاختبار = []
    
    for i, item in enumerate(all_tokens, 1):
        token = item['token']
        token_type = item['type']
        try:
            # تحديث رسالة الاختبار
            await testing_msg.edit_text(
                f"⏳ **اختبار التوكنات ({i}/{len(all_tokens)})**\n\n"
                f"🔍 جاري اختبار التوكن رقم {i} ({token_type})...\n"
                f"🔑 `{token[:15]}...{token[-10:]}`\n"
                f"🔬 اختبار {len(AVAILABLE_MODELS)} نماذج..."
            )
            
            # اختبار جميع النماذج للتوكن
            import time
            start_time = time.time()
            
            model_data = find_working_model(token)
            response_time = round(time.time() - start_time, 2)
            
            if model_data:
                # اختبار إضافي للتأكد
                response = model_data['model'].generate_content("اكتب 'مرحبا' فقط")
                
                if response and response.text:
                    masked_token = token[:10] + "..." + token[-8:] if len(token) > 18 else token[:12] + "..."
                    نتائج.append(f"{i}. ✅ `{masked_token}` ({token_type}) - {model_data['name']} ({response_time}s)")
                    تفاصيل_الاختبار.append({
                        'index': i,
                        'type': token_type,
                        'status': 'success',
                        'token': masked_token,
                        'model': model_data['name'],
                        'response': response.text[:50],
                        'time': response_time
                    })
                    ناجح += 1
                else:
                    masked_token = token[:10] + "..." + token[-8:]
                    نتائج.append(f"{i}. ❌ `{masked_token}` ({token_type}) - رد فارغ")
                    تفاصيل_الاختبار.append({
                        'index': i,
                        'type': token_type,
                        'status': 'empty',
                        'token': masked_token,
                        'error': 'رد فارغ'
                    })
                    فاشل += 1
            else:
                masked_token = token[:10] + "..." + token[-8:] if len(token) > 18 else token[:12] + "..."
                نتائج.append(f"{i}. ❌ `{masked_token}` ({token_type}) - جميع النماذج فاشلة")
                تفاصيل_الاختبار.append({
                    'index': i,
                    'type': token_type,
                    'status': 'error',
                    'token': masked_token,
                    'error': 'جميع النماذج فاشلة'
                })
                فاشل += 1
                
        except Exception as e:
            masked_token = token[:10] + "..." + token[-8:] if len(token) > 18 else token[:12] + "..."
            error_short = str(e)[:50]
            نتائج.append(f"{i}. ❌ `{masked_token}` ({token_type}) - خطأ: {error_short}")
            تفاصيل_الاختبار.append({
                'index': i,
                'type': token_type,
                'status': 'error',
                'token': masked_token,
                'error': str(e)
            })
            فاشل += 1
    
    # إعداد الرسالة النهائية
    رسالة = f"📋 **نتائج اختبار التوكنات**\n\n"
    
    # الإحصائيات
    if ناجح > 0:
        رسالة += f"✅ **الناجحة:** {ناجح}/{len(all_tokens)}\n"
    if فاشل > 0:
        رسالة += f"❌ **الفاشلة:** {فاشل}/{len(all_tokens)}\n"
    
    رسالة += f"\n"
    
    # النتائج المفصلة
    for detail in تفاصيل_الاختبار:
        if detail['status'] == 'success':
            رسالة += f"✅ التوكن {detail['index']} ({detail['type']}): `{detail['token']}`\n"
            رسالة += f"   🤖 النموذج: {detail.get('model', 'غير محدد')}\n"
            رسالة += f"   📤 رد: {detail['response'][:30]}...\n"
            رسالة += f"   ⏱️ وقت الاستجابة: {detail['time']}s\n\n"
        else:
            رسالة += f"❌ التوكن {detail['index']} ({detail['type']}): `{detail['token']}`\n"
            if detail['status'] == 'empty':
                رسالة += f"   ⚠️ الرد كان فارغاً\n\n"
            else:
                error_msg = detail['error']
                if "quota" in error_msg.lower():
                    رسالة += f"   📊 الحصة مستنفدة\n\n"
                elif "invalid" in error_msg.lower():
                    رسالة += f"   🔑 توكن غير صحيح\n\n"
                else:
                    رسالة += f"   ⚠️ خطأ: {error_msg[:40]}...\n\n"
    
    # التوصيات
    if ناجح == 0:
        رسالة += "🚨 **تحذير:** جميع التوكنات فاشلة!\n"
        رسالة += "🔧 **الحلول:**\n"
        رسالة += "• احصل على توكن جديد من Google AI Studio\n"
        رسالة += "• تحقق من الإنترنت\n"
        رسالة += "• راجع حصة API الخاصة بك\n"
    elif فاشل > 0:
        رسالة += f"💡 **اقتراح:** احذف التوكنات الفاشلة ({فاشل}) من '🗑️ حذف توكن'"
    else:
        رسالة += "🎉 **ممتاز!** جميع التوكنات تعمل بشكل صحيح!\n"
        رسالة += f"🚀 الذكاء الاصطناعي جاهز مع {ناجح} توكن نشط"
    
    await testing_msg.edit_text(رسالة)
    return await admin_menu(update, context)

# دوال إدارة التوكنات
async def إدارة_توكنات(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("➕ إضافة توكن عادي"), KeyboardButton("➕ إضافة توكن بريميم")],
        [KeyboardButton("📋 عرض التوكنات"), KeyboardButton("🗑️ حذف توكن")],
        [KeyboardButton("🔙 العودة لقائمة المدير")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    count_standard = len(GEMINI_TOKENS_STANDARD)
    count_premium = len(GEMINI_TOKENS_PREMIUM)
    
    await update.message.reply_text(
        f"🤖 **إدارة توكنات AI**\n\n"
        f"👤 **التوكنات العادية:** {count_standard}\n"
        f"🌟 **توكنات البريميم:** {count_premium}\n"
        f"⚡ **التوزيع:** تلقائي بالتناوب\n\n"
        f"اختر الإجراء المطلوب:",
        reply_markup=reply_markup
    )
    return ADMIN_TOKENS_MENU

async def handle_tokens_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    if user_input == "➕ إضافة توكن عادي":
        context.user_data['token_type'] = 'standard'
        await update.message.reply_text(
            "➕ **إضافة توكن عادي (Standard)**\n\n"
            "الرجاء إدخال توكن Gemini الجديد:"
        )
        return ADD_TOKEN

    elif user_input == "➕ إضافة توكن بريميم":
        context.user_data['token_type'] = 'premium'
        await update.message.reply_text(
            "➕ **إضافة توكن بريميم (Premium)**\n\n"
            "الرجاء إدخال توكن Gemini الجديد (سيكون مخصصاً للمشتركين):"
        )
        return ADD_TOKEN
    
    elif user_input == "📋 عرض التوكنات":
        if not GEMINI_TOKENS_STANDARD and not GEMINI_TOKENS_PREMIUM:
            await update.message.reply_text("📭 لا توجد توكنات محفوظة.")
            return ADMIN_TOKENS_MENU
        
        رسالة = "📋 **التوكنات المحفوظة:**\n\n"
        
        if GEMINI_TOKENS_STANDARD:
            رسالة += "👤 **التوكنات العادية:**\n"
            for i, token in enumerate(GEMINI_TOKENS_STANDARD, 1):
                masked = token[:10] + "..." + token[-10:] if len(token) > 20 else token
                رسالة += f"{i}. `{masked}`\n"
            رسالة += "\n"
            
        if GEMINI_TOKENS_PREMIUM:
            رسالة += "🌟 **توكنات البريميم:**\n"
            for i, token in enumerate(GEMINI_TOKENS_PREMIUM, 1):
                masked = token[:10] + "..." + token[-10:] if len(token) > 20 else token
                رسالة += f"{i}. `{masked}`\n"
        
        await update.message.reply_text(رسالة)
        return ADMIN_TOKENS_MENU
    
    elif user_input == "🗑️ حذف توكن":
        if not GEMINI_TOKENS_STANDARD and not GEMINI_TOKENS_PREMIUM:
            await update.message.reply_text("📭 لا توجد توكنات لحذفها.")
            return ADMIN_TOKENS_MENU
        
        رسالة = "🗑️ **حذف توكن**\n\nاختر رقم التوكن للحذف:\n\n"
        
        counter = 1
        context.user_data['tokens_map'] = {}
        
        if GEMINI_TOKENS_STANDARD:
            رسالة += "👤 **التوكنات العادية:**\n"
            for token in GEMINI_TOKENS_STANDARD:
                masked = token[:10] + "..." + token[-10:]
                رسالة += f"{counter}. {masked}\n"
                context.user_data['tokens_map'][counter] = ('standard', GEMINI_TOKENS_STANDARD.index(token))
                counter += 1
            رسالة += "\n"
            
        if GEMINI_TOKENS_PREMIUM:
            رسالة += "🌟 **توكنات البريميم:**\n"
            for token in GEMINI_TOKENS_PREMIUM:
                masked = token[:10] + "..." + token[-10:]
                رسالة += f"{counter}. {masked}\n"
                context.user_data['tokens_map'][counter] = ('premium', GEMINI_TOKENS_PREMIUM.index(token))
                counter += 1
        
        await update.message.reply_text(رسالة)
        return REMOVE_TOKEN
    
    elif user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
    
    return ADMIN_TOKENS_MENU

async def add_token_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GEMINI_TOKENS_STANDARD, GEMINI_TOKENS_PREMIUM, models_standard, models_premium, AI_جاهز
    
    new_token = update.message.text.strip()
    token_type = context.user_data.get('token_type', 'standard')
    
    # إظهار رسالة فحص فوري
    checking_msg = await update.message.reply_text(
        f"🔍 **جاري فحص التوكن ({'بريميم' if token_type == 'premium' else 'عادي'})...**\n\n"
        f"🔑 التوكن: `{new_token[:20]}...`\n"
        f"⏳ أرسل رسالة تجريبية للذكاء الاصطناعي..."
    )
    
    # التحقق من صحة التوكن بشكل مفصل
    try:
        # تحديث رسالة الفحص
        await checking_msg.edit_text(
            f"🔍 **جاري فحص التوكن...**\n\n"
            f"🔑 التوكن: `{new_token[:20]}...`\n"
            f"🔬 اختبار {len(AVAILABLE_MODELS)} نماذج...\n"
            f"⏳ هذا قد يستغرق بعض الوقت..."
        )
        
        # اختبار جميع النماذج
        import time
        start_time = time.time()
        model_data = find_working_model(new_token)
        test_time = round(time.time() - start_time, 2)
        
        if not model_data:
            await checking_msg.edit_text(
                f"❌ **فشل فحص التوكن**\n\n"
                f"🔑 التوكن: `{new_token[:20]}...`\n\n"
                f"❌ **جميع النماذج فاشلة**\n\n"
                f"📝 **تم اختبار النماذج:**\n"
                + "\n".join([f"• {model}" for model in AVAILABLE_MODELS]) +
                f"\n\n💡 **اقتراح:**\n"
                f"تحقق من صحة التوكن أو احصل على توكن جديد\n\n"
                f"🔧 للحصول على توكن جديد:\n"
                f"1. اذهب إلى: aistudio.google.com\n"
                f"2. أنشئ API Key جديد\n"
                f"3. انسخه كاملاً وجرب مرة أخرى"
            )
            return await إدارة_توكنات(update, context)
        
        # اختبار إضافي للتأكد
        response = model_data['model'].generate_content("مرحبا، هل تعمل؟")
        
        if response and response.text:
            # التوكن يعمل! إضافته للقائمة المناسبة
            if token_type == 'premium':
                GEMINI_TOKENS_PREMIUM.append(new_token)
                models_premium.append(model_data)
                GLOBAL_CONFIG['gemini_tokens_premium'] = GEMINI_TOKENS_PREMIUM
            else:
                GEMINI_TOKENS_STANDARD.append(new_token)
                models_standard.append(model_data)
                GLOBAL_CONFIG['gemini_tokens_standard'] = GEMINI_TOKENS_STANDARD
            
            # حفظ في الإعدادات
            save_config(GLOBAL_CONFIG)
            
            AI_جاهز = True
            
            # عرض نتيجة ناجحة
            await checking_msg.edit_text(
                f"✅ **تم إضافة التوكن ({'بريميم' if token_type == 'premium' else 'عادي'}) بنجاح!**\n\n"
                f"🔑 التوكن: `{new_token[:20]}...`\n"
                f"🤖 **النموذج المستخدم:** {model_data['name']}\n"
                f"⏱️ **وقت الاختبار:** {test_time}s\n"
                f"💬 **رد الذكاء الاصطناعي:**\n{response.text[:200]}{'...' if len(response.text) > 200 else ''}\n\n"
                f"🎉 **تم إضافة التوكن بنجاح!**\n"
                f"🔢 **عدد التوكنات العادية:** {len(GEMINI_TOKENS_STANDARD)}\n"
                f"🌟 **عدد توكنات البريميم:** {len(GEMINI_TOKENS_PREMIUM)}\n\n"
                f"✨ الذكاء الاصطناعي جاهز للاستخدام!"
            )
        else:
            # رد فارغ
            await checking_msg.edit_text(
                f"⚠️ **التوكن استجاب لكن بدون محتوى**\n\n"
                f"🔑 التوكن: `{new_token[:20]}...`\n"
                f"❌ الرد كان فارغاً\n\n"
                f"🔧 **الأسباب المحتملة:**\n"
                f"• التوكن قد يكون محدود الاستخدام\n"
                f"• مشكلة مؤقتة في الخدمة\n"
                f"• إعدادات النموذج\n\n"
                f"💡 جرب توكن آخر أو حاول مرة أخرى لاحقاً"
            )
            
    except Exception as e:
        # خطأ في التوكن
        error_msg = str(e)
        
        # تحليل نوع الخطأ وإعطاء رسالة مفهومة
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            error_type = "🔑 **توكن غير صحيح**"
            suggestion = "تأكد من نسخ التوكن بالكامل من Google AI Studio"
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            error_type = "📊 **حصة مستنفدة**"
            suggestion = "التوكن استنفد الحصة المجانية أو اليومية"
        elif "permission" in error_msg.lower() or "access" in error_msg.lower():
            error_type = "🚫 **مشكلة في الصلاحيات**"
            suggestion = "التوكن قد يحتاج تفعيل أو صلاحيات إضافية"
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            error_type = "🌐 **مشكلة في الاتصال**"
            suggestion = "تحقق من الإنترنت وحاول مرة أخرى"
        else:
            error_type = "❌ **خطأ غير معروف**"
            suggestion = "حاول توكن آخر أو راجع إعدادات Google AI"
        
        await checking_msg.edit_text(
            f"❌ **فشل فحص التوكن**\n\n"
            f"🔑 التوكن: `{new_token[:20]}...`\n\n"
            f"{error_type}\n\n"
            f"📝 **تفاصيل الخطأ:**\n```{error_msg[:300]}{'...' if len(error_msg) > 300 else ''}```\n\n"
            f"💡 **اقتراح:**\n{suggestion}\n\n"
            f"🔧 للحصول على توكن جديد:\n"
            f"1. اذهب إلى: aistudio.google.com\n"
            f"2. أنشئ API Key جديد\n"
            f"3. انسخه كاملاً وجرب مرة أخرى"
        )
    
    return await إدارة_توكنات(update, context)

async def remove_token_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GEMINI_TOKENS_STANDARD, GEMINI_TOKENS_PREMIUM, models_standard, models_premium, AI_جاهز
    
    try:
        رقم = int(update.message.text)
        tokens_map = context.user_data.get('tokens_map', {})
        
        if رقم not in tokens_map:
            await update.message.reply_text("❌ رقم غير صحيح")
            return REMOVE_TOKEN
        
        token_type, index = tokens_map[رقم]
        
        if token_type == 'standard':
            deleted_token = GEMINI_TOKENS_STANDARD.pop(index)
            models_standard.pop(index)
            GLOBAL_CONFIG['gemini_tokens_standard'] = GEMINI_TOKENS_STANDARD
        else:
            deleted_token = GEMINI_TOKENS_PREMIUM.pop(index)
            models_premium.pop(index)
            GLOBAL_CONFIG['gemini_tokens_premium'] = GEMINI_TOKENS_PREMIUM
        
        # حفظ في الإعدادات
        save_config(GLOBAL_CONFIG)
        
        if not GEMINI_TOKENS_STANDARD and not GEMINI_TOKENS_PREMIUM:
            AI_جاهز = False
        
        await update.message.reply_text(
            f"✅ **تم حذف التوكن ({'بريميم' if token_type == 'premium' else 'عادي'}) بنجاح!**\n\n"
            f"👤 **التوكنات العادية المتبقية:** {len(GEMINI_TOKENS_STANDARD)}\n"
            f"🌟 **توكنات البريميم المتبقية:** {len(GEMINI_TOKENS_PREMIUM)}"
        )
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
        return REMOVE_TOKEN
    
    return await إدارة_توكنات(update, context)

# دوال النسخ الاحتياطي
async def قائمة_النسخ_الاحتياطي(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📥 تصدير قاعدة البيانات"), KeyboardButton("📤 استيراد قاعدة البيانات")],
        [KeyboardButton("⏰ جدولة إرسال يومي"), KeyboardButton("🔙 العودة لقائمة المدير")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    backup_enabled = GLOBAL_CONFIG.get('backup_enabled', False)
    backup_time = GLOBAL_CONFIG.get('backup_time', '00:00')
    
    await update.message.reply_text(
        f"💾 **النسخ الاحتياطي**\n\n"
        f"📊 **الإرسال اليومي:** {'✅ مفعل' if backup_enabled else '❌ معطل'}\n"
        f"⏰ **الوقت المحدد:** {backup_time}\n\n"
        f"اختر الإجراء المطلوب:",
        reply_markup=reply_markup
    )
    return ADMIN_BACKUP_MENU

async def handle_backup_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    if user_input == "📥 تصدير قاعدة البيانات":
        return await تصدير_قاعدة_البيانات(update, context)
    
    elif user_input == "📤 استيراد قاعدة البيانات":
        # إنشاء كيبورد مخصص لهذه الحالة
        keyboard = [[KeyboardButton("🔙 العودة لقائمة النسخ الاحتياطي")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "📤 **استيراد قاعدة البيانات**\n\n"
            "الرجاء إرسال ملف قاعدة البيانات (.db)",
            reply_markup=reply_markup
        )
        return IMPORT_DB
    
    elif user_input == "⏰ جدولة إرسال يومي":
        await update.message.reply_text(
            "⏰ **جدولة الإرسال اليومي**\n\n"
            "الرجاء إدخال الوقت بالصيغة (HH:MM)\n"
            "مثال: 09:00 أو 18:30\n\n"
            "أو اكتب 'إيقاف' لتعطيل الإرسال"
        )
        return SET_BACKUP_TIME
    
    elif user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
    
    return ADMIN_BACKUP_MENU

async def تصدير_قاعدة_البيانات(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        db_path = f'{BASE_DIR}/البيانات/الطلاب.db'
        
        # إرسال الملف
        with open(db_path, 'rb') as db_file:
            await update.message.reply_document(
                document=db_file,
                filename=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                caption="✅ **نسخة احتياطية من قاعدة البيانات**\n\n"
                        f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
        await update.message.reply_text("✅ تم تصدير قاعدة البيانات بنجاح!")
    except Exception as e:
        logger.error(f"خطأ في تصدير قاعدة البيانات: {e}")
        await update.message.reply_text(f"❌ حدث خطأ: {e}")
    
    return await قائمة_النسخ_الاحتياطي(update, context)

async def استيراد_قاعدة_البيانات_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج استيراد قاعدة البيانات من ملف"""
    try:
        # التحقق من وجود ملف
        if not update.message or not update.message.document:
            await update.message.reply_text(
                "❌ الرجاء إرسال ملف قاعدة بيانات (.db)\n\n"
                "أو اضغط 🔙 العودة لقائمة المدير"
            )
            return IMPORT_DB
        
        # التحقق من امتداد الملف
        file_name = update.message.document.file_name
        if not file_name.endswith('.db'):
            await update.message.reply_text(
                "❌ الملف يجب أن يكون بصيغة .db\n\n"
                "الرجاء إرسال ملف قاعدة بيانات صحيح"
            )
            return IMPORT_DB
        
        file = await update.message.document.get_file()
        db_path = f'{BASE_DIR}/البيانات/الطلاب.db'
        backup_path = f'{BASE_DIR}/البيانات/backup_before_import_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        
        # نسخ احتياطي للقاعدة الحالية
        import shutil
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_path)
        
        # تنزيل الملف الجديد
        await file.download_to_drive(db_path)
        
        await update.message.reply_text(
            "✅ **تم استيراد قاعدة البيانات بنجاح!**\n\n"
            f"📥 الملف المستورد: {file_name}\n"
            f"💾 نسخة احتياطية: {os.path.basename(backup_path) if os.path.exists(backup_path) else 'لا يوجد'}"
        )
    except Exception as e:
        logger.error(f"خطأ في استيراد قاعدة البيانات: {e}")
        await update.message.reply_text(f"❌ حدث خطأ في الاستيراد: {str(e)}")
    
    return await قائمة_النسخ_الاحتياطي(update, context)

async def cancel_import_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء استيراد قاعدة البيانات والعودة للقائمة"""
    user_text = update.message.text
    
    # إذا ضغط على زر العودة للنسخ الاحتياطي
    if user_text == "🔙 العودة لقائمة النسخ الاحتياطي":
        return await قائمة_النسخ_الاحتياطي(update, context)
    
    # إذا ضغط على زر العودة لقائمة المدير
    if user_text == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
    
    # إذا كتب /start
    if user_text == "/start":
        return await start(update, context)
    
    # لو كتب أي شي ثاني، نطلب منه يرسل ملف
    await update.message.reply_text(
        "❌ الرجاء إرسال ملف قاعدة بيانات (.db)\n\n"
        "أو اضغط 🔙 للرجوع"
    )
    return IMPORT_DB

async def set_backup_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    
    if user_input == "إيقاف":
        GLOBAL_CONFIG['backup_enabled'] = False
        save_config(GLOBAL_CONFIG)
        await update.message.reply_text("✅ تم إيقاف الإرسال اليومي")
    else:
        # التحقق من صيغة الوقت
        import re
        if re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', user_input):
            GLOBAL_CONFIG['backup_enabled'] = True
            GLOBAL_CONFIG['backup_time'] = user_input
            GLOBAL_CONFIG['backup_chat_id'] = update.message.from_user.id
            save_config(GLOBAL_CONFIG)
            
            await update.message.reply_text(
                f"✅ **تم تفعيل الإرسال اليومي!**\n\n"
                f"⏰ **الوقت:** {user_input}\n"
                f"📬 **سيتم الإرسال لك يومياً**"
            )
        else:
            await update.message.reply_text("❌ صيغة الوقت غير صحيحة. استخدم (HH:MM)")
            return SET_BACKUP_TIME
    
    return await قائمة_النسخ_الاحتياطي(update, context)

# دوال إدارة الكوبونات للمدير
async def إدارة_الكوبونات(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة إدارة الكوبونات"""
    keyboard = [
        [KeyboardButton("➕ إنشاء كوبون جديد")],
        [KeyboardButton("📋 عرض جميع الكوبونات")],
        [KeyboardButton("🔙 العودة لقائمة المدير")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # إحصائيات سريعة
    كوبونات = جلب_الكوبونات()
    total = len(كوبونات)
    used = len([c for c in كوبونات if c[3] == 1])
    available = total - used
    
    await update.message.reply_text(
        f"🎟️ **إدارة الكوبونات**\n\n"
        f"📊 **الإحصائيات:**\n"
        f"• الإجمالي: {total}\n"
        f"• المستخدمة: {used}\n"
        f"• المتاحة: {available}\n\n"
        f"اختر الإجراء المطلوب:",
        reply_markup=reply_markup
    )
    return COUPON_MENU

async def handle_coupon_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج قائمة الكوبونات"""
    user_input = update.message.text
    
    if user_input == "➕ إنشاء كوبون جديد":
        # إظهار خيارات نوع المكافأة
        keyboard = [
            [KeyboardButton("💎 نقاط"), KeyboardButton("💵 ريال")],
            [KeyboardButton("🔙 إلغاء")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "🎟️ **إنشاء كوبون جديد**\n\n"
            "اختر نوع المكافأة:",
            reply_markup=reply_markup
        )
        return GENERATE_COUPON
        
    elif user_input == "📋 عرض جميع الكوبونات":
        كوبونات = جلب_الكوبونات()
        
        if not كوبونات:
            await update.message.reply_text("📭 لا توجد كوبونات محفوظة حالياً.")
            return COUPON_MENU
        
        # عرض الكوبونات (أول 15 فقط لتجنب الرسائل الطويلة)
        message = "📋 **الكوبونات المحفوظة:**\n\n"
        for i, (كود, نوع, قيمة, مستخدم, تاريخ) in enumerate(كوبونات[:15], 1):
            status = "✅ مستخدم" if مستخدم else "⏳ متاح"
            message += f"{i}. `{كود}`\n"
            message += f"   • {نوع}: {قيمة}\n"
            message += f"   • الحالة: {status}\n\n"
        
        if len(كوبونات) > 15:
            message += f"\n... و {len(كوبونات) - 15} كوبون آخر"
        
        await update.message.reply_text(message)
        return COUPON_MENU
        
    elif user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
    
    return COUPON_MENU

async def generate_coupon_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار نوع الكوبون (نقاط أو ريال)"""
    user_input = update.message.text
    logger.info(f"[COUPON] نوع المكافأة المختار: {user_input}")
    
    if user_input == "💎 نقاط":
        context.user_data['coupon_type'] = "نقاط"
        await update.message.reply_text(
            "💎 **كوبون نقاط**\n\n"
            "كم عدد النقاط؟\n"
            "(أدخل رقماً، مثال: 100)"
        )
        return GENERATE_COUPON_VALUE
        
    elif user_input == "💵 ريال":
        context.user_data['coupon_type'] = "ريال"
        await update.message.reply_text(
            "💵 **كوبون ريال**\n\n"
            "كم المبلغ بالريال؟\n"
            "(أدخل رقماً، مثال: 50)"
        )
        return GENERATE_COUPON_VALUE
        
    elif user_input == "🔙 إلغاء":
        context.user_data.pop('coupon_type', None)
        return await إدارة_الكوبونات(update, context)
    
    # إدخال غير صحيح
    await update.message.reply_text("❌ الرجاء اختيار أحد الخيارات من الأزرار")
    return GENERATE_COUPON

async def generate_coupon_value_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدخال قيمة الكوبون"""
    try:
        # التحقق من وجود النوع
        نوع = context.user_data.get('coupon_type')
        if not نوع:
            logger.error("[COUPON] النوع غير موجود في context")
            await update.message.reply_text("❌ خطأ: يجب اختيار نوع المكافأة أولاً")
            return await إدارة_الكوبونات(update, context)
        
        # محاولة تحويل المدخل لرقم
        قيمة = int(update.message.text.strip())
        logger.info(f"[COUPON] قيمة={قيمة}, نوع={نوع}")
        
        # التحقق من صحة القيمة
        if قيمة <= 0:
            await update.message.reply_text("❌ القيمة يجب أن تكون أكبر من صفر!\n\nأدخل قيمة صحيحة:")
            return GENERATE_COUPON_VALUE
        
        # إنشاء الكوبون
        logger.info(f"[COUPON] استدعاء توليد_كوبون...")
        success, result = توليد_كوبون(نوع, قيمة)
        
        if success:
            # نجح الإنشاء
            coupon_code = result
            await update.message.reply_text(
                f"✅ **تم إنشاء الكوبون بنجاح!**\n\n"
                f"🎟️ الكود: `{coupon_code}`\n"
                f"🎁 المكافأة: {قيمة} {نوع}\n\n"
                f"يمكن للمستخدمين استخدامه الآن من القائمة الرئيسية ✨"
            )
            logger.info(f"[COUPON] ✅ تم إنشاء الكوبون: {coupon_code}")
        else:
            # فشل الإنشاء
            error_msg = result
            await update.message.reply_text(f"❌ فشل إنشاء الكوبون:\n\n{error_msg}")
            logger.error(f"[COUPON] ❌ فشل: {error_msg}")
        
        # تنظيف البيانات المؤقتة
        context.user_data.pop('coupon_type', None)
        
    except ValueError:
        # المدخل ليس رقماً
        await update.message.reply_text(
            "❌ يجب إدخال رقم صحيح!\n\n"
            "مثال: 100\n\n"
            "حاول مرة أخرى:"
        )
        return GENERATE_COUPON_VALUE
        
    except Exception as e:
        logger.error(f"[COUPON] خطأ غير متوقع: {e}")
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
        context.user_data.pop('coupon_type', None)
    
    # العودة لقائمة الكوبونات
    return await إدارة_الكوبونات(update, context)

# دوال لوحة المدير المحدثة
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 **لوحة المدير:**\nالرجاء إدخال كلمة المرور:")
    return ADMIN_PASSWORD_ENTRY

async def get_admin_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text
    if password == ADMIN_PASSWORD:
        context.user_data['is_admin'] = True
        await update.message.reply_text("✅ **تم تسجيل الدخول كمدير!**")
        return await admin_menu(update, context)
    else:
        await update.message.reply_text("❌ كلمة مرور خاطئة. الرجاء البدء بـ admin مرة أخرى.")
        return MAIN_MENU

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المدير المحدثة"""
    keyboard = [
        [KeyboardButton("👥 عرض كل المستخدمين"), KeyboardButton("✨ عرض مشتركي بريميم")],
        [KeyboardButton("🚫 عرض غير المشتركين"), KeyboardButton("💎 إحصائيات النقاط")],
        [KeyboardButton("📋 إدارة المهام"), KeyboardButton("🎟️ إدارة الكوبونات")],
        [KeyboardButton("🔑 تفعيل بريميم لرمز"), KeyboardButton("🚫 إلغاء بريميم لرمز")],
        [KeyboardButton("🎁 تفعيل بريميم هدية"), KeyboardButton("🛠️ تعيين مدير جديد")],
        [KeyboardButton("➕ إضافة مستخدم يدوياً"), KeyboardButton("💵 تغيير سعر البوت")],
        [KeyboardButton("📣 مسابقات (إرسال إشعار للكل)"), KeyboardButton("📞 إدارة الدعم")],
        [KeyboardButton("💰 الرصيد المفتوح"), KeyboardButton("🤖 إدارة توكنات AI")],
        [KeyboardButton("✅ اختبار التوكنات"), KeyboardButton("💾 النسخ الاحتياطي")],
        [KeyboardButton("🎬 تغيير نقاط الإعلان"), KeyboardButton("📞 إعدادات التواصل")],
        [KeyboardButton("🤖 بوتاتنا الأخرى"), KeyboardButton("🔙 العودة للقائمة الرئيسية")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # قراءة الإعدادات الحالية
    config = load_config()
    ad_reward = config.get('ad_points_reward', 5)
    
    count_standard = len(GEMINI_TOKENS_STANDARD)
    count_premium = len(GEMINI_TOKENS_PREMIUM)
    token_count = count_standard + count_premium
    
    await update.message.reply_text(
        f"🛠️ **قائمة المدير - منهج Ai**\n\n"
        f"🧠 **حالة الذكاء الاصطناعي:** {'✅ جاهز' if AI_جاهز else '❌ غير جاهز'}\n"
        f"🔑 **عدد التوكنات:** {token_count} (عادي: {count_standard}, بريميم: {count_premium})\n"
        f"🎬 **نقاط مشاهدة الإعلان:** {ad_reward} نقطة\n\n"
        f"اختر الإجراء المطلوب:", 
        reply_markup=reply_markup
    )
    return ADMIN_MENU

async def handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة اختيارات قائمة المدير"""
    user_input = update.message.text
    
    # إظهار استجابة فورية
    await update.message.reply_chat_action("typing")
    
    # شاشة بوتاتنا الأخرى للمدير
    if context.user_data.get('bot_menu_mode'):
        bots_list = context.user_data.get('bots_list', [])
        
        # زر رجوع
        if user_input == "🔙 رجوع":
            context.user_data['bot_menu_mode'] = False
            context.user_data['add_bot_mode'] = False
            context.user_data.pop('pending_bot_id', None)
            return await admin_menu(update, context)
            
        # إضافة بوت جديد
        if user_input == "➕ إضافة بوت جديد":
            context.user_data['add_bot_mode'] = True
            context.user_data['bot_menu_mode'] = False
            
            # إضافة زر رجوع في وضع الإضافة
            keyboard = [[KeyboardButton("🔙 رجوع")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text("أدخل معرف البوت الجديد:", reply_markup=reply_markup)
            return ADMIN_MENU
            
        # اختيار بوت من القائمة
        for idx, bot in enumerate(bots_list):
            if user_input == bot['bot_id']:
                context.user_data['selected_bot_idx'] = idx
                keyboard = [
                    [KeyboardButton("✏️ تعديل البوت"), KeyboardButton("🗑️ حذف البوت")],
                    [KeyboardButton("🔙 رجوع")]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                await update.message.reply_text(
                    f"🔹 معرف البوت: `{bot['bot_id']}`\n📄 الوصف: {bot['description']}",
                    reply_markup=reply_markup
                )
                return ADMIN_MENU

    # استقبال إضافة بوت جديد إذا كان add_bot_mode مفعّل
    if context.user_data.get('add_bot_mode') and user_input != "🤖 بوتاتنا الأخرى":
        
        # زر رجوع أثناء الإضافة
        if user_input == "🔙 رجوع":
            context.user_data['add_bot_mode'] = False
            context.user_data.pop('pending_bot_id', None)
            
            # العودة لقائمة البوتات
            bots_file = f'{BASE_DIR}/البيانات/bots_list.json'
            try:
                with open(bots_file, 'r', encoding='utf-8') as f:
                    bots_list = json.load(f)
            except Exception:
                bots_list = []
                
            keyboard = []
            for idx, bot in enumerate(bots_list):
                if bot['bot_id']:
                    keyboard.append([KeyboardButton(f"{bot['bot_id']}")])
            keyboard.append([KeyboardButton("➕ إضافة بوت جديد")])
            keyboard.append([KeyboardButton("🔙 رجوع")])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                "🤖 قائمة البوتات:",
                reply_markup=reply_markup
            )
            context.user_data['bots_list'] = bots_list
            context.user_data['bot_menu_mode'] = True
            return ADMIN_MENU
            
        bots_file = f'{BASE_DIR}/البيانات/bots_list.json'
        try:
            with open(bots_file, 'r', encoding='utf-8') as f:
                bots_list = json.load(f)
        except Exception:
            bots_list = []

        # خطوة 1: إدخال المعرف
        if not context.user_data.get('pending_bot_id') and not user_input.startswith(('حذف:', 'تعديل:')):
            context.user_data['pending_bot_id'] = user_input.strip()
            
            # إضافة زر رجوع
            keyboard = [[KeyboardButton("🔙 رجوع")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text("✅ تم حفظ المعرف!\n\nالآن أدخل وصف البوت:", reply_markup=reply_markup)
            return ADMIN_MENU

        # خطوة 2: إدخال الوصف
        if context.user_data.get('pending_bot_id') and not user_input.startswith(('حذف:', 'تعديل:')):
            bot_id = context.user_data.pop('pending_bot_id')
            description = user_input.strip()
            bots_list.append({"bot_id": bot_id, "description": description})
            with open(bots_file, 'w', encoding='utf-8') as f:
                json.dump(bots_list, f, ensure_ascii=False, indent=2)
            
            # إعادة عرض قائمة البوتات
            keyboard = []
            for idx, bot in enumerate(bots_list):
                if bot['bot_id']:
                    keyboard.append([KeyboardButton(f"{bot['bot_id']}")])
            keyboard.append([KeyboardButton("➕ إضافة بوت جديد")])
            keyboard.append([KeyboardButton("🔙 رجوع")])
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                f"✅ تم إضافة البوت بنجاح!\n\nمعرف البوت: `{bot_id}`\nالوصف: {description}",
                reply_markup=reply_markup
            )
            context.user_data['add_bot_mode'] = False
            context.user_data['bot_menu_mode'] = True # العودة لقائمة البوتات
            return ADMIN_MENU

        # حذف بوت
        if user_input.startswith('حذف:'):
            try:
                idx = int(user_input.split(':')[1]) - 1
                if 0 <= idx < len(bots_list):
                    removed = bots_list.pop(idx)
                    with open(bots_file, 'w', encoding='utf-8') as f:
                        json.dump(bots_list, f, ensure_ascii=False, indent=2)
                    await update.message.reply_text(f"🗑️ تم حذف البوت رقم {idx+1}: `{removed['bot_id']}`")
                else:
                    await update.message.reply_text("❌ رقم غير صحيح.")
            except Exception:
                await update.message.reply_text("❌ صيغة خاطئة للحذف.")
            context.user_data['add_bot_mode'] = False
            return ADMIN_MENU

        # تعديل بوت
        if user_input.startswith('تعديل:'):
            try:
                parts = user_input.split(':', 3)
                idx = int(parts[1]) - 1
                new_id = parts[2].strip()
                new_desc = parts[3].strip()
                if 0 <= idx < len(bots_list):
                    bots_list[idx]['bot_id'] = new_id
                    bots_list[idx]['description'] = new_desc
                    with open(bots_file, 'w', encoding='utf-8') as f:
                        json.dump(bots_list, f, ensure_ascii=False, indent=2)
                    await update.message.reply_text(f"✏️ تم تعديل البوت رقم {idx+1} بنجاح!")
                else:
                    await update.message.reply_text("❌ رقم غير صحيح.")
            except Exception:
                await update.message.reply_text("❌ صيغة خاطئة للتعديل.")
            context.user_data['add_bot_mode'] = False
            return ADMIN_MENU
            
        # زر رجوع عام في حالة الخطأ
        if user_input == "🔙 رجوع":
             context.user_data['add_bot_mode'] = False
             context.user_data['bot_menu_mode'] = False
             return await admin_menu(update, context)
        
        return ADMIN_MENU

    # القائمة الرئيسية للمدير
    if user_input == "🤖 بوتاتنا الأخرى":
        bots_file = f'{BASE_DIR}/البيانات/bots_list.json'
        try:
            with open(bots_file, 'r', encoding='utf-8') as f:
                bots_list = json.load(f)
        except Exception:
            bots_list = []

        keyboard = []
        for idx, bot in enumerate(bots_list):
            if bot['bot_id']:
                keyboard.append([KeyboardButton(f"{bot['bot_id']}")])
        keyboard.append([KeyboardButton("➕ إضافة بوت جديد")])
        keyboard.append([KeyboardButton("🔙 رجوع")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "🤖 اختر أحد البوتات لعرض خيارات التعديل أو الحذف، أو اضغط إضافة بوت جديد:",
            reply_markup=reply_markup
        )
        context.user_data['bots_list'] = bots_list
        context.user_data['bot_menu_mode'] = True
        return ADMIN_MENU
    
    if user_input == "👥 عرض كل المستخدمين":
        return await display_all_users_info(update, context)
        
    elif user_input == "✨ عرض مشتركي بريميم":
        return await display_premium_users_info(update, context)
        
    elif user_input == "🚫 عرض غير المشتركين":
        return await display_non_premium_users_info(update, context)
        
    elif user_input == "💎 إحصائيات النقاط":
        return await عرض_إحصائيات_النقاط(update, context)
    
    elif user_input == "📋 إدارة المهام":
        return await إدارة_المهام(update, context)
    
    elif user_input == "🛒 طلبات البريميم":
        return await طلبات_البريميم(update, context)
    
    elif user_input == "🔑 تفعيل بريميم لرمز":
        await update.message.reply_text("الرجاء إدخال **الرمز الفريد** للطالب المطلوب تفعيله:")
        return PREMIUM_ID_ENTRY
        
    elif user_input == "🚫 إلغاء بريميم لرمز":
        await update.message.reply_text("الرجاء إدخال **الرمز الفريد** للطالب المطلوب **إلغاء** تفعيله:")
        return PREMIUM_DEACTIVATE_ID_ENTRY
        
    elif user_input == "🎁 تفعيل بريميم هدية":
        await update.message.reply_text("🎁 **تفعيل بريميم هدية**\n\nالرجاء إدخال **الرمز الفريد** للطالب المطلوب منحه الهدية:")
        return GIFT_PREMIUM_ENTRY
        
    elif user_input == "🛠️ تعيين مدير جديد":
        await update.message.reply_text("🛠️ **تعيين مدير جديد**\n\nالرجاء إدخال الرمز الفريد للمستخدم:")
        return ADD_MANAGER
    
    elif user_input == "📣 مسابقات (إرسال إشعار للكل)":
        await update.message.reply_text("📣 **وضع الإشعار الجماعي**\n\nالرجاء كتابة **الرسالة الكاملة** التي تريد إرسالها لجميع المستخدمين:")
        return BROADCAST_MESSAGE_ENTRY
        
    elif user_input == "💵 تغيير سعر البوت": 
        current_riyal_price = GLOBAL_CONFIG.get('premium_riyal_price', 10)
        await update.message.reply_text(
            f"💵 **تغيير سعر البوت**\n\n"
            f"💰 **السعر الحالي:** {current_riyal_price} ريال\n\n"
            f"📝 **أدخل السعر الجديد بالريال:**\n"
            f"مثال: 10"
        )
        return CHANGE_PRICE_ENTRY
    
    elif user_input == "🎬 تغيير نقاط الإعلان":
        current_ad_points = GLOBAL_CONFIG.get('ad_points_reward', 5)
        await update.message.reply_text(
            f"🎬 **تغيير نقاط مشاهدة الإعلان**\n\n"
            f"💎 **النقاط الحالية:** {current_ad_points} نقطة\n\n"
            f"📝 الرجاء إدخال عدد النقاط الجديد لمكافأة مشاهدة الإعلان:\n"
            f"مثال: 5"
        )
        return CHANGE_AD_REWARD

    elif user_input == "📞 إدارة الدعم":
        return await إدارة_الدعم(update, context)
    
    elif user_input == "💰 الرصيد المفتوح":
        return await الرصيد_المفتوح(update, context)
    
    elif user_input == "🤖 إدارة توكنات AI":
        return await إدارة_توكنات(update, context)
    
    elif user_input == "✅ اختبار التوكنات":
        return await اختبار_التوكنات(update, context)
    
    elif user_input == "✍️ تعديل البرومبت":
        current_prompt = GLOBAL_CONFIG.get('ai_prompt_template', 'غير محدد')
        await update.message.reply_text(
            f"✍️ **تعديل البرومبت**\n\n"
            f"**البرومبت الحالي:**\n{current_prompt[:200]}...\n\n"
            f"الرجاء إدخال البرومبت الجديد:\n\n"
            f"**المتغيرات المتاحة:**\n"
            f"{{name}} - اسم الطالب\n"
            f"{{stage}} - المرحلة الدراسية\n"
            f"{{country}} - الدولة\n"
            f"{{question}} - السؤال"
        )
        return EDIT_PROMPT
    
    elif user_input == "💾 النسخ الاحتياطي":
        return await قائمة_النسخ_الاحتياطي(update, context)
    
    elif user_input == "🎟️ إدارة الكوبونات":
        return await إدارة_الكوبونات(update, context)
    
    elif user_input == "➕ إضافة مستخدم يدوياً":
        await update.message.reply_text(
            "➕ **إضافة مستخدم يدوياً**\n\n"
            "الرجاء إدخال **معرف تليجرام (ID)** للمستخدم:\n\n"
            "💡 مثال: 123456789"
        )
        return ADD_USER_MANUAL
    

        
    elif user_input == "📞 إعدادات التواصل":
        return await إعدادات_التواصل(update, context)

    elif user_input == "🔙 العودة للقائمة الرئيسية":
        معلومات_الطالب = جلب_طالب(update.message.from_user.id)
        if معلومات_الطالب:
             context.user_data.update({
                 'الاسم': معلومات_الطالب[0],
                 'المرحلة_الدراسية': معلومات_الطالب[1],
                 'الدولة': معلومات_الطالب[2],
                 'معرف_التحقق_الفريد': معلومات_الطالب[3],
                 'is_premium': معلومات_الطالب[4],
                 'is_gift_premium': معلومات_الطالب[5],
                 'رصيد_النقاط': معلومات_الطالب[6],
                 'رصيد_الريال': معلومات_الطالب[7],
                 'is_manager': معلومات_الطالب[8],
                 'احالات_ناجحة': معلومات_الطالب[9],
                 'رمز_احالة_مستخدم': معلومات_الطالب[10]
             })

        context.user_data['is_admin'] = False
        await update.message.reply_text("↩️ تم تسجيل الخروج من وضع المدير.")
        await عرض_القائمة_الرئيسية(update, context) 
        return MAIN_MENU 
    
    else:
        await update.message.reply_text("اختيار غير صالح. الرجاء الاختيار من الأزرار.")
        return ADMIN_MENU

async def إعدادات_التواصل(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config()
    email = config.get('contact_email', 'غير محدد')
    instagram = config.get('contact_instagram', 'غير محدد')
    show_email = config.get('show_email', True)
    show_instagram = config.get('show_instagram', True)
    
    keyboard = [
        [KeyboardButton("📧 تغيير الإيميل"), KeyboardButton("📸 تغيير الانستجرام")],
        [KeyboardButton(f"👁️ إيميل: {'ظاهر' if show_email else 'مخفي'}"), KeyboardButton(f"👁️ انستجرام: {'ظاهر' if show_instagram else 'مخفي'}")],
        [KeyboardButton("🔙 العودة لقائمة المدير")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"📞 **إعدادات التواصل**\n\n"
        f"📧 **الإيميل الحالي:** {email}\n"
        f"📸 **الانستجرام الحالي:** {instagram}\n\n"
        f"اختر الإجراء المطلوب:",
        reply_markup=reply_markup
    )
    return ADMIN_CONTACT_MENU

async def handle_contact_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    config = load_config()
    
    if user_input == "📧 تغيير الإيميل":
        await update.message.reply_text("📧 **تغيير الإيميل**\n\nالرجاء إدخال الإيميل الجديد:")
        return SET_CONTACT_EMAIL
        
    elif user_input == "📸 تغيير الانستجرام":
        await update.message.reply_text("📸 **تغيير الانستجرام**\n\nالرجاء إدخال يوزر الانستجرام الجديد (بدون @):")
        return SET_CONTACT_INSTAGRAM
        
    elif user_input.startswith("👁️ إيميل:"):
        current_show = config.get('show_email', True)
        config['show_email'] = not current_show
        save_config(config)
        return await إعدادات_التواصل(update, context)
        
    elif user_input.startswith("👁️ انستجرام:"):
        current_show = config.get('show_instagram', True)
        config['show_instagram'] = not current_show
        save_config(config)
        return await إعدادات_التواصل(update, context)
        
    elif user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
        
    else:
        await update.message.reply_text("❌ اختيار غير صالح")
        return ADMIN_CONTACT_MENU

async def set_contact_email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_email = update.message.text.strip()
    config = load_config()
    config['contact_email'] = new_email
    save_config(config)
    
    await update.message.reply_text(f"✅ **تم تحديث الإيميل بنجاح!**\n\n📧 {new_email}")
    return await إعدادات_التواصل(update, context)

async def set_contact_instagram_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_instagram = update.message.text.strip().replace('@', '')
    config = load_config()
    config['contact_instagram'] = new_instagram
    save_config(config)
    
    await update.message.reply_text(f"✅ **تم تحديث الانستجرام بنجاح!**\n\n📸 @{new_instagram}")
    return await إعدادات_التواصل(update, context)

# دوال المدير الجديدة
async def display_all_users_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أسماء ورموز تفعيل كل مستخدمي البوت"""
    الطلاب = جلب_جميع_الطلاب()
    
    إذا_لم_يوجد = "❌ لا يوجد طلاب مسجلين."
    
    if الطلاب:
        رسالة = f"👥 **قائمة جميع المستخدمين:** (إجمالي: {len(الطلاب)} مستخدم)\n\n"
        
        for الاسم, الرمز, المرحلة, معرف_المستخدم, is_premium, is_gift in الطلاب:
            حالة = "🎁" if is_gift else "✅" if is_premium else "❌"
            رسالة += f"👤 {الاسم} | {الرمز} | {المرحلة} | {حالة}\n"
            
        await update.message.reply_text(رسالة)
    else:
        await update.message.reply_text(إذا_لم_يوجد)
        
    return ADMIN_MENU

async def display_premium_users_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض أسماء ورموز تفعيل المشتركين البريميم فقط"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT الاسم, معرف_التحقق_الفريد, معرف_المستخدم, is_gift_premium FROM الطلاب WHERE is_premium = 1')
        المشتركون = cursor.fetchall()
        conn.close()
        
        إذا_لم_يوجد = "❌ لا يوجد مشتركون حالياً في Premium."
        
        if المشتركون:
            رسالة = f"✨ **قائمة مشتركي Premium:** (إجمالي: {len(المشتركون)} مشترك)\n\n"
            
            for الاسم, الرمز, معرف_المستخدم, is_gift in المشتركون:
                نوع = "🎁 هدية" if is_gift else "💳 مدفوع"
                رسالة += f"👤 {الاسم} | {الرمز} | {نوع}\n"
                
            await update.message.reply_text(رسالة)
        else:
            await update.message.reply_text(إذا_لم_يوجد)
            
    except Exception as e:
        logger.error(f"خطأ في جلب المشتركين البريميم: {e}")
        await update.message.reply_text("❌ حدث خطأ في جلب البيانات")
        
    return ADMIN_MENU

async def display_non_premium_users_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض المستخدمين غير المشتركين في البريميم"""
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT الاسم, معرف_التحقق_الفريد, معرف_المستخدم FROM الطلاب WHERE is_premium = 0')
        غير_المشتركين = cursor.fetchall()
        conn.close()
        
        إذا_لم_يوجد = "✅ جميع المستخدمين مشتركون في Premium."
        
        if غير_المشتركين:
            رسالة = f"🚫 **قائمة غير المشتركين في Premium:** (إجمالي: {len(غير_المشتركين)} مستخدم)\n\n"
            
            for الاسم, الرمز, معرف_المستخدم in غير_المشتركين:
                رسالة += f"👤 {الاسم} | {الرمز}\n"
                
            await update.message.reply_text(رسالة)
        else:
            await update.message.reply_text(إذا_لم_يوجد)
            
    except Exception as e:
        logger.error(f"خطأ في جلب غير المشتركين: {e}")
        await update.message.reply_text("❌ حدث خطأ في جلب البيانات")
        
    return ADMIN_MENU

async def عرض_إحصائيات_النقاط(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # إجمالي النقاط في النظام
        cursor.execute('SELECT SUM(رصيد_النقاط), SUM(رصيد_الريال) FROM الطلاب')
        إجمالي_النقاط, إجمالي_الريال = cursor.fetchone()
        
        # أعلى 5 مستخدمين
        cursor.execute('''
            SELECT الاسم, رصيد_النقاط, رصيد_الريال 
            FROM الطلاب 
            ORDER BY رصيد_النقاط DESC 
            LIMIT 5
        ''')
        أعلى_المستخدمين = cursor.fetchall()
        
        conn.close()
        
        رسالة = f"📊 **إحصائيات النقاط**\n\n"
        رسالة += f"💰 **إجمالي النقاط في النظام:** {إجمالي_النقاط or 0} نقطة\n"
        رسالة += f"💵 **إجمالي الريال في النظام:** {إجمالي_الريال or 0} ريال\n\n"
        رسالة += f"🏆 **أعلى 5 مستخدمين:**\n"
        
        for i, (اسم, نقاط, ريال) in enumerate(أعلى_المستخدمين, 1):
            رسالة += f"{i}. {اسم} - {نقاط} نقطة - {ريال} ريال\n"
        
        await update.message.reply_text(رسالة)
        
    except Exception as e:
        logger.error(f"خطأ في عرض إحصائيات النقاط: {e}")
        await update.message.reply_text("❌ حدث خطأ في جلب الإحصائيات")
    
    return ADMIN_MENU

async def إدارة_المهام(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("➕ إضافة مهمة جديدة")],
        [KeyboardButton("📋 عرض المهام الحالية")],
        [KeyboardButton("🔙 العودة لقائمة المدير")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("📋 **إدارة المهام**\n\nاختر الإجراء المطلوب:", reply_markup=reply_markup)
    return ADMIN_MANAGE_TASKS

async def handle_manage_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    if user_input == "➕ إضافة مهمة جديدة":
        await update.message.reply_text("➕ **إضافة مهمة جديدة**\n\nالرجاء إدخال رابط المهمة:")
        return ADD_TASK
        
    elif user_input == "📋 عرض المهام الحالية":
        return await عرض_المهام_الحالية(update, context)
        
    elif user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
    
    else:
        await update.message.reply_text("❌ اختيار غير صالح")
        return ADMIN_MANAGE_TASKS

async def add_task_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رابط = update.message.text
    context.user_data['رابط_المهمة'] = رابط
    
    await update.message.reply_text("📝 الرجاء إدخال وصف المهمة:")
    return ADD_TASK_DESC

async def add_task_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    وصف = update.message.text
    context.user_data['وصف_المهمة'] = وصف
    
    await update.message.reply_text("💎 الرجاء إدخال عدد النقاط للمهمة:")
    return ADD_TASK_POINTS

async def add_task_points_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        نقاط = int(update.message.text)
        رابط = context.user_data['رابط_المهمة']
        وصف = context.user_data['وصف_المهمة']
        
        if إضافة_مهمة(رابط, وصف, نقاط):
            await update.message.reply_text(f"✅ **تم إضافة المهمة بنجاح!**\n\n📋 {وصف}\n💎 {نقاط} نقطة")
            
            # إرسال إشعار لجميع المستخدمين
            try:
                conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('SELECT معرف_المستخدم, الاسم FROM الطلاب')
                users = cursor.fetchall()
                conn.close()
                
                success_count = 0
                
                for user in users:
                    try:
                        user_id = user[0]
                        user_name = user[1]
                        
                        notification_text = (
                            f"مرحباً {user_name} 👋\n\n"
                            f"🎉 **يوجد مهمة جديدة لك!**\n"
                            f"💎 **عدد النقاط:** {نقاط}\n\n"
                            f"الرجاء مراجعة قسم **المهام** لإتمام المهمة والحصول على النقاط."
                        )
                        
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=notification_text
                        )
                        success_count += 1
                        # تأخير بسيط لتجنب الحظر
                        if success_count % 20 == 0:
                            await asyncio.sleep(1)
                    except Exception:
                        continue
                
                await update.message.reply_text(f"📣 **تم إرسال الإشعار لـ {success_count} مستخدم!**")
                
            except Exception as e:
                logger.error(f"خطأ في إرسال إشعار المهمة الجديدة: {e}")
                await update.message.reply_text("⚠️ تم إضافة المهمة ولكن فشل إرسال الإشعار للجميع.")
                
        else:
            await update.message.reply_text("❌ فشل في إضافة المهمة")
            
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح للنقاط")
        return ADD_TASK_POINTS
    
    context.user_data.pop('رابط_المهمة', None)
    context.user_data.pop('وصف_المهمة', None)
    
    return await admin_menu(update, context)

async def عرض_المهام_الحالية(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT مهمة_id, رابط, وصف, نقاط FROM المهام WHERE is_active = 1')
        مهام = cursor.fetchall()
        conn.close()
        
        if not مهام:
            await update.message.reply_text("📭 لا توجد مهام حالياً.")
            return ADMIN_MANAGE_TASKS
        
        رسالة = "📋 **المهام الحالية:**\n\n"
        for مهمة_id, رابط, وصف, نقاط in مهام:
            رسالة += f"🔹 **{وصف}**\n"
            رسالة += f"🔗 الرابط: {رابط}\n"
            رسالة += f"💎 النقاط: {نقاط}\n"
            رسالة += f"🆔 الرقم: {مهمة_id}\n\n"
        
        await update.message.reply_text(رسالة)
        
    except Exception as e:
        logger.error(f"خطأ في عرض المهام الحالية: {e}")
        await update.message.reply_text("❌ حدث خطأ في جلب المهام")
    
    return ADMIN_MANAGE_TASKS

async def طلبات_البريميم(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 **طلبات البريميم**\n\n"
        "حالياً لا توجد طلبات بريميم معلقة.\n"
        "سيظهر هنا أي مستخدم يحاول شراء البريميم ولكن رصيده غير كافي."
    )
    return ADMIN_MENU

async def add_manager_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رمز_فريد = update.message.text.strip().upper()
    
    # التحقق من وجود المستخدم
    مستخدم = التحقق_من_رمز_الاحالة(رمز_فريد)
    
    if not مستخدم:
        await update.message.reply_text("❌ لم يتم العثور على مستخدم بهذا الرمز الفريد. الرجاء المحاولة مرة أخرى:")
        return ADD_MANAGER
    
    معرف_المستخدم, اسم_المستخدم = مستخدم
    
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('UPDATE الطلاب SET is_manager = 1 WHERE معرف_المستخدم = ?', (معرف_المستخدم,))
        conn.commit()
        conn.close()
        
        # إرسال إشعار للمستخدم المعين
        try:
            await context.bot.send_message(
                chat_id=معرف_المستخدم,
                text=f"🎉 **تهانينا!**\n\n"
                     f"تم تعيينك كمدير في بوت منهج Ai!\n"
                     f"الآن يمكنك الدخول لوضع المدير من القائمة الرئيسية."
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال إشعار للمدير الجديد: {e}")
        
        await update.message.reply_text(f"✅ **تم تعيين {اسم_المستخدم} كمدير بنجاح!**")
        
    except Exception as e:
        logger.error(f"خطأ في تعيين المدير: {e}")
        await update.message.reply_text("❌ حدث خطأ في تعيين المدير")
    
    return await admin_menu(update, context)

async def إدارة_الدعم(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رسائل = جلب_رسائل_الدعم()
    
    if not رسائل:
        await update.message.reply_text("📭 لا توجد رسائل دعم جديدة.")
        return ADMIN_MENU
    
    keyboard = []
    for دعم_id, معرف_المستخدم, اسم, رسالة, تاريخ in رسائل:
        keyboard.append([KeyboardButton(f"📩 {اسم} - {رسالة[:30]}...")])
        context.user_data[f'دعم_{دعم_id}'] = (دعم_id, معرف_المستخدم, اسم, رسالة)
    
    keyboard.append([KeyboardButton("🔙 العودة لقائمة المدير")])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"📞 **رسائل الدعم الجديدة** ({len(رسائل)} رسالة)\n\n"
        f"اختر الرسالة للرد عليها:",
        reply_markup=reply_markup
    )
    return ADMIN_SUPPORT_MENU

async def handle_support_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    if user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
    
    # البحث عن الرسالة المختارة
    for key, value in context.user_data.items():
        if key.startswith('دعم_') and user_input.startswith(f"📩 {value[2]}"):
            دعم_id, معرف_المستخدم, اسم, رسالة = value
            context.user_data['دعم_محدد'] = (دعم_id, معرف_المستخدم, اسم)
            
            await update.message.reply_text(
                f"📩 **رسالة من {اسم}:**\n\n"
                f"{رسالة}\n\n"
                f"الرجاء كتابة الرد:"
            )
            return ADMIN_REPLY_SUPPORT
    
    await update.message.reply_text("❌ لم يتم التعرف على الرسالة")
    return ADMIN_SUPPORT_MENU

async def reply_support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    الرد = update.message.text
    دعم_محدد = context.user_data.get('دعم_محدد')
    
    if not دعم_محدد:
        await update.message.reply_text("❌ لم يتم تحديد رسالة دعم")
        return ADMIN_SUPPORT_MENU
    
    دعم_id, معرف_المستخدم, اسم = دعم_محدد
    
    ناجح, معرف_المستخدم = الرد_على_دعم(دعم_id, الرد)
    
    if ناجح:
        # إرسال الرد للمستخدم
        try:
            await context.bot.send_message(
                chat_id=معرف_المستخدم,
                text=f"📞 **رد الدعم:**\n\n"
                     f"{الرد}\n\n"
                     f"شكراً لاتصالك بنا! 🙏"
            )
        except Exception as e:
            logger.error(f"خطأ في إرسال الرد للمستخدم: {e}")
        
        await update.message.reply_text("✅ **تم إرسال الرد بنجاح!**")
    else:
        await update.message.reply_text("❌ فشل في إرسال الرد")
    
    context.user_data.pop('دعم_محدد', None)
    return await admin_menu(update, context)

async def الرصيد_المفتوح(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🎁 منح نقاط لمستخدم"), KeyboardButton("💸 منح ريال لمستخدم")],
        [KeyboardButton("🔙 العودة لقائمة المدير")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("💰 **الرصيد المفتوح**\n\nاختر الإجراء المطلوب:", reply_markup=reply_markup)
    return ADMIN_GIVE_POINTS

async def handle_give_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    if user_input == "🎁 منح نقاط لمستخدم":
        await update.message.reply_text("🎁 **منح نقاط لمستخدم**\n\nالرجاء إدخال الرمز الفريد للمستخدم:")
        return ADMIN_GIVE_POINTS_USER
        
    elif user_input == "💸 منح ريال لمستخدم":
        await update.message.reply_text("💸 **منح ريال لمستخدم**\n\nالرجاء إدخال الرمز الفريد للمستخدم:")
        return ADMIN_GIVE_MONEY_USER
        
    elif user_input == "🔙 العودة لقائمة المدير":
        return await admin_menu(update, context)
    
    else:
        await update.message.reply_text("❌ اختيار غير صالح")
        return ADMIN_GIVE_POINTS

async def give_points_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رمز_فريد = update.message.text.strip().upper()
    
    # التحقق من وجود المستخدم
    مستخدم = التحقق_من_رمز_الاحالة(رمز_فريد)
    
    if not مستخدم:
        await update.message.reply_text("❌ لم يتم العثور على مستخدم بهذا الرمز الفريد. الرجاء المحاولة مرة أخرى:")
        return ADMIN_GIVE_POINTS_USER
    
    context.user_data['مستخدم_لمنح_النقاط'] = مستخدم
    await update.message.reply_text("💎 الرجاء إدخال عدد النقاط التي تريد منحها:")
    return ADMIN_GIVE_POINTS_AMOUNT

async def give_points_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        نقاط = int(update.message.text)
        
        if نقاط <= 0:
            await update.message.reply_text("❌ عدد النقاط يجب أن يكون أكبر من الصفر")
            return ADMIN_GIVE_POINTS_AMOUNT
        
        مستخدم = context.user_data.get('مستخدم_لمنح_النقاط')
        
        if not مستخدم:
            await update.message.reply_text("❌ لم يتم تحديد مستخدم")
            return await admin_menu(update, context)
            
        معرف_المستخدم, اسم_المستخدم = مستخدم
        
        success = إضافة_نقاط(معرف_المستخدم, نقاط, "هدية من الإدارة")
        
        if success:
            # إرسال إشعار للمستخدم
            try:
                await context.bot.send_message(
                    chat_id=معرف_المستخدم,
                    text=f"🎉 **هدية من الإدارة!**\n\n"
                         f"لقد حصلت على {نقاط} نقطة هدية من الإدارة!\n"
                         f"💎 تم إضافتها لرصيدك تلقائياً"
                )
            except Exception as e:
                logger.error(f"خطأ في إرسال إشعار للمستخدم: {e}")
            
            await update.message.reply_text(f"✅ **تم منح {نقاط} نقطة لـ {اسم_المستخدم} بنجاح!**")
        else:
            await update.message.reply_text("❌ فشل في منح النقاط")
            
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
        return ADMIN_GIVE_POINTS_AMOUNT
    except Exception as e:
        logger.error(f"خطأ في منح النقاط: {e}")
        await update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
    
    context.user_data.pop('مستخدم_لمنح_النقاط', None)
    return await admin_menu(update, context)

async def give_money_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    رمز_فريد = update.message.text.strip().upper()
    
    # التحقق من وجود المستخدم
    مستخدم = التحقق_من_رمز_الاحالة(رمز_فريد)
    
    if not مستخدم:
        await update.message.reply_text("❌ لم يتم العثور على مستخدم بهذا الرمز الفريد. الرجاء المحاولة مرة أخرى:")
        return ADMIN_GIVE_MONEY_USER
    
    context.user_data['مستخدم_لمنح_الريال'] = مستخدم
    await update.message.reply_text("💸 الرجاء إدخال المبلغ بالريال الذي تريد منحه:")
    return ADMIN_GIVE_MONEY_AMOUNT

async def give_money_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        مبلغ = int(update.message.text)
        مستخدم = context.user_data.get('مستخدم_لمنح_الريال')
        
        if not مستخدم:
            await update.message.reply_text("❌ لم يتم تحديد مستخدم")
            return ADMIN_GIVE_MONEY_USER
            
        معرف_المستخدم, اسم_المستخدم = مستخدم
        
        # تنفيذ منح الريال
        try:
            conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('UPDATE الطلاب SET رصيد_الريال = رصيد_الريال + ? WHERE معرف_المستخدم = ?', (مبلغ, معرف_المستخدم))
            conn.commit()
            conn.close()
            
            # إرسال إشعار للمستخدم
            try:
                await context.bot.send_message(
                    chat_id=معرف_المستخدم,
                    text=f"🎉 **هدية من الإدارة!**\n\n"
                         f"لقد حصلت على {مبلغ} ريال هدية من الإدارة!\n"
                         f"💳 تم إضافتها لرصيدك تلقائياً"
                )
            except Exception as e:
                logger.error(f"خطأ في إرسال إشعار للمستخدم: {e}")
            
            await update.message.reply_text(f"✅ **تم منح {مبلغ} ريال لـ {اسم_المستخدم} بنجاح!**")
        except Exception as e:
            logger.error(f"خطأ في منح الريال: {e}")
            await update.message.reply_text("❌ فشل في منح الريال")
            
    except ValueError:
        await update.message.reply_text("❌ الرجاء إدخال رقم صحيح")
        return ADMIN_GIVE_MONEY_AMOUNT
    
    context.user_data.pop('مستخدم_لمنح_الريال', None)
    return await admin_menu(update, context)

# Handlers للمدير الأساسية
async def activate_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    premium_id = update.message.text.strip()
    
    try:
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE الطلاب 
            SET is_premium = 1, ردود_منذ_الإعلان = 0
            WHERE معرف_التحقق_الفريد = ?
        ''', (premium_id,))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            await update.message.reply_text(f"✅ **تم التفعيل بنجاح!**\n\nتم تفعيل حالة Premium للرمز: `{premium_id}`")
        else:
            await update.message.reply_text(f"❌ **فشل التفعيل!**\n\nلم يتم العثور على طالب يملك الرمز: `{premium_id}`")
            
        conn.close()
        
    except Exception as e:
        logger.error(f"خطأ في تفعيل البريميم: {e}")
        await update.message.reply_text(f"❌ حدث خطأ في قاعدة البيانات أثناء التفعيل.")

    return await admin_menu(update, context)

async def deactivate_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    premium_id = update.message.text.strip()
    
    if إلغاء_اشتراك_بريميم(premium_id):
        await update.message.reply_text(f"✅ **تم إلغاء التفعيل بنجاح!**\n\nتم إلغاء حالة Premium للرمز: `{premium_id}`.")
    else:
        await update.message.reply_text(f"❌ **فشل إلغاء التفعيل!**\n\nلم يتم العثور على طالب مفعل بريميم يملك الرمز: `{premium_id}`.")
        
    return await admin_menu(update, context)

async def activate_gift_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تفعيل بريميم هدية"""
    premium_id = update.message.text.strip()
    
    if تفعيل_بريميم_هدية(premium_id):
        await update.message.reply_text(f"✅ **تم منح الهدية بنجاح!**\n\nتم تفعيل حالة Premium كهدية للرمز: `{premium_id}`")
    else:
        await update.message.reply_text(f"❌ **فشل منح الهدية!**\n\nلم يتم العثور على طالب يملك الرمز: `{premium_id}`")
        
    return await admin_menu(update, context)

async def send_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال الإشعار لجميع المستخدمين"""
    message = update.message.text
    
    الطلاب = جلب_جميع_الطلاب() 
    معرفات_المستخدمين = [row[3] for row in الطلاب] 
    
    رسائل_مرسلة = 0
    رسائل_فاشلة = 0
    
    await update.message.reply_text("🚀 جاري إرسال الإشعار الجماعي...")
    
    for user_id in معرفات_المستخدمين:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📣 **إشعار المسابقات/الفعاليات**\n\n"
                     f"{message}",
                parse_mode='Markdown'
            )
            رسائل_مرسلة += 1
            await asyncio.sleep(0.05) 
        except Exception as e:
            رسائل_فاشلة += 1
            logger.warning(f"❌ فشل إرسال إشعار للمستخدم {user_id}: {e}")
            
    await update.message.reply_text(
        f"✅ **تم الانتهاء من الإرسال!**\n\n"
        f"✅ الرسائل المرسلة بنجاح: {رسائل_مرسلة}\n"
        f"❌ الرسائل الفاشلة (قد يكون المستخدم حظر البوت): {رسائل_فاشلة}"
    )
    
    return await admin_menu(update, context)

async def set_new_price_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حفظ السعر الجديد للبريميم فقط - لا يتعامل مع نقاط الإعلان"""
    new_value_input = update.message.text.strip()
    
    global GLOBAL_CONFIG
    
    try:
        # تحويل المدخل لرقم
        new_value = int(new_value_input)
        
        if new_value <= 0:
            await update.message.reply_text("❌ القيمة يجب أن تكون أكبر من صفر!")
            return CHANGE_PRICE_ENTRY
        
        # هذه الدالة للسعر فقط - نسأل المستخدم للتأكيد
        context.user_data['pending_value'] = new_value
        
        keyboard = [
            [KeyboardButton("💵 تغيير سعر البريميم")],
            [KeyboardButton("🎬 تغيير نقاط الإعلان")],
            [KeyboardButton("❌ إلغاء")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"🔍 **اختر ما تريد تغييره لـ {new_value}:**\n\n"
            f"💰 السعر الحالي: {GLOBAL_CONFIG.get('premium_riyal_price', 10)} ريال\n"
            f"💎 النقاط الحالية: {GLOBAL_CONFIG.get('ad_points_reward', 5)} نقطة",
            reply_markup=reply_markup
        )
        return CHANGE_PRICE_ENTRY + 1
        
        return await admin_menu(update, context)
        
    except ValueError:
        await update.message.reply_text(
            "❌ **خطأ في الإدخال!**\n\n"
            "الرجاء إدخال رقم صحيح فقط\n"
            "مثال: 10"
        )
        return CHANGE_PRICE_ENTRY

async def confirm_price_change_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تأكيد نوع التغيير (سعر أم نقاط)"""
    global GLOBAL_CONFIG
    
    user_choice = update.message.text
    pending_value = context.user_data.get('pending_value')
    
    if not pending_value:
        await update.message.reply_text("❌ حدث خطأ. الرجاء المحاولة مرة أخرى")
        return await admin_menu(update, context)
    
    if user_choice == "💵 تغيير سعر البريميم":
        GLOBAL_CONFIG['premium_riyal_price'] = pending_value
        save_config(GLOBAL_CONFIG)
        await update.message.reply_text(
            f"✅ **تم تحديث سعر البوت بنجاح!**\n\n"
            f"💵 **السعر الجديد:** {pending_value} ريال"
        )
    elif user_choice == "🎬 تغيير نقاط الإعلان":
        old_reward = GLOBAL_CONFIG.get('ad_points_reward', 5)
        GLOBAL_CONFIG['ad_points_reward'] = pending_value
        
        # حفظ الإعدادات والتحقق من النجاح
        save_success = save_config(GLOBAL_CONFIG)
        
        # إعادة تحميل للتحقق من الحفظ
        updated_config = load_config()
        saved_reward = updated_config.get('ad_points_reward', 5)
        
        if saved_reward == pending_value:
            await update.message.reply_text(
                f"✅ **تم تحديث نقاط الإعلان بنجاح!**\n\n"
                f"💎 **القيمة السابقة:** {old_reward} نقطة\n"
                f"💎 **القيمة الجديدة:** {pending_value} نقطة\n\n"
                f"✅ **تم التأكد من الحفظ!** سيحصل المستخدمون على {pending_value} نقطة عند مشاهدة كل إعلان."
            )
        else:
            await update.message.reply_text(
                f"⚠️ **مشكلة في الحفظ!** القيمة المحفوظة: {saved_reward}, المطلوبة: {pending_value}\n"
                f"الرجاء المحاولة مرة أخرى."
            )
    elif user_choice == "❌ إلغاء":
        await update.message.reply_text("❌ تم الإلغاء")
    else:
        await update.message.reply_text("❌ اختيار غير صحيح")
    
    context.user_data.pop('pending_value', None)
    return await admin_menu(update, context)

async def edit_prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل البرومبت الأساسي"""
    new_prompt = update.message.text.strip()
    
    global GLOBAL_CONFIG
    
    GLOBAL_CONFIG['ai_prompt_template'] = new_prompt
    save_config(GLOBAL_CONFIG)
    
    await update.message.reply_text(
        f"✅ **تم تحديث البرومبت بنجاح!**\n\n"
        f"**البرومبت الجديد:**\n{new_prompt[:200]}..."
    )
    return await admin_menu(update, context)

async def change_ad_reward_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تغيير مكافأة مشاهدة الإعلان"""
    global GLOBAL_CONFIG
    
    try:
        new_reward = int(update.message.text.strip())
        
        if new_reward < 0:
            await update.message.reply_text("❌ المكافأة يجب أن تكون 0 أو أكثر")
            return CHANGE_AD_REWARD
        
        if new_reward > 100:
            await update.message.reply_text(
                "⚠️ **تحذير!**\n\n"
                "المكافأة أكبر من 100 نقطة!\n"
                "هل أنت متأكد؟ (نعم/لا)"
            )
            context.user_data['pending_ad_reward'] = new_reward
            return CHANGE_AD_REWARD
        
        # حفظ المكافأة الجديدة
        old_reward = GLOBAL_CONFIG.get('ad_points_reward', 5)
        GLOBAL_CONFIG['ad_points_reward'] = new_reward
        
        # حفظ الإعدادات وإعادة تحميلها للتأكد
        save_success = save_config(GLOBAL_CONFIG)
        logger.info(f"[AD-CONFIG] حفظ الإعدادات: {save_success}")
        
        # إعادة تحميل الإعدادات للتأكد من الحفظ
        updated_config = load_config()
        saved_reward = updated_config.get('ad_points_reward', 5)
        logger.info(f"[AD-CONFIG] القيمة المحفوظة: {saved_reward}، المطلوبة: {new_reward}")
        
        if saved_reward == new_reward:
            await update.message.reply_text(
                f"✅ **تم تحديث المكافأة بنجاح!**\n\n"
                f"🎬 **القيمة السابقة:** {old_reward} نقطة\n"
                f"🎬 **القيمة الجديدة:** {new_reward} نقطة\n\n"
                f"✅ **تم التأكد من الحفظ!** سيحصل المستخدمون على {new_reward} نقطة عند مشاهدة كل إعلان."
            )
        else:
            await update.message.reply_text(
                f"⚠️ **تحذير!** قد يكون هناك مشكلة في الحفظ\n\n"
                f"القيمة المحفوظة: {saved_reward}\n"
                f"القيمة المطلوبة: {new_reward}\n\n"
                f"الرجاء المحاولة مرة أخرى أو فحص ملف الإعدادات."
            )
        return await admin_menu(update, context)
        
    except ValueError:
        # التحقق من تأكيد المكافأة الكبيرة
        user_input = update.message.text.strip().lower()
        pending_reward = context.user_data.get('pending_ad_reward')
        
        if pending_reward and user_input in ['نعم', 'yes', 'y']:
            old_reward = GLOBAL_CONFIG.get('ad_points_reward', 5)
            GLOBAL_CONFIG['ad_points_reward'] = pending_reward
            save_success = save_config(GLOBAL_CONFIG)
            context.user_data.pop('pending_ad_reward', None)
            
            # التحقق من نجاح الحفظ
            updated_config = load_config()
            saved_reward = updated_config.get('ad_points_reward', 5)
            
            if saved_reward == pending_reward:
                await update.message.reply_text(
                    f"✅ **تم تحديث المكافأة بنجاح!**\n\n"
                    f"🎬 **القيمة السابقة:** {old_reward} نقطة\n"
                    f"🎬 **القيمة الجديدة:** {pending_reward} نقطة\n\n"
                    f"✅ تم التأكد من الحفظ!"
                )
            else:
                await update.message.reply_text(
                    f"⚠️ مشكلة في الحفظ! القيمة المحفوظة: {saved_reward}, المطلوبة: {pending_reward}"
                )
            return await admin_menu(update, context)
        
        elif pending_reward and user_input in ['لا', 'no', 'n']:
            context.user_data.pop('pending_ad_reward', None)
            await update.message.reply_text("❌ تم إلغاء التغيير")
            return await admin_menu(update, context)
        
        await update.message.reply_text(
            "❌ **خطأ!**\n\n"
            "الرجاء إدخال رقم صحيح (مثال: 5 أو 10 أو 20):"
        )
        return CHANGE_AD_REWARD

async def add_user_manual_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدخال معرف تليجرام للمستخدم الجديد"""
    try:
        user_telegram_id = int(update.message.text.strip())
        
        # التحقق من أن المستخدم غير موجود مسبقاً
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT الاسم FROM الطلاب WHERE معرف_المستخدم = ?', (user_telegram_id,))
        existing = cursor.fetchone()
        conn.close()
        
        if existing:
            await update.message.reply_text(
                f"⚠️ **المستخدم موجود مسبقاً!**\n\n"
                f"📝 الاسم: {existing[0]}\n"
                f"🆔 المعرف: {user_telegram_id}\n\n"
                f"الرجاء إدخال معرف مستخدم آخر:"
            )
            return ADD_USER_MANUAL
        
        context.user_data['new_user_telegram_id'] = user_telegram_id
        
        await update.message.reply_text(
            f"✅ **تم حفظ المعرف:** {user_telegram_id}\n\n"
            f"📝 الآن أدخل **الاسم الثلاثي** للمستخدم:\n\n"
            f"💡 مثال: محمد أحمد علي"
        )
        return ADD_USER_MANUAL_NAME
        
    except ValueError:
        await update.message.reply_text(
            "❌ **خطأ!**\n\n"
            "الرجاء إدخال رقم صحيح (معرف تليجرام)\n"
            "مثال: 123456789"
        )
        return ADD_USER_MANUAL

async def add_user_manual_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إدخال اسم المستخدم الجديد"""
    user_name = update.message.text.strip()
    
    if len(user_name) < 3:
        await update.message.reply_text(
            "❌ **الاسم قصير جداً!**\n\n"
            "الرجاء إدخال الاسم الثلاثي كاملاً:\n"
            "مثال: محمد أحمد علي"
        )
        return ADD_USER_MANUAL_NAME
    
    context.user_data['new_user_name'] = user_name
    
    keyboard = [
        [KeyboardButton("🎓 الابتدائية"), KeyboardButton("📚 المتوسطة")],
        [KeyboardButton("🏫 الثانوية"), KeyboardButton("🎯 الجامعة")],
        [KeyboardButton("❌ إلغاء")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ **تم حفظ الاسم:** {user_name}\n\n"
        f"🎓 الآن اختر **المرحلة الدراسية:**",
        reply_markup=reply_markup
    )
    return ADD_USER_MANUAL_STAGE

async def add_user_manual_stage_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج اختيار المرحلة الدراسية وإضافة المستخدم"""
    user_choice = update.message.text
    
    if user_choice == "❌ إلغاء":
        context.user_data.pop('new_user_telegram_id', None)
        context.user_data.pop('new_user_name', None)
        await update.message.reply_text("❌ تم إلغاء إضافة المستخدم")
        return await admin_menu(update, context)
    
    # تحويل الزر للمرحلة
    stage_map = {
        "🎓 الابتدائية": "الابتدائية",
        "📚 المتوسطة": "المتوسطة",
        "🏫 الثانوية": "الثانوية",
        "🎯 الجامعة": "الجامعة"
    }
    
    stage = stage_map.get(user_choice)
    
    if not stage:
        await update.message.reply_text("❌ اختيار غير صحيح. الرجاء اختيار المرحلة من الأزرار")
        return ADD_USER_MANUAL_STAGE
    
    telegram_id = context.user_data.get('new_user_telegram_id')
    user_name = context.user_data.get('new_user_name')
    
    try:
        # توليد رمز تحقق فريد
        
        import string
        unique_code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        # إضافة المستخدم لقاعدة البيانات
        conn = sqlite3.connect(f'{BASE_DIR}/البيانات/الطلاب.db', check_same_thread=False)
        cursor = conn.cursor()
        
        from datetime import datetime
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO الطلاب (
                معرف_المستخدم, الاسم, الصف, معرف_التحقق_الفريد,
                عدد_الاسئلة, تاريخ_التسجيل, آخر_نشاط, ردود_منذ_الإعلان,
                is_premium, الدولة, is_gift_premium, رصيد_النقاط, رصيد_الريال,
                is_manager, احالات_ناجحة, رمز_احالة_مستخدم
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            telegram_id, user_name, stage, unique_code,
            0, current_time, current_time, 0,
            0, 'السعودية', 0, 0, 0,
            0, 0, None
        ))
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ **تم إضافة المستخدم بنجاح!**\n\n"
            f"🆔 **معرف تليجرام:** {telegram_id}\n"
            f"📝 **الاسم:** {user_name}\n"
            f"🎓 **المرحلة:** {stage}\n"
            f"🔑 **الرمز الفريد:** `{unique_code}`\n\n"
            f"💡 يمكن للمستخدم الآن استخدام البوت مباشرة!"
        )
        
        context.user_data.pop('new_user_telegram_id', None)
        context.user_data.pop('new_user_name', None)
        
    except Exception as e:
        logger.error(f"خطأ في إضافة مستخدم يدوياً: {e}")
        await update.message.reply_text(
            f"❌ **حدث خطأ في إضافة المستخدم!**\n\n"
            f"التفاصيل: {str(e)}"
        )
    
    return await admin_menu(update, context)

async def cancel(update: Update, context):
    await update.message.reply_text('تم إلغاء المحادثة.\nيمكنك البدء مرة أخرى بـ /start')
    return ConversationHandler.END

def main():
    print("🔍 جاري فحص النظام...")
    
    # إظهار حالة التوكنات عند التشغيل
    total_tokens = len(GEMINI_TOKENS_STANDARD) + len(GEMINI_TOKENS_PREMIUM)
    if total_tokens > 0:
        print(f"✅ تم تحميل {total_tokens} توكن (عادي: {len(GEMINI_TOKENS_STANDARD)}, بريميم: {len(GEMINI_TOKENS_PREMIUM)})")
    else:
        print("⚠️ لم يتم إضافة توكنات. الرجاء إضافتها من لوحة المدير.")
    
    print(f"🚀 بوت منهج Ai جاهز للتشغيل!")
    
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة وظيفة النسخ الاحتياطي التلقائي
        async def send_daily_backup(context: ContextTypes.DEFAULT_TYPE):
            """إرسال نسخة احتياطية يومية"""
            backup_enabled = GLOBAL_CONFIG.get('backup_enabled', False)
            backup_chat_id = GLOBAL_CONFIG.get('backup_chat_id')
            
            if backup_enabled and backup_chat_id:
                try:
                    db_path = f'{BASE_DIR}/البيانات/الطلاب.db'
                    
                    with open(db_path, 'rb') as db_file:
                        await context.bot.send_document(
                            chat_id=backup_chat_id,
                            document=db_file,
                            filename=f"backup_{datetime.now().strftime('%Y%m%d')}.db",
                            caption=f"📦 **نسخة احتياطية تلقائية**\n\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                    logger.info("تم إرسال النسخة الاحتياطية اليومية")
                except Exception as e:
                    logger.error(f"خطأ في إرسال النسخة الاحتياطية: {e}")
        
        # جدولة النسخ الاحتياطي
        backup_enabled = GLOBAL_CONFIG.get('backup_enabled', False)
        if backup_enabled:
            backup_time = GLOBAL_CONFIG.get('backup_time', '00:00')
            try:
                hour, minute = map(int, backup_time.split(':'))
                import datetime as dt
                backup_time_obj = dt.time(hour=hour, minute=minute)
                
                app.job_queue.run_daily(
                    send_daily_backup,
                    time=backup_time_obj,
                    name='daily_backup'
                )
                print(f"⏰ تم جدولة النسخ الاحتياطي اليومي في {backup_time}")
            except Exception as e:
                logger.error(f"خطأ في جدولة النسخ الاحتياطي: {e}")
        
        # إعداد محادثة التسجيل
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)], 
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                STAGE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_stage)],
                COUNTRY_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country)],
                REFERRAL_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_referral_code)],
                MAIN_MENU: [
                    MessageHandler(filters.Regex("^🤖 بوتاتنا الأخرى$"), handle_user_menu),
                    MessageHandler(filters.PHOTO, handle_photo_question),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)
                ],
                
                # حالات جديدة للنقاط والدعم
                CONVERT_POINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, convert_points_handler)],
                TRANSFER_MONEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, transfer_money_handler)],
                TRANSFER_MONEY_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, transfer_money_amount_handler)],
                SUPPORT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_message_handler)],
                TASKS_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tasks_menu)],
                
                # Admin States
                ADMIN_PASSWORD_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_admin_password)],
                ADMIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_menu)],
                PREMIUM_ID_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, activate_premium)],
                PREMIUM_DEACTIVATE_ID_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, deactivate_premium)],
                GIFT_PREMIUM_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, activate_gift_premium)],
                BROADCAST_MESSAGE_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast_message)],
                CHANGE_PRICE_ENTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_new_price_value)],
                CHANGE_PRICE_ENTRY + 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_price_change_type)],
                ADMIN_SUPPORT_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_support_messages)],
                ADMIN_REPLY_SUPPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, reply_support_handler)],
                ADMIN_MANAGE_TASKS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manage_tasks)],
                ADD_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_handler)],
                ADD_TASK_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_description_handler)],
                ADD_TASK_POINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_points_handler)],
                ADD_MANAGER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_manager_handler)],
                ADMIN_GIVE_POINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_give_points)],
                ADMIN_GIVE_POINTS_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_points_user_handler)],
                ADMIN_GIVE_POINTS_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_points_amount_handler)],
                ADMIN_GIVE_MONEY_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_money_user_handler)],
                ADMIN_GIVE_MONEY_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, give_money_amount_handler)],
                
                # حالات جديدة - التوكنات والنسخ الاحتياطي والكوبونات
                ADMIN_TOKENS_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tokens_menu)],
                ADD_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_token_handler)],
                REMOVE_TOKEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_token_handler)],
                EDIT_PROMPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_prompt_handler)],
                ADMIN_BACKUP_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_backup_menu)],
                IMPORT_DB: [
                    MessageHandler(filters.ATTACHMENT, استيراد_قاعدة_البيانات_handler),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, cancel_import_db)
                ],
                SET_BACKUP_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_backup_time_handler)],
                CHANGE_AD_REWARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_ad_reward_handler)],
                ADD_USER_MANUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_user_manual_id_handler)],
                ADD_USER_MANUAL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_user_manual_name_handler)],
                ADD_USER_MANUAL_STAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_user_manual_stage_handler)],
                COUPON_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_coupon_menu)],
                GENERATE_COUPON: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_coupon_type_handler)],
                GENERATE_COUPON_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, generate_coupon_value_handler)],
                USE_COUPON: [MessageHandler(filters.TEXT & ~filters.COMMAND, use_coupon_handler)],
                
                # حالات إعدادات التواصل
                ADMIN_CONTACT_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_contact_settings)],
                SET_CONTACT_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_contact_email_handler)],
                SET_CONTACT_INSTAGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_contact_instagram_handler)],
            },
            fallbacks=[
                CommandHandler('cancel', cancel),
                CommandHandler('start', start),
                CommandHandler('skip', skip_referral)
            ]
        )
        
        app.add_handler(conv_handler)
        
        # إضافة معالجات أزرار الإعلان
        app.add_handler(CallbackQueryHandler(handle_ad_start_callback, pattern='^' + AD_START_CALLBACK_DATA + '$'))
        app.add_handler(CallbackQueryHandler(handle_ad_check_callback, pattern='^' + AD_CHECK_CALLBACK_DATA + '$'))

        print("🎓 بوت منهج Ai يعمل الآن!")
        logger.info("📡 بدء استقبال الرسائل (polling)...")
        
        app.run_polling()
        
    except Exception as e:
        print(f"❌ خطأ فادح في تشغيل البوت: {e}")
        logger.error(f"خطأ فادح: {e}", exc_info=True)

if __name__ == "__main__":
    main()
