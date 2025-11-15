# Guía de Configuración Rápida

Esta guía te ayudará a ejecutar la API de Análisis Emocional en menos de 5 minutos.

## Prerequisitos

- Python 3.8+
- pip
- Git

## Instalación
```bash
# Clonar el repositorio
git clone https://github.com/SantiagoNavarroLlaguno/emotional_assistant.git
cd emotional_assistant/backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario (opcional, para acceso al admin)
python manage.py createsuperuser
# Usuario Existente: mindsurf
# Contraseña: admin123

# Iniciar servidor
python manage.py runserver
```

El servidor estará corriendo en `http://localhost:8000/`

## Prueba Rápida del API

### Usando curl:
```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": [
      {
        "timestamp": "2025-10-27T10:00:00Z",
        "role": "assistant",
        "text": "Hola, ¿cómo te sientes hoy? Me gustaría saber si hay algo en particular que te gustaría platicar."
      },
      {
        "timestamp": "2025-10-27T10:15:30Z",
        "role": "user",
        "text": "Me siento bien, gracias. Necesito hablar sobre mi trabajo, tengo una tarea importante."
      },
      {
        "timestamp": "2025-10-27T10:16:00Z",
        "role": "assistant",
        "text": "Claro, cuéntame más. ¿Qué tipo de tarea es?"
      }
    ]
  }'
```

### Respuesta Esperada:
```json
{
  "analysis_summary": {
    "session_count": 1,
    "key_moments": {
      "questions_asked": 2,
      "actions_identified": 2
    },
    "emotion_analysis_results": [
      {"emotion": "Happiness"},
      {"emotion": "Sadness"}
    ]
  }
}
```

### Usando Python:
```python
import requests
import json

url = "http://localhost:8000/api/analyze/"
data = {
    "transcript": [
        {
            "timestamp": "2025-10-27T10:00:00Z",
            "role": "assistant",
            "text": "Hola, ¿cómo estás?"
        },
        {
            "timestamp": "2025-10-27T10:15:30Z",
            "role": "user",
            "text": "Necesito ayuda con algo"
        }
    ]
}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))
```

## Acceder al Admin de Django

1. Visitar: `http://localhost:8000/admin/`
2. Iniciar sesión con las credenciales de superusuario creadas arriba
3. Explorar:
   - **Conversations**: Ver todas las conversaciones analizadas
   - **Messages**: Ver mensajes individuales con números de sesión
   - **Analysis Reports**: Revisar resultados de análisis con datos emocionales

## Ejecutar Tests
```bash
python manage.py test apps.analysis
```

Esperado: Los 9 tests deben pasar

## Ejemplos de Datos de Prueba

### Sesión única (conversación positiva):
```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": [
      {"timestamp": "2025-11-15T10:00:00Z", "role": "assistant", "text": "¡Hola! ¿Cómo te sientes?"},
      {"timestamp": "2025-11-15T10:02:00Z", "role": "user", "text": "¡Me siento genial! Tuve un día maravilloso."}
    ]
  }'
```

### Múltiples sesiones (silencios de 10+ minutos):
```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": [
      {"timestamp": "2025-11-15T09:00:00Z", "role": "assistant", "text": "Buenos días"},
      {"timestamp": "2025-11-15T09:05:00Z", "role": "user", "text": "Hola"},
      {"timestamp": "2025-11-15T09:20:00Z", "role": "assistant", "text": "¿Sigues ahí?"},
      {"timestamp": "2025-11-15T09:22:00Z", "role": "user", "text": "Sí, necesito ayuda"}
    ]
  }'
```

### Conversación con muchas acciones:
```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": [
      {"timestamp": "2025-11-15T14:00:00Z", "role": "user", "text": "Necesito ayuda urgente con una tarea"},
      {"timestamp": "2025-11-15T14:02:00Z", "role": "assistant", "text": "¿En qué puedo ayudarte?"},
      {"timestamp": "2025-11-15T14:05:00Z", "role": "user", "text": "Podrías ayudarme a hacer un plan?"}
    ]
  }'
```

### Conversación emocional larga:
```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": [
      {"timestamp": "2025-11-15T08:00:00Z", "role": "assistant", "text": "Buenos días, ¿cómo amaneciste hoy?"},
      {"timestamp": "2025-11-15T08:03:00Z", "role": "user", "text": "Mal, la verdad. Me siento muy triste y no tengo ganas de hacer nada. ¿Podrías ayudarme a entender por qué me siento así?"},
      {"timestamp": "2025-11-15T08:05:00Z", "role": "assistant", "text": "Entiendo que te sientes mal. ¿Pasó algo específico que desencadenó estos sentimientos?"},
      {"timestamp": "2025-11-15T08:08:00Z", "role": "user", "text": "Sí, ayer tuve una discusión fuerte con mi mejor amigo. Dijo cosas que me lastimaron mucho y ahora no sé si nuestra amistad puede continuar."}
    ]
  }'
```

### Conversación sobre ansiedad:
```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": [
      {"timestamp": "2025-11-15T11:15:00Z", "role": "user", "text": "Hola, me estoy sintiendo muy ansioso ahora mismo. ¿Es normal que mi corazón esté latiendo tan rápido?"},
      {"timestamp": "2025-11-15T11:16:00Z", "role": "assistant", "text": "Entiendo que te sientes ansioso. ¿Estás en un lugar seguro ahora mismo?"},
      {"timestamp": "2025-11-15T11:17:00Z", "role": "user", "text": "Sí, estoy en mi casa. Pero no puedo dejar de pensar en todo lo que podría salir mal. ¿Qué hago si no puedo controlar esto?"}
    ]
  }'
```

## Comando de Validación para Psicólogos

Para revisar manualmente el análisis de una conversación:
```bash
python manage.py validate_analysis <conversation_id>
```

Ejemplo:
```bash
python manage.py validate_analysis 1
```

Este comando muestra:
- Transcripción completa con timestamps
- Sesiones detectadas
- Preguntas identificadas con su texto
- Acciones identificadas con su texto
- Resultados del análisis emocional

## Solución de Problemas

### Puerto ya en uso:
```bash
python manage.py runserver 8001
```

### Tests fallando:
```bash
# Asegúrate de estar en el directorio backend
cd backend
source venv/bin/activate
python manage.py test apps.analysis -v 2
```

### No puedo acceder al admin:
Asegúrate de haber creado un superusuario con `python manage.py createsuperuser`

## Estructura del Proyecto
```
backend/
├── apps/
│   └── analysis/       # Aplicación principal
│       ├── management/
│       │   └── commands/
│       │       └── validate_analysis.py  # Comando de validación
│       ├── migrations/
│       ├── admin.py         # Interfaz admin
│       ├── models.py        # Conversation, Message, AnalysisReport
│       ├── serializers.py   # Serializadores DRF
│       ├── services.py      # ConversationAnalyzer (lógica de negocio)
│       ├── tests.py         # Tests unitarios e integración
│       ├── urls.py          # Rutas URL
│       └── views.py         # AnalyzeConversationView
├── core/                    # Configuración Django
│   ├── settings.py
│   └── urls.py
├── manage.py
├── requirements.txt
├── README.md               # Documentación detallada
└── SETUP.md               # Este archivo
```

Para decisiones de arquitectura detalladas y trade-offs, ver [README.md](README.md).
