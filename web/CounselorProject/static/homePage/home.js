//home to recording
document.addEventListener("DOMContentLoaded", function() {
    let createButton = document.getElementById("create-button");

    if (createButton) {
        createButton.addEventListener("click", function() {
            console.log("create clicked");
            window.location.href = "/CounselorProject/recordingPage/";
        });
    }

    let settingsButton = document.getElementById("settings-button");

    if (settingsButton) {
        settingsButton.addEventListener("click", function() {
            console.log("settings clicked");
            window.location.href = "/CounselorProject/settingsPage/";
        });
    }

    let summaryButton = document.getElementById("summary-button");

    if (summaryButton) {
        summaryButton.addEventListener("click", function() {
            console.log("summary clicked");
            window.location.href = "/CounselorProject/summaryPage/";
        });
    }
});
