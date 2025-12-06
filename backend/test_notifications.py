"""
Тест создания уведомлений
"""
from sqlalchemy.orm import sessionmaker
from database import engine
from models.user import User, UserRole
from models.notification import Notification, NotificationType
from models.ticket import Ticket
from uuid import uuid4

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("Testing notifications system...")
    
    # Получаем админа
    admin = db.query(User).filter(User.role == UserRole.ADMIN.value).first()
    if not admin:
        print("ERROR: No admin found!")
        exit(1)
    
    print(f"Admin found: {admin.email} (ID: {admin.id})")
    
    # Получаем последний тикет
    last_ticket = db.query(Ticket).order_by(Ticket.created_at.desc()).first()
    
    if last_ticket:
        print(f"Last ticket: {last_ticket.id}")
        
        # Проверяем уведомления для этого тикета
        notifications = db.query(Notification).filter(
            Notification.ticket_id == last_ticket.id
        ).all()
        
        print(f"Notifications for this ticket: {len(notifications)}")
        for notif in notifications:
            print(f"  - {notif.notification_type.value}: {notif.title}")
    else:
        print("No tickets found")
    
    # Проверяем все уведомления админа
    admin_notifications = db.query(Notification).filter(
        Notification.user_id == admin.id
    ).all()
    
    print(f"\nTotal notifications for admin: {len(admin_notifications)}")
    for notif in admin_notifications[:5]:  # Показываем первые 5
        print(f"  - [{notif.notification_type.value}] {notif.title} (read: {notif.is_read})")
    
    print("\n[OK] Test completed!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()


