$(document).ready(() => {
    $(document).on('click', '#for_user > *', (e) => {
        $(e.currentTarget).remove();
    });
});
