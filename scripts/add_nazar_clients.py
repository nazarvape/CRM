#!/usr/bin/env python3
"""
Script to add clients for Nazar (nazarvape@gmail.com)
"""
import asyncio
import sys
import os
from pathlib import Path
import re
from datetime import datetime, timezone

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid

# Load environment
ROOT_DIR = Path(__file__).parent.parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Client data from the provided list
clients_data = [
    "ВІП (працюємо) Шурма Олена (Гарікоф) 0 67 361 07 89",
    "ВІП (працюємо) Капанжи Андрій 0 68 583 43 98",
    "ВІП (працюємо) Лучка Роман",
    "ВІП (працюємо) Тимощук Назар",
    "ВІП (працюємо) Дунас Олег 29.09.2025",
    "ВІП (працюємо) Слободянюк Юрій",
    "ВІП (працюємо з 1 листопада) Палейчук Владислав",
    "Богдан Сивак передати собі",
    "Потенційні ВІП UVAPE 01.10.2025 перегладяє пропозицію",
    "ВІП (перемовини) Лесюк Антон 01.09.2025 перегладяє пропозицію",
    "амбасадор Смислов Даніїл",
    "амбасадор Антонюк Олег Олегович",
    "амбасадор Бабаян Іван Іванович",
    "амбасадор Василь Смоляк Іванович",
    "амбасадор Ишалин Андрей",
    "амбасадор Кармазін Станіслав Володимирович",
    "амбасадор Лебедева Юлія Олександрівна",
    "амбасадор Лисенко Наталія",
    "амбасадор Олександр Морзе",
    "амбасадор Покидченко Юрій окремий",
    "амбасадор През Владислав Володимирович",
    "амбасадор Пуценко Ольга + Земляченко",
    "амбасадор Ризнык Александр",
    "амбасадор Савчук Павел",
    "амбасадор Бурмака Назар Олександрович",
    "амбасадор Кудояр Денис - дзвони у тг",
    "амбасадор Олефиренко Антон Володимирович",
    "амбасадор Плебанська Діана Львов Старт Ап",
    "амбасадор Романив Сергей Калуш",
    "амбасадор Саакян Едгар Ерикович",
    "амбасадор Свинаренко Анастасія",
    "амбасадор Словицкий Вадим",
    "амбасадор Сугоняко Микола Андрійович",
    "амбасадор Хоптин Артем",
    "амбасадор Черкашин Максим",
    "амбасадор Юркив Ярослав",
    "амбасадор Барабановський Максим Юрійович",
    "амбасадор Булик Богдан",
    "амбасадор Висоцкий Сергей",
    "амбасадор Висоцький Володимир Іванович",
    "амбасадор Сівоха Владислав Святославович",
    "амбасадор Черкун Роман Васильович",
    "Потенційні ВІП (як тільки повернуть нас на полиці) Слива Богдан (Вандал)",
    "ВІП (перемовини) Антонов Іван 30.09.2025",
    "ВІП (пермовини) Чебаков Сергій 30.09.2025",
    "ВІП (пермовини) Романів Євген + Філімонов 29.09.2025 Зв'яжеться коли зможемо поспілкуватись",
    "ВІП (перемовини) Барабонвський Максим 29.09.2025",
    "ВІП (перемовини) Плотніков Артур 29.09.2025",
    "ВІП (перемовини) Чеховський Владислав 29.09.2025 хоче виключно аромки",
    "ВІП (перемовини) Васьків Остап 29.09.2025 ще чекаємо фітбек",
    "ВІП (перемовини) Радецький Ілля з 1 листопада можливо запустимось",
    "амбасадор Георгій Солдатенко Даніїл Вячеславович",
    "амбасадор Георгій Дудка Артур Анатолійович",
    "амбасадор Тарас Галушко Денис",
    "амбасадор Тарас Жосан Евгений",
    "амбасадор Тарас Котова Ірина Сергей Проценко",
    "амбасадор Тарас Покидченко Вадим (Музыкант)",
    "амбасадор Даша Болотян (Шейко) Юрій",
    "амбасадор Даша Турчин Олег Станіславович",
    "амбасадор Даша Шейко Олексій Ігорович",
    "амбасадор перевірити Фадеев Андрей",
    "амбасадор перевірити Табунщик Альона Ігорівна",
    "Потенційні ВІП (ігнорує) Булик Богдан 27.09.2025",
    "Потенційні ВІП (ігнорує) Лобасенко Роман 27.09.2025",
    "Потенційні ВІП (ігнорує) Злобін Владислав 27.09.2025",
    "Потенційні ВІП (ігнорує) Хоптин Артем 27.09.2025",
    "Потенційні ВІП (ігнорує) Кушнір Роман 27.09.2025",
    "Потенційні ВІП (ігнорує) Бабаян Іван 27.09.2025",
    "Відміна по ВІП Бірук Дмитро Відміна, запускає свою лінійку",
    "Відміна по ВІП Зуев Андрій Відміна по ньому, демпінгує, не хоче вирівнювати ціни",
    "Відміна (інтернет магазин) Василенко Василь Відміна тільки інтернет магазин",
    "Відміна по ВІП Солоніна Іван Відміна тільки інтернет магазин",
    "Відміна по ВІП Шейко Олексій не готовий збільшувати обороти",
    "Відміна по ВІП Лекомцев Дмитро дебіторить часто",
    "Відміна по ВІП Богатов Андрій по ньому відміна, зараз має 2 магазини, судиться за знесення його МАФів, поки не до акцій",
    "Відміна ВІП Клауд Кастл відміна хоче тільки аромки",
    "Відміна по ВІП Пугач Євген",
    "Відміна по ВІП (поки не вирішиться питання з демпінгом) Черкашин Максим",
    "Потенційні ВІП Коваль Дмитро 30.09.2025",
    "Відміна ВІП Гаврилюк Роман 29.09.2025",
    "Потенційні ВІП Відершпан Алекс 29.09.2025",
    "Потенційні ВІП Маладика Давид 29.09.2025",
    "Потенційні ВІП Пилипенко Сергій 29.09.2025",
    "Потенційні ВІП Олефиренко Антон 29.09.2025 передав пропозицію керівництву, чекаю фітбек",
    "Потенційні ВІП Мокрецов Станіслав 29.09.2025",
    "Потенційні ВІП Мирошніченко Андрій 29.09.2025",
    "Потенційні ВІП Манько Сергій 29.09.2025",
    "Потенційний ВІП Пилипенко Ярослав поки на паузі, з Кременчуга"
]

