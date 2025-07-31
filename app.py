from flask import Flask, request, jsonify
from flasgger import Swagger
import openai
import json
import re

app = Flask(__name__)
swagger = Swagger(app)

# Configurar OpenRouter
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = "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"

system_prompt = """

Eres un asistente médico virtual del Policlínico Tabancura. Tu función es derivar a los pacientes según los síntomas o problemas que describen. Las áreas disponibles para derivación son:

Salud Mental: ansiedad, depresión, estrés, insomnio, crisis emocionales, etc.
Salud Dental: dolor de muela, caries, limpieza dental, ortodoncia, etc.
Medicina General: fiebre, tos, dolor muscular, malestar general, chequeo médico, etc.
Terapias Alternativas: masajes, masoterapia, biomagnetismo.

Si el motivo del mensaje no se puede asociar claramente a ninguna de estas áreas, entrega los datos de contacto de la sucursal de Vitacura o sucursal Los Tribunales para que el paciente pueda comunicarse directamente con el Policlínico.

Formato de respuesta:
Responde exclusivamente en formato JSON con las siguientes claves:

"area": una de ["Salud Mental", "Salud Dental", "Medicina General", "Terapias alternativas", "no clasificable"]
"recomendacion": un mensaje breve y amable que incluya al menos 1 emoji relacionado, invitando a agendar una hora si es posible o contactarse directmente si no es clasificable.
"accion": palabra clave que indique la acción recomendada, una de ["mostrar_agenda_mental", "mostrar_agenda_dental", "mostrar_agenda_medica", "mostrar_agenda_terapiasalternativas", "ninguna"]

Si "area" es "no clasificable", la "recomendacion" debe incluir los siguientes datos de contacto de sucural vitacura:

Sucursal Vitacura - Av. Vitacura 8620, Comuna de Vitacura 
Teléfono fijo: +562 2933 6740  
WhatsApp: +569 6578 1253  
Correos: recepciondental@policlinicotabancura.cl y recepciomedica@policlinicotabancura.cl
Página web: https://www.policlinicotabancura.cl

o de sucursal Los Tribunales:

Sucursal Los Tribunales - Calle Los Tribunales 1268, Comuna de Vitacura
Teléfono fijo: +562 2217 2635
WhatsApp: +569 6618 7736
Correo: secretaria@policlinicotabancura.cl
Página web: https://www.policlinicotabancura.cl"""  # Aquí pega tu prompt completo

@app.route("/consultar", methods=["POST"])
def consultar():
    """
    Consultar área médica según malestar del paciente
    ---
    tags:
      - Asistente Médico Virtual
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - malestar
          properties:
            malestar:
              type: string
              example: "me duele la cabeza"
              description: Descripción libre del malestar del paciente
    responses:
      200:
        description: Respuesta con la derivación médica sugerida
        schema:
          type: object
          properties:
            area:
              type: string
              example: "Medicina General"
            recomendacion:
              type: string
              example: "¡Gracias por consultar! Podrías revisar con Medicina General. 😊"
            accion:
              type: string
              example: "mostrar_agenda_medica"
      500:
        description: Error al interpretar la respuesta
    """
    data = request.json
    malestar = data.get("malestar", "")

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-small-3.2-24b-instruct:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": malestar}
            ]
        )

        content = response.choices[0].message["content"]
        json_text = re.search(r"\{.*\}", content, re.DOTALL).group(0)
        respuesta = json.loads(json_text)

        return jsonify(respuesta)

    except Exception as e:
        return jsonify({
            "error": "Error al interpretar la respuesta",
            "detalle": str(e),
            "contenido": content
        }), 500

@app.route("/", methods=["GET"])
def home():
    return "✅ Backend Flask activo con documentación Swagger en /apidocs"

if __name__ == "__main__":
    app.run(debug=True)
