def _ges_rentenv_beitr_bemess_grenze_m(
    wohnort_ost: bool, soz_vers_beitr_params: dict
) -> float:
    """Calculating the income threshold up to which pension insurance payments apply.

    Parameters
    ----------
    wohnort_ost
        See :func:`wohnort_ost`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    params = soz_vers_beitr_params["beitr_bemess_grenze_m"]["ges_rentenv"]
    out = params["ost"] if wohnort_ost else params["west"]

    return float(out)


def _ges_krankenv_beitr_bemess_grenze_m(
    wohnort_ost: bool, soz_vers_beitr_params: dict
) -> float:
    """Calculating the income threshold up to which health insurance payments apply.

    Parameters
    ----------
    wohnort_ost
        See :func:`wohnort_ost`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    The income threshold up to which the rate of health insurance contributions apply.

    """
    params = soz_vers_beitr_params["beitr_bemess_grenze_m"]["ges_krankenv"]

    out = params["ost"] if wohnort_ost else params["west"]

    return float(out)


def _ges_krankenv_bezugsgröße_selbst_m(
    wohnort_ost: bool, soz_vers_beitr_params: dict
) -> float:
    """Threshold for self employment income subject to health insurance.

    Selecting by place of living the income threshold for self employed up to which the
    rate of health insurance contributions apply.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    out = (
        soz_vers_beitr_params["bezugsgröße_selbst_m"]["ost"]
        if wohnort_ost
        else soz_vers_beitr_params["bezugsgröße_selbst_m"]["west"]
    )

    return float(out)
