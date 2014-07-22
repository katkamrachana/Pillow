from helper import unittest, PillowTestCase
from io import BytesIO
from PIL import Image


test_files = ["Tests/images/sugarshack.mpo", "Tests/images/frozenpond.mpo"]


class TestFileMpo(PillowTestCase):

    def setUp(self):
        codecs = dir(Image.core)
        if "jpeg_encoder" not in codecs or "jpeg_decoder" not in codecs:
            self.skipTest("jpeg support not available")

    def roundtrip(self, im, **options):
        out = BytesIO()
        im.save(out, "MPO", **options)
        bytes = out.tell()
        out.seek(0)
        im = Image.open(out)
        im.bytes = bytes  # for testing only
        return im

    def test_sanity(self):
        for test_file in test_files:
            im = Image.open(test_file)
            im.load()
            self.assertEqual(im.mode, "RGB")
            self.assertEqual(im.size, (640, 480))
            self.assertEqual(im.format, "MPO")

    def test_app(self):
        for test_file in test_files:
            # Test APP/COM reader (@PIL135)
            im = Image.open(test_file)
            self.assertEqual(im.applist[0][0], 'APP1')
            self.assertEqual(im.applist[1][0], 'APP2')
            self.assertEqual(im.applist[1][1][:16],
                b'MPF\x00MM\x00*\x00\x00\x00\x08\x00\x03\xb0\x00')
            self.assertEqual(len(im.applist), 2)

    def test_exif(self):
        for test_file in test_files:
            im = Image.open(test_file)
            info = im._getexif()
            self.assertEqual(info[272], 'Nintendo 3DS')
            self.assertEqual(info[296], 2)
            self.assertEqual(info[34665], 188)

    def test_mp(self):
        for test_file in test_files:
            im = Image.open(test_file)
            info = im._getmp()
            self.assertEqual(info[45056], '0100')
            self.assertEqual(info[45057], 2)
    
    def test_seek(self):
        for test_file in test_files:
            im = Image.open(test_file)
            self.assertEqual(im.tell(), 0)
            # prior to first image raises an error, both blatant and borderline
            self.assertRaises(EOFError, im.seek, -1)
            self.assertRaises(EOFError, im.seek, -523)
            # after the final image raises an error, both blatant and borderline
            self.assertRaises(EOFError, im.seek, 2)
            self.assertRaises(EOFError, im.seek, 523)
            # bad calls shouldn't change the frame
            self.assertEqual(im.tell(), 0)
            # this one will work
            im.seek(1)
            self.assertEqual(im.tell(), 1)
            # and this one, too
            im.seek(0)
            self.assertEqual(im.tell(), 0)
            

if __name__ == '__main__':
    unittest.main()

# End of file
