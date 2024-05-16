const createPostButton = document.querySelector(".create-post-btn");
const createPostButton2 = document.querySelector("#create-post-btn-2");

const newPostSection = document.querySelector(".create-post");
const hideNewPostButton = document.querySelector(".hide1");

const allPostsButton = document.querySelector("#all-posts-btn");
const allPostSection = document.querySelector("#all-posts");
const hideAllPostButton = document.querySelector("#hide2");

const editPostButtons = document.querySelectorAll("#edit-post");
const deletePostButtons = document.querySelectorAll("#delete-post");

const backToTopButton = document.querySelector("#btn-back-to-top");

const followButton = document.querySelector(".follow-btn");
const unFollowButton = document.querySelector(".unfollow-btn");

const heartButtons = document.querySelectorAll(".heart");


// Initial View
initialView();

// Create new post events
if (createPostButton) {
    createPostButton.addEventListener("click", () => {
        hideElement(createPostButton);
        showElement(newPostSection);
    });

    hideNewPostButton.addEventListener("click", () => {
        hideElement(newPostSection);
        showElement(createPostButton);
    });

    createPostButton2.addEventListener("click", (event) => {
        event.preventDefault();
        hideElement(createPostButton);
        showElement(newPostSection);
    
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// All post events
if (allPostsButton) {

    allPostsButton.addEventListener("click", () => {
        hideElement(allPostsButton);
        showElement(allPostSection);
    });


    hideAllPostButton.addEventListener("click", () => {
        hideElement(allPostSection);
        showElement(allPostsButton);
    });

}

// Editing post 1. način
if (editPostButtons) {

    editPostButtons.forEach(button => {

        button.addEventListener("click", function () {

            const post_id = Number(this.dataset.post_id);
            const old_content = this.dataset.content;

            // When edit button is clicked new section should be open-ed
            const postDisplayDiv = document.querySelector(`#post-display${post_id}`)

            const postEditDiv = document.querySelector(`#post-edit${post_id}`)

            hideElement(postDisplayDiv);
            showElement(postEditDiv);

            const textarea = document.querySelector(`#edit-area${post_id}`);
            textAreaDisplay(textarea);

            // When edit button is clicked - two more button will be there Back and Save

            // If back button is clicked
            document.querySelectorAll("#back-btn").forEach(button => {
                button.addEventListener("click", () => {
                    hideElement(postEditDiv);
                    showElement(postDisplayDiv);
                })
            });

            // If save button is clicked
            document.querySelectorAll("#save-btn").forEach(button => {
                button.addEventListener("click", () => {
                    let new_content = textarea.value;
    
                    // If nothing is changed everything should be as like back button is hit
                    if (new_content === old_content) {
                        hideElement(postEditDiv);
                        showElement(postDisplayDiv);
                    }
                    else {
                        editPostAction(post_id, new_content);
                    }
                });
            });
        });
    });
}

// Deleting post 2. način
if (deletePostButtons) {
    deletePostButtons.forEach(button => {
        button.addEventListener("click", () => {
            post_id = Number(button.dataset.post_id);
            deletePostAction(post_id);
        });
    });
}

// Follow user
if (followButton) {
    followButton.addEventListener("click", () => {
        let username_to_follow = String(followButton.dataset.followee_username);
        let username_of_follower = String(followButton.dataset.follower_username);

        console.log(`User ${username_of_follower} start to follow ${username_to_follow}`);

        fetch(`/follow/${username_to_follow}`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then(data => {
                console.log("Sucess:", data);
                window.location.reload();
            })
            .catch(error => {
                console.error("Error:", error);
            });
    });
}

// Unfollow user
if (unFollowButton) {
    unFollowButton.addEventListener("click", function () {
        let username_to_unfollow = String(this.dataset.followee_username);
        let username_of_follower = String(this.dataset.follower_username);

        console.log(`User ${username_of_follower} unfollowes ${username_to_unfollow}`);

        fetch(`/unfollow/${username_to_unfollow}`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then(data => {
                console.log("Sucess:", data);
                window.location.reload();
            })
            .catch(error => {
                console.error("Error:", error);
            });

    })
}

// Liking and not liking the post
if (heartButtons) {
    heartButtons.forEach(button => {

        button.addEventListener("click", () => {

            const post_id = button.closest("div").parentNode.dataset.post_id;

            // When button is clicked it will trigger some action
            const action = String(button.dataset.action);
            console.log(action);

            fetch(`/${action}/${post_id}`)
            .then(response => response.json())
            .then(data => {
                console.log("Sucess:", data);
                window.location.reload();
            })
            .catch(error => {
                console.error("Error:", error);
            });
        })
    });
}

function hideElement(element) {
    element.classList.add("hide");
    element.classList.remove("show");
}

function showElement(element) {
    element.classList.add("show");
    element.classList.remove("hide");
}

function textAreaDisplay(textarea) {
    let lineHeight = textarea.style.lineHeight;
    let lines = textarea.value.split(/\r|\r\n|\n/).length + 1;
    let maxLines = 7;

    textarea.rows = lines > maxLines ? maxLines : lines;
    textarea.style.overflowY = lines > maxLines ? 'scroll' : 'hidden';

    textarea.addEventListener('input', event => {
        textarea.rows = 1;
        lines = Math.ceil(textarea.scrollHeight / lineHeight);
        textarea.rows = lines > maxLines ? maxLines : lines;
        textarea.style.overflowY = lines > maxLines ? 'scroll' : 'hidden';
    });
}

function deletePostAction(post_id) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(`/posts/${post_id}`, {
        method: "DELETE",
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
        .then(resposne => resposne.json())
        .then(data => {
            window.location.reload();
        })
}

function editPostAction(post_id, new_content) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(`/posts/${post_id}`, {
        method: "PUT",
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            edited: true,
            content: new_content,
        })
    })
        .then(resposne => resposne.json())
        .then(data => {
            window.location.reload();
        })
}

function initialView() {

    if (allPostSection != null) {
        hideElement(allPostsButton);
        showElement(allPostSection);
    }

    if (newPostSection != null) {
        hideElement(newPostSection);
        showElement(createPostButton);
    }
}



// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function () {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        backToTopButton.style.display = "block";
    }
    else {
        backToTopButton.style.display = "none";
    }
};

// When the user clicks on the button, scroll to the top of the document
backToTopButton.addEventListener("click", () => {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
});
