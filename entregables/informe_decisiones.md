
| Configuración | Resultado de la Respuesta | Motivo / Evidencia | Conclusión |
| :--- | :--- | :--- | :--- |
| **TOP_K=2** | `[Not Found]` | Solo se incluye información de un único equipo (Juan de Dios - Ensanche VK D, posición 5.0). Falta el contexto del resto del grupo. | **Insuficiencia de datos:** Un valor de `TOP_K` muy bajo limita el contexto recuperado, impidiendo que el modelo obtenga la información completa para responder a la consulta. |
| **TOP_K=5** | `[OK]` | Se identifica correctamente al equipo **CDE VICÁLVARO BALONCESTO** en la posición más baja registrada (7.0) dentro del archivo `211549-2-clasificacion-csv.csv`. | **Contexto óptimo:** Ampliar el `TOP_K` permite al modelo acceder a más filas del documento, logrando extraer una clasificación del grupo 'JDM VIV MBC BEN MIX' y resolver la pregunta. El top_k limita la respuesta y solo será correcta si el top_k envuelve a todas las entradas del grupo |
