# Активация виртуального окружения

## Windows (PowerShell)

```powershell
cd ml
.\venv\Scripts\Activate.ps1
```

Если возникает ошибка выполнения скриптов, выполните:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Windows (Command Prompt)

```cmd
cd ml
venv\Scripts\activate.bat
```

## Linux/Mac

```bash
cd ml
source venv/bin/activate
```

## Проверка активации

После активации в начале строки терминала должно появиться `(venv)`:

```
(venv) PS C:\Users\...\ml>
```

## Деактивация

Просто введите:
```bash
deactivate
```

## Установка зависимостей (если нужно переустановить)

```bash
pip install -r requirements.txt
```

