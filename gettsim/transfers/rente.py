from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.shared import add_rounding_spec


def sum_ges_rente_priv_rente_m(priv_rente_m: float, ges_rente_m: float) -> float:
    """Calculate total pension as sum of private and public pension.

    Parameters
    ----------
    priv_rente_m
        See basic input variable :ref:`priv_rente_m <priv_rente_m>`.
    ges_rente_m
        See :func:`ges_rente_m`.

    Returns
    -------

    """
    out = priv_rente_m + ges_rente_m
    return out


@add_rounding_spec(params_key="ges_rente")
def ges_rente_nach_grundr_m(
    ges_rente_vor_grundr_m: float,
    grundr_zuschlag_m: float,
    rentner: bool,
) -> float:
    """Calculate total public pension including Grundrentenzuschlag. Is
    only active after 2021 when Grundrente is in place.

    Parameters
    ----------
    ges_rente_vor_grundr_m
        See :func:`ges_rente_vor_grundr_m`.
    grundr_zuschlag_m
        See :func:`grundr_zuschlag_m`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.

    Returns
    -------

    """
    # Return 0 if person not yet retired
    out = ges_rente_vor_grundr_m + grundr_zuschlag_m if rentner else 0.0
    return out


@add_rounding_spec(params_key="ges_rente")
def ges_rente_vor_grundr_m(
    ges_rente_zugangsfaktor: float,
    entgeltp_update: float,
    rentenwert: float,
    rentner: bool,
) -> float:
    """Old-Age Pensions claim without Grundrentenzuschlag.
    The function follows the following equation:

    .. math::

        R = EP * ZF * Rw

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel


    Parameters
    ----------
    ges_rente_zugangsfaktor
        See :func:`ges_rente_zugangsfaktor`.
    entgeltp_update
        See :func:`entgeltp_update`.
    rentenwert
        See :func:`rentenwert`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.

    Returns
    -------

    """

    # Return 0 if person not yet retired
    if rentner:
        out = entgeltp_update * ges_rente_zugangsfaktor * rentenwert
    else:
        out = 0.0

    return out


def rentenwert(wohnort_ost: bool, ges_rente_params: dict) -> float:
    """Select the rentenwert depending on place of living.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    params = ges_rente_params["rentenwert"]

    out = params["ost"] if wohnort_ost else params["west"]

    return float(out)


def rentenwert_vorjahr(wohnort_ost: bool, ges_rente_params: dict) -> float:
    """Select the rentenwert of the last year depending on place of living.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    params = ges_rente_params["rentenwert_vorjahr"]

    out = params["ost"] if wohnort_ost else params["west"]

    return float(out)


def entgeltp_update(entgeltp: float, entgeltp_update_lohn: float) -> float:
    """Update earning points.

    Given earnings, social insurance rules, average
    earnings in a particular year and potentially other
    variables (e.g., benefits for raising children,
    informal care), return the new earnings points.

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

    Parameters
    ----------
    entgeltp
        See basic input variable :ref:`entgeltp <entgeltp>`.
    entgeltp_update_lohn
        See :func:`entgeltp_update_lohn`.

    Returns
    -------

    """

    # Note: We might need some interaction between the two
    # ways to accumulate earnings points (e.g., how to
    # determine what constitutes a 'care period')
    out = entgeltp + entgeltp_update_lohn
    return out


def entgeltp_update_lohn(
    bruttolohn_m: float,
    wohnort_ost: bool,
    _ges_rentenv_beitr_bemess_grenze_m: float,
    ges_rente_params: dict,
) -> float:
    """Return earning points for the wages earned in the last year.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    wohnort_ost
        See :func:`wohnort_ost`.
    _ges_rentenv_beitr_bemess_grenze_m
        See :func:`_ges_rentenv_beitr_bemess_grenze_m`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    Returns
    -------

    """

    # ToDo: Does the scaling bonus really apply to current wages or only to those that
    # ToDo: had been earned during GDR times?

    # Scale bruttolohn up if earned in eastern Germany
    if wohnort_ost:
        bruttolohn_scaled_east = (
            bruttolohn_m * ges_rente_params["umrechnung_entgeltp_beitrittsgebiet"]
        )
    else:
        bruttolohn_scaled_east = bruttolohn_m

    # Calculate the (scaled) wage, which is subject to pension contributions.
    if bruttolohn_scaled_east > _ges_rentenv_beitr_bemess_grenze_m:
        bruttolohn_scaled_rentenv = _ges_rentenv_beitr_bemess_grenze_m
    else:
        bruttolohn_scaled_rentenv = bruttolohn_scaled_east

    # Calculate monthly mean wage in Germany
    durchschnittslohn_m = (1 / 12) * ges_rente_params[
        "beitragspflichtiges_durchschnittsentgelt"
    ]

    out = bruttolohn_scaled_rentenv / durchschnittslohn_m
    return out


