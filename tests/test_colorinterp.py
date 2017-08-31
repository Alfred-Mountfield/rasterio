import pytest

import rasterio
from rasterio.enums import ColorInterp


def test_cmyk_interp(tmpdir):
    """A CMYK TIFF has cyan, magenta, yellow, black bands."""
    with rasterio.open('tests/data/RGB.byte.tif') as src:
        meta = src.meta
    meta['photometric'] = 'CMYK'
    meta['count'] = 4
    tiffname = str(tmpdir.join('foo.tif'))
    with rasterio.open(tiffname, 'w', **meta) as dst:
        assert dst.profile['photometric'] == 'cmyk'
        assert dst.colorinterp(1) == ColorInterp.cyan
        assert dst.colorinterp(2) == ColorInterp.magenta
        assert dst.colorinterp(3) == ColorInterp.yellow
        assert dst.colorinterp(4) == ColorInterp.black


@pytest.mark.skip(reason="crashing on OS X with Homebrew's GDAL")
def test_ycbcr_interp(tmpdir):
    """A YCbCr TIFF has red, green, blue bands."""
    with rasterio.open('tests/data/RGB.byte.tif') as src:
        meta = src.meta
    meta['photometric'] = 'ycbcr'
    meta['compress'] = 'jpeg'
    meta['count'] = 3
    tiffname = str(tmpdir.join('foo.tif'))
    with rasterio.open(tiffname, 'w', **meta) as dst:
        assert dst.colorinterp(1) == ColorInterp.red
        assert dst.colorinterp(2) == ColorInterp.green
        assert dst.colorinterp(3) == ColorInterp.blue


def test_set_colorinterp(path_rgba_byte_tif, tmpdir):
    """Test setting color interpretation by creating an image without CI
    and then setting to unusual values.
    """
    no_ci_path = str(tmpdir.join('no-ci.tif'))
    rasterio.copy(
        path_rgba_byte_tif,
        no_ci_path,
        photometric='minisblack',
        alpha='unspecified')

    # This is should be the default color interpretation of the copied
    # image.  GDAL defines these defaults, not Rasterio.
    initial_ci_map = {
        1: ColorInterp.gray,
        2: ColorInterp.undefined,
        3: ColorInterp.undefined,
        4: ColorInterp.undefined
    }

    end_ci_map = {
        1: ColorInterp.alpha,
        2: ColorInterp.blue,
        3: ColorInterp.green,
        4: ColorInterp.red
    }
    with rasterio.open(no_ci_path, 'r+') as src:
        for bidx, ci in initial_ci_map.items():
            assert src.colorinterp(bidx) == ci
        for bidx, ci in end_ci_map.items():
            src.set_colorinterp(bidx, ci)
        for bidx, ci in end_ci_map.items():
            assert src.colorinterp(bidx) == ci
