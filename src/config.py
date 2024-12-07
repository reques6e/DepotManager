from dynaconf import Dynaconf

# Пользовательские настройки панели
settings = Dynaconf(
    envvar_prefix="DEPTOMANAGER", 
    settings_files=['config/settings.yaml'], 
)

# Файл конфигурации
config = Dynaconf(
    envvar_prefix="DEPTOMANAGER", 
    settings_files=['config/config.yaml'], 
)
