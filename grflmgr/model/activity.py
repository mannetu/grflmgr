class Activity:
    def __init__(
        self,
        filehash: str = '',
        device: dict = {},
        session: dict = {},
        track: list = [],
    ):
        self._filehash = filehash
        self._device = device
        self._session = session
        self._track = track

    def __str__(self):
        return f"Activity: {self._filehash}"

    def get_dict(self, limit: int = None):
        return dict(
            hash=self._filehash,
            device=self._device,
            session=self._session,
            track=self._track[0:limit],
        )

    def get_track(self) -> list[tuple]:
        """Returns the track in format [(lat1, long1), (lat2, long2), ...]"""
        track = [(p["lat"], p["lon"]) for p in self._track]
        return track

    def get_map_corners(self) -> tuple[tuple, tuple]:
        """Returns the north-west and south-east corners required for a map covering the whole track 
        as ((nw_latitude, nw_longitude), (se_latitude, se_longitude)).
        """
        track = self.get_track()
        lats = []
        longs = []
        for position in track:
            lats.append(position[0])
            longs.append(position[1])
        self._session["corner_nw"] = (max(lats), min(longs))
        self._session["corner_se"] = (min(lats), max(longs))
        return (self._session["corner_nw"], self._session["corner_se"])
