import typer

app = typer.Typer()

@app.command()
def hello():
    print("Void Loop Content Engine is ready.")

if __name__ == "__main__":
    app()