def parse_client_line(line):
    """Parse a client line and extract information"""
    
    # Extract phone numbers (patterns like "0 67 361 07 89" or "067 361 07 89")
    phone_pattern = r'(\d\s\d{2}\s\d{3}\s\d{2}\s\d{2}|\d{3}\s\d{3}\s\d{2}\s\d{2})'
    phone_match = re.search(phone_pattern, line)
    phone = phone_match.group(1).replace(' ', '') if phone_match else ""
    
    # Extract dates (patterns like "29.09.2025")
    date_pattern = r'(\d{2}\.\d{2}\.\d{4})'
    date_match = re.search(date_pattern, line)
    date_str = date_match.group(1) if date_match else ""
    
    # Extract status (everything before the name)
    status_patterns = [
        r'^(ВІП \([^)]+\))',
        r'^(Потенційні ВІП[^a-zA-Zа-яА-Я]*(?:\([^)]+\))?)',
        r'^(амбасадор[^a-zA-Zа-яА-Я]*(?:перевірити)?)',
        r'^(Відміна[^a-zA-Zа-яА-Я]*(?:ВІП|по ВІП|\(інтернет магазин\))?)',
        r'^(Потенційний ВІП)'
    ]
    
    status = "Невизначений"
    name_start = 0
    
    for pattern in status_patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            status = match.group(1).strip()
            name_start = match.end()
            break
    
    # Extract name (everything after status but before phone/date/comments)
    remaining = line[name_start:].strip()
    
    # Remove phone from remaining text
    if phone_match:
        remaining = remaining.replace(phone_match.group(1), '').strip()
    
    # Remove date from remaining text
    if date_match:
        remaining = remaining.replace(date_match.group(1), '').strip()
    
    # Extract name and comment
    name_parts = remaining.split()
    
    # Find where the comment starts (usually after the second name or special markers)
    comment_markers = ['перегладяє', 'передати', 'хоче', 'дзвони', 'чекаємо', 'можливо', 'окремий', 
                      'Відміна', 'демпінгує', 'не готовий', 'дебіторить', 'поки', 'запускає', 
                      'судиться', 'передав', 'з Кременчуга', '+', '(', 'Львов', 'Калуш']
    
    first_name = ""
    last_name = ""
    comment = ""
    
    if name_parts:
        first_name = name_parts[0] if len(name_parts) > 0 else ""
        
        # Find comment start
        comment_start = len(name_parts)
        for i, part in enumerate(name_parts[1:], 1):
            if any(marker in part for marker in comment_markers):
                comment_start = i
                break
        
        # Extract last name (parts between first name and comment)
        if comment_start > 1:
            last_name = ' '.join(name_parts[1:comment_start])
        
        # Extract comment
        if comment_start < len(name_parts):
            comment = ' '.join(name_parts[comment_start:])
    
    # Clean up names
    first_name = re.sub(r'[()]+', '', first_name).strip()
    last_name = re.sub(r'[()]+', '', last_name).strip()
    
    # If no last name but have multiple words, split differently
    if not last_name and len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = name_parts[1]
        if len(name_parts) > 2:
            comment = ' '.join(name_parts[2:]) + ' ' + comment
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'status': status,
        'date': date_str,
        'comment': comment.strip()
    }

