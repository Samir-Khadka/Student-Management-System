// Profile Section Management

let isEditMode = false;

function loadProfileSection() {
    console.log('loadProfileSection called');
    const user = getCurrentUserData();

    if (!user) {
        console.error('No user data found');
        return;
    }

    // Update display fields
    const elements = {
        username: document.getElementById('profile-username'),
        fullname: document.getElementById('profile-fullname-input'), // Input field
        email: document.getElementById('profile-email'),
        role: document.getElementById('profile-role'),
        initials: document.getElementById('profile-initials-modal'),
        avatar: document.getElementById('profile-avatar-modal'),
        // joined: document.getElementById('profile-joined') // Removed from modal design
    };

    // Update text content for display divs
    if (elements.username) elements.username.textContent = user.username || '';
    if (elements.role) elements.role.textContent = capitalize(user.role) || '';

    // Update input values
    if (elements.fullname) elements.fullname.value = user.full_name || '';
    if (elements.email) elements.email.value = user.email || '';

    // Handle avatar
    const initials = getInitials(user.full_name || user.username || 'U');
    if (elements.initials) elements.initials.textContent = initials;

    if (user.profile_picture && elements.avatar) {
        const apiUrl = API_CONFIG.BASE_URL.replace('/api', '');
        const profilePictureUrl = `${apiUrl}${user.profile_picture}?t=${new Date().getTime()}`;
        console.log('Loading profile picture from:', profilePictureUrl);

        elements.avatar.innerHTML = `<img src="${profilePictureUrl}" alt="${user.full_name}" 
            onerror="console.error('Failed to load image:', this.src); this.style.display='none'; this.parentElement.querySelector('span').style.display='block';">
            <span id="profile-initials-modal" style="display:none">${initials}</span>`;
    } else if (elements.initials) {
        elements.avatar.innerHTML = `<span id="profile-initials-modal">${initials}</span>`;
    }
}

function toggleEditMode() {
    console.log('toggleEditMode called, current state:', isEditMode);
    isEditMode = !isEditMode;

    const form = document.getElementById('profile-form');
    const actions = document.getElementById('profile-actions');
    const editBtn = document.getElementById('edit-profile-btn');

    const inputs = [
        document.getElementById('profile-email'),
        document.getElementById('profile-fullname-input')
    ];

    inputs.forEach(input => {
        if (input) {
            input.disabled = !isEditMode;
            if (isEditMode) input.classList.add('editing');
            else input.classList.remove('editing');
        }
    });

    if (actions) {
        actions.style.display = isEditMode ? 'flex' : 'none';
        console.log('Actions display set to:', actions.style.display);
    } else {
        console.error('Profile actions container not found');
    }

    if (editBtn) {
        editBtn.style.display = isEditMode ? 'none' : 'inline-flex';
    } else {
        console.error('Edit profile button not found');
    }

    if (!isEditMode) {
        // Reset form if cancelled
        loadProfileSection();
    }
}

// Ensure global access
window.toggleEditMode = toggleEditMode;

async function saveProfile(event) {
    event.preventDefault();

    const fullnameInput = document.getElementById('profile-fullname-input');
    const emailInput = document.getElementById('profile-email');

    const updateData = {
        full_name: fullnameInput.value,
        email: emailInput.value
    };

    try {
        showToast('Updating profile...', 'info');
        const response = await updateUserProfile(updateData);

        if (response && response.user) {
            // Update local storage
            const currentUser = getCurrentUserData();
            const updatedUser = { ...currentUser, ...response.user };
            localStorage.setItem(APP_SETTINGS.USER_KEY, JSON.stringify(updatedUser));

            // Update UI
            updateUserInfo(updatedUser);
            loadProfileSection();
            toggleEditMode();

            showToast('Profile updated successfully', 'success');
        }
    } catch (error) {
        console.error('Profile update failed:', error);
        showToast(error.message || 'Failed to update profile', 'error');
    }
}

async function handleProfilePictureSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate
    if (!file.type.startsWith('image/')) {
        showToast('Please select an image file', 'error');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showToast('File size must be less than 5MB', 'error');
        return;
    }

    try {
        // Show preview immediately
        const reader = new FileReader();
        reader.onload = function (e) {
            const profileAvatar = document.getElementById('profile-avatar-modal');
            if (profileAvatar) {
                profileAvatar.innerHTML = `<img src="${e.target.result}" alt="Profile Preview" style="opacity: 0.5;">`;
            }
        };
        reader.readAsDataURL(file);

        showToast('Uploading picture...', 'info');
        const response = await uploadProfilePicture(file);

        if (response && response.profile_picture) {
            // Update local storage
            const currentUser = getCurrentUserData();
            currentUser.profile_picture = response.profile_picture;
            localStorage.setItem(APP_SETTINGS.USER_KEY, JSON.stringify(currentUser));

            // Update UI
            updateUserInfo(currentUser);
            loadProfileSection();

            showToast('Profile picture updated!', 'success');
        }
    } catch (error) {
        console.error('Upload failed:', error);
        showToast(error.message || 'Failed to upload picture', 'error');
    }

    // Reset input
    event.target.value = '';
}
