"""Скрипт для проверки загруженных эндпоинтов"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from main import app
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    print(f"Всего эндпоинтов: {len(routes)}")
    print(f"Эндпоинты для тикетов: {len([r for r in routes if 'ticket' in r.lower()])}")
    ticket_routes = [r for r in routes if 'ticket' in r.lower()]
    print("Эндпоинты тикетов:")
    for route in sorted(ticket_routes):
        print(f"  - {route}")
    
    if '/tickets' in routes:
        print("\n✅ Эндпоинт /tickets найден!")
    else:
        print("\n❌ Эндпоинт /tickets НЕ найден!")
        
except Exception as e:
    import traceback
    print(f"ОШИБКА при загрузке: {e}")
    traceback.print_exc()

