# Entregables finales (guía, sección 9)

| # | Entregable | Estado | Archivos |
|---|---|---|---|
| 01 | Repositorio Git con código, historial, README, scripts, Docker, pruebas y pipeline de CI | Entregado | 7 |
| 02 | Sistema desplegado y accesible (URL) o ejecutable con un solo comando documentado | Entregado (desplegado en Railway) | 1 |
| 03 | Documentación del componente A (requisitos, ERD, arquitectura, UML, manuales) | Entregado (revisar manuales) | 8 |
| 04 | Informe técnico del componente B (8 a 12 páginas, APA 7.ª) | Entregado (extensión y APA por verificar) | 1 |
| 05 | Archivos del modelo de simulación (.mod u otro) con instrucciones para reproducir | Entregado | 12 |
| 06 | Infografía de la comparación de escenarios (1 página) | Pendiente (versión anterior) | 2 |
| 07 | Bitácora de equipo y cronograma | Entregado (revisar aporte individual) | 2 |
| 08 | Video individual de postura crítica (máximo 5 minutos) por cada integrante | Pendiente (no grabado) | 1 |
| 09 | Presentación de la sustentación | Entregado (diseño por revisar) | 1 |
| 10 | Declaración de uso de herramientas de IA y autoevaluación/coevaluación | Pendiente (borrador) | 2 |

Generado desde el repositorio (último commit confirmado: 1596cd4).

## Notas por entregable
- **01** El repositorio está en https://github.com/esteban-nieto/Modelacion, rama principal main.
- **02** URL de la aplicación: https://modelacion-api-production.up.railway.app (documentación de la API en /docs). El enlace completo y los roles de acceso están en Enlace_sistema_desplegado.docx. Alternativa local: `docker compose --env-file .env up --build` (README).
- **03** Revisar que los manuales de usuario y técnico estén completos dentro del documento.
- **04** No se ha contado la extensión (8 a 12 páginas sin anexos) ni revisado el formato APA 7.
- **05** Modelo en SimPy (código Python) y modelos Vensim (.mdl). Pasos de reproducción en el README, sección 'Reproducir la simulación'.
- **06** La infografía muestra los casos de una versión anterior de B2. Hay que regenerarla con la tabla de casos final (docs/generar_infografia_b2.py).
- **07** La bitácora debe mostrar el aporte individual identificable de cada integrante.
- **08** Cada integrante debe grabar su video. Se deja el guion; el video no se puede generar desde aquí.
- **09** Revisar el renderizado de todas las diapositivas en PowerPoint antes de la sustentación.
- **10** Ver el borrador en la subcarpeta 10_declaracion_IA_y_coevaluacion. El equipo debe revisarlo, completarlo y firmarlo.
