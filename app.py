from flask import Flask

app = Flask(__name__)

@app.route("/")
def inicio():
    return """
    <html>
        <head>
            <title>Oferta Play</title>
        </head>
        <body>
            <h1>Oferta Play</h1>
            <h2>Loja de Produtos Digitais</h2>
            <p>Sistema iniciado com sucesso.</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
