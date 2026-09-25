# 📊 InfoSport: Motor RAG Corporativo de Gestión Deportiva Municipal

> **Transforma el caos de los datos abiertos y la normativa pública en un asistente conversacional infalible, ultra-anclado a contexto y con cero alucinaciones.**

---

## 🌟 Valor Comercial y Propuesta de Valor

**InfoSport** no es un bot genérico de IA; es un **motor RAG end-to-end de nivel empresarial** diseñado específicamente para resolver el problema de la fragmentación de información en la administración pública y deportiva. 

### ¿Por qué InfoSport?
* **Anclaje Radical al Contexto (Anti-Alucinación):** Nuestro sistema implementa barreras de seguridad (*guardrails*) estrictas. Si la respuesta no está en el corpus documental autorizado, el sistema se abstiene de responder de manera segura en lugar de inventar datos. Un activo crítico para la reputación de tu entidad.
* **Arquitectura de Extracción Multiformato:** Procesa de forma unificada desde documentos narrativos de alta densidad (normativas en PDF) hasta datos tabulares estructurados (tarifas y polideportivos en CSV).
* **Diseñado para el Futuro (Agent-Ready):** La lógica de negocio está 100% aislada de la interfaz gráfica. Cuenta con un contrato de API interna (`responder()`) diseñado específicamente para integrarse directamente como una **Tool** en arquitecturas de Agentes Autónomos o pipelines de MLOps.

---

## 📌 Temática y Corpus de Datos Curado

El sistema está entrenado y especializado en el **Dominio de Deporte Municipal de Madrid**, procesando datos actualizados para el año **2026**.

