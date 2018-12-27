{% if no_ads != true %}
try {
    (adsbygoogle = window.adsbygoogle || []).push({});
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
    gtag("set",
        {"user_id": "{{ user_id }}"}
    );
} catch (e) {
    console.log(e);
}
{% endif %}