from pathlib import Path

import docker


def test_build_botkit_with_poetry_in_container():
    client = docker.from_env()
    botkit_root_path = Path(__file__).parent.parent.parent
    dockerfile_path: Path = (Path(__file__).parent / "DOCKERFILE").relative_to(botkit_root_path)
    client.images.build(path=str(botkit_root_path), dockerfile=dockerfile_path.as_posix())
