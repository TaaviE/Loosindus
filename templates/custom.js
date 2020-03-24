// Copyright: Taavi Eomäe 2017-2020
// SPDX-License-Identifier: AGPL-3.0-only

{% if no_ads != true and config.GOOGLE_ADS %}
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
            let ad_div = document.getElementById("google-ad-div");
            ad_div.style.display = "none";
        }
    } catch (e) {
        console.log(e);
    }
};
{% endif %}
{% if no_tracking != true %}
try {
    window.dataLayer = window.dataLayer || [];

    function gtag() {
        dataLayer.push(arguments);
    }

    gtag("js", new Date());
    gtag("set", "anonymizeIp", true);
    gtag("config", "{{ config.GAUA }}");
} catch (e) {
    console.log(e);
}
{% endif %}

if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker.register("/worker.js")
            .then(function (registration) {
                console.log("Success", registration);
            }, function (exception) {
                console.log("An error occured", exception);
            });
    });
}