async def add_clients_for_nazar():
    """Add all clients for Nazar"""
    
    # Find Nazar's user ID
    nazar_user = await db.users.find_one({'email': 'nazarvape@gmail.com'})
    if not nazar_user:
        print("❌ Nazar user not found!")
        return
    
    nazar_user_id = nazar_user['id']
    print(f"✅ Found Nazar's user ID: {nazar_user_id}")
    
    # Clear existing clients for Nazar
    deleted_count = await db.clients.delete_many({'user_id': nazar_user_id})
    print(f"🗑️  Deleted {deleted_count.deleted_count} existing clients")
    
    # Parse and create clients
    clients_to_add = []
    
    print("\n📋 Parsing clients:")
    for i, line in enumerate(clients_data, 1):
        parsed = parse_client_line(line)
        
        client_data = {
            "id": str(uuid.uuid4()),
            "user_id": nazar_user_id,
            "first_name": parsed['first_name'],
            "last_name": parsed['last_name'],
            "phone": parsed['phone'],
            "client_status": parsed['status'],
            "crm_link": "",
            "expected_order_sets": 0,
            "expected_order_amount": 0.0,
            "sets_ordered_this_month": 0,
            "amount_this_month": 0.0,
            "debt": 0.0,
            "last_contact_date": None,
            "task_description": "",
            "comment": parsed['comment'],
            "action_status": {
                "made_order": False,
                "completed_survey": False,
                "notified_about_promotion": False,
                "has_additional_questions": False,
                "need_callback": False,
                "not_answering": False,
                "planning_order": False
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        clients_to_add.append(client_data)
        
        print(f"  {i:2d}. {parsed['first_name']} {parsed['last_name']} ({parsed['status']}) - {parsed['phone']}")
        if parsed['comment']:
            print(f"      💬 {parsed['comment']}")
    
    # Insert all clients
    if clients_to_add:
        result = await db.clients.insert_many(clients_to_add)
        print(f"\n✅ Successfully added {len(result.inserted_ids)} clients for Nazar!")
        
        # Verify
        total_clients = await db.clients.count_documents({'user_id': nazar_user_id})
        print(f"✅ Total clients for Nazar: {total_clients}")
    else:
        print("❌ No clients to add")

async def main():
    """Main function"""
    print("👥 Adding clients for Nazar (nazarvape@gmail.com)")
    print("=" * 60)
    
    try:
        await add_clients_for_nazar()
        print("\n🎉 All done!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())