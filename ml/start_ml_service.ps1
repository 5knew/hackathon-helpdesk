# Скрипт для запуска ML сервиса после завершения обучения моделей
Write-Host "Ожидание завершения обучения моделей..." -ForegroundColor Yellow

$modelsPath = "C:\Users\Anubis\Desktop\hackathon-helpdesk\ml\models"
$requiredModels = @(
    "classifier_category.pkl",
    "classifier_priority.pkl", 
    "classifier_problem_type.pkl"
)

$maxWait = 1800 # 30 минут максимум
$elapsed = 0
$checkInterval = 10 # проверка каждые 10 секунд

while ($elapsed -lt $maxWait) {
    if (Test-Path $modelsPath) {
        $allModelsExist = $true
        foreach ($model in $requiredModels) {
            if (-not (Test-Path (Join-Path $modelsPath $model))) {
                $allModelsExist = $false
                break
            }
        }
        
        if ($allModelsExist) {
            Write-Host "`n✅ Все модели найдены! Запуск ML сервиса..." -ForegroundColor Green
            Set-Location "C:\Users\Anubis\Desktop\hackathon-helpdesk\ml"
            python api.py
            break
        }
    }
    
    Write-Host "." -NoNewline -ForegroundColor Gray
    Start-Sleep -Seconds $checkInterval
    $elapsed += $checkInterval
}

if ($elapsed -ge $maxWait) {
    Write-Host "`n⚠️  Превышено время ожидания. Модели не найдены." -ForegroundColor Red
}

