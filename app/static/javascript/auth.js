addEventListener("DOMContentLoaded", (event) => {
    const passwordField = document.getElementById("floatingPW");
    const pwConfirmField = document.getElementById("floatingPWConf")
    const passwordAlert = document.getElementById("password-alert");
    const passwordConfirmAlert = document.getElementById("passwordConfirm-alert");
    const requirements = document.querySelectorAll(".requirements");
    let lengBoolean, hasCapital, hasNum, hasSpecialChar, hasLowerCase;
    let confirmValidator = document.querySelector(".confirmReq")
    let lengValidator = document.querySelector(".leng");
    let capLetterValidator = document.querySelector(".big-letter");
    let numValidator = document.querySelector(".num");
    let specialCharValidator = document.querySelector(".special-char");
    let lowerCaseLetter = document.querySelector(".lowercase-letter");

    requirements.forEach((element) => element.classList.add("wrong"));
    confirmValidator.classList.add("wrong");

    passwordField.addEventListener("focus", () => {
        if (!passwordAlert.classList.contains("is-valid")){
            passwordAlert.classList.add("alert-warning");
        }
    });

    pwConfirmField.addEventListener("focus", () => {
        if (!passwordConfirmAlert.classList.contains("is-valid")){
            passwordConfirmAlert.classList.add("alert-warning");
        }
    });

    passwordField.addEventListener("input", () => {
        let value = passwordField.value;
        if (value.length < 8) {
            lengBoolean = false;
            lengValidator.classList.add("wrong");
            lengValidator.classList.remove("good");
        } else {
            lengBoolean = true;
            lengValidator.classList.add("good");
            lengValidator.classList.remove("wrong");
        }

        if (value.toLowerCase() == value) {
            hasCapital = false;
            capLetterValidator.classList.add("wrong");
            capLetterValidator.classList.remove("good");
        } else {
            hasCapital = true;
            capLetterValidator.classList.add("good");
            capLetterValidator.classList.remove("wrong");
        }

        if (value.toUpperCase() == value) {
            hasLowerCase = false;
            lowerCaseLetter.classList.add("wrong");
            lowerCaseLetter.classList.remove("good");
        } else {
            hasLowerCase = true;
            lowerCaseLetter.classList.add("good");
            lowerCaseLetter.classList.remove("wrong");
        }

        var numRegex = /\d/;
        hasNum = numRegex.test(value)

        var specRegex = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?\`\~]/;
        hasSpecialChar = specRegex.test(value)

        if (lengBoolean && hasCapital && hasNum && hasSpecialChar && hasLowerCase) {
            passwordField.classList.remove("is-invalid");
            passwordField.classList.add("is-valid");

            requirements.forEach((element) => {
                element.classList.remove("wrong");
                element.classList.add("good");
            });
            passwordAlert.classList.remove("alert-warning");
            passwordAlert.classList.add("alert-success");
        } else {
            passwordField.classList.remove("is-valid");
            passwordField.classList.add("is-invalid");

            passwordAlert.classList.add("alert-warning");
            passwordAlert.classList.remove("alert-success");

            if (hasNum == false) {
                numValidator.classList.add("wrong");
                numValidator.classList.remove("good");
            } else {
                numValidator.classList.add("good");
                numValidator.classList.remove("wrong");
            }

            if (hasSpecialChar == false) {
                specialCharValidator.classList.add("wrong");
                specialCharValidator.classList.remove("good");
            } else {
                specialCharValidator.classList.add("good");
                specialCharValidator.classList.remove("wrong");
            }
        }
    });

    pwConfirmField.addEventListener("input", () => {
        let value = pwConfirmField.value;
        if (value === passwordField.value) {
            pwConfirmField.classList.remove("is-invalid");
            pwConfirmField.classList.add("is-valid");
            passwordConfirmAlert.classList.remove("alert-warning");
            passwordConfirmAlert.classList.add("alert-success");
            confirmValidator.classList.remove("wrong");
            confirmValidator.classList.add("good");
        } else  {
            pwConfirmField.classList.remove("is-valid");
            pwConfirmField.classList.add("is-invalid");
            passwordConfirmAlert.classList.remove("alert-success");
            passwordConfirmAlert.classList.add("alert-warning");
            confirmValidator.classList.remove("good");
            confirmValidator.classList.add("wrong");
        }
    });
});

function toggle(id) {
    let pwField = document.getElementById(id);
     
    if (pwField.type === "password") {
        pwField.type = "text";
    }
    else {
        pwField.type = "password";
    }
}

