# Proyecto Miguel
- Programa que administre una constelación satelital
	- muchos satélites - LEO (Low Earth Orbit)
- Plan de vuelo de satélites
	- Cuando usar la cámara
	- Descargar la imagen
- Cada satélite tiene propiedades diferentes
	- Diferentes lugares de órbita
- Set de satélites y set de tareas - hacer plan de vuelo y enviarlo a la constelación
	- Problem domain definition
- Todos los días y debe ser MUY optimizado
	- Hacer formulación orbital de forma consciente
	- Qué satélite puede cumplir la tarea en el menor tiempo
- Ventana de comunicación
	- Cuando la comunicación de la tierra se encuentra con la del satélite
	- Comunicar plan y comunicar de vuelta las imágenes
- Usar la carga útil - depende de la foto

- Cómo resolver todo lo anterior
	- Programa que pueda traducir instrucciones en lenguaje natural a un plan de vuelo optimizado
- El usuario
	- Constelación: nombre de satélites, NORAD id, carga útil
	- Tareas que debe realizar
- Contexto (algo que debe hacer el programa al darle lo anterior)
	- TLE (Órbita) 
	- Info de la organización
	- Misión que cumple: Ver la tierra, ver el espacio, ver etc.
	- Capacidades - Carga útil - Cámaras (*multiscape 100*)
		- Comunicaciones 
- Problemas
	- NLP
	- Optimización
	- Orbital
	- Retorno
	- GENERACIÓN DEL CONTEXTO
- Generar el contexto
	- A partir del NORAD id crear contexto entero de la organización
	- Que el sistema se supla de ese contexto
	- Usando bases de datos públicas de IDs 
	- Agente que busque en la web y se lo ofrezca al resto del programa

Alcance
- Límite

Restricciones
- Para mí
- Cosas que puedan surgir
- Problemas
	- Acceso a bases de datos

Suposiciones
- Cosas que se asumen como hechas

Arquitectura multiagente
- proponer arquitectura
# Estándares de código
## DO-178C
Links:
- https://www.rtca.org/do-178/

Información: Software Considerations in Airborne Systems and Equipment Certification

- Le sigue a DO-178B
- Fue completado en 2011

- DO-178(), originally published in 1981, is the core document for defining both design assurance and product assurance for airborne software.  The current version, DO-178C, was published in 2011 and is referenced for use by FAA’s Advisory Circular.
- Software Supplemental Standards: DO-331, DO-332 and DO-333 are intended to be used with either DO-178C or DO-278A to add, modify or delete content in the core documents as it relates to the specific technologies.
-----
- the Radio Technical Commission for Aeronautics (RTCA) hopes to address software development challenges through DO-178C – a new standard that embraces contemporary technologies and methodologies necessary to achieve these aims.
- avionics systems require software certification following the guidelines in DO-178B, a document developed by the Radio Technical Commission for Aeronautics (RTCA) for the FAA in 1992. But DO-178B’s effectiveness is under question as the complexity of modern avionics software increases.
- The DO-178C standard, due to be finalized in late 2010 by a joint RTCA/EUROCAE committee, will address this shortfall and assist in bringing the certification of avionics software in line with these 21st-century technologies.

DO-178B overview
- Before we discuss the new DO-178C standard, let’s take a look at where we are today. DO-178B is a comprehensive and leveled set of software development activities and objectives. “Leveled” refers to the five Safety Integrity Levels (SILs) included in the standard – levels A, B, C, D, and E – with level A being the most safety critical and Level E having no impact on aircraft safety. “Activities” describes the processes that must be performed to meet specific “objectives.” A comprehensive cross-referencing of these objectives is provided in the standard against each of the five SILs. In this way, DO-178B is well structured and its intent clearly defined.


# Herramientas de diseño de misiones espaciales
- Buscar: generacion de codigo para sistemas espaciales

# Proyecto: Integracion de NLP y planificación en la gestión de satélites.
- Este proyecto propone una solución innovadora: traducir peticiones en lenguaje natural (NL) a representaciones formales en PDDL (Planning Domain Definition Language), permitiendo que un planificador temporal optimice la asignación de satélites, recursos y tiempos.
- Desarrollar un prototipo de sistema que integre procesamiento de lenguaje natural (NLP) y planificación automática para generar planes de misión factibles y optimizados en constelaciones LEO.

