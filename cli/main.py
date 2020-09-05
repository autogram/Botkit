from enum import Enum, auto

from typer import Typer, echo


class ConfigFileType(Enum):
    dotenv = "dotenv"
    settings_config = "dotconfig"


app = Typer()
config_app = Typer()
app.add_typer(config_app, name="config")


@config_app.command("create")
def items_create(file_type: ConfigFileType):
    echo(f"Creating a {file_type.name} file")


@config_app.command("delete")
def items_delete(item: str):
    echo(f"Deleting item: {item}")


@config_app.command("sell")
def items_sell(item: str):
    echo(f"Selling item: {item}")


if __name__ == "__main__":
    app()
