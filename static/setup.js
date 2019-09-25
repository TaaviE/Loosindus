let add_family_button;
let reset_button;
let submit_button;
let form_root;

let family_count = 0;
let member_count = 0;
let valid = false;

function onAddFamily() {
    console.log("Adding family", family_count);
    let family_id = family_count;
    family_count++;

    let family = document.createElement("div");
    family.setAttribute("id", "family-element-" + family_id);
    family.setAttribute("class", "mdl-shadow--2dp mdl-color--white mdl-cell mdl-cell--8-col-tablet mdl-cell--6-col-desktop mdl-cell--4-col-phone mdl-cell--6-col");

    let family_container = document.createElement("div");
    family_container.setAttribute("class", "mdl-card__supporting-text mdl-color-text--grey-600");

    let family_name_container = document.createElement("div");
    family_name_container.setAttribute("class", "mdl-textfield mdl-js-textfield mdl-textfield--floating-label");
    family_name_container.setAttribute("id", "family-name-container-" + family_id);
    family_name_container.setAttribute("family_id", family_id);

    let family_name = document.createElement("input");
    family_name.setAttribute("class", "mdl-textfield__input");
    family_name.setAttribute("type", "text");
    family_name.setAttribute("name", "family-name-" + family_id);
    family_name.setAttribute("minlength", "1");
    family_name.setAttribute("pattern", "[^?!;:()/<>[\\],'|\"]+");
    family_name.setAttribute("id", "family-name-text-" + family_id);
    family_name.setAttribute("family_id", family_id);

    let family_name_label = document.createElement("label");
    family_name_label.setAttribute("class", "mdl-textfield__label");
    family_name_label.setAttribute("for", "family-name-text-" + family_id);
    family_name_label.textContent = "Family name";

    let family_name_error = document.createElement("span");
    family_name_error.setAttribute("class", "mdl-textfield__error");
    family_name_error.textContent = "Make sure you enter a family name";

    let add_member_button = document.createElement("a");
    add_member_button.setAttribute("class", "mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect mdl-button--accent");
    add_member_button.setAttribute("href", "#");
    add_member_button.setAttribute("id", "family-member-button-" + family_id);
    add_member_button.textContent = "Add member";
    add_member_button.addEventListener("click", function () {
        onAddMember(family_container, family_id);
    });

    let delete_button = document.createElement("a");
    delete_button.setAttribute("class", "custom-left-margin mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect mdl-button--accent");
    delete_button.setAttribute("href", "#");
    delete_button.setAttribute("id", "family-member-button-" + family_id);
    delete_button.textContent = "Delete family";
    delete_button.addEventListener("click", function () {
        onDeleteElement(family);
    });


    family_name_container.appendChild(family_name);
    family_name_container.appendChild(family_name_label);
    family_name_container.appendChild(family_name_error);
    componentHandler.upgradeElement(family_name_container);

    family_container.append(add_member_button);
    family_container.append(delete_button);
    family_container.append(document.createElement("p"));
    family_container.appendChild(family_name_container);
    componentHandler.upgradeElement(delete_button);

    family.appendChild(family_container);
    form_root.appendChild(family);
};

function onReset() {
    console.log("Resetting form");
    for (let i = 0; i < member_count; i++) {
        let elem = document.getElementById("member-element-" + i);
        onDeleteElement(elem);
    }

    for (let i = 0; i < family_count; i++) {
        let elem = document.getElementById("family-element-" + i);
        onDeleteElement(elem);
    }
    family_count = 0;
    member_count = 0;
};

function onSubmit() {
    console.log("Submit requested");
    let contents = getFormContents();
    if (contents === null) {
        console.log("Form is not valid!");
        return null;
    }
    console.log("Form is valid");

    let data = JSON.stringify(contents);
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/setup", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(data);
    xhr.onload = function () {
        let data = JSON.parse(this.responseText);
        console.log("Got a reply from server", data);
        if (xhr.status !== 200) {
            addWarning(data["error_message"])
        }
    };
};

function addWarning(warning_content) {
    console.log("Displaying warning", family_count);
    let family = document.createElement("div");
    family.setAttribute("class", "mdl-shadow--2dp mdl-color--white mdl-cell mdl-cell--8-col-tablet mdl-cell--6-col-desktop mdl-cell--4-col-phone mdl-cell--6-col");

    let family_card_title = document.createElement("div");
    family_card_title.setAttribute("class", "mdl-color--red-400 custom-white-text mdl-card__title mdl-card--expand mdl-shadow--2dp");

    let family_card_title_text = document.createElement("h2");
    family_card_title_text.innerText = "Error!";

    let family_container = document.createElement("div");
    family_container.setAttribute("class", "mdl-card__supporting-text mdl-color-text--grey-600");
    family_container.textContent = warning_content;

    let delete_button = document.createElement("a");
    delete_button.setAttribute("class", "custom-left-margin mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect mdl-button--accent");
    delete_button.setAttribute("href", "#");
    delete_button.textContent = "Dismiss";
    delete_button.addEventListener("click", function () {
        onDeleteElement(family);
    });

    family_container.append(delete_button);
    family_container.append(document.createElement("p"));
    componentHandler.upgradeElement(delete_button);
    componentHandler.upgradeElement(family_container);

    family_card_title.appendChild(family_card_title_text);
    family.appendChild(family_card_title);
    family.appendChild(family_container);
    form_root.insertBefore(family, form_root.firstChild);
}


