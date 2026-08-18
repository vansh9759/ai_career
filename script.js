// ===========================================
// Generate Resume
// ===========================================

document.getElementById("generateResume").addEventListener("click", function () {

    // Show Loading Spinner
    document.getElementById("loading").style.display = "block";

    // Personal Details
    document.getElementById("namePreview").innerText =
        document.getElementById("name").value;

    document.getElementById("titlePreview").innerText =
        document.getElementById("title").value;

    document.getElementById("emailPreview").innerText =
        document.getElementById("email").value;

    document.getElementById("phonePreview").innerText =
        document.getElementById("phone").value;

    document.getElementById("locationPreview").innerText =
        document.getElementById("location").value;

    document.getElementById("websitePreview").innerText =
        document.getElementById("website").value;

    document.getElementById("summaryPreview").innerText =
        document.getElementById("summary").value;

    document.getElementById("educationPreview").innerText =
        document.getElementById("education").value;

    document.getElementById("experiencePreview").innerText =
        document.getElementById("experience").value;

    // Skills
    let skills = document.getElementById("skills").value.split(",");

    let skillHTML = "";

    skills.forEach(function (skill) {

        if (skill.trim() !== "") {

            skillHTML +=
                `<span class="badge bg-primary m-1">${skill.trim()}</span>`;

        }

    });

    document.querySelector(".section:nth-of-type(4)").innerHTML = `
        <h3>
            <i class="bi bi-code-slash"></i>
            Skills
        </h3>

        <hr>

        ${skillHTML}
    `;

    // Save Resume
    saveResume();

    // Success Message
    document.getElementById("successMessage").style.display = "block";

    setTimeout(function () {

        document.getElementById("successMessage").style.display = "none";

    }, 3000);

    // Hide Loading Spinner
    setTimeout(function () {

        document.getElementById("loading").style.display = "none";

    }, 1000);

});
document.getElementById("profileImage").addEventListener("change", function () {

    const file = this.files[0];

    if (file) {

        const reader = new FileReader();

        reader.onload = function (e) {

            document.getElementById("profilePreview").src = e.target.result;

        };

        reader.readAsDataURL(file);

    }

});
document.getElementById("themeBtn").addEventListener("click", function () {

    document.body.classList.toggle("light-theme");

});
function saveResume() {

    const data = {

        name: name.value,
        title: title.value,
        email: email.value,
        phone: phone.value,
        location: location.value,
        website: website.value,
        summary: summary.value,
        education: education.value,
        experience: experience.value,
        skills: skills.value

    };

    localStorage.setItem("resumeData", JSON.stringify(data));

}
window.onload = function () {

    let data = JSON.parse(localStorage.getItem("resumeData"));

    if (data) {

        name.value = data.name;
        title.value = data.title;
        email.value = data.email;
        phone.value = data.phone;
        location.value = data.location;
        website.value = data.website;
        summary.value = data.summary;
        education.value = data.education;
        experience.value = data.experience;
        skills.value = data.skills;

    }

};