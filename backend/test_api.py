"""
Скрипт для тестирования всех API эндпоинтов и CRUD операций
"""
import requests
import json
import uuid
from typing import Optional

BASE_URL = "http://localhost:8002"

def print_response(title: str, response: requests.Response):
    """Печатает ответ в удобном формате"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print()

def test_health():
    """Тест health check"""
    print("🔍 Тест 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    assert response.status_code == 200, "Health check failed"
    return True

def test_root():
    """Тест корневого эндпоинта"""
    print("🔍 Тест 2: Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print_response("Root", response)
    assert response.status_code == 200, "Root endpoint failed"
    return True

def test_create_ticket() -> Optional[str]:
    """Тест создания тикета (CREATE)"""
    print("🔍 Тест 3: CREATE Ticket")
    
    # Сначала нужно создать пользователя или использовать существующий UUID
    test_user_id = str(uuid.uuid4())
    
    payload = {
        "source": "email",
        "user_id": test_user_id,
        "subject": "Тестовая заявка",
        "body": "Не могу войти в систему. Проблема с паролем.",
        "language": "ru"
    }
    
    response = requests.post(
        f"{BASE_URL}/tickets/create",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print_response("CREATE Ticket", response)
    
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        ticket_id = data.get("id")
        print(f"✅ Тикет создан с ID: {ticket_id}")
        return ticket_id
    else:
        print(f"❌ Ошибка создания тикета: {response.status_code}")
        return None

def test_get_ticket(ticket_id: str):
    """Тест получения тикета (READ)"""
    print(f"🔍 Тест 4: READ Ticket (GET /tickets/{ticket_id})")
    
    response = requests.get(f"{BASE_URL}/tickets/{ticket_id}")
    print_response(f"GET Ticket {ticket_id}", response)
    
    assert response.status_code == 200, f"Failed to get ticket {ticket_id}"
    data = response.json()
    assert data.get("id") == ticket_id, "Ticket ID mismatch"
    print(f"✅ Тикет получен успешно")
    return True

def test_list_tickets():
    """Тест получения списка тикетов (READ ALL)"""
    print("🔍 Тест 5: READ All Tickets (GET /tickets)")
    
    response = requests.get(f"{BASE_URL}/tickets?skip=0&limit=10")
    print_response("GET Tickets List", response)
    
    assert response.status_code == 200, "Failed to get tickets list"
    data = response.json()
    assert isinstance(data, list), "Response should be a list"
    print(f"✅ Получено тикетов: {len(data)}")
    return True

def test_update_ticket(ticket_id: str):
    """Тест обновления тикета (UPDATE)"""
    print(f"🔍 Тест 6: UPDATE Ticket (PUT /tickets/{ticket_id})")
    
    payload = {
        "status": "in_work",
        "priority": "high"
    }
    
    response = requests.put(
        f"{BASE_URL}/tickets/{ticket_id}",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print_response(f"UPDATE Ticket {ticket_id}", response)
    
    assert response.status_code == 200, f"Failed to update ticket {ticket_id}"
    data = response.json()
    assert data.get("status") == "in_work", "Status not updated"
    assert data.get("priority") == "high", "Priority not updated"
    print(f"✅ Тикет обновлен успешно")
    return True

def test_delete_ticket(ticket_id: str):
    """Тест удаления тикета (DELETE)"""
    print(f"🔍 Тест 7: DELETE Ticket (DELETE /tickets/{ticket_id})")
    
    response = requests.delete(f"{BASE_URL}/tickets/{ticket_id}")
    print_response(f"DELETE Ticket {ticket_id}", response)
    
    # DELETE может вернуть 204 (No Content) или 200
    if response.status_code in [200, 204]:
        print(f"✅ Тикет удален успешно")
        return True
    elif response.status_code == 404:
        print(f"⚠️ Тикет не найден (возможно уже удален)")
        return True
    else:
        print(f"❌ Ошибка удаления: {response.status_code}")
        return False

def test_get_nonexistent_ticket():
    """Тест получения несуществующего тикета"""
    print("🔍 Тест 8: GET Non-existent Ticket (404 test)")
    
    fake_id = str(uuid.uuid4())
    response = requests.get(f"{BASE_URL}/tickets/{fake_id}")
    
    print_response(f"GET Non-existent Ticket {fake_id}", response)
    
    assert response.status_code == 404, "Should return 404 for non-existent ticket"
    print(f"✅ Корректно обработан несуществующий тикет")
    return True

def test_filter_tickets():
    """Тест фильтрации тикетов"""
    print("🔍 Тест 9: Filter Tickets by Status")
    
    response = requests.get(f"{BASE_URL}/tickets?status=new&limit=5")
    print_response("Filter Tickets (status=new)", response)
    
    assert response.status_code == 200, "Failed to filter tickets"
    data = response.json()
    print(f"✅ Получено тикетов со статусом 'new': {len(data)}")
    return True

def main():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ API И CRUD ОПЕРАЦИЙ")
    print("="*60 + "\n")
    
    results = []
    ticket_id = None
    
    try:
        # Базовые тесты
        results.append(("Health Check", test_health()))
        results.append(("Root Endpoint", test_root()))
        
        # CRUD операции
        ticket_id = test_create_ticket()
        if ticket_id:
            results.append(("CREATE Ticket", True))
            
            results.append(("READ Ticket", test_get_ticket(ticket_id)))
            results.append(("READ All Tickets", test_list_tickets()))
            results.append(("UPDATE Ticket", test_update_ticket(ticket_id)))
            
            # DELETE тест (в конце, чтобы не мешать другим тестам)
            # results.append(("DELETE Ticket", test_delete_ticket(ticket_id)))
        else:
            results.append(("CREATE Ticket", False))
        
        # Дополнительные тесты
        results.append(("GET Non-existent Ticket", test_get_nonexistent_ticket()))
        results.append(("Filter Tickets", test_filter_tickets()))
        
    except Exception as e:
        print(f"\n❌ ОШИБКА при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()
    
    # Итоги
    print("\n" + "="*60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n✅ Пройдено: {passed}/{total}")
    print(f"{'='*60}\n")
    
    if ticket_id:
        print(f"💡 Созданный тикет для тестирования: {ticket_id}")
        print(f"   Проверьте вручную: GET {BASE_URL}/tickets/{ticket_id}\n")

if __name__ == "__main__":
    main()

