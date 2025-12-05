// Скрипт для тестирования регистрации и входа через консоль Chrome DevTools
// Откройте http://localhost:3004/register в браузере и выполните этот код в консоли

async function testRegistration() {
  console.log('🧪 Тестирование регистрации...');
  
  const testData = {
    email: 's.muratkhan@aues.kz',
    password: 'g@kb$78N',
    name: 'Шынгыс',
    role: 'client'
  };

  try {
    const response = await fetch('http://localhost:8002/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testData)
    });

    const data = await response.json();
    console.log('✅ Регистрация:', response.status, data);
    return data;
  } catch (error) {
    console.error('❌ Ошибка регистрации:', error);
    return null;
  }
}

async function testLogin() {
  console.log('🧪 Тестирование входа...');
  
  const loginData = {
    email: 's.muratkhan@aues.kz',
    password: 'g@kb$78N'
  };

  try {
    const response = await fetch('http://localhost:8002/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(loginData)
    });

    const data = await response.json();
    console.log('✅ Вход:', response.status, data);
    
    if (data.access_token) {
      console.log('✅ Токен получен:', data.access_token.substring(0, 20) + '...');
      console.log('✅ User ID:', data.user_id);
      console.log('✅ Имя:', data.name);
      console.log('✅ Роль:', data.role);
    }
    
    return data;
  } catch (error) {
    console.error('❌ Ошибка входа:', error);
    return null;
  }
}

async function testFormRegistration() {
  console.log('🧪 Тестирование формы регистрации...');
  
  // Находим поля формы
  const nameInput = document.getElementById('regName');
  const emailInput = document.getElementById('regEmail');
  const passwordInput = document.getElementById('regPassword');
  const submitButton = document.querySelector('button.primary');
  
  if (!nameInput || !emailInput || !passwordInput) {
    console.error('❌ Форма не найдена');
    return;
  }
  
  console.log('✅ Форма найдена');
  
  // Заполняем форму
  nameInput.value = 'Шынгыс';
  emailInput.value = 's.muratkhan@aues.kz';
  passwordInput.value = 'g@kb$78N';
  
  // Триггерим события изменения
  nameInput.dispatchEvent(new Event('input', { bubbles: true }));
  emailInput.dispatchEvent(new Event('input', { bubbles: true }));
  passwordInput.dispatchEvent(new Event('input', { bubbles: true }));
  
  console.log('✅ Форма заполнена');
  console.log('📝 Нажмите кнопку "Создать аккаунт" или выполните: submitButton.click()');
  
  return { nameInput, emailInput, passwordInput, submitButton };
}

// Запуск всех тестов
async function runAllTests() {
  console.log('🚀 Запуск всех тестов...\n');
  
  // Тест 1: API регистрации
  await testRegistration();
  console.log('\n');
  
  // Тест 2: API входа
  await testLogin();
  console.log('\n');
  
  // Тест 3: Форма регистрации
  await testFormRegistration();
  
  console.log('\n✅ Все тесты завершены!');
}

// Экспорт функций для использования в консоли
window.testRegistration = testRegistration;
window.testLogin = testLogin;
window.testFormRegistration = testFormRegistration;
window.runAllTests = runAllTests;

console.log('📋 Тестовые функции загружены:');
console.log('  - testRegistration() - тест API регистрации');
console.log('  - testLogin() - тест API входа');
console.log('  - testFormRegistration() - тест формы регистрации');
console.log('  - runAllTests() - запуск всех тестов');

