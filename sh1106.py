import framebuf

class SH1106:
    def __init__(self, i2c, addr=0x3C, width=128, height=64):
        self.i2c    = i2c
        self.addr   = addr
        self.width  = width
        self.height = height
        self.pages  = height // 8
        self.buf    = bytearray(self.pages * width)
        self.fb     = framebuf.FrameBuffer(self.buf, width, height, framebuf.MONO_VLSB)
        self._init()
        self._clear_edge()
        self.fill(0)
        self.show()

    def _cmd(self, cmd):
        self.i2c.writeto(self.addr, bytes([0x00, cmd]))

    def _clear_edge(self):
        for page in range(self.pages):
            self._cmd(0xB0 + page)
            self._cmd(0x00)
            self._cmd(0x18)
            self.i2c.writeto(self.addr, b'\x40\x00\x00\x00\x00')

    def _init(self):
        for cmd in [
            0xAE, 0xA8, 0x3F, 0xD3, 0x00, 0x40,
            0xA1, 0xC8, 0xDA, 0x12, 0x81, 0xCF,
            0xD9, 0xF1, 0xDB, 0x40, 0xA4, 0xA6,
            0xD5, 0x80, 0x8D, 0x14, 0xAF,
        ]:
            self._cmd(cmd)

    def fill(self, col):
        self.fb.fill(col)

    def text(self, s, x, y, col=1):
        self.fb.text(s, x, y, col)

    def hline(self, x, y, w, col=1):
        self.fb.hline(x, y, w, col)

    def rect(self, x, y, w, h, col=1):
        self.fb.rect(x, y, w, h, col)

    def show(self):
        for page in range(self.pages):
            self._cmd(0xB0 + page)
            self._cmd(0x00)
            self._cmd(0x10)
            self.i2c.writeto(self.addr, b'\x40' + self.buf[page*128:(page+1)*128])
