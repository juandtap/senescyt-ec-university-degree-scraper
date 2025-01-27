## Proyecto Scraping Senescyt

### Autor: Diego Tapia

### Descripción

Este script de **Python** es un scraper de información de títulos universitarios de la web:

"https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml"

La información se extrae a partir de un número de cédula, el cual se lee desde un archivo de texto ```cedula.txt```.

Luego, con la librería Selenium, se llena el campo de cédula y se extrae el captcha para resolverlo con la librería ```pytesseract```.

Una vez resuelto el captcha, con Selenium se presiona el botón de buscar. Si el captcha se resolvió correctamente, se muestra la información de la persona (en caso contrario, se intenta nuevamente hasta resolverlo correctamente). Lo que se muestra son sus títulos e información personal en el siguiente formato:

#### Tabla de títulos de educación superior

| Título       | Institución de Educación Superior | Tipo      | Reconocido Por | Número de Registro    | Fecha de Registro |
|--------------|-----------------------------------|-----------|----------------|------------------------|--------------------|
| ODONTÓLOGA   | UNIVERSIDAD CATÓLICA DE CUENCA   | Nacional  |                | 1029-2018-1970664     | 2018-06-08         |

Esta información también se guarda en el archivo ```resultados.txt```.

### Ejecución

En un ambiente virtual, instalar las librerías con pip o conda. Las librerías necesarias se encuentran en el archivo ```requirements.txt```.

Se pueden instalar con el siguiente comando tanto en Windows como en Linux:


```
pip install -r requirements.txt
```


**Nota:** En Windows se debe instalar Tesseract OCR, que se puede encontrar en el siguiente [enlace a Tesseract-OCR](https://sourceforge.net/projects/tesseract-ocr.mirror/). También se puede instalar siguiendo las instrucciones en su [repositorio de GitHub](https://github.com/tesseract-ocr/tesseract).

Una vez instaladas las librerías, se debe ejecutar el archivo ```scraper-ver2.py```.

Antes de ejecutar, verificar que en el archivo ```cedula.txt``` haya un número válido y que esté registrado en la Senescyt.



```
python scraper-ver2.py

```

**Nota**: Los ids de las tablas cambian periódicamente por lo que hay que revisar el código fuente de la web en caso de presentarse un error, verificar que los IDs (el número al final de j_idtXX) sean similares a los que se tienen en las siguientes líneas de código:


```
tabla1 = wait.until(EC.presence_of_element_located((By.ID, "formPrincipal:j_idt63:0:tablaAplicaciones")))  
tabla2 = wait.until(EC.presence_of_element_located((By.ID, "formPrincipal:j_idt51")))  
```



En caso de no ser los mismos, reemplazarlos con los que aparezcan en el código fuente de la web e intentar nuevamente.
