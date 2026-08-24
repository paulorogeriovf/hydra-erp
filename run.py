# Hydra ERP
# Responsável por: Ponto de entrada utilizado para iniciar o Hydra ERP.

from app import create_app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)