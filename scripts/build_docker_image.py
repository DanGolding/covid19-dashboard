import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import docker


DOCKERFILE_PATH = Path("Dockerfile")
REQUIREMENTS_PATH = Path("requirements.txt")
DEV_REQUIREMENTS_PATH = Path("dev_requirements.txt")
SETUP_PATH = Path("setup.py")
SRC_PATH = Path("src")


def main() -> None:

    with TemporaryDirectory() as docker_context:
        shutil.copy2(DOCKERFILE_PATH, docker_context)
        shutil.copy2(REQUIREMENTS_PATH, docker_context)
        shutil.copy2(DEV_REQUIREMENTS_PATH, docker_context)
        shutil.copy2(SETUP_PATH, docker_context)
        shutil.copytree(SRC_PATH, Path(docker_context) / SRC_PATH)

        for file in Path(docker_context).glob("**/*"):
            print(file)

        client = docker.from_env()
        image, build_logs = client.images.build(path=docker_context, tag="covid19:v0.1")

        print(list(build_logs))


if __name__ == "__main__":
    main()
