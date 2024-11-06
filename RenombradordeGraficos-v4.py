import os
import re
from datetime import datetime
import locale
import shutil

# Configuración regional para manejar nombres de meses en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def clean_underscores_in_directory(directory):
    """
    Elimina todos los guiones bajos ('_') de los nombres de los archivos en el directorio especificado.
    """
    for filename in os.listdir(directory):
        new_name = filename.replace("_", " ").strip()  # Reemplaza '_' con espacio
        if new_name != filename:
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))
            print(f"Renombrado: {filename} -> {new_name}")
        else:
            print(f"No se renombró: {filename}")

def parse_date_time(date_time_str):
    """
    Intenta analizar la cadena de fecha y hora en varios formatos y devuelve la fecha y hora formateadas.
    """
    formats = [
        ('%d %B %H hrs', '%Y-%m-%d %H%Mhrs'),         # Ejemplo: 30 julio 05 hrs
        ('%d-%m-%y %H%Mhrs', '%Y-%m-%d %H%Mhrs'),     # Ejemplo: 02-08-24 0300hrs
        ('%d-%m-%y %H%Mhrs', '%Y-%m-%d %H%Mhrs'),     # Ejemplo: 02-08-24 0200hrs
        ('%d-%m-%Y %H%Mhrs', '%Y-%m-%d %H%Mhrs'),     # Ejemplo: 02-08-2024 0200hrs
        ('%d %B %Y %H hrs', '%Y-%m-%d %H%Mhrs'),      # Ejemplo: 02 agosto 2024 05 hrs
        ('%d %B %Y %H hrs', '%Y-%m-%d %H%Mhrs'),      # Ejemplo: 02 agosto 2024 17 hrs
        ('%d-%m-%y %H%Mhrs', '%Y-%m-%d %H%Mhrs'),     # Ejemplo: 02-08-24 0200hrs
        ('%d %B %H hrs', '%Y-%m-%d %H%Mhrs'),         # Ejemplo: 02 agosto 05 hrs
        ('%d %B %H hrs', '%Y-%m-%d %H%Mhrs'),         # Ejemplo: 02 agosto 17 hrs
        ('%d-%m-%y %H%Mhrs', '%Y-%m-%d %H%Mhrs'),     # Ejemplo: 02-08-24 0700hrs
        ('%d %B %Y %H%Mh', '%Y-%m-%d %H%Mhrs'),       # Ejemplo: 02 agosto 2024 0500h
        ('%d %B %Y %H hrs', '%Y-%m-%d %H%Mhrs'),      # Ejemplo: 02 agosto 2024 05 hrs
        ('%d-%m-%Y %H%M hrs', '%Y-%m-%d %H%Mhrs'),    # Ejemplo: 02-08-2024 0100 hrs
        ('%Y-%m-%d %H%Mhrs', '%Y-%m-%d %H%Mhrs'),     # Ejemplo: 2024-08-02 1900hrs
        ('%d-%m-%y %H%M horas', '%Y-%m-%d %H%Mhrs'),  # Ejemplo: 02-08-24 1600 horas
        ('%d-%m-%Y %H%M horas', '%Y-%m-%d %H%Mhrs'),  # Ejemplo: 02-08-2024 1600 horas
        ('%d-%m-%y %H%M hrs', '%Y-%m-%d %H%Mhrs'),    # Ejemplo: 02-08-24 0200 hrs
        ('%d.%m.%Y %H%M horas', '%Y-%m-%d %H%Mhrs'),  # Ejemplo: 02.08.2024 0800 horas
        ('%d %B %Y %H%Mh', '%Y-%m-%d %H%Mhrs'),       # Ejemplo: 02 agosto 2024 0500h
        ('%d %B %Y %H hrs', '%Y-%m-%d %H%Mhrs'),      # Ejemplo: 02 agosto 2024 05 hrs
    ]

    for date_format, output_format in formats:
        try:
            parsed_date_time = datetime.strptime(date_time_str, date_format)
            return parsed_date_time.strftime(output_format)
        except ValueError:
            continue
    return None

