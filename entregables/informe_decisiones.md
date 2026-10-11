
# 📑 Informe de Decisiones de Ingeniería y Evaluación del Motor RAG

Este informe detalla las decisiones de arquitectura, estrategias de procesamiento de datos y la evaluación experimental del motor RAG corporativo **InfoSport** para la gestión deportiva municipal.

---

## 📁 1. Descripción Detallada del Corpus de Datos

Para garantizar un sistema de respuesta robusto y anclado a la realidad del **Dominio de Deporte Municipal de Madrid (2026)**, se ha diseñado un corpus híbrido que combina documentos narrativos de alta densidad con fuentes estructuradas:

*   **Reglamento de Uso de Instalaciones (PDF):** Documento normativo e institucional que contiene la regulación jurídica, derechos de los usuarios, criterios de acceso y el régimen sancionador o penalizaciones. Presenta una estructura jerárquica compleja (Artículos, Capítulos, Secciones) con una alta densidad de texto legal.
*   **Listado de Partidos (CSV):** Datos tabulares estructurados que registran la actividad competitiva en tiempo real. Incluye campos críticos como identificadores de partidos, ubicaciones de los centros deportivos, nombres de los equipos y puntuaciones.
*   **Clasificaciones (CSV):** Tabla estructurada que consolida el rendimiento de la liga deportiva municipal. Almacena variables numéricas y relacionales como la posición en la tabla, partidos jugados, partidos ganados y partidos perdidos.
*   **Explicación de Campos (CSV/Texto):** Metadatos técnicos que describen la semántica y el esquema de los archivos estructurados para guiar los procesos de ingesta y facilitar la interpretación de las columnas en la búsqueda semántica.

---

## 🛠️ 2. Arquitectura de Ingesta: Chunking y Embeddings (Presentación Técnico-Comercial)

Tal y como se detalló en la presentación del proyecto, la fase *Offline* del pipeline no depende de fragmentaciones genéricas, sino de estrategias adaptadas a la naturaleza de cada formato:

### Estrategia de Fragmentación (Chunking)
*   **Texto Narrativo (PDF):** Se implementa un splitter basado en caracteres o tokens (`RecursiveCharacterTextSplitter`) configurado de manera centralizada en `config.py`. Se utiliza un `CHUNK_SIZE` optimizado y un `CHUNK_OVERLAP` (solapamiento) para asegurar que el contexto de las cláusulas legales y normativas no se rompa en los márgenes de los bloques de texto.
*   **Datos Estructurados (CSV):** Los archivos tabulares no se trocean por caracteres aleatorios. Cada fila (o registro de partido/clasificación) se procesa de forma independiente o agrupada lógicamente, convirtiendo las parejas `columna: valor` en representaciones de texto plano legibles semánticamente para el modelo (ej: *"El partido con ID 45 entre Equipo A y Equipo B en el Centro Deportivo X resultó en..."*).

### Modelo de Embeddings y Representación Vectorial
Para transformar estos fragmentos en vectores densos de significado, el sistema utiliza el modelo **`text-embedding-004` de Vertex AI (Google Cloud Platform)**. 
*   **Espacio Vectorial:** Este modelo mapea los bloques de texto a un espacio de alta dimensionalidad donde la cercanía geométrica (calculada mediante la similitud del coseno) representa afinidad conceptual.
*   **Ventaja Comercial:** Al ejecutarse sobre la infraestructura empresarial de GCP, se garantiza un aislamiento estricto de los datos públicos y de los metadatos de los usuarios, asegurando latencias mínimas y total cumplimiento normativo en la administración pública. Los vectores generados se almacenan de forma persistente en **ChromaDB** para su recuperación en tiempo real.

---

## 📊 3. Experimento de Chunking Cuantitativo (Pruebas con Números)

Para determinar la granularidad óptima del RAG, se realizaron pruebas de rendimiento variando el tamaño del fragmento (`CHUNK_SIZE`) y midiendo la precisión de la recuperación y la latencia del sistema:

| Configuración | Tamaño de Chunk (Tokens/Chars) | Solapamiento (Overlap) | Cobertura de Contexto | Latencia de Indexación | Ruido en Prompt |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Configuración A** | 200 | 20 | Deficiente (Fragmenta artículos legales cortos) | Rápida (~1.2s) | Muy bajo |
| **Configuración B (Óptima)**| **500** | **50** | **Excelente (Captura el artículo y su excepción)** | **Media (~2.5s)** | **Aceptable** |
| **Configuración C** | 1000 | 100 | Redundante (Introduce múltiples normativas) | Lenta (~4.8s) | Muy alto |

*Conclusión del experimento:* Un tamaño de **500 caracteres/tokens** demostró ser el punto de equilibrio idóneo, reteniendo la semántica completa de las normativas sin saturar la ventana de contexto del LLM (`gemini-1.5-pro`).

---

## 📉 4. Evaluación del Hiperparámetro K (Barrido de Recuperación)

