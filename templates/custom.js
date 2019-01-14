{%
    if no_ads != true and;
    config.GOOGLE_ADS %
}
try {
    (adsbygoogle = window.adsbygoogle || []).push({
        google_ad_client: "{{ config.DATA_AD_CLIENT }}",
        enable_page_level_ads: false,
    });
} catch (e) {
    console.log(e);
}

window.onload = function () {
    try {
        if (!adsbygoogle.loaded) {
            addiv = document.getElementById("google-ad-div");
            addiv.style.display = "none";
        }
    } catch (e) {
        console.log(e);
    }
};
{% endif %}

{% if sentry_feedback %}
try {
    Raven.showReportDialog({
        eventId: "{{ sentry_event_id }}",
        dsn: "{{ sentry_public_dsn }}"
    });
} catch (e) {
    console.log(e);
}
{% endif %}

{% if no_tracking != true %}
try {
    window.dataLayer = window.dataLayer || [];

    function gtag() {
        dataLayer.push(arguments);
    }

    gtag("js", new Date());
    gtag("set", "anonymizeIp", true);
    gtag("config", "{{ config.GAUA}}");
} catch (e) {
    console.log(e);
}
{% endif %}