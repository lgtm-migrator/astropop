# Licensed under a 3-clause BSD style license - see LICENSE.rst
import os
import copy
import numpy as np
from astroscrappy import detect_cosmics
from astropy.io import fits
from astropy.nddata.utils import block_reduce as br

from ..fits_utils import check_hdu, check_header_keys, save_hdu
from .imarith import imarith, imcombine
from ..math.opd_utils import read_opd_header_number as opd_number
from ..math.slices import slices_from_string
from ..logger import logger

# TODO: functions to add
#   - subtract_overscan(image, overscan, inplace=False)
#   - block_replicate(image, block_size, conserve_sum=True, inplace=False)
#   - wcs_project(ccd, target_wcs, target_shape=None, order='bilinear')

# TODO: put header checking on the functions

combine = imcombine


def trim_image(image, section, fits_convention=False, inplace=False,
               logger=logger):
    """Trim a section from a image.

    If original_section passed, it will be used as reference for trimming.
    """
    if not inplace:
        im = copy.copy(image)
    else:
        im = image

    slices = slices_from_string(section, fits_convention=fits_convention)

    # check boundaries
    shape = im.data.shape
    for i,m in zip(slices, shape):
        m = int(m)
        l = [i.start or 0, i.stop or m]
        if np.min(l) < 0 or i.stop > m:
            raise ValueError('Slice out of the limits of the image.')

    ndata = np.array(im.data[slices])
    im.data = ndata
    im.header['trimmed'] = True
    im.header['trimmed slice'] = section
    im.header['trimmed fits_convention'] = fits_convention
    return im


def subtract_bias(image, master_bias, check_keys=[], inplace=False,
                  logger=logger):
    """Subtract a master_bias frame from an image."""
    if len(check_keys) > 0:
        check_header_keys(image, master_bias, check_keys)
    nim = imarith(image, master_bias, '-', inplace=inplace)

    nim.header['hierarch bias corrected'] = True
    biasfile = check_hdu(master_bias).fileinfo()
    if biasfile is not None:
        name = biasfile['file'].name
        nim.header['hierarch bias master'] = os.path.basename(name)

    return nim


def subtract_dark(image, dark_frame, dark_exposure=None, image_exposure=None,
                  exposure_key=None, check_keys=[], inplace=False,
                  logger=logger):
    """Subtract dark frame from an image, scaling by exposure."""
    if len(check_keys) > 0:
        check_header_keys(image, dark_frame, check_keys)
    dark = check_hdu(dark_frame)
    imag = check_hdu(image)

    if exposure_key is not None:
        try:
            d_exp = opd_number(dark.header[exposure_key])
            i_exp = opd_number(imag.header[exposure_key])
            if dark_exposure is not None or image_exposure is not None:
                logger.info('exposure_key and data exposures passed to the '
                            'function. Using only exposure_key')
        except KeyError:
            logger.warn('exposure_key is invalid, using dark_exposure and '
                        'image_exposure instead.')
            d_exp = dark_exposure
            i_exp = image_exposure

    if d_exp is not None and i_exp is not None:
        logger.debug('{} {}'.format(i_exp, d_exp))
        scale = i_exp/d_exp
        dark = imarith(dark, scale, '*', inplace=False)
        logger.debug('dark_frame values scaled by {} to fit the image'
                     ' exposure.'.format(scale))
    else:
        scale = None
        logger.debug('No exposures for image and/or dark_frame found.'
                     ' Ignoring scaling.')

    nim = imarith(imag, dark, '-', inplace=inplace)
    nim.header['hierarch dark corrected'] = True
    darkfile = dark.fileinfo()
    if darkfile is not None:
        name = darkfile['file'].name
        nim.header['hierarch dark frame'] = os.path.basename(name)
    if scale is not None:
        nim.header['hierarch dark scaled'] = scale

    return nim


def divide_flat(image, master_flat, check_keys=[], inplace=False,
                logger=logger):
    """Divide a image by a master flat field frame."""
    if len(check_keys) > 0:
        check_header_keys(image, master_flat, check_keys)
    nim = imarith(image, master_flat, '-', inplace=inplace)

    nim.header['hierarch flat corrected'] = True
    flatfile = check_hdu(master_flat).fileinfo()
    if flatfile is not None:
        name = flatfile['file'].name
        nim.header['hierarch flat master'] = os.path.basename(name)

    return nim


