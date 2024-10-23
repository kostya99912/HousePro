document.addEventListener('DOMContentLoaded', function () {
    var userForm = document.getElementById('userForm');
    var masterForm = document.getElementById('masterForm');
    var normalUserBtn = document.getElementById('normalUserBtn');
    var masterUserBtn = document.getElementById('masterUserBtn');

    // Function to enable/disable form fields
    function setFormFieldsDisabled(form, disabled) {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            // Enable/disable fields
            input.disabled = disabled;
            
            // Remove required attribute from hidden fields and restore it for visible ones
            if (disabled) {
                input.removeAttribute('required');
            } else {
                // Restore the required attribute only for fields that should be mandatory
                if (input.hasAttribute('data-required')) {
                    input.setAttribute('required', 'required');
                }
            }
        });
    }

    // Function to toggle the visible form
    function toggleForm(isUserFormVisible) {
        if (isUserFormVisible) {
            userForm.style.display = 'block'; // Show user form
            masterForm.style.display = 'none'; // Hide master form
            setFormFieldsDisabled(masterForm, true);  // Disable master fields
            setFormFieldsDisabled(userForm, false);   // Enable user fields
        } else {
            userForm.style.display = 'none'; // Hide user form
            masterForm.style.display = 'block'; // Show master form
            setFormFieldsDisabled(userForm, true);    // Disable user fields
            setFormFieldsDisabled(masterForm, false); // Enable master fields
        }
    }

    // Button event handlers
    normalUserBtn.addEventListener('click', function () {	
        toggleForm(true);  // Show user form
    });

    masterUserBtn.addEventListener('click', function () {
        toggleForm(false);  // Show master form
    });

    // Initially show the user form
    toggleForm(true);
});