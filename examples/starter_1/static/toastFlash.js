"use strict";

function showFlashToast(){
    var flashToast = document.getElementById('flashToast');
    var toast = new bootstrap.Toast(flashToast);
    toast.show();
}

showFlashToast();
