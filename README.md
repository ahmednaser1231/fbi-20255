# Discord Bot

بوت ديسكورد متعدد المهام مع نظام نقاط وإدارة.

## المميزات
- نظام نقاط متكامل
- أوامر إدارة (حظر، طرد، ميوت)
- نظام إمبيد مخصص
- حماية متكاملة

## الأوامر المتاحة
- `/points` - عرض نقاطك
- `/addpoints` - إضافة نقاط (للمشرفين فقط)
- `/removepoints` - سحب نقاط (للمشرفين فقط)
- `/leaderboard` - عرض المتصدرين
- `/mute` - إسكات عضو
- `/unmute` - إلغاء إسكات عضو
- `/ban` - حظر عضو
- `/kick` - طرد عضو
- `/clear` - مسح رسائل
- `/createembed` - إنشاء إمبيد
- `/addembedfield` - إضافة حقل للإمبيد

## التثبيت
1. قم بتثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

2. قم بتعديل ملف `.env` وأضف توكن البوت:
```
TOKEN=your_bot_token_here
```

3. شغل البوت:
```bash
python fbi.py
```

## Railway Deployment
1. قم برفع الكود على GitHub
2. قم بإنشاء حساب على Railway
3. قم بربط المشروع مع GitHub
4. أضف متغير البيئة `TOKEN` في إعدادات Railway 