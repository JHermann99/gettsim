from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def grundsicherung_m_hh(
    grundsicherung_m_minus_eink_hh: FloatSeries,
    wohngeld_vorrang_hh: BoolSeries,
    kinderzuschlag_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschlag_vorrang_hh: BoolSeries,
    regelaltersgrenze,
    alter,
    anz_erwachsene_hh,
    anz_rentner_hh,
) -> FloatSeries:
    """Calcualte Grundsicherung im Alter on household level

    Parameters
    ----------
    grundsicherung_m_minus_eink_hh
    wohngeld_vorrang_hh
    kinderzuschlag_vorrang_hh
    wohngeld_kinderzuschlag_vorrang_hh
    regelaltersgrenze
    alter
    Returns
    -------

    """

    out = grundsicherung_m_minus_eink_hh.clip(lower=0)
    cond = (
        wohngeld_vorrang_hh
        | kinderzuschlag_vorrang_hh
        | wohngeld_kinderzuschlag_vorrang_hh
        | (alter < regelaltersgrenze)
        | (anz_erwachsene_hh != anz_rentner_hh)
    )
    out.loc[cond] = 0
    return out


def grundsicherung_m_minus_eink_hh(
    regelbedarf_m_grundsicherung_vermögens_check_hh: FloatSeries,
    kindergeld_m_hh: FloatSeries,
    unterhaltsvors_m_hh: FloatSeries,
    grundsicherung_eink_hh: FloatSeries,
) -> FloatSeries:
    """Calcualte remaining basic subsistence after recieving other benefits.

    Parameters
    ----------
    regelbedarf_m_grundsicherung_vermögens_check_hh
    kindergeld_m_hh
    unterhaltsvors_m_hh
    grundsicherung_eink_hh

    Returns
    -------

    """
    out = (
        regelbedarf_m_grundsicherung_vermögens_check_hh
        - grundsicherung_eink_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    )
    return out


def grundsicherung_eink_hh(
    grundsicherung_eink: FloatSeries, hh_id: IntSeries
) -> FloatSeries:
    """sum up income for calculation of Grundsicherung im Alter per household

    Parameters
    ----------
    grundsicherung_eink
    hh_id

    Returns
    -------

    """

    return grundsicherung_eink.groupby(hh_id).sum()


def grundsicherung_eink(
    arbeitsl_geld_2_brutto_eink: FloatSeries,
    eink_st_tu: FloatSeries,
    tu_id: IntSeries,
    soli_st_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    sozialv_beitr_m: FloatSeries,
    eink_anr_frei_grundsicherung: FloatSeries,
    freibetrag_grundsicherung_grundrente,
) -> FloatSeries:
    """sum up income for calculation of Grundsicherung im Alter

    Parameters
    ----------
    arbeitsl_geld_2_brutto_eink
    eink_st_tu
    tu_id
    soli_st_tu
    anz_erwachsene_tu
    sozialv_beitr_m
    eink_anr_frei_grundsicherung
    freibetrag_grundsicherung_grundrente

    Returns
    -------

    """

    return (
        arbeitsl_geld_2_brutto_eink
        - tu_id.replace((eink_st_tu / anz_erwachsene_tu) / 12)
        - tu_id.replace((soli_st_tu / anz_erwachsene_tu) / 12)
        - sozialv_beitr_m
        - eink_anr_frei_grundsicherung
        - freibetrag_grundsicherung_grundrente
    ).clip(lower=0)


def eink_anr_frei_grundsicherung(bruttolohn_m, arbeitsl_geld_2_params):
    """calculate income not considered for amount of Grundsicherung im Alter

    Parameters
    ----------
    bruttolohn_m
    arbeits_geld_2_params

    Returns
    -------

    """
    out = (bruttolohn_m * 0.3).clip(upper=0.5 * arbeitsl_geld_2_params["regelsatz"][1])

    return out


def regelbedarf_m_grundsicherung_vermögens_check_hh(
    regelbedarf_m_hh: FloatSeries,
    unter_vermögens_freibetrag_grundsicherung_hh: BoolSeries,
) -> FloatSeries:
    """Set preliminary basic subsistence to zero if it exceeds the wealth exemption.


    Parameters
    ----------
    regelbedarf_m_hh
    unter_vermögens_freibetrag_grundsicherung_hh

    Returns
    -------

    """

    out = regelbedarf_m_hh
    out.loc[~unter_vermögens_freibetrag_grundsicherung_hh] = 0
    return out


def unter_vermögens_freibetrag_grundsicherung_hh(
    vermögen_hh, freibetrag_vermögen_grundsicherung_hh
):
    """check if capital of household is below limit of Grundsicherung im Alter


    Parameters
    ----------
    vermögen_hh
    freibetrag_vermögen_grundsicherung_hh

    Returns
    -------

    """
    return vermögen_hh < freibetrag_vermögen_grundsicherung_hh


def freibetrag_vermögen_grundsicherung_hh(haushaltsgröße_hh):
    """maximum capital allowed for Grundsicherung im Alter


    Parameters
    ----------
    haushaltsgröße

    Returns
    -------

    """
    out = 5000 * haushaltsgröße_hh
    return out
