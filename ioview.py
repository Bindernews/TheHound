
import io

class ReadView:
    """
    Allows you to pass a "view" of a file-like object.
    The source must be seekable.
    As a side benefit, it also records the maximum location which was read.
    """

    def __init__(self, source, start, end):
        super().__init__()
        self.__source = source
        # Starting position of the view
        self.__start = start
        # End position of the stream
        self.__end = end
        self.max_pos = start

    def read(self, size=-1):
        end = self.__end
        if size > 0:
            newpos = min(self.__tell() + size, end)
        else:
            newpos = end
        length = newpos - self.__tell()
        self.max_pos = max(self.max_pos, newpos)
        # Return empty bytearray if we're at the end of the view
        if length == 0:
            return b''
        else:
            return self.__source.read(length)

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            newpos = self.__start + offset
        elif whence == io.SEEK_CUR:
            newpos = self.__tell() + offset
        elif whence == io.SEEK_END:
            newpos = self.__end + offset
        else:
            # whence = unknown
            raise OSError(22)
        self.__boundcheck1(newpos)
        self.__source.seek(newpos, io.SEEK_SET)            

    def __boundcheck1(self, pos):
        if pos < self.__start:
            raise OSError(22)

    def __boundcheck2(self, pos):
        if pos < self.__start or (self.__end and pos > self.__end):
            raise OSError(22)

    def __tell(self):
        return self.__source.tell()

    def close(self):
        pass

    def tell(self):
        return self.__tell() - self.__start

    def seekable(self):
        return self.__source.seekable()

    def readable(self):
        return True

    def writable(self):
        return False