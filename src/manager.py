# Основная логика
# делаем вывод через логер
# начинаем смотреть конфиг + проверяем его целостность
# подгружаем локализацию
# подключаемся к базе данных
# запускаем основные компоненты
# запускаем асинхронные функцию работающие в отдельном потоке
# ...


# Делаем 2FA
# import time 
# import pyotp 
# import qrcode 
  
# from src.config import config

# key = config.SECRET_KEY
  
# uri = pyotp.totp.TOTP(key).provisioning_uri( 
#     name='Dwaipayan_Bandyopadhyay', 
#     issuer_name='GeeksforGeeks') 
  
# print(uri) 
  
  
# qrcode.make(uri).save("qr.png") 
    
# totp = pyotp.TOTP(key) 
  
# while True: 
#   print(totp.verify(input(("Enter the Code : "))))
