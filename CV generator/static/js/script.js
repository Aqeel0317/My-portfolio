document.addEventListener('DOMContentLoaded', function() {
    // --- Add Skill ---
    const addSkillButton = document.getElementById('add-skill');
    const skillsContainer = document.getElementById('skills-container');
    let skillCounter = skillsContainer.getElementsByClassName('skill-entry').length; // Start counting from existing entries

    if (addSkillButton) {
        addSkillButton.addEventListener('click', function() {
            skillCounter++;
            const newSkillEntry = document.createElement('div');
            newSkillEntry.classList.add('skill-entry');
            newSkillEntry.innerHTML = `
                <label for="skill_${skillCounter}">Skill:</label>
                <input type="text" name="skill_${skillCounter}" id="skill_${skillCounter}">
                <button type="button" class="remove-entry">Remove</button>
            `;
            skillsContainer.appendChild(newSkillEntry);
        });
    }

    // --- Add Experience ---
    const addExperienceButton = document.getElementById('add-experience');
    const experienceContainer = document.getElementById('experience-container');
    let experienceCounter = experienceContainer.getElementsByClassName('experience-entry').length;

    if (addExperienceButton) {
        addExperienceButton.addEventListener('click', function() {
            experienceCounter++;
            const newExperienceEntry = document.createElement('div');
            newExperienceEntry.classList.add('experience-entry');
            newExperienceEntry.innerHTML = `
                <h4>Experience ${experienceCounter}</h4>
                <label for="job_title_${experienceCounter}">Job Title:</label>
                <input type="text" name="job_title_${experienceCounter}" id="job_title_${experienceCounter}"><br>
                <label for="company_${experienceCounter}">Company:</label>
                <input type="text" name="company_${experienceCounter}" id="company_${experienceCounter}"><br>
                <label for="exp_years_${experienceCounter}">Years (e.g., 2020-Present):</label>
                <input type="text" name="exp_years_${experienceCounter}" id="exp_years_${experienceCounter}"><br>
                <label for="exp_desc_${experienceCounter}">Description/Responsibilities:</label><br>
                <textarea name="exp_desc_${experienceCounter}" id="exp_desc_${experienceCounter}" rows="3"></textarea><br>
                <button type="button" class="remove-entry">Remove</button>
            `;
            experienceContainer.appendChild(newExperienceEntry);
        });
    }

     // --- Add Education ---
    const addEducationButton = document.getElementById('add-education');
    const educationContainer = document.getElementById('education-container');
    let educationCounter = educationContainer.getElementsByClassName('education-entry').length;

    if (addEducationButton) {
        addEducationButton.addEventListener('click', function() {
            educationCounter++;
            const newEducationEntry = document.createElement('div');
            newEducationEntry.classList.add('education-entry');
            newEducationEntry.innerHTML = `
                 <h4>Education ${educationCounter}</h4>
                 <label for="degree_${educationCounter}">Degree/Certificate:</label>
                 <input type="text" name="degree_${educationCounter}" id="degree_${educationCounter}"><br>
                 <label for="institution_${educationCounter}">Institution:</label>
                 <input type="text" name="institution_${educationCounter}" id="institution_${educationCounter}"><br>
                 <label for="edu_years_${educationCounter}">Years (e.g., 2016-2020):</label>
                 <input type="text" name="edu_years_${educationCounter}" id="edu_years_${educationCounter}"><br>
                 <button type="button" class="remove-entry">Remove</button>
            `;
            educationContainer.appendChild(newEducationEntry);
        });
    }

    // --- Generic Remove Button Handler (for Skills, Experience, Education) ---
    // Use event delegation on the containers
    function setupRemoveButtons(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.addEventListener('click', function(event) {
                if (event.target && event.target.classList.contains('remove-entry')) {
                    // Find the parent entry div and remove it
                    let entryToRemove = event.target.closest('.skill-entry, .experience-entry, .education-entry');
                    if (entryToRemove) {
                        entryToRemove.remove();
                        // Optional: Renumber remaining items if strict numbering is needed by backend (though current backend handles gaps)
                    }
                }
            });
        }
    }

    setupRemoveButtons('skills-container');
    setupRemoveButtons('experience-container');
    setupRemoveButtons('education-container');

});