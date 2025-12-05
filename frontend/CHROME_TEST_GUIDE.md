# Руководство по тестированию в Chrome DevTools

## Быстрая проверка функциональности

### 1. Откройте страницу регистрации
```
http://localhost:3004/register
```

### 2. Откройте Chrome DevTools (F12 или Cmd+Option+I)

### 3. Перейдите на вкладку Console и выполните:

```javascript
// Тест API входа (ваши данные уже зарегистрированы)
fetch('http://localhost:8002/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 's.muratkhan@aues.kz',
    password: 'g@kb$78N'
  })
})
.then(r => r.json())
.then(data => {
  console.log('✅ Вход успешен:', data);
  console.log('Токен:', data.access_token);
  console.log('User ID:', data.user_id);
  console.log('Имя:', data.name);
});
```

### 4. Проверка формы регистрации

В консоли выполните:
```javascript
// Заполнить форму
document.getElementById('regName').value = 'Шынгыс';
document.getElementById('regEmail').value = 's.muratkhan@aues.kz';
document.getElementById('regPassword').value = 'g@kb$78N';

// Проверить, что поля заполнены
console.log('Имя:', document.getElementById('regName').value);
console.log('Email:', document.getElementById('regEmail').value);
console.log('Пароль:', document.getElementById('regPassword').value ? 'заполнен' : 'пусто');
```

### 5. Проверка Network запросов

1. Откройте вкладку **Network** в DevTools
2. Заполните форму регистрации вручную
3. Нажмите "Создать аккаунт"
4. Проверьте запросы:
   - `POST /auth/register` - должен вернуть 201
   - `POST /auth/login` - должен вернуть 200 с токеном

### 6. Проверка localStorage

После успешной регистрации/входа выполните в консоли:
```javascript
// Проверить сохраненные данные
const user = JSON.parse(localStorage.getItem('user') || '{}');
console.log('Сохраненный пользователь:', user);
console.log('Токен:', user.token ? '✅ Сохранен' : '❌ Отсутствует');
console.log('User ID:', user.userId);
```

### 7. Проверка формы входа

1. Перейдите на `http://localhost:3004/`
2. Откройте DevTools → Network
3. Заполните форму:
   - Email: `s.muratkhan@aues.kz`
   - Пароль: `g@kb$78N`
4. Нажмите "Войти"
5. Проверьте:
   - Запрос `POST /auth/login` в Network
   - Токен в localStorage
   - Редирект на `/dashboard`

## Автоматический тест в консоли

Скопируйте и выполните весь код из `test-auth-console.js` в консоли браузера, затем выполните:
```javascript
runAllTests()
```

## Что должно работать:

✅ Форма регистрации с полем "Имя"  
✅ API запрос к `/auth/register`  
✅ Автоматический вход после регистрации  
✅ Сохранение токена в localStorage  
✅ Форма входа с API запросом  
✅ Получение и сохранение токена при входе  

## Проверка ошибок:

Если что-то не работает, проверьте:
1. Backend запущен на `http://localhost:8002`
2. Frontend запущен на `http://localhost:3004`
3. CORS настроен правильно
4. В консоли нет ошибок JavaScript
5. В Network tab нет ошибок 404/500

