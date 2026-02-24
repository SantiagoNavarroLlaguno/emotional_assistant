# API de Análisis Emocional

API RESTful para análisis de conversaciones de asistente emocional con IA. Procesa transcripciones de chat, identifica sesiones, detecta momentos clave y realiza análisis emocional.

## Inicio Rápido

Ver [SETUP.md](SETUP.md) para instrucciones completas de instalación y ejemplos de uso.
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Características

- **Detección de sesiones**: Identifica automáticamente sesiones separadas por silencios de 10+ minutos
- **Análisis de momentos clave**: Cuenta preguntas (mensajes con "?") y acciones (palabras clave: necesito, podrías, ayúdame, tarea, hacer)
- **Análisis emocional optimizado**: Agrupa texto en bloques de 100+ caracteres para reducir llamadas a API
- **Validación por psicólogos**: Comando CLI y Django admin para auditoría manual
- **Tests comprehensivos**: 9 tests cubriendo toda la lógica de negocio

## Uso del API

### POST /api/analyze/
```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": [
      {
        "timestamp": "2025-10-27T10:00:00Z",
        "role": "assistant",
        "text": "Hola, ¿cómo te sientes hoy?"
      },
      {
        "timestamp": "2025-10-27T10:15:30Z",
        "role": "user",
        "text": "Me siento bien, necesito hablar sobre mi día"
      }
    ]
  }'
```

**Respuesta (201 Created)**:
```json
{
  "analysis_summary": {
    "session_count": 1,
    "key_moments": {
      "questions_asked": 1,
      "actions_identified": 1
    },
    "emotion_analysis_results": [
      {"emotion": "Happiness"}
    ]
  }
}
```

## Decisiones de Diseño

### Arquitectura de Tres Modelos
**Decisión**: `Conversation`, `Message`, `AnalysisReport` separados

**Razón**: Permite consultas eficientes, facilita auditoría por psicólogos, y el reporte puede evolucionar sin afectar datos históricos.

### Servicio de Análisis Independiente
**Decisión**: Clase `ConversationAnalyzer` en `services.py`

**Razón**: Testeable sin Django, reutilizable en tasks asíncronos o scripts, y separa lógica de negocio de views.

### Campo `session_number` en Message
**Decisión**: Guardar número de sesión al crear el mensaje

**Razón**: Evita recálculo en cada consulta, garantiza consistencia histórica para validación, y permite queries eficientes.

### Transacciones Atómicas
**Decisión**: `@transaction.atomic()` en el endpoint

**Razón**: Garantiza integridad (todo se guarda o nada), previene datos huérfanos, y es crítico para validación confiable.

### Optimización de Llamadas AI
**Decisión**: Acumular texto hasta 100+ caracteres

**Razón**: Reduce costos significativamente, proporciona mejor contexto, y balancea granularidad vs. eficiencia.

### bulk_create para Mensajes
**Decisión**: Insertar todos los mensajes en una operación

**Razón**: 1 query vs N queries mejora performance drásticamente en conversaciones largas.

## Trade-offs

### Lo que sacrifiqué conscientemente:

**1. Análisis emocional simulado** (`random.choices()`)
- **Por qué**: Enfoque en arquitectura; integración real es trivial (cambiar función, agregar API key)
- **Mejora futura**: Integrar OpenAI/Anthropic o entrenar modelo propio

**2. Procesamiento síncrono**
- **Por qué**: Simplicidad; conversaciones típicas < 1 segundo
- **Cuándo migrarlo**: Conversaciones 500+ mensajes, análisis real tarda 5+ segundos, o alta concurrencia
- **Mejora futura**: Celery + Redis con webhooks

**3. Sin autenticación**
- **Por qué**: No especificado en requirements; permite testing inmediato
- **Producción**: JWT + rate limiting esencial

**4. SQLite en lugar de PostgreSQL**
- **Por qué**: Zero-config para evaluación; suficiente para < 1M registros
- **Producción**: Migrar a PostgreSQL (mejor concurrencia, JSONField indexado, full-text search)

