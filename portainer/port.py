"""TODO: module docstring."""

from ssl import SSLContext

from aiohttp import ClientSession

from .container import Container


class PortainerContainerStatus:
    """TODO: class docstring."""

    def __init__(
        self,
        session: ClientSession,
        context: SSLContext,
        host,
        username,
        password,
        ca_path=None,
    ) -> None:
        """Init."""
        self.__session = session
        self.__host = host
        self.__username = username
        self.__password = password
        self.__context = context
        self.__headers = {}

    async def get_auth_token(self):
        """TODO: docstring."""
        auth_url = f"{self.__host}/api/auth"

        async with self.__session.post(
            auth_url,
            json={"password": self.__password, "username": self.__username},
            ssl=self.__context,
            timeout=15,
        ) as r:
            j = await r.json()
            token = j["jwt"]
            self.__headers = {"Authorization": f"Bearer {token}"}

    async def get_containers(self):
        """TODO: docstring."""
        containers = []
        endpoint_url = f"{self.__host}/api/endpoints"
        async with self.__session.get(
            endpoint_url, headers=self.__headers, ssl=self.__context, timeout=15
        ) as r:
            j = await r.json()
            for e in j:
                env_id = e["Id"]
                for s in e["Snapshots"]:
                    for c in s["DockerSnapshotRaw"]["Containers"]:
                        container_id = c["Id"]
                        name = c["Names"][0]
                        image = c["Image"]
                        state = c["State"]
                        status = c["Status"]
                        update = await self.get_update_status(env_id, container_id)
                        container = Container(
                            container_id, name, image, state, status, None, update
                        )
                        containers.append(container)
        return containers

    async def get_update_status(self, env_id, container_id):
        """TODO: docstring."""
        update_url = (
            f"{self.__host}/api/docker/{env_id}/containers/{container_id}/image_status"
        )
        async with self.__session.get(
            update_url, headers=self.__headers, ssl=self.__context, timeout=15
        ) as ur:
            uj = await ur.json()
            return uj["Status"] == "outdated"
