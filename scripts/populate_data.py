#!/usr/bin/env python3
"""
Script to populate the CRM database with initial data
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid
from datetime import datetime, timezone, date

# Load environment
ROOT_DIR = Path(__file__).parent.parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def create_status_types():
    """Create default client status types"""
    status_types = [
        {"id": str(uuid.uuid4()), "name": "ВІП (працюємо)", "color": "#22C55E", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Потенційні ВІП", "color": "#3B82F6", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "амбасадор", "color": "#8B5CF6", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "ВІП (перемовини)", "color": "#F59E0B", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "ВІП (працюємо з 1 листопада)", "color": "#10B981", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Потенційні ВІП (як тільки повернуть нас на полиці)", "color": "#6366F1", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Потенційні ВІП (ігнорує)", "color": "#EF4444", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Відміна по ВІП", "color": "#DC2626", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Відміна (інтернет магазин)", "color": "#991B1B", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "Відміна ВІП", "color": "#7F1D1D", "created_at": datetime.now(timezone.utc).isoformat()},
        {"id": str(uuid.uuid4()), "name": "амбасадор перевірити", "color": "#A855F7", "created_at": datetime.now(timezone.utc).isoformat()},
    ]
    
    # Clear existing status types
    await db.client_status_types.delete_many({})
    
    # Insert new status types
    await db.client_status_types.insert_many(status_types)
    print(f"Created {len(status_types)} status types")

async def create_clients():
    """Create clients from the provided list"""
    clients_data = [
        # ВІП (працюємо)
        ("Шурма", "Олена", "0 67 361 07 89", "ВІП (працюємо)"),
        ("Капанжи", "Андрій", "0 68 583 43 98", "ВІП (працюємо)"),
        ("Лучка", "Роман", "", "ВІП (працюємо)"),
        ("Тимощук", "Назар", "", "ВІП (працюємо)"),
        ("Дунас", "Олег", "", "ВІП (працюємо)"),
        ("Слободянюк", "Юрій", "", "ВІП (працюємо)"),
        
        # ВІП (працюємо з 1 листопада)
        ("Палейчук", "Владислав", "", "ВІП (працюємо з 1 листопада)"),
        
        # Потенційні ВІП
        ("UVAPE", "", "", "Потенційні ВІП"),
        ("Коваль", "Дмитро", "", "Потенційні ВІП"),
        ("Відершпан", "Алекс", "", "Потенційні ВІП"),
        ("Маладика", "Давид", "", "Потенційні ВІП"),
        ("Пилипенко", "Сергій", "", "Потенційні ВІП"),
        ("Олефиренко", "Антон", "", "Потенційні ВІП"),
        ("Мокрецов", "Станіслав", "", "Потенційні ВІП"),
        ("Мирошніченко", "Андрій", "", "Потенційні ВІП"),
        ("Манько", "Сергій", "", "Потенційні ВІП"),
        ("Пилипенко", "Ярослав", "", "Потенційні ВІП"),
        
        # ВІП (перемовини)
        ("Лесюк", "Антон", "", "ВІП (перемовини)"),
        ("Антонов", "Іван", "", "ВІП (перемовини)"),
        ("Чебаков", "Сергій", "", "ВІП (перемовини)"),
        ("Романів", "Євген", "", "ВІП (перемовини)"),
        ("Барабанський", "Максим", "", "ВІП (перемовини)"),
        ("Плотніков", "Артур", "", "ВІП (перемовини)"),
        ("Чеховський", "Владислав", "", "ВІП (перемовини)"),
        ("Васьків", "Остап", "", "ВІП (перемовини)"),
        ("Радецький", "Ілля", "", "ВІП (перемовини)"),
        
        # амбасадор
        ("Смислов", "Даніїл", "", "амбасадор"),
        ("Антонюк", "Олег Олегович", "", "амбасадор"),
        ("Бабаян", "Іван Іванович", "", "амбасадор"),
        ("Смоляк", "Василь Іванович", "", "амбасадор"),
        ("Ишалин", "Андрей", "", "амбасадор"),
        ("Кармазін", "Станіслав Володимирович", "", "амбасадор"),
        ("Лебедева", "Юлія Олександрівна", "", "амбасадор"),
        ("Лисенко", "Наталія", "", "амбасадор"),
        ("Морзе", "Олександр", "", "амбасадор"),
        ("Покидченко", "Юрій", "", "амбасадор"),
        ("През", "Владислав Володимирович", "", "амбасадор"),
        ("Пуценко", "Ольга", "", "амбасадор"),
        ("Ризнык", "Александр", "", "амбасадор"),
        ("Савчук", "Павел", "", "амбасадор"),
        ("Бурмака", "Назар Олександрович", "", "амбасадор"),
        ("Кудояр", "Денис", "", "амбасадор"),
        ("Олефиренко", "Антон Володимирович", "", "амбасадор"),
        ("Плебанська", "Діана", "", "амбасадор"),
        ("Романив", "Сергей", "", "амбасадор"),
        ("Саакян", "Едгар Ерикович", "", "амбасадор"),
        ("Свинаренко", "Анастасія", "", "амбасадор"),
        ("Словицкий", "Вадим", "", "амбасадор"),
        ("Сугоняко", "Микола Андрійович", "", "амбасадор"),
        ("Хоптин", "Артем", "", "амбасадор"),
        ("Черкашин", "Максим", "", "амбасадор"),
        ("Юркив", "Ярослав", "", "амбасадор"),
        ("Барабановський", "Максим Юрійович", "", "амбасадор"),
        ("Булик", "Богдан", "", "амбасадор"),
        ("Висоцкий", "Сергей", "", "амбасадор"),
        ("Висоцький", "Володимир Іванович", "", "амбасадор"),
        ("Сівоха", "Владислав Святославович", "", "амбасадор"),
        ("Черкун", "Роман Васильович", "", "амбасадор"),
        ("Солдатенко", "Георгій Даніїл Вячеславович", "", "амбасадор"),
        ("Дудка", "Георгій Артур Анатолійович", "", "амбасадор"),
        ("Галушко", "Тарас Денис", "", "амбасадор"),
        ("Жосан", "Тарас Евгений", "", "амбасадор"),
        ("Котова", "Тарас Ірина", "", "амбасадор"),
        ("Покидченко", "Тарас Вадим", "", "амбасадор"),
        ("Болотян", "Даша Юрій", "", "амбасадор"),
        ("Турчин", "Даша Олег Станіславович", "", "амбасадор"),
        ("Шейко", "Даша Олексій Ігорович", "", "амбасадор"),
        
        # амбасадор перевірити
        ("Фадеев", "Андрей", "", "амбасадор перевірити"),
        ("Табунщик", "Альона Ігорівна", "", "амбасадор перевірити"),
        
        # Потенційні ВІП (як тільки повернуть нас на полиці)
        ("Слива", "Богдан", "", "Потенційні ВІП (як тільки повернуть нас на полиці)"),
        
        # Потенційні ВІП (ігнорує)
        ("Булик", "Богдан", "", "Потенційні ВІП (ігнорує)"),
        ("Лобасенко", "Роман", "", "Потенційні ВІП (ігнорує)"),
        ("Злобін", "Владислав", "", "Потенційні ВІП (ігнорує)"),
        ("Хоптин", "Артем", "", "Потенційні ВІП (ігнорує)"),
        ("Кушнір", "Роман", "", "Потенційні ВІП (ігнорує)"),
        ("Бабаян", "Іван", "", "Потенційні ВІП (ігнорує)"),
        
        # Відміна по ВІП
        ("Бірук", "Дмитро", "", "Відміна по ВІП"),
        ("Зуев", "Андрій", "", "Відміна по ВІП"),
        ("Солоніна", "Іван", "", "Відміна по ВІП"),
        ("Шейко", "Олексій", "", "Відміна по ВІП"),
        ("Лекомцев", "Дмитро", "", "Відміна по ВІП"),
        ("Богатов", "Андрій", "", "Відміна по ВІП"),
        ("Пугач", "Євген", "", "Відміна по ВІП"),
        ("Черкашин", "Максим", "", "Відміна по ВІП"),
        ("Гаврилюк", "Роман", "", "Відміна по ВІП"),
        
        # Відміна (інтернет магазин)
        ("Василенко", "Василь", "", "Відміна (інтернет магазин)"),
        
        # Відміна ВІП
        ("Клауд", "Кастл", "", "Відміна ВІП"),
        
        # Інші
        ("Сивак", "Богдан", "", "ВІП (працюємо)"),
    ]
    
    clients = []
    for first_name, last_name, phone, status in clients_data:
        client = {
            "id": str(uuid.uuid4()),
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "client_status": status,
            "crm_link": "",
            "expected_order_sets": 0,
            "expected_order_amount": 0.0,
            "sets_ordered_this_month": 0,
            "amount_this_month": 0.0,
            "debt": 0.0,
            "last_contact_date": None,
            "task_description": "",
            "comment": "",
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
        clients.append(client)
    
    # Clear existing clients
    await db.clients.delete_many({})
    
    # Insert new clients
    await db.clients.insert_many(clients)
    print(f"Created {len(clients)} clients")

async def main():
    """Main function to populate database"""
    print("Populating CRM database...")
    
    try:
        await create_status_types()
        await create_clients()
        print("Database population completed successfully!")
    except Exception as e:
        print(f"Error populating database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())