function getFormContents() {
    let families = {};
    if (family_count <= 0) {
        addWarning("Too few families have been added");
        return null;
    }

    if (member_count <= 3) {
        addWarning("Not enough members in families");
        return null;
    }

    for (let i = 0; i < family_count; i++) {
        let family_name = document.getElementById("family-name-text-" + i);
        if (!(family_name.textContent === null) && !(family_name.textContent === "")) {
            families[i]["name"] = family_name.textContent;
            families[i]["users"] = [];
        } else {
            addWarning("One family doesn't have a name!");
            console.log("Family name is null");
            return null;
        }
    }
    ;

    for (let i = 0; i < member_count; i++) {
        let user_name = document.getElementById("user-name-" + i);
        let user_email = document.getElementById("user-email-" + i);

        let family_id = user_name.getAttribute("family_id");
        let user_id = user_name.getAttribute("user_id");
        if (!(user_name.textContent === null) && !(user_name.textContent === "")) {
            families[family_id]["users"][user_id]["name"] = user_name.textContent;
        } else {
            addWarning("One user doesn't have a name!");
            console.log("Username is empty", user_id);
            return null;
        }
        if (!(user_email.textContent === null) && !(user_email.textContent === "")) {
            families[family_id]["users"][user_id]["email"] = user_email.textContent;
        } else {
            addWarning("One user doesn't have an e-mail!");
            console.log("User e-mail is empty", user_id);
            return null;
        }
    }

    for (let i = 0; i < family_count; i++) {
        if (families[i]["users"].length <= 0) {
            addWarning("One family is empty!");
            console.log("One family has 0 users");
            return null;
        }
        ;
    }
    ;
}

function onDeleteElement(element) {
    element.parentNode.removeChild(element);
}

function onAddMember(family, family_id) {
    let member = document.createElement("div");
    member.setAttribute("class", "custom-equal mdl-card__supporting-text mdl-color-text--grey-600");

    let member_id = member_count;
    member_count++;

    console.log("Added member", member_id);

    let member_name = document.createElement("div");
    member_name.setAttribute("class", "custom-half mdl-textfield mdl-js-textfield mdl-textfield--floating-label");

    let member_name_text = document.createElement("input");
    member_name_text.setAttribute("class", "mdl-textfield__input");
    member_name_text.setAttribute("type", "text");
    member_name_text.setAttribute("minlength", "1");
    member_name_text.setAttribute("pattern", "[^!?;:()/<>[\\],'|\"]+");
    member_name_text.setAttribute("name", "user-name-" + member_id);
    member_name_text.setAttribute("id", "user-name-" + member_id);
    member_name_text.setAttribute("user_id", member_id);
    member_name_text.setAttribute("family_id", family_id);

    let member_name_label = document.createElement("label");
    member_name_label.setAttribute("class", "mdl-textfield__label");
    member_name_label.setAttribute("for", "user-name-" + member_id);
    member_name_label.textContent = "User's name";

    let member_name_error = document.createElement("span");
    member_name_error.setAttribute("class", "mdl-textfield__error");
    member_name_error.textContent = "Entered text must not be empty";

    let member_email = document.createElement("div");
    member_email.setAttribute("class", "custom-half mdl-textfield mdl-js-textfield mdl-textfield--floating-label");

    let member_email_text = document.createElement("input");
    member_email_text.setAttribute("class", "mdl-textfield__input");
    member_email_text.setAttribute("type", "text");
    member_email_text.setAttribute("name", "user-email-" + member_id);
    member_email_text.setAttribute("id", "user-email-" + member_id);
    member_email_text.setAttribute("pattern", ".+\@.+\..+");
    member_email_text.setAttribute("minlength", "3");
    member_email_text.setAttribute("user_id", member_id);
    member_email_text.setAttribute("family_id", family_id);

    let member_email_label = document.createElement("label");
    member_email_label.setAttribute("class", "mdl-textfield__label");
    member_email_label.setAttribute("for", "user-name-" + member_id);
    member_email_label.textContent = "E-mail";

    let member_email_error = document.createElement("span");
    member_email_error.setAttribute("class", "mdl-textfield__error");
    member_email_error.textContent = "Entered text must be a valid e-mail";

    member_name.appendChild(member_name_text);
    member_name.appendChild(member_name_label);
    member_name.appendChild(member_name_error);
    componentHandler.upgradeElement(member_name);

    member_email.appendChild(member_email_text);
    member_email.appendChild(member_email_label);
    member_email.appendChild(member_email_error);
    componentHandler.upgradeElement(member_email);

    let delete_member = document.createElement("a");
    delete_member.setAttribute("class", "mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect mdl-button--accent");
    delete_member.setAttribute("href", "#");
    delete_member.setAttribute("id", "family-member-button-" + family_id);
    delete_member.textContent = "Delete";
    componentHandler.upgradeElement(delete_member);
    delete_member.addEventListener("click", function () {
        onDeleteElement(member);
    });

    member.appendChild(member_name);
    member.appendChild(member_email);
    member.appendChild(delete_member);
    member.appendChild(document.createElement("br"));

    family.appendChild(member);
};

function setupListeners() {
    add_family_button = document.getElementById("add-family-button");
    reset_button = document.getElementById("reset-button");
    submit_button = document.getElementById("submit-button");
    form_root = document.getElementById("mdl-grid");


    add_family_button.addEventListener("click", onAddFamily);
    reset_button.addEventListener("click", onReset);
    submit_button.addEventListener("click", onSubmit);
};

document.addEventListener("DOMContentLoaded", setupListeners);