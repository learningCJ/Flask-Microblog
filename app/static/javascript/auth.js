addEventListener("DOMContentLoaded", (event) => {
    const password = document.getElementById("floatingPW");
    const password_confirm = document.getElementById("floatingPWConf")
    const passwordAlert = document.getElementById("password-alert");
    const passwordConfirmAlert = document.getElementById("passwordConfirm-alert");
    const requirements = document.querySelectorAll(".requirements");
    let lengBoolean, bigLetterBoolean, numBoolean, specialCharBoolean, lowerCaseBoolean, confirmEqualBoolean;
    let conf = document.querySelector(".confirmReq")
    let leng = document.querySelector(".leng");
    let bigLetter = document.querySelector(".big-letter");
    let num = document.querySelector(".num");
    let specialChar = document.querySelector(".special-char");
    let lowerCaseLetter = document.querySelector(".lowercase-letter");
    const specialChars = "!@#$%^&-_"//"!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?`~";
    const numbers = "0123456789";

    requirements.forEach((element) => element.classList.add("wrong"));
    conf.classList.add("wrong");

    password.addEventListener("focus", () => {
        if (!passwordAlert.classList.contains("is-valid")){
            passwordAlert.classList.add("alert-warning");
        }
        //passwordAlert.classList.remove("d-none");
        //if (!password.classList.contains("is-valid")) {
        //    password.classList.add("is-invalid");
        //}
    });

    password_confirm.addEventListener("focus", () => {
        if (!passwordConfirmAlert.classList.contains("is-valid")){
            passwordConfirmAlert.classList.add("alert-warning");
        }
        //passwordAlert.classList.remove("d-none");
        //if (!password.classList.contains("is-valid")) {
        //    password.classList.add("is-invalid");
        //}
    });

    password.addEventListener("input", () => {
        let value = password.value;
        if (value.length < 8) {
            lengBoolean = false;
        } else if (value.length > 7) {
            lengBoolean = true;
        }

        if (value.toLowerCase() == value) {
            bigLetterBoolean = false;
        } else {
            bigLetterBoolean = true;
        }

        if (value.toUpperCase() == value) {
            lowerCaseBoolean = false;
        } else {
            lowerCaseBoolean = true;
        }

        numBoolean = false;
        for (let i = 0; i < value.length; i++) {
            for (let j = 0; j < numbers.length; j++) {
                if (value[i] == numbers[j]) {
                    numBoolean = true;
                }
            }
        }

        specialCharBoolean = false;
        for (let i = 0; i < value.length; i++) {
            for (let j = 0; j < specialChars.length; j++) {
                if (value[i] == specialChars[j]) {
                    specialCharBoolean = true;
                }
            }
        }

        if (lengBoolean == true && bigLetterBoolean == true && numBoolean == true && specialCharBoolean == true && lowerCaseBoolean == true) {
            password.classList.remove("is-invalid");
            password.classList.add("is-valid");

            requirements.forEach((element) => {
                element.classList.remove("wrong");
                element.classList.add("good");
            });
            passwordAlert.classList.remove("alert-warning");
            passwordAlert.classList.add("alert-success");
        } else {
            password.classList.remove("is-valid");
            password.classList.add("is-invalid");

            passwordAlert.classList.add("alert-warning");
            passwordAlert.classList.remove("alert-success");

            if (lengBoolean == false) {
                leng.classList.add("wrong");
                leng.classList.remove("good");
            } else {
                leng.classList.add("good");
                leng.classList.remove("wrong");
            }

            if (bigLetterBoolean == false) {
                bigLetter.classList.add("wrong");
                bigLetter.classList.remove("good");
            } else {
                bigLetter.classList.add("good");
                bigLetter.classList.remove("wrong");
            }

            if (numBoolean == false) {
                num.classList.add("wrong");
                num.classList.remove("good");
            } else {
                num.classList.add("good");
                num.classList.remove("wrong");
            }

            if (specialCharBoolean == false) {
                specialChar.classList.add("wrong");
                specialChar.classList.remove("good");
            } else {
                specialChar.classList.add("good");
                specialChar.classList.remove("wrong");
            }
            if (lowerCaseBoolean == false) {
                lowerCaseLetter.classList.add("wrong");
                lowerCaseLetter.classList.remove("good");
            } else {
                lowerCaseLetter.classList.add("good");
                lowerCaseLetter.classList.remove("wrong");
            }
        }
    });

    /*password.addEventListener("blur", () => {
        passwordAlert.classList.add("d-none");
    });*/

    password_confirm.addEventListener("input", () => {
        let value = password_confirm.value;
        confirmEqualBoolean = false
        if (value === password.value) {
            confirmEqualBoolean = true;
        } else  {
            confirmEqualBoolean = false;
        }

        if (confirmEqualBoolean == true) {
            password_confirm.classList.remove("is-invalid");
            password_confirm.classList.add("is-valid");
            passwordConfirmAlert.classList.remove("alert-warning");
            passwordConfirmAlert.classList.add("alert-success");
            conf.classList.remove("wrong");
            conf.classList.add("good");

        } else {
            password_confirm.classList.remove("is-valid");
            password_confirm.classList.add("is-invalid");
            passwordConfirmAlert.classList.remove("alert-success");
            passwordConfirmAlert.classList.add("alert-warning");
            conf.classList.remove("good");
            conf.classList.add("wrong");
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

