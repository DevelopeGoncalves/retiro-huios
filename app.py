import mercadopago
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
import io

app = Flask(__name__)
CORS(app)

# SUBSTITUA PELO SEU ACCESS TOKEN REAL (APP_USR-...)
sdk = mercadopago.SDK("SEU_ACCESS_TOKEN_AQUI")

@app.route('/create_preference', methods=['POST'])
def create_preference():
    try:
        data = request.json
        
        preference_data = {
            "items": [{
                "title": f"Retiro Huios 2026 - {data['lote']}",
                "quantity": 1,
                "unit_price": float(data['valor']),
                "currency_id": "BRL"
            }],
            "payer": {"email": data['email'], "name": data['nome']},
            "back_urls": {
                "success": "http://localhost:5000/sucesso",
                "failure": "http://localhost:5000/erro"
            },
            "auto_return": "approved"
        }
        
        result = sdk.preference().create(preference_data)
        return jsonify({"id": result["response"]["id"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/gerar_ingresso', methods=['POST'])
def gerar_ingresso():
    data = request.json
    buffer = io.BytesIO()
    
    # Criando o PDF tamanho A5 (ideal para ingressos)
    p = canvas.Canvas(buffer, pagesize=A5)
    largura, altura = A5

    # Cabeçalho Estilizado
    p.setFillColorRGB(0.04, 0.1, 0.18) # Azul Marinho (Huios Primary)
    p.rect(0, altura - 80, largura, 80, fill=1)
    
    p.setFillColorRGB(1, 1, 1) # Branco
    p.setFont("Helvetica-Bold", 20)
    p.drawString(40, altura - 50, "INGRESSO HUIOS.26")
    
    # Corpo do Ingresso
    p.setFillColorRGB(0, 0, 0) # Preto
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, altura - 130, f"PARTICIPANTE: {data['nome'].upper()}")
    
    p.setFont("Helvetica", 12)
    p.drawString(40, altura - 160, f"WHATSAPP: {data['whatsapp']}")
    p.drawString(40, altura - 180, f"DATA NASC.: {data['nascimento']}")
    p.drawString(40, altura - 200, f"LOTE: {data['lote']}")
    p.drawString(40, altura - 220, f"VALOR: R$ {data['valor']},00")
    
    # Rodapé / Info Local
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, altura - 260, "LOCAL: SÍTIO BELA VISTA")
    p.setFont("Helvetica", 10)
    p.drawString(40, altura - 275, "Timbuí, Santa Teresa - ES")
    
    # Linha de Corte Simbolizada
    p.setDash(1, 2)
    p.line(20, altura - 310, largura - 20, altura - 310)
    
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    p.drawString(40, altura - 330, "Apresente este documento impresso ou no celular no check-in.")

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(
        buffer, 
        as_attachment=True, 
        download_name=f"Ingresso_Huios_{data['nome'].replace(' ', '_')}.pdf", 
        mimetype='application/pdf'
    )

if __name__ == "__main__":
    app.run(port=5000, debug=True)