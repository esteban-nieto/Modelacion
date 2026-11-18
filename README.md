# Gestión de turnos en un puesto de salud rural

Proyecto integrador de Modelación, Simulación y Desarrollo CRUD. El sistema gestiona pacientes, profesionales, servicios y citas de un puesto de salud rural, y usa los datos históricos para simular escenarios y mejorar la asignación de turnos.

## Contenido

| Carpeta | Descripción |
| --- | --- |
| `app/` | API REST (FastAPI) por capas: routers, negocio y acceso a datos |
| `static/` | Interfaz web en HTML, CSS y JavaScript |
| `scripts/` | Siembra de datos y exportación de esquema SQL y OpenAPI |
| `simulacion/` | Ajuste de distribuciones, modelo SimPy, escenarios, Monte Carlo y modelo financiero |
| `diagramas/` | Modelos de Vensim (`.mdl`), figuras y escenarios de dinámica de sistemas |
| `docs/` | Esquema SQL, OpenAPI, figuras e informes |
| `tests/` | Pruebas unitarias y de integración |

## Ejecución con Docker

```powershell
Copy-Item .env.example .env
```

Edite `.env` y defina `SECRET_KEY`, `POSTGRES_PASSWORD` y, si lo desea, las claves de los usuarios de demostración:

```powershell
docker compose --env-file .env up --build
```

La aplicación queda en `https://localhost:8443` (el certificado es local y el navegador pedirá confirmarlo). Al primer arranque se siembran 700 pacientes y más de 4 000 citas.

## Ejecución local

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
$env:SECRET_KEY = "una-clave-larga-y-aleatoria"
.venv\Scripts\python scripts\sembrar_datos.py
.venv\Scripts\python -m uvicorn app.main:app
```

Abra `http://localhost:8000`. La documentación interactiva de la API está en `/docs`.

Usuarios de demostración (cambian con las variables `CLAVE_ADMIN`, `CLAVE_OPERADOR` y `CLAVE_CONSULTA`):

| Rol | Correo | Clave por defecto |
| --- | --- | --- |
| administrador | administrador@saludrural.co | Admin12345 |
| operador | operador@saludrural.co | Operador12345 |
| consulta | consulta@saludrural.co | Consulta12345 |

## Pruebas

```powershell
.venv\Scripts\python -m pytest --cov=app
```

## Reproducir la simulación

Cada paso lee la salida del anterior y deja sus resultados en `simulacion/salidas/`.

```powershell
.venv\Scripts\python simulacion\exportar_datos.py
.venv\Scripts\python simulacion\ajuste_distribuciones.py
.venv\Scripts\python -m simulacion.escenarios
.venv\Scripts\python -m simulacion.monte_carlo
.venv\Scripts\python -m simulacion.financiero
```

`escenarios` genera `resultados.json`, que el tablero de la aplicación compara con los indicadores reales.

## Modelos de Vensim

`diagramas/turnos_causal.mdl` contiene el diagrama causal y `diagramas/turnos_flujos_niveles.mdl` el diagrama de flujos y niveles. Se abren con Vensim PLE y se regeneran con `python diagramas/generar_vensim.py`. El segundo modelo se ejecuta también desde Python con `python diagramas/correr_vensim.py`.

## Seguridad

- Contraseñas con scrypt y sal aleatoria.
- Autenticación con JWT en el encabezado `Authorization`, por lo que no hay cookies de sesión que un ataque CSRF pueda aprovechar.
- Consultas con SQLAlchemy parametrizado, sin SQL concatenado.
- La interfaz inserta texto con `textContent` y el servidor envía una política `Content-Security-Policy` estricta.
- Secretos únicamente por variables de entorno.
- HTTPS mediante el proxy Caddy del `docker-compose.yml`.