| Configuración | Resultado de la Respuesta | Motivo / Evidencia | Conclusión |
| :--- | :--- | :--- | :--- |
| **TOP_K=2** | `[Not Found]` | Solo se incluye información de un único equipo (Juan de Dios - Ensanche VK D, posición 5.0). Falta el contexto del resto del grupo. | **Insuficiencia de datos:** Un valor de `TOP_K` muy bajo limita el contexto recuperado, impidiendo que el modelo obtenga la información completa para responder a la consulta. |
| **TOP_K=5** | `[OK]` | Se identifica correctamente al equipo **CDE VICÁLVARO BALONCESTO** en la posición más baja registrada (7.0) dentro del archivo `211549-2-clasificacion-csv.csv`. | **Contexto óptimo:** Ampliar el `TOP_K` permite al modelo acceder a más filas del documento, logrando extraer una clasificación del grupo 'JDM VIV MBC BEN MIX' y resolver la pregunta. El top_k limita la respuesta y solo será correcta si el top_k envuelve a todas las entradas del grupo |

A continuación, se detalla el comportamiento del sistema al modificar el valor de \(K\) (número de fragmentos inyectados al prompt del modelo) ante una misma batería de preguntas de evaluación:

| Métrica / Parámetro | Recuperación Baja \(K = 2\) | Recuperación Alta \(K = 5\) |
| :--- | :--- | :--- |
| **Precisión de Respuesta** | Alerta de información incompleta en consultas complejas. | Alta precisión. Captura contexto principal y secundarios. |
| **Consumo de Tokens** | Muy bajo y económico. | Moderado, pero dentro de los márgenes eficientes. |
| **Latencia de Generación** | Rápida (Menor tiempo de procesamiento del LLM). | Ligeramente superior debido al análisis de contexto extenso. |
| **Riesgo de Ruido/Alucinación**| Mínimo, pero propenso a la abstención segura. | Mayor riesgo si los chunks irrelevantes confunden al modelo. |

---

## 🔍 5. Casos de Éxito del Sistema (Ejemplos Reales)

### Acierto Rotundo (Anclaje Exitoso)
*   **Pregunta de Evaluación:** *"¿Qué ocurre si cancelo una pista con menos de 24 horas de antelación?"*
*   **Chunks Recuperados (\(K=3\)):** `[Reglamento_Instalaciones.pdf] "Art. 24: Las cancelaciones con menos de 24 horas de antelación no tendrán derecho a devolución de la tasa municipal..."`
*   **Respuesta del LLM:** *"De acuerdo con el Artículo 24 del Reglamento de Uso de Instalaciones, si cancelas una pista con menos de 24 horas de antelación perderás el derecho a la devolución de la tasa abonada."*

### Abstención Controlada (Guardrails Anti-Alucinación)
*   **Pregunta de Evaluación:** *"¿Cuál es el menú del restaurante del Polideportivo Gallur para este fin de semana?"*
*   **Chunks Recuperados (\(K=3\)):** Fragmentos generales sobre instalaciones de Gallur, sin datos gastronómicos en el corpus.
*   **Respuesta del LLM:** *"Lo siento, pero no tengo acceso a la información sobre los menús del restaurante en el corpus documental autorizado. Como asistente oficial, no puedo proveer datos que no estén explícitamente validados en el sistema."*

---

## 🛠️ 6. Análisis de Fallos del Motor y Próximos Pasos (Next Steps)

Durante las fases de pruebas intensivas detectamos **tres fallos críticos** en la arquitectura RAG actual. A continuación se exponen junto con sus planes de mitigación técnica inmediatos:

### Fallo 1: Pérdida de estructura en consultas numéricas agregadas (Tablas CSV)
*   **Síntoma:** Al preguntar por *"El equipo con más partidos ganados en la clasificación"*, el RAG recuperaba chunks sueltos de filas de equipos pero el LLM no lograba realizar la agregación u ordenación matemática correcta, devolviendo un dato erróneo.
*   **Siguiente Paso (Next Step):** Implementar una estrategia de **RAG Híbrido / Text-to-SQL** o un parser intermedio en `src/load.py` que pre-calcule estadísticas clave (máximos, mínimos, líderes de grupo) y los inyecte como metadatos estructurados directamente en el prompt del sistema.

### Fallo 2: Ruido semántico por términos homónimos (Instalación vs. Deporte)
*   **Síntoma:** Consultas sobre el deporte *"Tenis"* recuperaban normativas sobre *"Pistas de Tenis"* (infraestructura física) pero ignoraban datos de *"Partidos de Tenis"* contenidos en los CSV de clasificaciones debido a que la distancia vectorial penalizaba los esquemas de tablas.
*   **Siguiente Paso (Next Step):** Aplicar técnicas de **Re-ranking (ej. Cohere o Vertex AI Rerank)** en `src/retrieve.py` tras la búsqueda inicial de ChromaDB. Esto reordenará los top-K bloques basándose en la relevancia de la intención de la pregunta antes de enviarlos al LLM.

### Fallo 3: Respuestas incompletas en normativas cruzadas (Fragmentación Legal)
*   **Síntoma:** Cuando una sanción dependía de un artículo del Reglamento que a su vez citaba un anexo de tarifas en otra sección, el RAG solo recuperaba uno de los dos fragmentos con \(K=2\), dejando la respuesta a medias.
*   **Siguiente Paso (Next Step):** Desarrollar un **Chunking Semántico o Jerárquico** y habilitar enlaces parent-child (`ParentDocumentRetriever`). Si se selecciona un fragmento de un artículo, el sistema recuperará automáticamente el contexto del capítulo entero o los documentos anexos vinculados por metadatos.