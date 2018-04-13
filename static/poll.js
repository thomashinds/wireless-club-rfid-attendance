function update() {
    $.ajax({
        url: '/card-data',
        success:  function(data) {
            $('#name').text(data.name);
            $('#uid').text(data.uid);
            if (data.recognized === 'no') {
                $('#register').style.visibility = 'visible'
            } else {
                $('#register').style.visibility = 'hidden'
            }
            update();
        },
        timeout: 500000 //If timeout is reached run again
    });
}

$(document).ready(function() {
    update();
});
