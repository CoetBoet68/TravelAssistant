# TravelAssistant

### Setup Guide
- **Install Django** 
  - 5.1.2
- **Install Postgress**
  - 16.4
  - [Download](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
- **Activate Virtual Environment**
  - `travel_space\Scripts\activate.bat`
  - add the Virtual Environment as Interpreter on your IDE
  - [Guide](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html)
- Add .env file
  - Add all the necessary secrets (request on WhatsApp group)
  - Make sure it is in your .gitignore file
- **Run Application**
  - Navigate to Project Directory
  - `python manage.py runserver`

### Development tips
To remove vitrual environment use `deactivate` in Terminal <br>
To apply migrations: 
```python
python manage.py makemigrations travelapis
python manage.py migrate travelapis
#Check models afterwards
python manage.py inspectdb > models.py
```

