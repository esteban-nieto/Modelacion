# Declaración de uso de herramientas de IA (BORRADOR)

Revisar, completar y firmar antes de entregar. Lo siguiente es lo que consta en el repositorio.

- **Herramienta:** Claude Code (Anthropic), asistente de programación con modelo de lenguaje.
- **Para qué se usó:** escribir y depurar código Python y JavaScript, generar scripts de simulación y de pruebas, redactar y regenerar documentos (B2, informes), buscar fuentes bibliográficas y generar figuras.
- **Despliegue:** configuración del despliegue en Railway (Dockerfile con el puerto PORT, normalización de la URL de PostgreSQL al driver psycopg2, variables de entorno y comandos de la CLI de Railway).
- **Depuración:** diagnóstico de errores de ejecución y de despliegue (por ejemplo, el fallo 502 por el driver de la base de datos y los errores de renderizado de la presentación y de los documentos). Cada corrección fue revisada y probada por el equipo.
- **Qué se verificó:** las pruebas automáticas (49 pruebas, cobertura 96,84 %), la ejecución de los modelos SimPy y Vensim, la validación de Vensim contra datos no usados en la calibración (error 0,31 %), la búsqueda de los datos bibliográficos en revistas y bases (PubMed, Crossref, páginas de las revistas), con los casos que no se pudieron comprobar excluidos del informe, y la revisión de los resultados en la aplicación en ejecución.
- **Qué no se verificó con IA:** el texto completo de las fuentes citadas (solo se revisaron metadatos y resúmenes); la revisión de usabilidad con usuarios reales (no se hizo); las respuestas del formulario (son simuladas, y así deben declararse).
- **Quién lo declara:** Gaddiel Esteban Nieto Rojas.
