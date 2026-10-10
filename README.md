# InfoSport
Sistema RAG para la consulta de información deportiva municipal

InfoSport es un sistema de *Retrieval-Augmented Generation* (RAG) orientado a la consulta de información relacionada con la gestión deportiva municipal. El proyecto integra fuentes documentales heterogéneas, técnicas de recuperación semántica y modelos de lenguaje para proporcionar respuestas fundamentadas en un corpus de información previamente seleccionado.

El sistema se ha desarrollado tomando como dominio de aplicación la gestión deportiva municipal de Madrid, utilizando información procedente de fuentes públicas y estructurada en diferentes formatos, principalmente documentos PDF y archivos CSV.

El objetivo del proyecto es diseñar e implementar una arquitectura RAG que permita combinar recuperación de información, representación vectorial y generación de lenguaje natural en un dominio concreto y controlado.

## 1. Objetivos
Los principales objetivos del proyecto son:
* Diseñar e implementar una arquitectura RAG modular.
* Integrar información procedente de documentos con estructuras diferentes.
* Transformar el corpus documental en representaciones vectoriales.
* Recuperar los fragmentos de información más relevantes ante una consulta.
* Utilizar un modelo de lenguaje para generar respuestas a partir del contexto recuperado.
* Reducir la generación de información no respaldada por las fuentes.
* Separar las fases de ingesta e indexación de las fases de consulta y generación.
* Proporcionar mecanismos para analizar el comportamiento del sistema y sus parámetros.
* Exponer el sistema mediante una interfaz de línea de comandos y una aplicación web desarrollada con Streamlit.

## 2. Motivación
La información relacionada con la actividad deportiva municipal se encuentra distribuida entre diferentes fuentes y formatos. Reglamentos, instalaciones, partidos, clasificaciones y otros datos pueden presentar estructuras heterogéneas, lo que dificulta su consulta mediante mecanismos tradicionales.

Desde una perspectiva de recuperación de información, este escenario plantea dos problemas principales:
1. **Heterogeneidad documental:** la información puede estar almacenada tanto en documentos textuales como en estructuras tabulares.
2. **Necesidad de contextualización:** una respuesta generada automáticamente debe estar fundamentada en información disponible en las fuentes de referencia.

InfoSport aborda estos problemas mediante una arquitectura RAG. En lugar de solicitar al modelo de lenguaje que genere una respuesta únicamente a partir de sus parámetros internos, el sistema realiza previamente una búsqueda sobre el corpus y proporciona al modelo los fragmentos considerados relevantes.

