    from fastapi import FastAPI, File, UploadFile
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
            url = "http://localhost:5033/api/EstudianteControlador/RegistrarEstudianteAsync"
            
            # Instanciar la clase de seguridad
            seguridad = Seguridad()
                    
            urlDiscapacidad = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/discapacidad.json"
            urlEps = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/eps.json"
            urlEstratoSocial = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/estratoSocial.json"
            urlGenero = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/genero.json"
            urlGrado = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/grado.json"
            urlGrupo = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/grupo.json"
            urlJornada = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/jornada.json"
            urlNivelEscolaridad = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/nivelEscolaridad.json"
            urlRh = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/rh.json"
            urlSede = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/sede.json"
            urlSisben = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/sisben.json"
            urlTipoDocumento = "https://gist.githubusercontent.com/AlexanderMoreno2938/a318729ac3010434a8a70871db71bfa8/raw/4ea235c58ff32073720e06cf2b29ab602e897754/tipoDocumento.json"

            responseDiscapacidad = requests.get(urlDiscapacidad)
            responseEps = requests.get(urlEps)
            responseEstratoSocial = requests.get(urlEstratoSocial)
            responseGenero = requests.get(urlGenero)
            responseGrado = requests.get(urlGrado)
            responseGrupo = requests.get(urlGrupo)
            responseJornada = requests.get(urlJornada)
            responsenivelEscolaridad = requests.get(urlNivelEscolaridad)
            responseRh = requests.get(urlRh)
            responseSede = requests.get(urlSede)
            responseSisben = requests.get(urlSisben)
            responseTipoDocumento = requests.get(urlTipoDocumento)

            # Definir un diccionarios vacios por si falla la solicitud
            mapeoDiscapacidad = {}
            mapeoEps = {}
            mapeoEstratoSocial = {}
            mapeoGenero = {}
            mapeoGrado = {}
            mapeoGrupo = {}
            mapeoJornada = {}
            mapeoNivelEscolaridad = {}
            mapeoRh = {}
            mapeoSede = {}
            mapeoSisben = {}
            mapeoTipoDocumento = {} 

            if responseDiscapacidad.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonDiscapacidad = responseDiscapacidad.json()  
                    mapeoDiscapacidad = {item['nombre']: item['id'] for item in jsonDiscapacidad.get('Discapacidad', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de discapacidad {e}")
                    
            if responseEps.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonEps = responseEps.json()  
                    mapeoEps = {item['nombre']: item['id'] for item in jsonEps.get('Eps', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de eps {e}")

            if responseEstratoSocial.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonEstratoSocial = responseEstratoSocial.json()  
                    mapeoEstratoSocial = {item['nombre']: item['id'] for item in jsonEstratoSocial.get('Estrato Social', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de estrato social {e}")

            if responseGenero.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonGenero = responseGenero.json()  
                    mapeoGenero = {item['nombre']: item['id'] for item in jsonGenero.get('Genero', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de genero {e}")

            if responseGrado.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonGrado = responseGrado.json()  
                    mapeoGrado = {item['nombre']: item['id'] for item in jsonGrado.get('Grado', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de grado {e}")

            if responseGrupo.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonGrupo = responseGrupo.json()  
                    mapeoGrupo = {item['nombre']: item['id'] for item in jsonGrupo.get('Grupo', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de grupo {e}")

            if responseJornada.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonJornada = responseJornada.json()  
                    mapeoJornada = {item['nombre']: item['id'] for item in jsonJornada.get('Jornada', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de jornada {e}")

            if responsenivelEscolaridad.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonNivelEscolaridad = responsenivelEscolaridad.json()  
                    mapeoNivelEscolaridad = {item['nombre']: item['id'] for item in jsonNivelEscolaridad.get('Nivel Escolaridad', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de nivel escolaridad {e}")

            if responseRh.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonRh = responseRh.json()  
                    mapeoRh = {item['nombre']: item['id'] for item in jsonRh.get('Tipo Rh', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de rh {e}")

            if responseSede.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonSede = responseSede.json()  
                    mapeoSede = {item['nombre']: item['id'] for item in jsonSede.get('Sede', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de sede {e}")

            if responseSisben.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonSisben = responseSisben.json()  
                    mapeoSisben = {item['nombre']: item['id'] for item in jsonSisben.get('Sisben', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de sisben {e}")

            if responseTipoDocumento.status_code == 200:
                try:
                    # Convertir la respuesta en JSON
                    jsonTipoDocumento = responseTipoDocumento.json()  
                    mapeoTipoDocumento = {item['nombre']: item['id'] for item in jsonTipoDocumento.get('Tipo Documento', [])}

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar el JSON de tipo de documento {e}")

            # Manejar posibles errores al leer el archivo
            try:
                df = pd.read_excel(temp_file)
            except PermissionError as e:
                raise HTTPException(status_code=403, detail=f"Error de permisos al acceder al archivo: {e}")
            except FileNotFoundError as e:
                raise HTTPException(status_code=404, detail=f"Archivo no encontrado: {e}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Ocurrió un error al leer el archivo: {e}")


            # Iterar sobre cada fila del Dataframe y enviar los datos a la API
            for index, row in df.iterrows(): 
                
                # Construir el diccionario con los valores de la fila

                discapacidad = row['DISCAPACIDAD'] if pd.notnull(row['DISCAPACIDAD']) else None
                idDiscapacidad = mapeoDiscapacidad.get(discapacidad, None)

                eps = row['EPS'] if pd.notnull(row['EPS']) else None
                idEps = mapeoEps.get(eps, None)

                estratoSocial = row['ESTRATO'] if pd.notnull(row['ESTRATO']) else None
                idEstratoSocial = mapeoEstratoSocial.get(estratoSocial, None)
                    
                sisben = row['SISBEN IV'] if pd.notnull(row['SISBEN IV']) else None
                idSisben = mapeoSisben.get(sisben, None)

                grupo = str(row['GRUPO']) if pd.notnull(row['GRUPO']) else None
                idGrupo = mapeoGrupo.get(grupo, None)

                jornada = row['JORNADA'] if pd.notnull(row['JORNADA']) else None
                idJornada = mapeoJornada.get(jornada, None)

                grado = str(row['GRADO_COD']) if pd.notnull(row['GRADO_COD']) else None
                idGrado = mapeoGrado.get(grado, None)
                        
                sede = row['SEDE'] if pd.notnull(row['SEDE']) else None
                idSede = mapeoSede.get(sede, None)

                nivelEscolaridad = row['NIVEL'] if pd.notnull(row['NIVEL']) else None
                idNivelEscolaridad = mapeoNivelEscolaridad.get(nivelEscolaridad, None)

                tipoDocumento = row['TIPODOC'] if pd.notnull(row['TIPODOC']) else None
                idTipoDocumento = mapeoTipoDocumento.get(tipoDocumento, None) 

                tipoRh = row['TIPO DE SANGRE'] if pd.notnull(row['TIPO DE SANGRE']) else None
                idTipoRh = mapeoRh.get(tipoRh, None)

                genero = row['GENERO'] if pd.notnull(row['GENERO']) else None
                idGenero = mapeoGenero.get(genero, None)


                numeroDocumento = str(row['DOC'])

                contrasenaEncriptada = seguridad.encriptar_contrasenia(numeroDocumento, numeroDocumento)

                datos ={
                    "pPrimerNombre": row["NOMBRE1"],
                    "pPrimerApellido": row["APELLIDO1"],
                    "pFechaNacimiento": row["FECHA_NACIMIENTO"].strftime("%Y-%m-%d"),
                    "pEdad": int(row["EDAD"]),
                    "pNumeroDocumento": str(row['DOC']),
                    "pIdTipoDocumento": idTipoDocumento,
                    "pIdGenero": idGenero,
                    "pCodigoEstudiante": str(row['NUI']),
                    "pfechaMatriculaEstudiante": row["FECHAINI"].strftime("%Y-%m-%d %H:%M:%S"),
                    "pEstadoEstudiante": str(row['ESTADO']),
                    "pIdDiscapacidad": idDiscapacidad,
                    "pIdGrupo": idGrupo,
                    "pIdJornada": idJornada,
                    "pIdGrado": idGrado,
                    "pIdSede": idSede,
                    "pIdNivelEscolaridad": idNivelEscolaridad,
                    "pContraseinaUsuario": contrasenaEncriptada,      
                    "pSegundoNombre": str(row['NOMBRE2']) if pd.notna(row['NOMBRE2']) else None,
                    "pSegundoApellido": str(row['APELLIDO2']) if pd.notna(row['APELLIDO2']) else None,
                    "pDireccionResidencia": str(row['BARRIO']) if pd.notna(row['BARRIO']) else None,
                    "pIdEps": idEps if idEps is not None else None,
                    "pIdRh": idTipoRh if idTipoRh is not None else None,
                    "pIdEstratoSocial": idEstratoSocial if idEstratoSocial is not None else None,
                    "pIdSisben": idSisben if idSisben is not None else None
                }
                # Enviar la solicitud POST a la API .NET
                respuesta = requests.post(url, json=datos)
                print(f"Registro {index + 1}: {respuesta.status_code} - {respuesta.text}")
        except Exception as e:
                return {"status": "error", "message": str(e)}
            
        return {"status": "ok", "message": "Archivo procesado exitosamente"}

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)