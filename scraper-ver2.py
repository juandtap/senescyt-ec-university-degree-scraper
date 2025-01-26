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
import time
import pandas as pd

# Configuracion del driver, se usa chrome
driver_path = os.path.join(os.getcwd(), "chromedriver.exe")  
service = Service(driver_path)
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # para abrir el navegador
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(service=service, options=options)

# URL objetivo
url = "https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml"

# Leer el nuemro de cedula desde el archivo cedula.txt
dni_file = os.path.join(os.getcwd(), "cedula.txt")
try:
    with open(dni_file, "r") as file:
        dni = file.readline().strip() 
except FileNotFoundError:
    print("El archivo cedula.txt no se encuentra en el directorio.")
    driver.quit()
    exit()

try:
    driver.get(url)
    wait = WebDriverWait(driver, 10)  # Espera hasta 10 segundos para cargar elementos dinámicos

    for attempt in range(5):  # Intentar hasta 5 veces si falla el captcha
        print(f"Intento {attempt + 1} para resolver el captcha...")
        # Captura los campos ocultos
        campos_ocultos = {}
        hidden_inputs = driver.find_elements(By.XPATH, "//input[@type='hidden']")
        for input_field in hidden_inputs:
            name = input_field.get_attribute("name")
            value = input_field.get_attribute("value")
            if name:
                campos_ocultos[name] = value

        # Captura el captcha como imagen
        captcha_element = wait.until(EC.presence_of_element_located((By.ID, "formPrincipal:capimg")))  # Reemplaza con el ID correcto
        captcha_path = os.path.join(os.getcwd(), "Captcha.png")
        captcha_element.screenshot(captcha_path)

        # Procesa el captcha con pytesseract
        captcha_img = Image.open(captcha_path)
        captcha_texto = pytesseract.image_to_string(captcha_img).strip()
        captcha_texto = re.sub(r'[^a-zA-Z0-9]', '', captcha_texto)  # Limpia caracteres no deseados
        print(f"Captcha reconocido: {captcha_texto}")

        # se llena  el formulario
        # los ID se obtienen inspeccionando el codigo fuente de la pagina web
        dni_input = wait.until(EC.presence_of_element_located((By.ID, "formPrincipal:identificacion")))  
        dni_input.clear() 
        dni_input.send_keys(dni)

        captcha_input = driver.find_element(By.ID, "formPrincipal:captchaSellerInput")  
        captcha_input.clear()  # limpia el campo para reintentar en caso de fallo
        captcha_input.send_keys(captcha_texto)

        # clic en  buscar
        boton_buscar = driver.find_element(By.ID, "formPrincipal:boton-buscar")  
        ActionChains(driver).move_to_element(boton_buscar).click().perform()

        # Verifica si el captcha fue incorrecto
        try:
            mensaje_error = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@id='formPrincipal:messages']//span[contains(@class, 'ui-messages-error-detail') and text()='Caracteres incorrectos']")
                )
            )
            print("Captcha falló: caracteres incorrectos detectados.")
            time.sleep(1)  # Espera 1 segundo antes de intentar nuevamente
            continue  # Intenta nuevamente
        except Exception:
            print("Captcha resuelto correctamente.")
            break  # Si no aparece el mensaje de error, el captcha fue correcto

    else:
        print("No se pudo resolver el captcha después de 5 intentos.")
        driver.quit()
        exit()

    
    # Espera la tabla de resultados de titulos
    tabla1 = wait.until(EC.presence_of_element_located((By.ID, "formPrincipal:j_idt54:0:tablaAplicaciones")))  # Reemplaza con el ID correcto
    print("Tabla de titulos encontrada con éxito!")

    # Extrae encabezados de la tabla de titulos
    encabezados_tabla1 = []
    encabezados = tabla1.find_elements(By.TAG_NAME, "th")
    for encabezado in encabezados:
        span = encabezado.find_element(By.TAG_NAME, "span")  # Extrae el texto dentro del <span>
        encabezados_tabla1.append(span.text if span.text else "")

    # Extrae el contenido de la tabla de titulos 
    filas_tabla1 = tabla1.find_elements(By.TAG_NAME, "tr")
    data_tabla1 = []
    for fila in filas_tabla1:
        columnas = fila.find_elements(By.TAG_NAME, "td")
        fila_datos = [columna.text if columna.text else "" for columna in columnas]  # Reemplaza None con ""
        if any(fila_datos):  # Incluye solo filas con al menos un valor no vacío
            data_tabla1.append(fila_datos)

    # Espera la segunda tabla de informacion personal
    tabla2 = wait.until(EC.presence_of_element_located((By.ID, "formPrincipal:j_idt44")))  
    print("tabla de informacion personal encontrada con éxito!")

    # Extrae el contenido de la segunda tabla
    filas_tabla2 = tabla2.find_elements(By.TAG_NAME, "tr")
    data_tabla2 = []
    for fila in filas_tabla2:
        columnas = fila.find_elements(By.TAG_NAME, "td")
        fila_datos = [columna.text if columna.text else "" for columna in columnas]  # Reemplaza None con ""
        if any(fila_datos):  # Incluye solo filas con al menos un valor no vacío
            data_tabla2.append(fila_datos)

    # Organiza las tablas en un dataframe de pandas
    df_tabla1 = pd.DataFrame(data_tabla1, columns=encabezados_tabla1 if encabezados_tabla1 else None)
    df_tabla2 = pd.DataFrame(data_tabla2)

    # mostrar los datos por consola
    print("Tabla de Título(s) de tercer nivel de grado:")
    print(df_tabla1.to_string(index=False))

    print("\nTabla de Información Personal:")
    print(df_tabla2.to_string(index=False))

    # Se guarda el resultado  en un archivo de texto 
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
