from src.api import create_app  # ✅ Absolute import (if needed)

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
