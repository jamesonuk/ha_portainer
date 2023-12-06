"""TODO: module docstring."""


class Container:
    """TODO: class docstring."""

    def __init__(
        self, container_id, name, image, state, status, created_date, update_available
    ) -> None:
        """init."""
        self._container_id = container_id
        self._name = name
        self._image = image
        self._state = state
        self._status = status
        self._created_date = created_date
        self._update_available = update_available

    def __str__(self):
        """str."""
        return f"{self.container_id} : {self.name} : {self.image} : {self.state} : {self.status} : {self.update_available}"

    @property
    def container_id(self):
        """TODO: ."""
        return self._container_id

    @property
    def name(self):
        """TODO: ."""
        return self._name

    @property
    def image(self):
        """TODO: ."""
        return self._image

    @property
    def state(self):
        """TODO: ."""
        return self._state

    @property
    def status(self):
        """TODO: ."""
        return self._status

    @property
    def created_date(self):
        """TODO: ."""
        return self._created_date

    @property
    def update_available(self):
        """TODO: ."""
        return self._update_available
