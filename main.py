from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uvicorn
import json
from datetime import datetime
import hashlib
import base64
import requests

app = FastAPI()

# Configurar CORS para permitir solicitudes desde el frontend de Angular.
origins = [
    "http://localhost:4200",  # URL de tu aplicación Angular (ajusta si es necesario)
    # Puedes agregar otros orígenes si requieres
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir estos orígenes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clase de seguridad para encriptar la contraseña
class Seguridad:
    CLAVE_SECRETA = "MyApp@2025_SecretKey#123!"

    @staticmethod
    def encriptar_contrasenia(contrasenia: str, nombre_usuario: str) -> str:
        salt_input = (nombre_usuario + Seguridad.CLAVE_SECRETA).encode('ascii')
        salt = hashlib.sha256(salt_input).digest()
        hashed_password = hashlib.pbkdf2_hmac(
            hash_name='sha512',
            password=contrasenia.encode('utf-8'),
            salt=salt,
            iterations=10000,
            dklen=32
        )
        return base64.b64encode(hashed_password).decode('utf-8')

# Endpoint para recibir el archivo XLSX y procesarlo
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Leer el contenido del archivo subido y guardarlo temporalmente
    contents = await file.read()
    temp_file = "temp.xlsx"
    with open(temp_file, "wb") as f:
        f.write(contents)

    try:
        # Procesar el archivo usando pandas
        df = pd.read_excel(temp_file)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=f"Error de permisos al acceder al archivo: {e}")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al leer el archivo: {e}")

    url = "http://localhost:5033/api/EstudianteControlador/RegistrarEstudianteAsync"
    seguridad = Seguridad()

    # URLs para datos de referencia
    urls = {
        "Discapacidad": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/discapacidad.json",
        "Eps": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/eps.json",
        "Estrato Social": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/estratoSocial.json",
        "Genero": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/genero.json",
        "Grado": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/grado.json",
        "Grupo": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/grupo.json",
        "Jornada": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/jornada.json",
        "Nivel Escolaridad": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/nivelEscolaridad.json",
        "Tipo Rh": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/rh.json",
        "Sede": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/sede.json",
        "Sisben": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/sisben.json",
        "Tipo Documento": "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/tipoDocumento.json",
    }

    # Descargar y mapear los datos
    mapeos = {}
    for key, url_ref in urls.items():
        try:
            response = requests.get(url_ref)
            if response.status_code == 200:
                json_data = response.json()
                mapeos[key] = {item['nombre']: item['id'] for item in json_data.get(key, [])}
            else:
                mapeos[key] = {}
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON de {key}: {e}")
            mapeos[key] = {}

    # Iterar sobre cada fila del DataFrame y enviar los datos a la API
    for index, row in df.iterrows():
        discapacidad = row.get('DISCAPACIDAD', None)
        idDiscapacidad = mapeos.get('Discapacidad', {}).get(discapacidad) if pd.notnull(discapacidad) else None

        eps = row.get('EPS', None)
        idEps = mapeos.get('Eps', {}).get(eps) if pd.notnull(eps) else None

        estratoSocial = row.get('ESTRATO', None)
        idEstratoSocial = mapeos.get('Estrato Social', {}).get(estratoSocial) if pd.notnull(estratoSocial) else None

        sisben = row.get('SISBEN IV', None)
        idSisben = mapeos.get('Sisben', {}).get(sisben) if pd.notnull(sisben) else None

        grupo = str(row.get('GRUPO', None)) if pd.notnull(row.get('GRUPO')) else None
        idGrupo = mapeos.get('Grupo', {}).get(grupo) if grupo else None

        jornada = row.get('JORNADA', None)
        idJornada = mapeos.get('Jornada', {}).get(jornada) if pd.notnull(jornada) else None

        grado = str(row.get('GRADO_COD', None)) if pd.notnull(row.get('GRADO_COD')) else None
        idGrado = mapeos.get('Grado', {}).get(grado) if grado else None

        sede = row.get('SEDE', None)
        idSede = mapeos.get('Sede', {}).get(sede) if pd.notnull(sede) else None

        nivelEscolaridad = row.get('NIVEL', None)
        idNivelEscolaridad = mapeos.get('Nivel Escolaridad', {}).get(nivelEscolaridad) if pd.notnull(nivelEscolaridad) else None

        tipoDocumento = row.get('TIPODOC', None)
        idTipoDocumento = mapeos.get('Tipo Documento', {}).get(tipoDocumento) if pd.notnull(tipoDocumento) else None

        genero = row.get('GENERO', None)
        idGenero = mapeos.get('Genero', {}).get(genero) if pd.notnull(genero) else None

        rh = row.get('RH', None)
        idRh = mapeos.get('Tipo Rh', {}).get(rh) if pd.notnull(rh) else None

        # Encriptar contraseña con Seguridad
        contrasenia_encriptada = seguridad.encriptar_contrasenia(
            contrasenia=str(row.get('CONTRASENIA', '')),
            nombre_usuario=str(row.get('USUARIO', ''))
        )

        # Construir payload para enviar a la API
        payload = {
            "apellidos": row.get('APELLIDOS', ''),
            "contrasenia": contrasenia_encriptada,
            "correo": row.get('CORREO', ''),
            "direccion": row.get('DIRECCION', ''),
            "fechaNacimiento": str(row.get('FECHANACIMIENTO', '')),
            "idDiscapacidad": idDiscapacidad,
            "idEps": idEps,
            "idEstratoSocial": idEstratoSocial,
            "idGenero": idGenero,
            "idGrado": idGrado,
            "idGrupo": idGrupo,
            "idJornada": idJornada,
            "idNivelEscolaridad": idNivelEscolaridad,
            "idRh": idRh,
            "idSede": idSede,
            "idSisben": idSisben,
            "idTipoDocumento": idTipoDocumento,
            "nombre": row.get('NOMBRES', ''),
            "numeroDocumento": str(row.get('NUMDOCUMENTO', '')),
            "telefono": str(row.get('TELEFONO', '')),
            "usuario": row.get('USUARIO', ''),
        }

        # Enviar datos a la API
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print(f"Error al enviar datos para fila {index}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Excepción al enviar datos para fila {index}: {e}")

    return {"mensaje": "Archivo procesado y datos enviados correctamente"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
