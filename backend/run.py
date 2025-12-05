"""
Скрипт для запуска Backend API сервера
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,  # Backend на порту 8002, ML сервис на 8000
        reload=True
    )

