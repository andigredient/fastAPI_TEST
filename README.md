Результаты тестирования можно увидеть на скриншотах (в корне)

## Покрытие кода: 94%
![Coverage Report](coverage.png)

## API тесты:
![API](api_tests.png)

## locust
![locust](locust_result.png)
![locust2](locust_result2.png)


## Порядок проверки:
- psql -U postgres -c "CREATE DATABASE test_db;"
- pytest tests/ --cov=app --cov-report=html
- start htmlcov/index.html
- locust -f locustfile.py --host=http://localhost:8000