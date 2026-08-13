from flask import Flask, render_template_string
import os

app = Flask(__name__)

# ============================================================
# PRODUTOS DA OFERTA PLAY
# Edite somente esta parte para alterar produtos e valores
# ============================================================

PRODUTOS = [
    {
        "nome": "Canva Pro",
        "descricao": "Acesso Canva Pro por 30 dias",
        "preco": 5.00,
        "icone": "🎨"
    },
    {
        "nome": "GPT Go",
        "descricao": "Acesso ao GPT Go",
        "preco": 10.00,
        "icone": "🤖"
    },
    {
        "nome": "Netflix Premium",
        "descricao": "Tela Netflix Premium",
        "preco": 12.00,
        "icone": "🎬"
    },
    {
        "nome": "Disney+",
        "descricao": "Tela Disney+",
        "preco": 7.00,
        "icone": "🏰"
    }
]

WHATSAPP = "5598987894338"

# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Oferta Play</title>

    <style>

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: Arial, Helvetica, sans-serif;
        }

        body {
            background: #080808;
            color: white;
        }

        header {
            background: linear-gradient(135deg, #16002b, #32005c);
            padding: 25px 20px;
            text-align: center;
            border-bottom: 1px solid #5d1b91;
        }

        .logo {
            font-size: 34px;
            font-weight: 800;
            color: #ffffff;
        }

        .logo span {
            color: #a855f7;
        }

        .subtitulo {
            margin-top: 8px;
            color: #d1d1d1;
            font-size: 15px;
        }

        .hero {
            padding: 45px 20px 30px;
            text-align: center;
        }

        .hero h1 {
            font-size: 32px;
            margin-bottom: 12px;
        }

        .hero p {
            color: #aaa;
            max-width: 600px;
            margin: auto;
            line-height: 1.6;
        }

        .produtos {
            max-width: 1100px;
            margin: auto;
            padding: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 20px;
        }

        .produto {
            background: #111111;
            border: 1px solid #292929;
            border-radius: 18px;
            padding: 25px;
            text-align: center;
            transition: 0.2s;
        }

        .produto:hover {
            transform: translateY(-4px);
            border-color: #8b3dca;
        }

        .icone {
            font-size: 50px;
            margin-bottom: 15px;
        }

        .produto h2 {
            font-size: 21px;
            margin-bottom: 10px;
        }

        .descricao {
            color: #999;
            min-height: 42px;
            font-size: 14px;
            line-height: 1.5;
        }

        .preco {
            font-size: 30px;
            font-weight: bold;
            margin: 20px 0;
            color: #c084fc;
        }

        .botao {
            display: block;
            background: #7c3aed;
            color: white;
            text-decoration: none;
            padding: 13px;
            border-radius: 10px;
            font-weight: bold;
            transition: 0.2s;
        }

        .botao:hover {
            background: #9333ea;
        }

        .sobre {
            max-width: 900px;
            margin: 50px auto;
            padding: 30px 20px;
            text-align: center;
        }

        .sobre h2 {
            margin-bottom: 15px;
        }

        .sobre p {
            color: #999;
            line-height: 1.7;
        }

        footer {
            border-top: 1px solid #222;
            text-align: center;
            padding: 25px;
            color: #777;
            font-size: 13px;
        }

        @media (max-width: 600px) {

            .hero h1 {
                font-size: 27px;
            }

            .logo {
                font-size: 29px;
            }

        }

    </style>

</head>

<body>

<header>

    <div class="logo">
        Oferta <span>Play</span>
    </div>

    <div class="subtitulo">
        Produtos digitais com atendimento pelo WhatsApp
    </div>

</header>


<section class="hero">

    <h1>Escolha seu produto</h1>

    <p>
        Confira nossas ofertas e fale conosco pelo WhatsApp
        para realizar seu pedido.
    </p>

</section>


<section class="produtos">

    {% for produto in produtos %}

    <div class="produto">

        <div class="icone">
            {{ produto.icone }}
        </div>

        <h2>
            {{ produto.nome }}
        </h2>

        <div class="descricao">
            {{ produto.descricao }}
        </div>

        <div class="preco">
            R$ {{ "%.2f"|format(produto.preco)|replace(".", ",") }}
        </div>

        <a
            class="botao"
            href="https://wa.me/{{ whatsapp }}?text=Olá!%20Tenho%20interesse%20no%20{{ produto.nome }}"
            target="_blank"
        >
            Comprar pelo WhatsApp
        </a>

    </div>

    {% endfor %}

</section>


<section class="sobre">

    <h2>Oferta Play</h2>

    <p>
        Sua loja de produtos digitais.
        Escolha uma oferta, clique no botão e fale diretamente
        com nosso atendimento pelo WhatsApp.
    </p>

</section>


<footer>

    © 2026 Oferta Play — Todos os direitos reservados.

</footer>

</body>

</html>
"""


@app.route("/")
def inicio():
    return render_template_string(
        HTML,
        produtos=PRODUTOS,
        whatsapp=WHATSAPP
    )


@app.route("/status")
def status():
    return {
        "status": "online",
        "sistema": "Oferta Play",
        "produtos": len(PRODUTOS)
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