def gain_correct(image, gain=None, gain_key=None, inplace=False,
                 logger=logger):
    """Process the gain correction of an image."""
    im = check_hdu(image)
    if gain_key is not None:
        try:
            g = opd_number(im.header[gain_key])
            if gain is not None:
                logger.info('gain_key and gain passed. Using gain_key.')
        except Exception:
            g = gain
    elif gain is not None:
        g = gain
    else:
        raise ValueError('No gain or gain_key passed.')

    nim = imarith(image, g, '*', inplace=inplace)
    nim.header['hierarch gain corrected'] = True
    nim.header['hierarch gain corrected_value'] = g

    return nim


def block_reduce(image, block_size, func=np.sum, readnoise_key=None,
                 inplace=False, logger=logger):
    """Process rebinnig in one image. Like block_reduce."""
    im = check_hdu(image)
    if not inplace:
        im = fits.PrimaryHDU(im.data, header=im.header)

    im.data = br(im.data, block_size, func)
    summed = br(im.data, block_size, np.sum)
    im.header['hierarch block_reduced'] = block_size

    # Fix readnoise if readnoise_key is passed
    if readnoise_key in im.header.keys():
        try:
            rdnoise = opd_number(im.header[readnoise_key])
            im.header[readnoise_key] = block_size * rdnoise
            if func == np.sum:
                # fix the readnoise by functions that are not the sum
                im.header[readnoise_key] /=  np.sqrt(np.nanmean(summed/im.data))
            im.header['hierarch block_reduced readnoise_old'] = rdnoise
        except ValueError:
            pass

    return im


block_reduce.__doc__ += br.__doc__


def cosmic_lacosmic(image, inplace=False, **lacosmic_kwargs, logger=logger):
    """Remove cosmic rays with LAcosmic. From astroscrappy package."""
    im = check_hdu(image)
    if not inplace:
        im = fits.PrimaryHDU(im.data, im.header)

    im.data = detect_cosmics(im.data, **lacosmic_kwargs)[1]
    im.header['hierarch lacosmic'] = True

    return im


def process_image(image, save_to=None, overwrite=True,
                  master_bias=None, dark_frame=None, master_flat=None,
                  gain=None, gain_key=None, image_exposure=None,
                  dark_exposure=None, exposure_key=None, trim=None,
                  trim_fits_convention=False,
                  lacosmic=False, lacosmic_params={}, rebin_func=np.sum,
                  rebin_size=None, readnoise_key=None, badpixmask=None,
                  inplace=False, bias_check_keys=[], flat_check_keys=[],
                  dark_check_keys=[], badpix_check_keys=[],
                  logger=logger):
    """Full process of an image."""
    im = check_hdu(image, logger=logger)
    if im.fileinfo() is not None:
        logger.info('Processing image {}'.format(im.fileinfo()['file'].name))

    if not inplace:
        im = fits.PrimaryHDU(im.data, header=im.header)

    # Process order: lacosmic, block_reduce, gain, bias, dark, flat
    if lacosmic:
        logger.info('Processing lacosmic.')
        im = cosmic_lacosmic(image, inplace=inplace, **lacosmic_params,
                             logger=logger)

    if rebin_size is not None:
        logger.info('Process rebining with block size {}'.format(rebin_size))
        im = block_reduce(im, rebin_size, func=rebin_func,
                          readnoise_key=readnoise_key, inplace=inplace,
                          logger=logger)

    if trim is not None:
        logger.info('Trimming the image to: {}'.format(trim))
        im = trim_image(im, trim, fits_convention=trim_fits_convention,
                        inplace=inplace, logger=logger)

    if gain is not None or gain_key is not None:
        logger.info('Gain correct with gain {} and gain_key {}'
                    .format(gain, gain_key))
        im = gain_correct(im, gain=gain, gain_key=gain_key, inplace=inplace,
                          logger=logger)

    if master_bias is not None:
        logger.info('Bias correction {}'.format(master_bias))
        im = subtract_bias(im, master_bias, check_keys=bias_check_keys,
                           inplace=inplace, logger=logger)

    if dark_frame is not None:
        logger.info('Dark correction {}'.format(dark_frame))
        im = subtract_dark(im, dark_frame, dark_exposure=dark_exposure,
                           image_exposure=image_exposure,
                           check_keys=dark_check_keys,
                           exposure_key=exposure_key, inplace=inplace,
                           logger=logger)

    if master_flat is not None:
        logger.info('flat correction {}'.format(master_flat))
        im = divide_flat(im, master_flat, check_keys=flat_check_keys,
                         inplace=inplace, logger=logger)

    if badpixmask is not None:
        im.mask = badpixmask
    else:
        im.mask = None

    if save_to:
        save_hdu(im, save_to, overwrite=overwrite,
                 logger=logger)

    return im
