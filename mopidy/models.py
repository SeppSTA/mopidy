from copy import copy

from mopidy.frontends.mpd import translator

class ImmutableObject(object):
    """
    Superclass for immutable objects whose fields can only be modified via the
    constructor.

    :param kwargs: kwargs to set as fields on the object
    :type kwargs: any
    """

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise TypeError('__init__() got an unexpected keyword ' + \
                    'argument \'%s\'' % key)
            self.__dict__[key] = value

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super(ImmutableObject, self).__setattr__(name, value)
        raise AttributeError('Object is immutable.')

    def __hash__(self):
        hash_sum = 0
        for key, value in self.__dict__.items():
            hash_sum += hash(key) + hash(value)
        return hash_sum

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def copy(self, **kwargs):
        data = {}
        for key in self.__dict__.keys():
            public_key = key.lstrip('_')
            data[public_key] = kwargs.pop(public_key, self.__dict__[key])
        for key in kwargs.keys():
            if hasattr(self, key):
                data[key] = kwargs.pop(key)
        if kwargs:
            raise TypeError("copy() got an unexpected keyword argument '%s'" % key)
        return self.__class__(**data)

class Artist(ImmutableObject):
    """
    :param uri: artist URI
    :type uri: string
    :param name: artist name
    :type name: string
    :param musicbrainz_id: musicbrainz id
    :type musicbrainz_id: string
    """

    #: The artist URI. Read-only.
    uri = None

    #: The artist name. Read-only.
    name = None

    #: The musicbrainz id of the artist. Read-only.
    musicbrainz_id = None


class Album(ImmutableObject):
    """
    :param uri: album URI
    :type uri: string
    :param name: album name
    :type name: string
    :param artists: album artists
    :type artists: list of :class:`Artist`
    :param num_tracks: number of tracks in album
    :type num_tracks: integer
    :param musicbrainz_id: musicbrainz id
    :type musicbrainz_id: string
    """

    #: The album URI. Read-only.
    uri = None

    #: The album name. Read-only.
    name = None

    #: The number of tracks in the album. Read-only.
    num_tracks = 0

    #: The musicbrainz id of the album. Read-only.
    musicbrainz_id = None

    def __init__(self, *args, **kwargs):
        self._artists = frozenset(kwargs.pop('artists', []))
        super(Album, self).__init__(*args, **kwargs)

    @property
    def artists(self):
        """List of :class:`Artist` elements. Read-only."""
        return list(self._artists)


class Track(ImmutableObject):
    """
    :param uri: track URI
    :type uri: string
    :param name: track name
    :type name: string
    :param artists: track artists
    :type artists: list of :class:`Artist`
    :param album: track album
    :type album: :class:`Album`
    :param track_no: track number in album
    :type track_no: integer
    :param date: track release date
    :type date: :class:`datetime.date`
    :param length: track length in milliseconds
    :type length: integer
    :param bitrate: bitrate in kbit/s
    :type bitrate: integer
    :param musicbrainz_id: musicbrainz id
    :type musicbrainz_id: string
    """

    #: The track URI. Read-only.
    uri = None

    #: The track name. Read-only.
    name = None

    #: The track :class:`Album`. Read-only.
    album = None

    #: The track number in album. Read-only.
    track_no = 0

    #: The track release date. Read-only.
    date = None

    #: The track length in milliseconds. Read-only.
    length = None

    #: The track's bitrate in kbit/s. Read-only.
    bitrate = None

    #: The musicbrainz id of the track. Read-only.
    musicbrainz_id = None

    def __init__(self, *args, **kwargs):
        self._artists = frozenset(kwargs.pop('artists', []))
        super(Track, self).__init__(*args, **kwargs)

    @property
    def artists(self):
        """List of :class:`Artist`. Read-only."""
        return list(self._artists)

    def mpd_format(self, *args, **kwargs):
        return translator.track_to_mpd_format(self, *args, **kwargs)


class Playlist(ImmutableObject):
    """
        :param uri: playlist URI
        :type uri: string
        :param name: playlist name
        :type name: string
        :param tracks: playlist's tracks
        :type tracks: list of :class:`Track` elements
        :param last_modified: playlist's modification time
        :type last_modified: :class:`datetime.datetime`
    """

    #: The playlist URI. Read-only.
    uri = None

    #: The playlist name. Read-only.
    name = None

    #: The playlist modification time. Read-only.
    #:
    #: :class:`datetime.datetime`, or :class:`None` if unknown.
    last_modified = None

    def __init__(self, *args, **kwargs):
        self._tracks = kwargs.pop('tracks', [])
        super(Playlist, self).__init__(*args, **kwargs)

    @property
    def tracks(self):
        """List of :class:`Track` elements. Read-only."""
        return copy(self._tracks)

    @property
    def length(self):
        """The number of tracks in the playlist. Read-only."""
        return len(self._tracks)

    def mpd_format(self, *args, **kwargs):
        return translator.playlist_to_mpd_format(self, *args, **kwargs)