**5. Sin paginación**
- **Por qué**: Response de análisis es pequeño (< 1KB); no hay endpoint de listado
- **Mejora futura**: Necesario para `GET /api/conversations/`

1 palabra tiene en promedio 5 chars
1 char 1 byte
5 bytes
10 palabras = 50 bytes
4 oraciones por conv = 200/250 bytes
4-5 sesiones por conv - 

## Mejoras con Más Tiempo

**1. Dashboard de validación para psicólogos**
- UI amigable (no Django admin técnico)
- Visualización lado-a-lado: transcripción vs análisis
- Correcciones in-line y exportación a PDF

**2. Versionado de análisis**
- Guardar historial de recálculos
- Comparar versiones y hacer rollback
- Métricas de mejora de algoritmo

**3. WebSockets para análisis en tiempo real**
- Alertas inmediatas en emociones críticas (rage, fear)
- Dashboard en vivo para supervisores
- Intervención de psicólogo durante conversación activa

**4. Machine Learning con feedback**
- Psicólogos corrigen emociones → datos de entrenamiento
- Fine-tuning mensual de modelo
- A/B testing de versiones

**5. Caché con Redis**
- Resultados recientes en memoria
- Reduce queries en dashboards

## Validación por Psicólogos

### Comando CLI (Recomendado)

Para validar cualquier conversación:
```bash
python manage.py validate_analysis <conversation_id>
```

**Output**:
```
=== Análisis de Conversación #1 ===

TRANSCRIPCIÓN:
[Sesión 1] 2025-11-15 08:00:00 - ASSISTANT:
  Buenos días, ¿cómo amaneciste hoy?

[Sesión 1] 2025-11-15 08:03:00 - USER:
  Me siento muy triste. ¿Podrías ayudarme?

RESUMEN:
Sesiones: 1
Preguntas: 2
Acciones: 1

PREGUNTAS ENCONTRADAS:
  • Buenos días, ¿cómo amaneciste hoy?
  • Me siento muy triste. ¿Podrías ayudarme?

ACCIONES IDENTIFICADAS:
  • Me siento muy triste. ¿Podrías ayudarme?

EMOCIONES:
  • Sadness
  • Fear
```

### Django Admin

Acceder a `http://localhost:8000/admin/` para:
- Ver transcripciones completas con timestamps
- Filtrar mensajes por sesión, rol, fecha
- Comparar análisis con datos originales
- Buscar por texto en mensajes

### Proceso de Validación Recomendado

**Fase 1 - Muestra aleatoria (primera semana)**:
```bash
# Validar 20 conversaciones aleatorias
for i in {1..20}; do python manage.py validate_analysis $i; done
```

**Criterios de éxito**:
- Sesiones: > 95% precisión
- Preguntas: > 98% precisión  
- Acciones: > 90% precisión

**Fase 2 - Casos edge**:
- Conversaciones muy cortas/largas
- Múltiples sesiones
- Sin preguntas/acciones

**Fase 3 - Validar emociones**:
- Leer texto → asignar emoción manualmente → comparar
- Documentar discrepancias para mejora futura

## Tests
```bash
python manage.py test apps.analysis
```

**Cobertura**: 9 tests para sesiones, preguntas, acciones, emociones, API, validación de entrada.

## Estructura
```
backend/
├── apps/analysis/
│   ├── management/commands/
│   │   └── validate_analysis.py    # Comando de validación
│   ├── models.py                   # Conversation, Message, AnalysisReport
│   ├── services.py                 # ConversationAnalyzer
│   ├── views.py                    # API endpoint
│   ├── serializers.py              # DRF serializers
│   ├── tests.py                    # Tests
│   └── admin.py                    # Django admin config
├── core/
│   ├── settings.py
│   └── urls.py
├── requirements.txt
├── README.md                       # Este archivo
└── SETUP.md                        # Guía de instalación
```

## Licencia

Proyecto de evaluación técnica