def ges_rente_zugangsfaktor(
    geburtsjahr: int,
    rentner: bool,
    jahr_renteneintr: int,
    ges_rente_regelaltersgrenze: float,
    ges_rente_params: dict,
) -> float:
    """Calculate the zugangsfaktor based on the year the
    subject retired.

    At the regelaltersgrenze - normal retirement age (NRA), the agent is allowed to
    get pensions with his full claim. In general, if the agent retires earlier or later,
    the Zugangsfaktor and therefore the pension claim is higher or lower.

    Legal reference: § 77 Abs. 2 Nr. 2 SGB VI

    However, under certain conditions agents can receive their full pension claim
    (Zugangsfaktor=1) at an earlier age - full retirement age (FRA) -  (e.g. women,
    long term insured, disabled). That is the zugangsfaktor is 1 in [FRA, NRA].
    It only increases after the NRA for all agents without exeptions.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    if rentner:
        # Calc age at retirement
        alter_renteneintritt = jahr_renteneintr - geburtsjahr

        # Calc difference to Regelaltersgrenze
        diff = alter_renteneintritt - ges_rente_regelaltersgrenze
        faktor_pro_jahr_vorzeitig = ges_rente_params[
            "zugangsfaktor_veränderung_pro_jahr"
        ]["vorzeitiger_renteneintritt"]
        faktor_pro_jahr_später = ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
            "späterer_renteneintritt"
        ]

        # Zugangsfactor lower if retired before Regelaltersgrenze
        # Zugangsfactor larger if retired before Regelaltersgrenze
        if diff < 0:
            out = 1 + diff * faktor_pro_jahr_vorzeitig
        else:
            out = 1 + diff * faktor_pro_jahr_später

        out = max(out, 0.0)
    # Return 0 if person not yet retired
    else:
        out = 0.0

    return out


def ges_rente_regelaltersgrenze(geburtsjahr: int, ges_rente_params: dict) -> float:
    """Calculates the age, at which a worker is eligible to claim his regular pension.
        Normal retirement age (NRA)

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    """
    out = piecewise_polynomial(
        x=geburtsjahr,
        thresholds=ges_rente_params["regelaltersgrenze"]["thresholds"],
        rates=ges_rente_params["regelaltersgrenze"]["rates"],
        intercepts_at_lower_thresholds=ges_rente_params["regelaltersgrenze"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return out


def ges_rente_grenze_altersrente(
    geburtsjahr: int, geburtsmonat: int, geschlecht: int, ges_rente_params: dict
) -> float:
    """Calculates the age, at which a worker is eligible to claim his full pension.
        Full retirement age (FRA). This age is smaller or equal to the regelaltersgrenze
        (FRA<=NRA) and depends on personal characteristics as gender, insurance
        duration, health/disability, employment status. Note: this is just implementing
        pension  for women. Todo: to be extended for long term insured etc.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    geschlecht
        Needs to become basic input variable!
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    """
    regelrente = piecewise_polynomial(
        x=geburtsjahr,
        thresholds=ges_rente_params["regelaltersgrenze"]["thresholds"],
        rates=ges_rente_params["regelaltersgrenze"]["rates"],
        intercepts_at_lower_thresholds=ges_rente_params["regelaltersgrenze"][
            "intercepts_at_lower_thresholds"
        ],
    )

    pension_for_women = piecewise_polynomial(
        x=geburtsjahr + geburtsmonat / 12,
        thresholds=ges_rente_params["altersrente_für_frauen"]["thresholds"],
        rates=ges_rente_params["altersrente_für_frauen"]["rates"],
        intercepts_at_lower_thresholds=ges_rente_params["altersrente_für_frauen"][
            "intercepts_at_lower_thresholds"
        ],
    )

    thresholds_m = [regelrente]
    thresholds_w = thresholds_m.extend(pension_for_women)

    if geschlecht == 0:
        thresholds = thresholds_m
    else:
        thresholds = thresholds_w

    out = min(thresholds)

    return out
