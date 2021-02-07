# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Handle the IRAF's imarith and imcombine functions."""
# TODO: reimplement imcombine

import numpy as np

from ..framedata import FrameData, check_framedata, EmptyDataError
from ..math.physical import QFloat, convert_to_qfloat
from ..logger import logger, log_to_list

__all__ = ['imarith', 'imcombine']


_arith_funcs = {'+': np.add,
                '-': np.subtract,
                '/': np.true_divide,
                '//': np.floor_divide,
                '*': np.multiply,
                '**': np.power,
                '%': np.remainder}


def _qf_or_framedata(data, alternative=QFloat):
    """Check if the data is QFloat or FrameData. Else, convert it."""
    if isinstance(data, (QFloat, FrameData)):
        return data
    return alternative(data)


def _arith_mask(operand1, operand2, logger):
    """Handle the arithmatics of the masks."""
    def _extract(operand):
        if hasattr(operand, 'mask'):
            return operand.mask
        return False

    mask1 = operand1.mask
    mask2 = operand2.mask

    old_n = np.count_nonzero(mask1)
    nmask = np.logical_or(mask1, mask2)
    new_n = np.count_nonzero(nmask)
    logger.debug(f'Updating mask in math operation. '
                 f'From {old_n} to {new_n} masked elements.')
    return nmask


def _arith(operand1, operand2, operation):
    """Perform the math operation itself using QFloats."""
    qf1 = convert_to_qfloat(operand1)
    qf2 = convert_to_qfloat(operand2)

    res = _arith_funcs[operation](qf1, qf2)
    return res.nominal, res.std_dev


def _join_headers(operand1, operand2, operation, logger):  # noqa
    """Join the headers to result."""
    # TODO: Think if this is the best behavior
    return operand1.header.copy()


def imarith(operand1, operand2, operation, inplace=False,
            join_masks=False, logger=logger):
    """Perform arithmetic operations using `~astropop.framedata.FrameData`.

    Notes
    -----
    * Keeps the header of the first image.

    * If ``operand1`` is not a `~astropop.framedata.FrameData` instance,
      inplies in ``inplace=False``, and a new `~astropop.framedata.FrameData`
      instance will be created.

    * Supported operations:
        - ``+`` : add. Example: 1+1=2
        - ``-`` : subtract. Example: 2-1=1
        - ``*`` : scalar product. Example: 2*3=6
        - ``/`` : true division. Example: 3/2=1.5
        - ``**`` : power. Example: 3**2=9
        - ``%`` : modulus. Example: 7%2=1
        - ``//`` : floor division. Example: 7//2=3

    Parameters
    ----------
    operand1, operand2 : `~astropop.framedata.FrameData` compatible
        Values to perform the operation. `~astropop.math.physical.QFloat`
        `~astropy.units.Quantity`, numerical values and
        `~astropy.nddata.CCDData` are also suported.
    operation : {``+``, ``-``, ``*``, ``/``, ``**``, ``%``, ``//``}
        Math operation.
    inplace : bool, optional
        If True, the operations will be performed inplace in the operand 1.
    join_masks : bool, optional
        Join masks in the end of the operation.
    logger : `logging.Logger`
        Python logger to log the actions.

    Returns
    -------
    `~astropop.framedata.FrameData`:
        new `FrameData` instance if not ``inplace``, else the ``operand1``
        `~astropop.framedata.FrameData` instance.
    """
    # TODO: handle WCS
    if operation not in _arith_funcs.keys():
        raise ValueError(f"Operation {operation} not supported.")

    if isinstance(operand1, FrameData) and inplace:
        ccd = operand1
    else:
        ccd = FrameData(None)

    operand1 = _qf_or_framedata(operand1)
    operand2 = _qf_or_framedata(operand2)
    if operand1.data.empty or operand2.data.empty:
        raise EmptyDataError(f'Operation {operation} not permited with empty'
                             f' data containers.')

    # Add the operation entry to the ccd history.
    lh = log_to_list(logger, ccd.history)
    logger.debug(f'Operation {operation} between {operand1} and {operand2}')

    # Perform data, mask and uncertainty operations
    ccd.data, ccd.uncertainty = _arith(operand1, operand2, operation)

    if join_masks:
        ccd.mask = _arith_mask(operand1, operand2, logger)
    else:
        ccd.mask = False

    ccd.meta = _join_headers(operand1, operand2, operation, logger)

    logger.removeHandler(lh)

    return ccd


def imcombine(*args, **kwargs):
    raise NotImplementedError
