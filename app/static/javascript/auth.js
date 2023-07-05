let successFieldCSS = "is-valid"
let errorFieldCSS = "is-invalid"
let successAlertCSS = "alert-success"
let errorAlertCSS = "alert-warning"
let successPolicyCSS = "good"
let errorPolicyCSS = "wrong"

//adds/removes classes to dom elements
function domElemUpdate(domElement, addCls, removeCls = null){
    domElement.classList.remove(removeCls);
    domElement.classList.add(addCls);
}

//verifies dom elements satisfy policy based on REGEX 
function verifyElem (domElemObj, value){
    domElemObj.pass = domElemObj.regexpr.test(value)
    if (domElemObj.pass){
        domElemUpdate(domElemObj.elem, successPolicyCSS, errorPolicyCSS)
    }
    else{
        domElemUpdate(domElemObj.elem, errorPolicyCSS, successPolicyCSS)
    }
}

//checks that a list of elements all pass the policy
function allPass(lstElem){
    let boolAllPass = true
    lstElem.forEach(function(itm){
        if (itm.pass === false){
            boolAllPass = false
            return boolAllPass;
        }
    });
    return boolAllPass 
}


addEventListener("DOMContentLoaded", (event) => {
    const passwordField = document.getElementById("floatingPW");
    const pwConfirmField = document.getElementById("floatingPWConf")
    const passwordAlert = document.getElementById("password-alert");
    const pwConfirmAlert = document.getElementById("passwordConfirm-alert");

    let pwConfig = {
        "pwMinLenREGEX":".{8,}",
        "pwSpecialCharREGEX": "[!@#$%^&*()_+\\-=\\[\\]{};':\"\\\\|,.<>\\/?`~]",
        "pwNumREGEX":"\d",
        "pwLowerCaseREGEX": "[a-z]",
        "pwUpperCaseREGEX": "[A-Z]"
    };

    let lengValidator = {elem: document.querySelector(".leng"), pass:false, regexpr:RegExp(pwConfig.pwMinLenREGEX)};
    let capLetterValidator = {elem: document.querySelector(".big-letter"), pass:false, regexpr:RegExp(pwConfig.pwUpperCaseREGEX)};
    let numValidator = {elem: document.querySelector(".num"), pass: false, regexpr: RegExp(pwConfig.pwNumREGEX)};
    let specialCharValidator = {elem: document.querySelector(".special-char"), pass: false, regexpr: RegExp(pwConfig.pwSpecialCharREGEX)};
    let lowerCaseLetterValidator = {elem: document.querySelector(".lowercase-letter"), pass:false, regexpr: RegExp(pwConfig.pwLowerCaseREGEX)};
    const confirmValidator = document.querySelector(".confirmReq")

    let policyRequirements = [lengValidator, capLetterValidator, numValidator, specialCharValidator, lowerCaseLetterValidator]

    //initializing all policies to fail
    policyRequirements.forEach((element) => domElemUpdate(element, errorPolicyCSS, successPolicyCSS));
    domElemUpdate(confirmValidator, errorPolicyCSS, successPolicyCSS);

    //initializing the alerts 
    passwordField.addEventListener("focus", () => {
        if (!passwordAlert.classList.contains(successAlertCSS)){
            domElemUpdate(passwordAlert, errorAlertCSS)
        }
    });

    pwConfirmField.addEventListener("focus", () => {
        if (!pwConfirmAlert.classList.contains(successAlertCSS)){
            domElemUpdate(pwConfirmAlert, errorAlertCSS)
        }
    });

    //Update Logic for Password
    passwordField.addEventListener("input", () => {
        let pwValue = passwordField.value;

        policyRequirements.forEach(function(validator){
            verifyElem(validator, pwValue)
        });

        if (allPass(policyRequirements)) {
            domElemUpdate(passwordField, successFieldCSS, errorFieldCSS);
            domElemUpdate(passwordAlert, successAlertCSS, errorAlertCSS);
        } else {
            domElemUpdate(passwordField, errorFieldCSS, successFieldCSS);
            domElemUpdate(passwordAlert, errorAlertCSS, successAlertCSS);
        }
    });

    //Update Logic for Password Confirm
    pwConfirmField.addEventListener("input", () => {
        let pwConfValue = pwConfirmField.value;
        if (pwConfValue === passwordField.value) {
            domElemUpdate(pwConfirmField, successFieldCSS, errorFieldCSS)
            domElemUpdate(pwConfirmAlert, successAlertCSS, errorAlertCSS)
            domElemUpdate(confirmValidator, successPolicyCSS, errorPolicyCSS)
        } else  {
            domElemUpdate(pwConfirmField, errorFieldCSS, successFieldCSS,)
            domElemUpdate(pwConfirmAlert, errorAlertCSS, successAlertCSS)
            domElemUpdate(confirmValidator, errorPolicyCSS, successPolicyCSS)
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