El funcionamiento general puede representarse de la siguiente manera:
```text
┌──────────────────┐
│ Fuentes de datos │
│   PDF / CSV      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     Ingesta      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     Chunking     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    Embeddings    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Índice vectorial │
│    ChromaDB      │
└────────┬─────────┘
         │
 Consulta del usuario
         │
         ▼
┌──────────────────┐
│ Recuperación     │
│     Top-K        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Modelo de        │
│    lenguaje      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│     Respuesta    │
└──────────────────┘
3. Arquitectura del sistemaLa arquitectura del proyecto se divide en varias etapas independientes.3.1. Ingesta de datosLa primera fase consiste en cargar las fuentes que forman el corpus de conocimiento.El sistema contempla diferentes tipos de entrada:PDF, utilizado principalmente para información normativa y documental.CSV, utilizado para información estructurada como partidos, clasificaciones y otros registros deportivos.Esta separación permite adaptar el proceso de extracción a las características de cada formato.3.2. Fragmentación documentalUna vez extraída la información, los documentos se dividen en fragmentos o chunks.La fragmentación permite trabajar con unidades de información más pequeñas y facilita posteriormente la recuperación semántica.El sistema permite controlar parámetros como:CHUNK_SIZE: tamaño de cada fragmento.CHUNK_OVERLAP: cantidad de información compartida entre fragmentos consecutivos.Estos parámetros tienen una influencia directa sobre la recuperación. Una fragmentación demasiado pequeña puede provocar pérdida de contexto, mientras que una excesivamente grande puede introducir información irrelevante.3.3. Representación vectorialCada fragmento se transforma en un vector mediante un modelo de embeddings.Estos vectores permiten representar semánticamente los fragmentos del corpus y realizar búsquedas basadas en similitud.De forma simplificada:Texto → Modelo de embeddings → VectorLa consulta del usuario sigue un proceso equivalente:Consulta → Modelo de embeddings → Vector de consultaLa comparación entre ambos vectores permite identificar los fragmentos que presentan mayor relación semántica con la pregunta.3.4. Índice vectorialLos embeddings generados se almacenan en un índice vectorial mediante ChromaDB.Este componente permite realizar consultas de similitud y recuperar los fragmentos más relevantes para una determinada pregunta.La arquitectura utiliza un mecanismo de recuperación Top-K, donde K determina el número de fragmentos que se incorporan al contexto utilizado posteriormente por el modelo de lenguaje.El parámetro TOP_K se encuentra centralizado en la configuración del proyecto para facilitar la experimentación.3.5. Generación aumentada mediante recuperaciónTras recuperar los fragmentos relevantes, estos se incorporan al contexto proporcionado al modelo de lenguaje.El proceso general es:PlaintextPregunta
   │
   ▼
Embedding de la pregunta
   │
   ▼
Búsqueda semántica
   │
   ▼
Top-K fragmentos relevantes
   │
   ▼
Construcción del contexto
   │
   ▼
Modelo de lenguaje
   │
   ▼
Respuesta
El modelo no recibe únicamente la pregunta, sino también la información recuperada desde el corpus.Este mecanismo permite condicionar la generación sobre el conocimiento disponible en las fuentes utilizadas por el sistema.4. Control de respuestasUno de los aspectos relevantes del proyecto es limitar la generación de información que no se encuentre respaldada por el corpus.Para ello, la generación se realiza mediante instrucciones que delimitan el contexto disponible para el modelo.Cuando una consulta no puede ser respondida adecuadamente a partir de la información recuperada, el sistema puede evitar completar la respuesta mediante información externa al corpus.Este comportamiento resulta especialmente relevante en dominios como la normativa deportiva, donde una respuesta aparentemente plausible pero incorrecta puede conducir a interpretaciones erróneas.Por tanto, el sistema prioriza:Trazabilidad de la información.Contextualización de las respuestas.Reducción de respuestas no fundamentadas.Separación entre recuperación y generación.5. Corpus de informaciónEl corpus utilizado por InfoSport está especializado en información relacionada con el deporte municipal de Madrid.5.1. Documentación normativaLos documentos PDF permiten incorporar información de carácter textual y normativo, como reglamentos relacionados con la utilización de instalaciones deportivas.5.2. Datos estructuradosLos archivos CSV contienen información que puede ser representada mediante registros tabulares, incluyendo datos relativos a:partidos;equipos;ubicaciones;puntos;clasificaciones;resultados deportivos.El uso simultáneo de fuentes documentales y tabulares permite estudiar el comportamiento de un sistema RAG sobre información de naturaleza heterogénea.6. Estructura del repositorioLa organización del proyecto sigue una separación de responsabilidades entre los diferentes componentes:PlaintextInfoSport/
│
├── .streamlit/
│   └── Configuración de la aplicación web
│
├── data/
│   └── Corpus documental utilizado por el sistema
│
├── entregables/
│   └── Documentación y resultados
│
├── queries/
│   └── Archivo json con las preguntas de evaluacion
│
├── src/
│   ├── load.py
│   ├── chunk.py
│   ├── embed.py
│   ├── index.py
│   ├── retrieve.py
│   ├── generate.py
│   ├── eval.py
│   └── logging_utils.py
│
├── .env.example
├── .gitignore
├── app.py
├── config.py
├── main.py
└── requirements.txt
src/load.py: Implementa la carga y extracción de información a partir de las diferentes fuentes documentales.src/chunk.py: Contiene la lógica relacionada con la fragmentación del contenido y la configuración del solapamiento entre fragmentos.src/embed.py: Gestiona la generación de representaciones vectoriales mediante modelos de embeddings.src/index.py: Gestiona la creación y utilización del índice vectorial basado en ChromaDB.src/retrieve.py: Implementa la recuperación semántica de los fragmentos más relevantes para una consulta.src/generate.py: Gestiona la interacción con el modelo de lenguaje y la generación de respuestas a partir del contexto recuperado.src/eval.py: Gestiona la evaluación del modelo con preguntas preestablecidas.src/logging_utils.py: Centraliza la información relacionada con la monitorización y registro de las ejecuciones.config.py: Centraliza los principales parámetros configurables del sistema (tamaño de fragmentos, solapamiento, valor de TOP_K, modelos, prompts, etc.).main.py: Proporciona una interfaz de línea de comandos para ejecutar las diferentes fases del sistema.app.py: Implementa la interfaz web interactiva mediante Streamlit.7. Flujo de ejecuciónEl sistema distingue entre dos procesos principales: preparación del conocimiento y consulta.7.1. Preparación del corpusEl procesamiento inicial del corpus se realiza antes de efectuar consultas mediante:Bashpython main.py --prepare
python main.py --index
La primera orden prepara la información disponible en data/, mientras que la segunda genera y almacena el índice vectorial.Esta separación evita tener que repetir el procesamiento completo del corpus cada vez que se realiza una consulta.Si se modifican parámetros fundamentales como el tamaño de los fragmentos o el modelo de embeddings, se debe regenerar el índice para mantener la coherencia entre el corpus y sus representaciones vectoriales.7.2. Consulta semánticaEl sistema permite consultar directamente el componente de recuperación:Bashpython main.py --query "¿Cuáles son las tarifas de la piscina olímpica?"
Este modo permite analizar qué información considera relevante el sistema sin introducir todavía el modelo generativo, resultando útil para evaluar de forma independiente el comportamiento del recuperador.7.3. Consulta RAG completaPara ejecutar el flujo completo:Bashpython main.py --ask "¿Qué ocurre si cancelo una pista con menos de 24 horas de antelación?"
En este caso se ejecutan las fases de recuperación y generación para producir una respuesta contextualizada.8. Aplicación webEl proyecto incorpora una interfaz web desarrollada mediante Streamlit.Para ejecutarla:Bashstreamlit run app.py
La aplicación proporciona una interfaz conversacional desde la que realizar consultas sobre el corpus.Además de mostrar la respuesta generada, la interfaz permite inspeccionar información relacionada con el proceso de recuperación y diferentes métricas de ejecución.Entre los elementos disponibles se encuentran:fragmentos recuperados;valor de K;latencia de generación;fuentes asociadas al contexto recuperado.De esta manera, la interfaz puede utilizarse tanto como mecanismo de consulta como herramienta para analizar el comportamiento del sistema.9. RequisitosEl proyecto está desarrollado en Python y utiliza las dependencias especificadas en requirements.txt.El sistema utiliza servicios de Google Cloud Vertex AI para las funcionalidades relacionadas con los modelos de lenguaje y la generación de embeddings.Para ejecutar el proyecto es necesario disponer de:Python;un proyecto de Google Cloud;Vertex AI habilitado;credenciales con los permisos necesarios;las dependencias Python del proyecto.10. Configuración del entornoEn primer lugar, se crea un entorno virtual:Bashpython -m venv .venv
En Linux/macOS:Bashsource .venv/bin/activate
En Windows:Bash.venv\Scripts\activate
Posteriormente se instalan las dependencias:Bashpip install -r requirements.txt
Se debe crear el archivo de configuración local a partir de la plantilla:Bashcp .env.example .env
La configuración incluye parámetros como:Fragmento de códigoGCP_PROJECT_ID="tu-proyecto-gcp-id"
GCP_LOCATION="europe-west1"
GOOGLE_APPLICATION_CREDENTIALS="gcp-credentials.json"
Las credenciales deben mantenerse fuera del control de versiones y no deben incorporarse al repositorio.11. Evaluación y experimentaciónEl diseño del proyecto permite analizar de forma independiente diferentes componentes de la arquitectura RAG.Entre los parámetros susceptibles de evaluación se encuentran:Tamaño del fragmento: El valor de CHUNK_SIZE determina la cantidad de información contenida en cada unidad recuperable. (Nota: si una fila de un CSV pasada a documento supera CHUNK_SIZE, pasa a ser el nuevo tamaño del chunk).Solapamiento: CHUNK_OVERLAP permite conservar continuidad contextual entre fragmentos consecutivos.Número de resultados: TOP_K controla cuántos fragmentos recuperados se proporcionan al modelo de lenguaje.El proyecto contempla la comparación de diferentes valores de K, entre ellos:K = 2K = 5La finalidad de esta experimentación es estudiar el compromiso existente entre cantidad de contexto y presencia de información irrelevante.12. Separación entre recuperación y generaciónUna característica metodológica importante es la posibilidad de evaluar por separado:La calidad de la recuperación, analizando los fragmentos obtenidos.La calidad de la generación, estudiando la respuesta producida a partir de dichos fragmentos.Esta separación facilita la identificación de errores.Por ejemplo, una respuesta incorrecta puede deberse a:PlaintextConsulta
   │
   ├── Recuperación incorrecta
   │       └── Se recupera información irrelevante
   │
   └── Recuperación correcta
           └── El modelo interpreta incorrectamente el contexto
Distinguir ambos escenarios resulta fundamental para evaluar de manera rigurosa una arquitectura RAG.13. TrazabilidadInfoSport incorpora mecanismos destinados a facilitar la inspección de la información utilizada durante una respuesta.La interfaz permite visualizar los fragmentos recuperados y asociarlos con su fuente original.De esta manera, una respuesta puede analizarse siguiendo el recorrido:Respuesta → Contexto utilizado → Chunk recuperado → Documento originalEsta característica facilita la auditoría del sistema y permite comprobar si las respuestas generadas están respaldadas por el corpus disponible.14. Gobernanza y control de versionesEl desarrollo del proyecto sigue un modelo basado en ramas y Pull Requests.La rama main se reserva para versiones estables, mientras que las nuevas funcionalidades se desarrollan mediante ramas específicas (por ejemplo, feature/index-retrieval, feature/streamlit-ui).La incorporación de cambios mediante Pull Requests permite revisar las modificaciones antes de integrarlas en las ramas principales, facilitando la estabilidad del sistema y la trazabilidad de los cambios.15. LimitacionesA pesar de las ventajas de la arquitectura propuesta, el sistema presenta determinadas limitaciones:Dependencia del corpus: La capacidad de respuesta está directamente condicionada por la información disponible en las fuentes utilizadas.Dependencia del proceso de recuperación: Si el recuperador no identifica los fragmentos adecuados, el modelo generativo puede carecer de la información necesaria para construir una respuesta correcta.Dependencia de los modelos: Tanto los embeddings como el modelo de lenguaje pueden influir en el comportamiento final del sistema.Actualización de la información: Cuando las fuentes originales cambian, es necesario actualizar el corpus y regenerar las representaciones e índices correspondientes.Por estas razones, un sistema RAG no elimina completamente los errores, sino que proporciona una arquitectura para controlar, estudiar y reducir determinados tipos de errores asociados a la generación de lenguaje.16. Tecnologías utilizadasTecnologíaFunciónPythonLenguaje principalGoogle Cloud Vertex AIServicios de IA generativa y embeddingsChromaDBAlmacenamiento e indexación vectorialStreamlitInterfaz webCSV / PDFFuentes de informaciónGit / GitHubControl de versiones y colaboración17. ConclusionesInfoSport constituye una implementación de una arquitectura Retrieval-Augmented Generation aplicada a un dominio deportivo específico.El proyecto aborda las principales etapas necesarias para construir un sistema RAG:Ingesta → Procesamiento → Chunking → Embeddings → Indexación → Recuperación → Generación → EvaluaciónLa separación modular de estas etapas permite experimentar con diferentes configuraciones y analizar individualmente los componentes del sistema.Asimismo, la incorporación de mecanismos de trazabilidad, configuración centralizada y evaluación del proceso de recuperación proporciona una base para estudiar el comportamiento de modelos generativos condicionados por un corpus documental específico.En consecuencia, InfoSport puede considerarse tanto una aplicación para la consulta de información deportiva municipal como un entorno experimental para el estudio de técnicas de recuperación semántica y generación aumentada mediante recuperación.18. Fuentes de informaciónLas fuentes utilizadas por el proyecto proceden principalmente de organismos y portales públicos relacionados con la ciudad de Madrid.Para reproducir los experimentos, se recomienda consultar los materiales incluidos en las carpetas data/, entregables/ y queries/ del repositorio.