from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import base64
import os

app = Flask(__name__)
CORS(app, origins=["https://jesseprestes7-arch.github.io"])

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        image_b64 = data.get("image", "")
        mime = data.get("mime", "image/jpeg")

        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

        message = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=256,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime,
                            "data": image_b64
                        }
                    },
                    {
                        "type": "text",
                        "text": """Esta é uma foto de câmera de segurança Reolink de um porto de areia. Analise e responda APENAS em JSON sem markdown:
{"data":"DD/MM/AAAA","hora":"HH:MM","cor":"cor da cabine do caminhão","tipo":"Truck ou Carreta ou Toco ou Bitruck","capNom":numero,"vol":numero,"obs":"observação breve"}

Para cor use: Vermelho, Laranja, Amarelo, Branco, Cinza, Azul, Verde, Preto.
Para tipo: Truck=2 eixos traseiros, Carreta=semirreboque, Toco=1 eixo traseiro, Bitruck=3 eixos.
Leia a data e hora do timestamp visível na imagem (ex: 30/03/2026 15:21:25).
Se não houver timestamp, use null para data e hora.
Estime o volume em m³ baseado no preenchimento visível da caçamba."""
                    }
                ]
            }]
        )

        text = message.content[0].text.strip()
        import json
        result = json.loads(text)
        return jsonify({"ok": True, "result": result})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