Development and Implementation of Automated Planning in CubeSats
- SSRL is implementing an operational pipeline to effectively integrate the newly authored Multi-aspect Automated Satellite Scheduler (MASS) into both missions.
- we have presented our preliminary results and procedures for integrating a predictive scheduling software, the Multi-aspect Automated Satellite Scheduler. This novel FreeFlyer-based program is intended to be usable by any CubeSat mission and fulfill the needs for accessible hybrid automation in the accelerating aerospace industry

# Glosario
- CubeSats:  satélites en miniatura llamados CubeSats han revolucionado la industria espacial, facilitando y abaratando el acceso al espacio para quienes antes solo podían soñar con él. Los CubeSats suelen construirse a partir de unidades cúbicas estándar, cada una de 10 cm x 10 cm x 10 cm. Estos pequeños satélites ofrecen acceso asequible al espacio a pequeñas empresas, institutos de investigación y universidades. Su diseño modular permite que los subsistemas estén disponibles de forma inmediata a través de diferentes proveedores y puedan apilarse según las necesidades de la misión. Esto permite que los proyectos CubeSat estén listos para volar con extrema rapidez, normalmente en uno o dos años.

# Tareas

- Buscar bases de datos de IDs
	- https://www.n2yo.com/database/

- TLE
	- Predecir la orbita por la cual se está yendo y por dónde va a pasar el satélite

- Telemetría de un satélite
	- Mensajes de dónde están los satélite

- Los leo se mueven más rápido que la tierra
	- Identificar la órbita para realizar una acción
	- No tienen propulsión, se mueven con la gravedad

Extraer la informacion disponible y que otro calcule la órbita
- Sistema multiagente

TAREA: Agentes que permitan extraer información de páginas de datos 


1. Leer sobre arquitecturas multiagente
2. Protocolo MCP - Agente herramienta
3. Protocolo A2A - Agente-agente
4. N8N / Langraph / LAN chain / Google adk
5. Listado de fuentes públicas con información de satélites (incluyendo TLE)
6. Extraer la info de las fuentes en 5

![[Pasted image 20250903171546.png]]

# Plan: 2026
- [x] Inicio la propuesta del proyecto y revisión guiada del contexto.
- [ ] Inicio del desarrollo del programa y búsqueda de bases de datos
	- [ ] Buscar bases de datos de IDs
- [ ] Implementación de conectores y autenticación a catálogos/TLE.
- [ ] Normalización de datos, validación de TLE, manejo de errores.
- [ ] Construcción de plantilla de \textit{contexto} (JSON/Markdown) y renderer.
- [ ] Prototipo de servicio (CLI/API), caché y trazabilidad de fuentes.
- [ ] Integración con LLM/planificador y diseño de prompts. 
- [ ] Diseño de experimento y conjunto de pruebas (baseline vs. con contexto).
- [ ] Ejecución de experimentos y recolección de métricas.
- [ ] Análisis de resultados y mejora iterativa del pipeline.
- [ ] Documentación técnica y guía de despliegue/reproducibilidad.
- [ ] Redacción del documento de tesis y preparación de presentación.
- [ ] Revisión final, ajustes y entrega/divulgación del documento final. 
# Proyecto Orion
- SATCAT
    - Recolectar datos 
    - Base de datos centralizada
    - Primer módulo
## proyecto
- Agente autónomo
    - Aislar la tarea como un agente
- El input se asume que ya se tiene
- Hacer funcionamiento de microservicio más que de script
# Propósito
- Propósito: El agente debe actuar como un "filtro de realidad" que valide si un satélite puede observar un objetivo en el tiempo solicitado.    
- Responsabilidad: Validar la factibilidad física de la misión (es decir, verificar si el satélite puede estar en el lugar correcto, en el momento correcto, con la visibilidad adecuada).

# Requisitos del sistema
- Recibir datos como el **NORAD ID**, la **fecha del objetivo**, la **ubicación en coordenadas** y los **grados sobre el horizonte**.
- Retornar la **ubicación**, **tiempo de la ventana de contacto**, y si la **misión es posible**.


# Extensiones
- pip install skyfield
- pip install sgp4
- pip install requests
- pip install pandas


# Diccionario TLE
