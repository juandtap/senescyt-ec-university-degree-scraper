from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import pytesseract
from PIL import Image
import re
import os
import pandas as pd

# Configuración del driver
driver_path = os.path.join(os.getcwd(), "chromedriver.exe")  # El driver debe estar en el mismo directorio que el script
service = Service(driver_path)
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Quita esta línea si quieres ver el navegador en acción
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=service, options=options)

# URL objetivo
url = "https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml"  # Reemplaza con la URL de tu página objetivo

# Leer el DNI desde el archivo cedula.txt
dni_file = os.path.join(os.getcwd(), "cedula.txt")
try:
    with open(dni_file, "r") as file:
        dni = file.readline().strip()  # Lee la primera línea y elimina espacios en blanco
except FileNotFoundError:
    print("El archivo cedula.txt no se encuentra en el directorio.")
    driver.quit()
    exit()

try:
    driver.get(url)
    wait = WebDriverWait(driver, 10)  # Espera hasta 10 segundos para cargar elementos dinámicos

    # Captura el captcha como imagen
    captcha_element = wait.until(EC.presence_of_element_located((By.ID, "formPrincipal:capimg")))  # Reemplaza con el ID correcto
    captcha_path = os.path.join(os.getcwd(), "Captcha.png")
    captcha_element.screenshot(captcha_path)

    # Procesa el captcha con pytesseract
    captcha_img = Image.open(captcha_path)
    captcha_texto = pytesseract.image_to_string(captcha_img).strip()
    captcha_texto = re.sub(r'[^a-zA-Z0-9]', '', captcha_texto)  # Limpia caracteres no deseados
    print(f"Captcha reconocido: {captcha_texto}")

    # Llena el formulario
    dni_input = wait.until(EC.presence_of_element_located((By.ID, "formPrincipal:identificacion")))  # Reemplaza con el ID correcto
    dni_input.send_keys(dni)

    captcha_input = driver.find_element(By.ID, "formPrincipal:captchaSellerInput")  # Reemplaza con el ID correcto
    captcha_input.send_keys(captcha_texto)

    # Haz clic en el botón de buscar
    boton_buscar = driver.find_element(By.ID, "formPrincipal:boton-buscar")  # Reemplaza con el ID correcto
    ActionChains(driver).move_to_element(boton_buscar).click().perform()

    # Espera la tabla de resultados principal
    tabla1 = wait.until(EC.presence_of_element_located((By.ID, "formPrincipal:j_idt54:0:tablaAplicaciones")))  # Reemplaza con el ID correcto
    print("Tabla principal encontrada con éxito!")

    # Extrae encabezados de la tabla principal
    encabezados_tabla1 = []
    encabezados = tabla1.find_elements(By.TAG_NAME, "th")
    for encabezado in encabezados:
        span = encabezado.find_element(By.TAG_NAME, "span")  # Extrae el texto dentro del <span>
        encabezados_tabla1.append(span.text if span.text else "")

    # Extrae el contenido de la tabla principal
    filas_tabla1 = tabla1.find_elements(By.TAG_NAME, "tr")
    data_tabla1 = []
    for fila in filas_tabla1:
        columnas = fila.find_elements(By.TAG_NAME, "td")
        fila_datos = [columna.text if columna.text else "" for columna in columnas]  # Reemplaza None con ""
        if any(fila_datos):  # Incluye solo filas con al menos un valor no vacío
            data_tabla1.append(fila_datos)

    # Espera la segunda tabla de resultados
    tabla2 = wait.until(EC.presence_of_element_located((By.ID, "formPrincipal:j_idt44")))  # ID de la segunda tabla
    print("Segunda tabla encontrada con éxito!")

    # Extrae el contenido de la segunda tabla
    filas_tabla2 = tabla2.find_elements(By.TAG_NAME, "tr")
    data_tabla2 = []
    for fila in filas_tabla2:
        columnas = fila.find_elements(By.TAG_NAME, "td")
        fila_datos = [columna.text if columna.text else "" for columna in columnas]  # Reemplaza None con ""
        if any(fila_datos):  # Incluye solo filas con al menos un valor no vacío
            data_tabla2.append(fila_datos)

    # Organiza las tablas en pandas DataFrame
    df_tabla1 = pd.DataFrame(data_tabla1, columns=encabezados_tabla1 if encabezados_tabla1 else None)
    df_tabla2 = pd.DataFrame(data_tabla2)

    # Muestra los datos por consola
    print("Tabla de Título(s) de tercer nivel de grado:")
    print(df_tabla1.to_string(index=False))

    print("\nTabla de Información Personal:")
    print(df_tabla2.to_string(index=False))

    # Guarda las tablas en un archivo de texto formateado
    with open("resultado.txt", "w", encoding="utf-8") as f:
        f.write("Tabla de Título(s) de tercer nivel de grado:\n")
        f.write(df_tabla1.to_string(index=False))
        f.write("\n\n")
        f.write("Tabla de Información Personal:\n")
        f.write(df_tabla2.to_string(index=False))

    print("\nInformación guardada en 'resultado.txt'.")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()