def rename_files_in_directory(directory):
    """
    Renombra archivos en el directorio basado en patrones de nombres y luego busca la fecha y hora.
    Si no se encuentra ningún patrón o fecha, conserva el nombre original.
    Mueve archivos sin patrón definido a la carpeta "Revisión manual".
    """
    # Crear la carpeta de revisión manual si no existe
    revision_directory = os.path.join(directory, "Revisión manual")
    if not os.path.exists(revision_directory):
        os.makedirs(revision_directory)

    # Patrones de nombres de archivos
    patterns = {
        "1 Suministro a la RO": "Suministro de crudo de la TMDB a la RO",
        "2 Calidad de punto cercano a la RO": "Calidad de punto cercano a la RO",
        "3 Envío calidad al SNR": "Comportamiento de calidad (Envío al SNR)",
        "4 Calidad exportacion": "Exportación TMDB",
        "5 Retorno crudo RO a TMDB": "Retorno de crudo de la RO a la TMDB",
        "6 Seguimiento de calidad de crudo a RO": "Entrega de crudo a Refinería Olmeca",
        "7 Crudo reposado": "TMDB Crudo reposado",
        "8. Tanques de repaso": "Comportamiento – TV-5009 (repaso)",
        "ACONDICIONAMIENTO": "ACONDICIONAMIENTO DE CRUDO MAYA EN TANQUE",
        "RDI LAB ID INFORME DE LINEAS": "INFORME DIARIO DE LÍNEAS",
        "Escenario de distribución de crudo en tanques": "Escenario de distribución de crudo en tanques"
    }

    total_renamed_files = 0
    total_files_for_revision = 0

    print(f"\nIniciando el proceso de renombrado de archivos en la carpeta: {directory}\n")
    for filename in os.listdir(directory):
        if filename == "Revisión manual":
            # Omitir la carpeta de revisión manual
            continue

        print(f"Procesando archivo: {filename}")
        name, ext = os.path.splitext(filename)

        # Buscar patrón de nombre primero
        new_name = None
        for key in patterns.keys():
            if name.startswith(key):
                new_name = patterns[key]
                break

        # Si no se encuentra un patrón de nombre, mantener el nombre original
        if not new_name:
            print(f"No se encontró un patrón coincidente para {filename}. Moviendo a revisión manual.")
            shutil.move(os.path.join(directory, filename), os.path.join(revision_directory, filename))
            total_files_for_revision += 1
            continue

        # Intentar extraer la fecha y hora solo después de encontrar el patrón de nombre
        print("Intentando extraer la fecha y hora del nombre del archivo...")
        date_time_match = re.search(
            r'\d{2}[-.]\d{2}[-.](\d{2}|\d{4}) \d{4}\s?hrs|'  # Captura: 02-08-24 0200hrs o 0200 hrs
            r'\d{2}[-.]\d{2}[-.](\d{2}|\d{4}) \d{4} horas|'  # Captura: 02-08-24 1600 horas
            r'\d{2}[-.]\d{2}[-.](\d{2}|\d{4}) \d{4}|'        # Captura: 02-08-24 0200
            r'\d{2} \w+ (\d{2}|\d{4}) \d{4}h|'               # Captura: 02 agosto 2024 0500h
            r'\d{2} \w+ (\d{2}|\d{4}) \d{2}\s?hrs|'          # Captura: 02 agosto 2024 05 hrs o 05hrs
            r'\d{2} \w+ \d{2}\s?hrs',                        # Captura: 02 agosto 05 hrs o 05hrs
            name
        )

        if date_time_match:
            date_time_str = date_time_match.group()
            formatted_date_time = parse_date_time(date_time_str)
            if formatted_date_time:
                new_filename = f"{new_name} {formatted_date_time}{ext}"
            else:
                new_filename = f"{new_name}{ext}"  # Mantener el nombre con solo el patrón de búsqueda
                print(f"Fecha y hora no formateadas correctamente. Asignando nombre sin fecha: {new_filename}")
        else:
            new_filename = f"{new_name}{ext}"  # Mantener el nombre con solo el patrón de búsqueda
            print(f"No se encontró fecha y hora en el nombre del archivo. Asignando nombre: {new_filename}")

        # Comprobar si el archivo ya existe y agregar un sufijo si es necesario
        count = 1
        original_new_filename = new_filename
        while os.path.exists(os.path.join(directory, new_filename)):
            new_filename = f"{original_new_filename[:-len(ext)]} ({count}){ext}"
            count += 1

        # Renombrar el archivo
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
        print(f"Archivo renombrado de {filename} a {new_filename}\n")

        total_renamed_files += 1

    # Informe final
    print(f"\nProceso completado. Total de archivos renombrados: {total_renamed_files}")
    print(f"Total de archivos movidos a revisión manual: {total_files_for_revision}")

# Ruta de la carpeta de prueba
test_directory = r"D:\Memoria de Servicio\202410-21 0900hrs - copia"

# Primero limpiar los _
clean_underscores_in_directory(test_directory)

# Luego ejecutar la función de renombrado
rename_files_in_directory(test_directory)