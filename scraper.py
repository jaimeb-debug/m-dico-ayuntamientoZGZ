import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage

# Variables de entorno (se configuran en GitHub más adelante)
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')
URL = "https://www.zaragoza.es/oferta/"

def scrape_ofertas():
    # Simulamos ser un navegador para que la web no nos bloquee
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        print(f"Error al acceder a la página: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    convocatorias = []
    
    # NOTA: Este es un buscador genérico. Busca enlaces (<a>) que contengan palabras clave.
    # Si la web cambia su estructura, podrías necesitar inspeccionar el código fuente (F12)
    # y cambiar esto por algo como: soup.find_all('div', class_='clase-de-oferta')
    for a in soup.find_all('a', href=True):
        texto = a.get_text(strip=True).lower()
        if 'convocatoria' in texto or 'oposición' in texto or 'bolsa' in texto:
            enlace = a['href']
            # Si el enlace es relativo, le añadimos el dominio principal
            if not enlace.startswith('http'):
                enlace = "https://www.zaragoza.es" + enlace
            
            titulo_formateado = f"- {a.get_text(strip=True)}: {enlace}"
            convocatorias.append(titulo_formateado)
            
    # Devolvemos la lista eliminando posibles duplicados
    return list(set(convocatorias))

def enviar_correo(convocatorias):
    msg = EmailMessage()
    msg['Subject'] = 'Nuevas Convocatorias - Ayto. Zaragoza'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECEIVER_EMAIL

    cuerpo = "Hola,\n\nSe han detectado las siguientes menciones de convocatorias en la web del Ayuntamiento:\n\n"
    cuerpo += "\n".join(convocatorias)
    cuerpo += f"\n\nPuedes revisarlo directamente aquí: {URL}"
    
    msg.set_content(cuerpo)

    # Configuración para Gmail (usa el puerto 465 para SSL)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Correo enviado con éxito.")
    except Exception as e:
        print(f"Error enviando el correo: {e}")

if __name__ == '__main__':
    print("Buscando ofertas...")
    ofertas = scrape_ofertas()
    
    if ofertas:
        print(f"Se encontraron {len(ofertas)} posibles convocatorias. Enviando correo...")
        enviar_correo(ofertas)
    else:
        print("No se encontraron convocatorias hoy.")
