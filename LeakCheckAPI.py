import os
import configparser
from leakcheck import LeakCheckAPI
from colorama import init, Fore, Style
import readline
import re
import socket
import requests

# Inicializar colorama para el soporte de colores en la consola
init()

# Ruta del archivo de configuración
config_file = "config.ini"

# Crear archivo de configuración si no existe
if not os.path.isfile(config_file):
    config = configparser.ConfigParser()
    config.add_section("API")
    config.set("API", "key", "")
    with open(config_file, "w") as file:
        config.write(file)

# Leer la API KEY del archivo de configuración
config = configparser.ConfigParser()
config.read(config_file)
api_key = config.get("API", "key")

# Verificar si la API KEY no está configurada
if not api_key:
    api_key = input(f"{Fore.BLUE}Ingrese la API KEY: {Style.RESET_ALL}")

    # Almacenar la API KEY en el archivo de configuración
    config.set("API", "key", api_key)
    with open(config_file, "w") as file:
        config.write(file)


# Mostrar el banner
print(r"""
                                                                                                             
88                                  88          ,ad8888ba,   88                                   88         
88                                  88         d8"'    `"8b  88                                   88         
88                                  88        d8'            88                                    88         
88           ,adPPYba,  ,adPPYYba,  88   ,d8  88             88,dPPYba,    ,adPPYba,   ,adPPYba,  88   ,d8   
88          a8P_____88  ""     `Y8  88 ,a8"   88             88P'    "8a  a8P_____88  a8"     ""  88 ,a8"    
88          8PP"""""""  ,adPPPPP88  8888[     Y8,            88       88  8PP"""""""  8b          8888[      
88          "8b,   ,aa  88,    ,88  88`"Yba,   Y8a.    .a8P  88       88  "8b,   ,aa  "8a,   ,aa  88`"Yba,   
88888888888  `"Ybbd8"'  `"8bbdP"Y8  88   `Y8a   `"Y8888Y"'   88       88   `"Ybbd8"'   `"Ybbd8"'  88   `Y8a  
                                                                                                             
                                                                                                               
""")

# Bucle principal
while True:
    try:
        # Inicializar API
        api = LeakCheckAPI()

        # Configurar clave de API
        api.set_key(api_key)

        # Solicitar correo al usuario utilizando readline
        correo = input(f"{Fore.BLUE}Ingrese el correo que desea consultar (o 'q' para salir): {Style.RESET_ALL}")

        # Verificar si se desea salir
        if correo.lower() == "q":
            break

        # Verificar si el correo ingresado es válido
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            print(f"{Fore.LIGHTYELLOW_EX}La dirección de correo electrónico ingresada no es válida.{Style.RESET_ALL}")
            continue

        # Realizar la solicitud utilizando el correo ingresado
        result = api.lookup(correo)  # lista de diccionarios

        # Verificar si hay coincidencias
        if result:
            print(Fore.GREEN + "¡Estás de suerte! Se encontraron coincidencias:" + Style.RESET_ALL)
            print(f"Total de coincidencias: {len(result)}")
            print("-" * 30)  # Línea separadora

            # Mostrar los resultados obtenidos
            for r in result:
                print(Fore.BLUE + "Fuentes:" + Style.RESET_ALL, ", ".join(r["sources"]))
                print(Fore.BLUE + "Email:" + Style.RESET_ALL, r["line"])

                # Separar campo de contraseña si hay ":" en el mensaje
                if ":" in r["line"]:
                    correo, _, contrasena = r["line"].partition(":")
                    print(Fore.BLUE + "Correo:" + Style.RESET_ALL, correo)
                    print(Fore.BLUE + "Contraseña:" + Style.RESET_ALL, contrasena)

                # Mostrar "sin datos" si el campo "Última violación" está vacío
                if r["last_breach"]:
                    print(Fore.BLUE + "Última violación:" + Style.RESET_ALL, r["last_breach"])
                else:
                    print(Fore.BLUE + "Última violación:" + Style.RESET_ALL, "Sin datos")

                print("-" * 30)  # Línea separadora

        else:
            print("No se encontraron coincidencias para el correo ingresado.")

    except AssertionError as e:
        error_msg = str(e)
        if error_msg == "IP linking is required":
            try:
                response = requests.get("https://api.ipify.org")
                ip_address = response.text
            except requests.exceptions.RequestException:
                ip_address = "desconocida"
            error_msg = f"{Fore.LIGHTYELLOW_EX}{error_msg}{Style.RESET_ALL}"
            error_msg += f" - Debes autorizar tu dirección IP pública ({ip_address}) en la configuración de la API."
        print("\n" + error_msg)
        with open("error_logs.txt", "a") as file:
            file.write(error_msg + "\n")

    except ValueError as e:
        error_msg = str(e)
        print("\n" + f"{Fore.LIGHTYELLOW_EX}{error_msg}{Style.RESET_ALL}")
        with open("error_logs.txt", "a") as file:
            file.write(error_msg + "\n")

    except Exception as e:
        error_msg = "Ocurrió un error inesperado: " + str(e)
        print("\n" + error_msg)
        with open("error_logs.txt", "a") as file:
            file.write(error_msg + "\n")