### 📁 Fuentes Oficiales e Ingesta de Datos:
El corpus combina **múltiples formatos (PDF y CSV)** para una recuperación híbrida óptima:
1. **Formatos de Texto Técnico (PDF):**
   * *Reglamento de Uso de Instalaciones:* Normativa jurídica de acceso y penalizaciones ([Enlace Oficial](https://madrid.es)).
   * *Explicacion campos csv*
2. **Formatos Estructurados (CSV):**
   * *Listado de partidos:* Ubicaciones, equipos, puntos... [Enlace Oficial](https://datos.madrid.es/dataset/211549-0-juegos-deportivos-actual)
   * *Clasificaciones:* posición, partidos ganados, partidos perdidos... [Enlace Oficial](https://datos.madrid.es/dataset/211549-0-juegos-deportivos-actual)

---

## 🧩 Estructura Modular del Proyecto

El código sigue una estricta **separación de responsabilidades**, eliminando los scripts monolíticos para garantizar un mantenimiento empresarial limpio:

```text
project_break_rag/
├── .streamlit/             # Configuración visual de la interfaz de usuario
├── data/                   # Carpeta local del corpus (Documentos PDF y CSV públicos)
├── entregables/            # Documentación estratégica de ingeniería
│   └── informe_decisiones.md  # Informe de experimentos de Chunking, barridos de K y fallos
├── queries/                # Baterías de preguntas de evaluación (In/Out corpus)
├── src/                    # Núcleo modular del Motor RAG (API Interna)
│   ├── load.py             # Ingestores específicos por tipo de archivo (PDF/CSV)
│   ├── chunk.py            # Estrategias avanzadas de fragmentación y solapamiento
│   ├── embed.py            # Generación de vectores densos de significado
│   ├── index.py            # Conector de base de datos vectorial persistente (ChromaDB)
│   ├── retrieve.py         # Algoritmo de búsqueda semántica Top-K
│   ├── generate.py         # Orquestador del LLM con prompts delimitados
│   └── logging_utils.py    # Auditoría de rendimiento (tiempos, modelo, K)
├── .env.example            # Plantilla limpia de variables de entorno (Sin secretos)
├── .gitignore              # Exclusión estricta de entornos virtuales, claves e índices Chroma
├── app.py                  # Interfaz Conversacional Comercial en Streamlit
├── config.py               # Centralización de hiperparámetros (Límites, modelos, K)
├── main.py                 # Interfaz de Línea de Comandos (CLI) para administración
└── requirements.txt        # Dependencias de producción congeladas
```

---

## 🛠️ Requisitos Técnicos, Google Cloud y Configuración de Vertex AI

A diferencia de los proveedores de consumo que utilizan una API Key simple, **InfoSport utiliza Vertex AI (Google Cloud Platform)** como motor de IA de nivel empresarial. Esto garantiza el cumplimiento normativo de datos, aislamiento y latencia óptima.

### 1. Requisitos Previos en Google Cloud Platform (GCP)
Para que el motor RAG pueda conectarse con los modelos de Vertex AI (como `gemini-1.5-pro` o `text-embedding-004`), debes configurar tu infraestructura en GCP:

1. **Crear un Proyecto:** Dispón de un proyecto activo en Google Cloud y copia tu `PROJECT_ID`.
2. **Habilitar las APIs:** Dentro de la consola de GCP, busca y activa la **Vertex AI API**.
3. **Crear una Cuenta de Servicio (Service Account):**
   * Ve a *IAM & Admin* > *Service Accounts*.
   * Crea una cuenta de servicio con los permisos mínimos necesarios: **Vertex AI User** (Usuario de Vertex AI).
4. **Generar la Clave de Acceso (JSON Key):**
   * Entra en la cuenta de servicio recién creada, ve a la pestaña **Keys** (Claves).
   * Haz clic en *Add Key* > *Create new key* y selecciona el formato **JSON**.
   * El archivo se descargará automáticamente a tu ordenador (ej. `gcp-credentials.json`).

---

### 2. Guía de Despliegue Local e Inyección de Credenciales

Sigue estos pasos estrictos para inicializar el entorno e inyectar las credenciales de GCP sin comprometer la seguridad del repositorio:

```bash
# 1. Clonar el repositorio
git clone https://github.com
cd InfoSport

# 2. Crear e iniciar el entorno virtual aislado
python -m venv .venv
source .venv/bin/activate  # En Windows usar: .venv\Scripts\activate

# 3. Instalar las dependencias de producción (incluye google-cloud-aiplatform)
pip install -r requirements.txt

# 4. Configurar las variables de entorno empresariales
cp .env.example .env
```

#### 🛡️ Configuración de Archivos Seguros (`.env` y Credenciales)

1. **Mover la clave de GCP:** Coge el archivo JSON descargado en el paso anterior (`gcp-credentials.json`), renombralo si lo deseas y colócalo en la **raíz de este proyecto**. 
2. **Configurar el archivo `.env`:** Abre el archivo `.env` y rellena los parámetros con los datos de tu infraestructura:

```env
# Configuración del Entorno de Google Cloud
GCP_PROJECT_ID="tu-proyecto-gcp-id-unico"
GCP_LOCATION="europe-west1"  # O la región asignada a tus modelos de Vertex AI

# Ruta local al archivo JSON de credenciales de la Cuenta de Servicio
GOOGLE_APPLICATION_CREDENTIALS="gcp-credentials.json"
```

> ⚠️ **REGLA DE ORO DE SEGURIDAD (ANTI-FILTRACIONES):** Tanto el archivo `.env` como cualquier archivo `.json` de credenciales están estrictamente incluidos en el archivo `.gitignore`. **Nunca, bajo ningún concepto, realices un commit o push de estos archivos al repositorio público de GitHub.** El sistema cargará el JSON en memoria local mediante la variable de entorno nativa de Google `GOOGLE_APPLICATION_CREDENTIALS`.

---

## 🚀 Guía de Uso del Motor (Manual de la CLI)

El motor separa estrictamente los procesos **Offline** (Carga e indexación de datos en frío) de los procesos **Online** (Consultas en tiempo real).

### 1. Inicialización y Recreación del Índice (Proceso Offline)
Para leer los archivos de la carpeta `data/`, aplicar las estrategias de chunking, generar vectores e indexarlos en la base de datos persistente **ChromaDB**:
```bash
python main.py --prepare
python main.py --index
```
*Nota: Si modificas el tamaño del chunk o el modelo de embeddings en `config.py`, ejecuta este comando para destruir la colección antigua y regenerar el índice de manera limpia.*

### 2. Modo Auditoría: Solo Recuperación Semántica
Si quieres inspeccionar qué bloques de texto extrae el buscador semántico según una pregunta, aislando la respuesta de la IA (útil para optimizar el ruido):
```bash
python main.py --query "¿Cuáles son las tarifas de la piscina olímpica?"
```

### 3. Modo RAG Completo en Consola
Para obtener la respuesta estructurada final generada por el LLM, estrictamente anclada al contexto del corpus:
```bash
python main.py --ask "¿Qué ocurre si cancelo una pista con menos de 24 horas de antelación?"
```

---

## 💻 Interfaz Web Comercial (Streamlit)

Para mostrar el producto a clientes finales o usuarios no técnicos de la federación deportiva, InfoSport incluye una aplicación web interactiva que simula una experiencia de producción.

Para lanzar la aplicación:
```bash
streamlit run app.py
```

### Características de la UI de Control:
* **Chat de Conversación Fluido:** Diseñado mediante componentes nativos `st.chat_input` y `st.chat_message`.
* **Transparencia en la Evidencia:** Al desplegar una respuesta, el usuario puede inspeccionar visualmente los **Chunks de Contexto Recuperados**, visualizando el archivo `source` original del que se extrajo la información.
* **Cuadro de Mandos de Métricas (Dashboard):** Visualización en tiempo real de los metadatos de rendimiento de cada interacción:
  * Valor de recuperación $K$ activo.
  * Número total de chunks procesados por el prompt.
  * Tiempo exacto de latencia en la generación (segundos).
  * Identificación del modelo fundacional utilizado.

---

## 📋 Normas de Ingeniería, Calidad y Gobernanza del Proyecto

Para garantizar que el software sea robusto y escalable, el desarrollo sigue un estricto flujo de ingeniería de software corporativa:

### ⚙️ Configuración y Gobierno de Datos (`config.py`)
Cualquier cambio de comportamiento del RAG se gestiona centralizadamente desde el archivo de configuración. Parámetros auditables:
* `TOP_K`: Número de fragmentos inyectados al prompt (Evaluado exhaustivamente en valores como `K=1`, `K=3` y `K=5` para mitigar el ruido).
* `CHUNK_SIZE` y `CHUNK_OVERLAP`: Control numérico de la granularidad de la información.
* `PROMPT_TEMPLATES`: Secciones rígidamente delimitadas mediante bloques claros:

### 🌿 Políticas de Trabajo en Equipo y Control de Versiones (Git)
* **Garantía de Estabilidad:** La rama `main` es sagrada; solo contiene versiones estables de producción aptas para demostración.
* **Integración Continua de Equipo:** Queda terminantemente prohibido hacer push directo sobre `main` o `develop`. Todo cambio de funcionalidad se realiza mediante ramas secundarias descriptivas (p. ej., `feature/index-retrieval`, `feature/streamlit-ui`) y requiere una **Pull Request (PR) revisada, comentada y aprobada** por los miembros del equipo antes de su fusión.
